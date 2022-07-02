# import项目，把项目提交到svn

1. 进入到桌面文件夹

   ```
   cd Desktop/
   ```

2. import项目

   ```
   svn import ExcellentArtProject/ svn://123.57.53.21/yyt/ios -m ""
   ```

   注：

   svn服务器的地址后面要加上`-m ""`，如果不加`-m ""`的话，会提示下面错误：

   ```
   svn: E205007: Could not use external editer to fetch log message; consider setting the $SVN_EDITOR environment variable or using the —message (-m) or —file (-f) options
   svn: E205007: None of the environment variables SVN_EDITOR are set, and no ‘editor-cmd’ run-time configuration option was found
   ```

3. Authentication

   身份验证，验证电脑密码，然后验证SVN远程用户名和密码。



