# hosts

## 配置Hosts

在ipaddress中查找github.com与github.global.ssl.fastly.net对应的ip，配置到hosts即可。

```shell
sudo vi /etc/hosts
```

```
https://www.ipaddress.com/
```

```
xxxx  github.global.ssl.fastly.net
xxxx  github.com
```

在`/etc/hosts`中添加：

```
151.101.72.249 github.http://global.ssl.fastly.net
140.82.113.4 github.com
```

## Windows清除DNS缓存：

修改hosts文件后，你可能需要清除DNS缓存才能让更改生效。打开命令提示符（以管理员身份）并输入`ipconfig /flushdns`。

##  设置终端代理

```sh
PS C:\Users\micha> git config --global https.proxy http://127.0.0.1:10809
PS C:\Users\micha> git config --global http.proxy http://127.0.0.1:10809
```

## ping github.com超时

针对Windows系统中`ping github.com`出现超时的问题，通常是由于DNS解析失败或网络限制导致的。以下是综合多个解决方案的步骤和注意事项：

---

### **解决方法**
#### **1. 修改Hosts文件** 
**步骤：**

1. **获取最新IP地址**  
   - 访问IP查询网站（如 [IPAddress.com](https://www.ipaddress.com/ip-lookup)），输入`github.com`和`github.global.ssl.fastly.net`，获取当前有效的IPv4地址。  
   - 示例（需替换为最新IP）：
     ```
     192.30.255.112  github.com
     185.31.16.184   github.global.ssl.fastly.net
     ```

2. **编辑Hosts文件**  
   
   - 路径：`C:\Windows\System32\drivers\etc\hosts`。  
   - 右键选择“以管理员身份运行”记事本或其他文本编辑器，打开并编辑文件。  
   - 在文件末尾添加上述IP与域名映射，保存时若提示权限不足，可将文件复制到桌面修改后再替换原文件。
   
3. **刷新DNS缓存**  
   - 打开命令提示符（管理员权限），输入：  
     ```bash
     ipconfig /flushdns
     ```

4. **验证**  
   - 重新执行`ping github.com`，若回复时间正常（如300ms左右），表示解析成功。

---

#### **2. 处理Hosts文件权限问题**
若无法保存修改：
1. 右键点击`hosts`文件 → **属性** → **安全** → 选择当前用户 → 勾选“写入”权限 → 应用并保存。

---

#### **3. 备用方案**
- **使用代理或VPN**：某些网络环境可能直接屏蔽GitHub，启用代理工具可绕过限制。
- **更换公共DNS**：将DNS服务器设置为`8.8.8.8`（Google DNS）或`114.114.114.114`（国内DNS）。

---

### **注意事项**
1. **IP地址动态变化**  
   GitHub的IP地址可能频繁变动，需定期查询更新Hosts文件。
2. **多域名关联**  
   除`github.com`外，还需添加`github.global.ssl.fastly.net`以解决SSL证书加载问题。
3. **系统兼容性**  
   Windows 10/11需以管理员权限操作，否则修改可能失败。

---

### **验证失败时的排查**
- **防火墙/杀毒软件**：临时禁用以排除干扰。
- **网络路由**：使用`tracert github.com`检查网络节点是否中断。

---

通过上述方法，可解决大多数因DNS解析导致的GitHub访问超时问题。若仍无法解决，建议检查本地网络环境或联系网络管理员。

