# SSH

SSH 是 "Secure Shell" 的缩写，它是一种网络协议。用于在不安全的网络上提供安全的加密通信。SSH 通过在网络服务如远程登录或远程文件传输过程中使用安全的加密方法，可以有效防止信息泄露、内容篡改和未授权访问。

SSH 协议主要用于远程控制系统和服务器，允许用户通过不安全的网络环境安全地登录到另一台计算机上，并在两台计算机之间执行命令和移动文件。SSH 通常用于系统管理员管理系统和应用程序，也用于在不同系统之间传输信息。

SSH 工作原理涉及公钥和私钥的使用，以确保两个通信端之间的数据传输是加密的。用户在第一次连接到 SSH 服务器时，会接收到服务器的公钥，用于之后的加密验证。用户可以生成一对密钥（公钥和私钥），并将公钥放在需要远程访问的服务器上。在建立连接时，服务器会用用户的公钥来加密一个随机生成的消息，只有对应的私钥持有者才能解密并继续安全通信。

SSH 既可以通过密码认证用户，也可以通过密钥对进行无密码登录。后者更为安全，因为它不容易受到字典攻击或暴力破解攻击。

SSH 协议还支持端口转发功能，允许将其他协议的网络连接通过 SSH 连接进行转发，从而实现安全的网络服务隧道。