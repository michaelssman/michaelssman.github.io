# ECS 微服务启动顺序优化

目标：让 hhjava 等基础设施就绪后，再依次启动微服务，降低多个 JVM（Java Virtual Machine，Java 虚拟机）同时初始化造成的 CPU 高峰。

## 方案

启动顺序：**Nacos、MySQL 就绪 → user → gateway → backup-file → fund**。MinIO 在 backup-file 启动前单独检查；先恢复登录，不因文件服务故障阻塞前面的网关。

systemd 是 Linux 的服务管理器，`.service` 文件描述服务怎样运行。本文新增的 **drop-in（附加配置）**放在 `.service.d/` 中，不覆盖原服务文件，方便回退。

现有 `Type=simple` 只表示 Java 进程已创建，不代表应用可用。我们用 `ExecStartPost` 等待接口响应，再用 `After` 安排下一个服务；`ExecStartPre` 则是在 Java 启动前检查依赖。[systemd 官方说明](https://github.com/systemd/systemd/blob/main/man/systemd.service.xml)

应用之间使用 `Wants + After`：请求按顺序启动，但不因前一个应用失败就强制停止后一个。所有应用对基础设施检查使用 `Requires + After`：检查失败，本轮应用不能启动。[依赖关系说明](https://github.com/systemd/systemd/blob/main/man/systemd.unit.xml)

这不是 CPU 限流或持续健康监控；整体启动可能变慢，运行期自动重试也不保证严格串行。

## 1. 准备与备份

### 1.1 确认环境

先完成 [Spring Boot 部署到阿里云 ECS](SpringBoot部署到阿里云ECS.md)。本教程要求：

- Nacos、MySQL、MinIO 已能随 Docker 启动，四个 hhjava 服务原本运行正常并已开机启用。
- MySQL 容器名为 `mysql`，其中已有有效的 `MYSQL_ROOT_PASSWORD`；脚本沿用它，不填写或打印真实密码。
- 网关地址为 `https://47.120.56.43`，证书有效。如果地址、端口或容器名变了，先修改下文脚本中的对应值。

**以下全部在 ECS 的 root 终端操作，当前目录不限。每块命令成功后再进行下一步；有错误就停下排查。** 保留另一条 SSH 连接或云控制台入口，后面的验证会短暂停服。

```bash
free -h
command -v bash curl docker timeout runuser vi
docker ps --format 'table {{.Names}}\t{{.Status}}'
systemctl is-active hhjava-user hhjava-gateway hhjava-backup-file hhjava-fund
systemctl is-enabled hhjava-user hhjava-gateway hhjava-backup-file hhjava-fund
```

命令应都存在，四个服务应分别显示 `active` 和 `enabled`。先处理已有故障，不用本教程修改原有启用范围。

### 1.2 避免覆盖已有文件

```bash
for path in \
  /usr/local/libexec/hhjava-wait-ready \
  /etc/systemd/system/hhjava-infra-ready.service \
  /etc/systemd/system/hhjava-user.service.d/20-startup-order.conf \
  /etc/systemd/system/hhjava-gateway.service.d/20-startup-order.conf \
  /etc/systemd/system/hhjava-backup-file.service.d/20-startup-order.conf \
  /etc/systemd/system/hhjava-fund.service.d/20-startup-order.conf; do
  if test -e "$path" || test -L "$path"; then
    printf '已存在，停止并检查：%s\n' "$path"
  fi
done
```

**预期没有输出。** 有输出说明同名文件已存在，不能继续覆盖。然后备份原服务配置：

```bash
HHJAVA_ORDER_BACKUP=$(mktemp -d /var/backups/hhjava-startup-order.XXXXXX)
for service in hhjava-user hhjava-gateway hhjava-backup-file hhjava-fund; do
  cp -a "/etc/systemd/system/$service.service" "$HHJAVA_ORDER_BACKUP/"
  if test -d "/etc/systemd/system/$service.service.d"; then
    cp -a "/etc/systemd/system/$service.service.d" "$HHJAVA_ORDER_BACKUP/"
  fi
done
printf '保存此备份路径，回退时使用：%s\n' "$HHJAVA_ORDER_BACKUP"
```

目录仅 root 可读。记下输出路径；换终端后，要将 `HHJAVA_ORDER_BACKUP` 重新设为这个真实路径。

## 2. 安装等待脚本

脚本每隔 2 秒检查一次，就绪立即退出，约 180 秒仍未就绪则失败。它被多个服务共用，不需要四份重复脚本。

```bash
install -d -m 0755 /usr/local/libexec
vi /usr/local/libexec/hhjava-wait-ready
```

编辑方法：按 `i`，粘贴完整内容，按 `Esc`，输入 `:wq` 并回车保存。后面的配置文件也用此方法编辑。

```bash
#!/usr/bin/env bash
set -u
PATH=/usr/sbin:/usr/bin:/sbin:/bin
export PATH
mode="${1:-}"

case "$mode" in
  infra|minio|user|gateway|backup-file|fund) ;;
  *) printf '未知检查类型\n' >&2; exit 2 ;;
esac
if [[ "$mode" == infra && "$EUID" -ne 0 ]]; then
  printf '基础设施检查需要 root，不要给应用账号授予 Docker 权限\n' >&2
  exit 2
fi

http_ready() {
  local expected="$1" url="$2" code
  shift 2
  # 不跟随重定向、不跳过证书校验；401 只能由指定的受保护接口返回。
  code=$(curl --noproxy '*' --silent --connect-timeout 2 --max-time 5 \
    --output /dev/null --write-out '%{http_code}' "$@" "$url" 2>/dev/null) || return 1
  [[ "$code" == "$expected" ]]
}

mysql_ready() {
  local result
  # 秘密只在已有容器内部使用；不进入命令参数、脚本正文或日志输出。
  result=$(timeout 5 docker exec mysql sh -c '
    test -n "$MYSQL_ROOT_PASSWORD" || exit 1
    export MYSQL_PWD="$MYSQL_ROOT_PASSWORD"
    exec mysql --user=root --connect-timeout=3 --batch \
      --skip-column-names --execute="SELECT 1"
  ' 2>/dev/null) || return 1
  [[ "$result" == 1 ]]
}

ready() {
  case "$mode" in
    infra)
      http_ready 200 http://127.0.0.1:8848/nacos/v1/console/health/readiness \
        && mysql_ready ;;
    minio) http_ready 200 http://127.0.0.1:9000/minio/health/ready ;;
    user) http_ready 200 http://127.0.0.1:8080/user/oauth2/jwks ;;
    gateway)
      http_ready 200 https://47.120.56.43/user/oauth2/jwks \
        --resolve 47.120.56.43:443:127.0.0.1 ;;
    backup-file) http_ready 401 http://127.0.0.1:63030/files/database ;;
    fund) http_ready 401 http://127.0.0.1:8083/fund/v1/ledger ;;
  esac
}

# 每次检查都有网络超时，整体等待约 180 秒；最后一次检查可能略超出此时间。
deadline=$((SECONDS + 180))
while (( SECONDS < deadline )); do
  if ready; then
    printf '启动检查通过：%s\n' "$mode"
    exit 0
  fi
  sleep 2
done
printf '启动检查超时：%s；请单独检查对应依赖\n' "$mode" >&2
exit 1
```

设置权限并检查语法：

```bash
chown root:root /usr/local/libexec/hhjava-wait-ready
chmod 0755 /usr/local/libexec/hhjava-wait-ready
bash -n /usr/local/libexec/hhjava-wait-ready
```

语法检查应无输出。再趁服务仍在运行，验证脚本和各服务账号的执行权限：

```bash
/usr/local/libexec/hhjava-wait-ready infra
runuser -u hhjava-user -- /usr/local/libexec/hhjava-wait-ready user
runuser -u hhjava-gateway -- /usr/local/libexec/hhjava-wait-ready gateway
runuser -u hhjava-backup-file -- /usr/local/libexec/hhjava-wait-ready minio
runuser -u hhjava-backup-file -- /usr/local/libexec/hhjava-wait-ready backup-file
runuser -u hhjava-fund -- /usr/local/libexec/hhjava-wait-ready fund
```

每条应输出“启动检查通过”。这里有三个要点：

- `infra` 等待 Nacos 的就绪接口返回 200，并实际执行 MySQL 的只读 `SELECT 1`，不是只检查端口。
- user、gateway 使用现有 JWKS 公钥接口检查；相关概念见 [JWT 与 JWKS](认证授权和网关/JWT与JWKS.md)。gateway 的 `--resolve` 让请求走本机回环地址，同时正常校验证书。
- backup-file、fund 预期返回匿名 **401（缺少登录凭据）**，只证明 HTTP 安全处理链已响应，不代表全部业务健康。不要改成放开接口或跳过证书校验。

## 3. 创建基础设施检查单元

用 `vi /etc/systemd/system/hhjava-infra-ready.service` 新建文件，写入：

```ini
[Unit]
Description=Check hhjava infrastructure readiness at startup
Wants=network-online.target
Requires=docker.service
After=network-online.target docker.service

[Service]
Type=oneshot
User=root
ExecStart=/usr/local/libexec/hhjava-wait-ready infra
TimeoutStartSec=210s
RemainAfterExit=yes
```

`oneshot` 表示脚本检查一次后退出；`RemainAfterExit=yes` 让成功结果保持 `active (exited)`，供本轮启动共用。该单元由应用自动拉起，不需要单独 `enable`。

**它不是实时监控。** 应用普通重启不会重做基础设施检查；需要只读复查时直接运行脚本的 `infra` 模式。不要在应用运行中停止或重启这个检查单元，强依赖可能连带影响应用。

## 4. 添加四个服务的附加配置

先创建目录：

```bash
for service in hhjava-user hhjava-gateway hhjava-backup-file hhjava-fund; do
  install -d -m 0755 "/etc/systemd/system/$service.service.d"
done
```

分别用 `vi` 编辑下面四个文件，保留原 `.service`、受限账号、秘密文件和内存设置。

### user

文件：`/etc/systemd/system/hhjava-user.service.d/20-startup-order.conf`

```ini
[Unit]
Requires=hhjava-infra-ready.service
After=hhjava-infra-ready.service
StartLimitIntervalSec=1800s
StartLimitBurst=3

[Service]
ExecStartPost=/usr/local/libexec/hhjava-wait-ready user
TimeoutStartSec=600s
RestartSec=30s
```

### gateway

文件：`/etc/systemd/system/hhjava-gateway.service.d/20-startup-order.conf`

```ini
[Unit]
Requires=hhjava-infra-ready.service
Wants=hhjava-user.service
After=hhjava-infra-ready.service hhjava-user.service
StartLimitIntervalSec=1800s
StartLimitBurst=3

[Service]
ExecStartPost=/usr/local/libexec/hhjava-wait-ready gateway
TimeoutStartSec=600s
RestartSec=30s
```

### backup-file

文件：`/etc/systemd/system/hhjava-backup-file.service.d/20-startup-order.conf`

```ini
[Unit]
Requires=hhjava-infra-ready.service
Wants=hhjava-gateway.service
After=hhjava-infra-ready.service hhjava-gateway.service
StartLimitIntervalSec=1800s
StartLimitBurst=3

[Service]
ExecStartPre=/usr/local/libexec/hhjava-wait-ready minio
ExecStartPost=/usr/local/libexec/hhjava-wait-ready backup-file
TimeoutStartSec=600s
RestartSec=30s
```

### fund

文件：`/etc/systemd/system/hhjava-fund.service.d/20-startup-order.conf`

```ini
[Unit]
Requires=hhjava-infra-ready.service
Wants=hhjava-backup-file.service
After=hhjava-infra-ready.service hhjava-backup-file.service
StartLimitIntervalSec=1800s
StartLimitBurst=3

[Service]
ExecStartPost=/usr/local/libexec/hhjava-wait-ready fund
TimeoutStartSec=600s
RestartSec=30s
```

这些配置中：`TimeoutStartSec=600s` 给启动前后检查留足总时间，不是固定等待 600 秒；保留原 `Restart=on-failure`，失败间隔 30 秒重试，30 分钟内最多启动 3 次。应用之间的顺序不等于成功保证，仍需各自处理业务依赖故障。

统一设置新增配置的权限：

```bash
chown root:root /etc/systemd/system/hhjava-infra-ready.service
chmod 0644 /etc/systemd/system/hhjava-infra-ready.service
for service in hhjava-user hhjava-gateway hhjava-backup-file hhjava-fund; do
  chown root:root "/etc/systemd/system/$service.service.d/20-startup-order.conf"
  chmod 0644 "/etc/systemd/system/$service.service.d/20-startup-order.conf"
done
```

检查 Docker 的脚本只由 root 单元执行，不给应用账号 Docker 管理权限。原有附加配置若也有 `ExecStartPre/Post`，会影响最终执行列表，应核对后保留必要检查，不随意清空。

## 5. 在维护窗口启用并验证

### 5.1 检查配置，暂停证书定时任务

```bash
systemd-analyze verify \
  /etc/systemd/system/hhjava-infra-ready.service \
  /etc/systemd/system/hhjava-user.service \
  /etc/systemd/system/hhjava-gateway.service \
  /etc/systemd/system/hhjava-backup-file.service \
  /etc/systemd/system/hhjava-fund.service
systemctl is-active hhjava-certbot-renew.service
```

配置检查不能有本次新增错误；证书续期服务应为 `inactive`，若为 `active`，等它结束再继续。保存定时任务原状态，避免它在测试期间重启网关：

```bash
HHJAVA_RENEW_WAS_ACTIVE=$(systemctl is-active hhjava-certbot-renew.timer || true)
printf '记下定时任务原状态：%s\n' "$HHJAVA_RENEW_WAS_ACTIVE"
if test "$HHJAVA_RENEW_WAS_ACTIVE" = active; then
  systemctl stop hhjava-certbot-renew.timer
fi
systemctl is-active hhjava-certbot-renew.service
```

再次确认续期服务未运行。**后续无论成功还是失败，都要执行 5.3 的恢复命令。** 若中途断开终端，先按记下的原状态恢复定时任务。

### 5.2 重载配置，顺序启动

```bash
systemctl stop hhjava-fund hhjava-backup-file hhjava-gateway hhjava-user
systemctl daemon-reload
systemctl show hhjava-user hhjava-gateway hhjava-backup-file hhjava-fund \
  -p After -p Wants -p Requires -p ExecStartPre -p ExecStartPost -p TimeoutStartUSec
```

`daemon-reload` 只重新读取配置。确认输出包含新增依赖、检查脚本及 600 秒超时后，再启动：

```bash
systemctl start hhjava-user hhjava-gateway hhjava-backup-file hhjava-fund
```

另一个 ECS 终端查看进度，不反复执行启动命令：

```bash
vmstat 2 10
systemctl show hhjava-user hhjava-gateway hhjava-backup-file hhjava-fund \
  -p ActiveState -p SubState -p NRestarts
journalctl -b -u hhjava-infra-ready -u hhjava-user -u hhjava-gateway \
  -u hhjava-backup-file -u hhjava-fund --no-pager -o short-monotonic -n 120
```

预期：日志先显示基础设施通过，再按顺序显示四个应用通过。等待时 `activating (start-post)` 正常，最终应用应为 `active`，检查单元为 `active (exited)`。`vmstat` 忽略第一条统计数据，观察后续每 2 秒采样；日志分享前先脱敏。

### 5.3 检查入口，恢复定时任务

```bash
curl --noproxy '*' --silent --show-error --max-time 10 \
  --output /dev/null --write-out 'JWKS HTTP=%{http_code}\n' \
  https://47.120.56.43/user/oauth2/jwks
curl --noproxy '*' --silent --show-error --max-time 10 \
  --output /dev/null --write-out 'Fund HTTP=%{http_code}\n' \
  https://47.120.56.43/fund/v1/ledger
if test "$HHJAVA_RENEW_WAS_ACTIVE" = active; then
  systemctl start hhjava-certbot-renew.timer
fi
systemctl is-active hhjava-certbot-renew.timer
```

接口预期分别为 200、401，定时任务应恢复原状态。然后从 Mac 或 App 验证真实登录、文件和基金功能，不能只看匿名接口。

这次通过后，再单独安排整机重启验收，确认基础设施也从停止状态启动时顺序仍正确；记录 CPU、内存和恢复时间。顺序启动通过不等于冷启动或压力测试通过。

## 6. 出错时怎么处理和回退

### 6.1 先看失败的检查

- `infra` 超时：查 Nacos、MySQL 容器名及数据库认证。
- `gateway` 超时：查 user、网关路由和 HTTPS 证书。
- `minio` 超时：查 MinIO，不为此停止已经恢复的登录服务。
- `start-post` 超时或 `start-limit-hit`：查看对应应用日志，先修原因，不循环重启。

基础设施依赖失败后，不会自动保证补跑整组应用。修复后如需重新检查，先按 5.1 协调证书任务，在维护窗口执行：

```bash
systemctl stop hhjava-fund hhjava-backup-file hhjava-gateway hhjava-user
systemctl stop hhjava-infra-ready
systemctl reset-failed hhjava-infra-ready hhjava-user hhjava-gateway hhjava-backup-file hhjava-fund
systemctl start hhjava-user hhjava-gateway hhjava-backup-file hhjava-fund
```

再做 5.3 的验收和定时任务恢复。只有单个应用故障时，先单独排查，不默认重启全部服务。

### 6.2 撤销本次配置

先按 5.1 协调证书任务。确认 `HHJAVA_ORDER_BACKUP` 是第 1 步记录的真实备份目录；换终端后须重新设置该变量。

```bash
test -n "$HHJAVA_ORDER_BACKUP" && test -d "$HHJAVA_ORDER_BACKUP"
```

检查成功后，停服务并将本教程新增的文件移入备份目录。**只移动这些指定文件，不删除原服务或其他附加配置。**

```bash
systemctl stop hhjava-fund hhjava-backup-file hhjava-gateway hhjava-user
systemctl stop hhjava-infra-ready
for service in hhjava-user hhjava-gateway hhjava-backup-file hhjava-fund; do
  mv -n "/etc/systemd/system/$service.service.d/20-startup-order.conf" \
    "$HHJAVA_ORDER_BACKUP/$service.20-startup-order.conf"
done
mv -n /etc/systemd/system/hhjava-infra-ready.service "$HHJAVA_ORDER_BACKUP/"
mv -n /usr/local/libexec/hhjava-wait-ready "$HHJAVA_ORDER_BACKUP/"
```

核对新增文件都已离开原位置、存在于备份目录，再执行下一块命令。`mv -n` 不覆盖同名目标；若移动失败或只安装了部分文件，先处理相应情况，不继续启动。

```bash
systemctl daemon-reload
systemctl reset-failed hhjava-user hhjava-gateway hhjava-backup-file hhjava-fund
systemctl start hhjava-user hhjava-gateway hhjava-backup-file hhjava-fund
if test "$HHJAVA_RENEW_WAS_ACTIVE" = active; then
  systemctl start hhjava-certbot-renew.timer
fi
```

按 5.3 重新验收。回退不改程序包、数据库、Nacos、MinIO 数据或密钥；移走的配置仍可恢复。

实际实施成功后，将验证过的脚本、检查单元和附加配置纳入 hhjava 的 `scripts/ecs/`，同步部署记录，避免只改服务器而无法复现。
