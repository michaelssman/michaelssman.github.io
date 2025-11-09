# Nginx

## 前后端分离

![image-20240705114631016](assets/image-20240705114631016.png)

## 前端项目部署思路

**反向代理及负载均衡**

在一台服务器上部署网站，只有一台服务器，若服务器发生故障，网站就无法运行。

所以在多台服务器上都部署网站。通过访问每个服务器的ip都可以访问网站。

![image-20210426110913007](assets/image-20210426110913007.png)

通过nginx来进行配置，功能如下

- 通过nginx的反向代理功能访问后台的网关资源，并且可以设置负载均衡。
- 通过nginx的静态服务器功能访问前端静态页面。

## 配置nginx

在下面的地址中输入cmd回车，输入nginx，没报错就说明成功。

![image-20240709221707185](assets/image-20240709221707185.png)

2、解压资料文件夹中的前端项目app-web.zip

3、配置nginx.conf文件

在nginx安装的conf目录下新建一个文件夹`leadnews.conf`，在当前文件夹中新建`heima-leadnews-app.conf`文件

heima-leadnews-app.conf配置如下：

```
# 配置反向代理
upstream  heima-app-gateway{
    server localhost:51601; # 网关地址修改（localhost:51601）
}

server {
	listen 8801; # 访问端口修改(8801)
	location / {
		root C:/Users/micha/Documents/java_demo/heima-leadnews/app-web/; #前端项目目录修改
		index index.html;
	}
	
	location ~/app/(.*) {
		proxy_pass http://heima-app-gateway/$1;
		proxy_set_header HOST $host;  # 不改变源请求头的值
		proxy_pass_request_body on;  #开启获取请求体
		proxy_pass_request_headers on;  #开启获取请求头
		proxy_set_header X-Real-IP $remote_addr;   # 记录真实发出请求的客户端IP
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;  #记录代理信息
	}
}
```

nginx.conf   把里面注释的内容和静态资源配置相关删除，引入heima-leadnews-app.conf文件加载

```
#user  nobody;
worker_processes  1;

events {
    worker_connections  1024;
}
http {
    include       mime.types;
    default_type  application/octet-stream;
    sendfile        on;
    keepalive_timeout  65;
	# 引入自定义配置文件
	include leadnews.conf/*.conf;
}
```

4、启动nginx

​    在nginx安装包中使用命令提示符打开，输入命令nginx启动项目

​    可查看进程，检查nginx是否启动

​    **重新加载nginx配置文件：**`nginx -s reload`

5、启动app微服务和对应网关

6、打开前端项目进行测试  -- >  http://localhost:8801

​     用谷歌浏览器打开，调试移动端模式进行访问

**通过nginx的虚拟主机功能，使用同一个nginx访问多个项目，其它前端项目配置和上面一样，只是修改对应的网关、端口、前端项目目录。**

## 如何发布网站系列：反向代理及负载均衡

### 引言：多服务器架构的必要性

当单台服务器部署网站时，存在单点故障风险（服务器故障导致网站不可用）且并发处理能力有限。通过部署多台服务器同时提供服务，可有效避免单点故障并提升系统并发处理能力。

## 反向代理

访问**Nginx服务器**转发到**后端其他服务器**就叫做**反向代理**。

### Nginx 配置反向代理步骤

1. **修改 Nginx 配置文件**：删除原有网站部署相关配置（如和），仅保留请求转发功能。
2. **设置代理目标**：在配置中添加指令，指定后端服务器地址（如http://192.168.1.20）。
3. **验证效果**：保存配置并重启 Nginx 后，访问 Nginx 服务器 IP 即可打开指向的后端网站。

```
server {
	listen 8801; # 访问端口修改(8801)
	location / {
		proxy_pass http://192.168.1.20; # 将请求转发到http://192.168.1.20这个网站
	}
	
	location ~/app/(.*) {
		proxy_pass http://heima-app-gateway/$1;
		proxy_set_header HOST $host;  # 不改变源请求头的值
		proxy_pass_request_body on;  #开启获取请求体
		proxy_pass_request_headers on;  #开启获取请求头
		proxy_set_header X-Real-IP $remote_addr;   # 记录真实发出请求的客户端IP
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;  #记录代理信息
	}
}
```

## 负载均衡

将客户端请求**分配到多个后端服务器**的机制，通过 Nginx 的模块实现服务器集群管理，提升系统可用性和处理效率。

将`proxy_pass`后面的服务器地址改为一个地址池，就实现了一个负载均衡。

### Nginx 配置负载均衡核心步骤

1. **定义服务器集群（upstream 模块）**：在代码块上方添加配置，定义集群名称（如）及后端服务器列表。

- 示例配置：

- 故障处理参数：（服务器被 "拉黑" 时间）和（100 秒内允许的最大失败次数），超过阈值服务器暂时下线，100 秒后自动恢复。

1. **关联反向代理与集群**：将指令的目标地址改为集群名称（如）。

1. **编译 Nginx 时的注意事项**：需添加模块以支持功能。

```
# 配置反向代理
upstream  app_web{
	#ip_hash;
	least_conn;
    server 192.168.1.20:80 fail_timeout=100s max_fails=10 weight=3;    
    server 192.168.1.21:80 fail_timeout=100s max_fails=10 weight=2;    
    server 192.168.1.22:80 fail_timeout=100s max_fails=10 weight=1;
}

server {
	listen 8801; # 访问端口修改(8801)
	location / {
		proxy_pass http://app_web; # 将请求转发到http://192.168.1.20这个网站
	}
	
	location ~/app/(.*) {
		proxy_pass http://heima-app-gateway/$1;
		proxy_set_header HOST $host;  # 不改变源请求头的值
		proxy_pass_request_body on;  #开启获取请求体
		proxy_pass_request_headers on;  #开启获取请求头
		proxy_set_header X-Real-IP $remote_addr;   # 记录真实发出请求的客户端IP
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;  #记录代理信息
	}
}
```

### 负载均衡算法

- **默认轮询**：按服务器配置顺序依次轮流分配请求。
- **加权轮询**：为服务器分配权重`weight`，权重越高接收请求越多。
- **会话保持**：在中添加配置`ip_hash`，使同一 IP 客户端始终访问同一后端服务器，确保会话一致性。
- **最小连接数分配**：在中添加配置`least_conn`，Nginx 实时监控后端服务器活跃连接数，将新请求优先分配给当前连接数最少的服务器。

## 使用 1Panel 工具配置负载均衡

### 步骤

1. **创建静态网站**：在 1Panel 面板中创建静态网站，填写内网 IP 作为域名。

1. **配置负载均衡**：

- 选择 "负载均衡" 功能，编辑名称并填写后端 3 台 Web 服务器地址。

- 选择负载均衡算法（默认轮询、ip_hash 或最小连接数least_conn），确认创建。

1. **创建反向代理**：

- 填写名称，后端代理地址指定为已创建的负载均衡名称，完成配置。

1. **验证效果**：访问 1Panel 服务器 IP，多次刷新可观察请求被转发到不同后端 Web 服务器。

## 总结

通过 Nginx 的反向代理和负载均衡功能，可实现多服务器协同工作，解决单点故障并提升并发处理能力。配置方式包括手动修改 Nginx 配置文件（适合技术人员）和使用 1Panel 等工具（简化配置流程），可根据实际需求选择。
