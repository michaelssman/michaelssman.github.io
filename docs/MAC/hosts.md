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

例如：Ubuntu上在`/etc/hosts`中添加：

```
151.101.72.249 github.http://global.ssl.fastly.net
140.82.113.4 github.com
```

 