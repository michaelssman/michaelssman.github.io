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

### Windows清除DNS缓存：

修改hosts文件后，你可能需要清除DNS缓存才能让更改生效。打开命令提示符（以管理员身份）并输入`ipconfig /flushdns`。

###  设置终端代理

```sh
PS C:\Users\micha> git config --global https.proxy http://127.0.0.1:10809
PS C:\Users\micha> git config --global http.proxy http://127.0.0.1:10809
```



