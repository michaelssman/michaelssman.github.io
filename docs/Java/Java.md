# Java

课件PPT地址：https://cloud.fynote.com/share/s/z9JGaVu6
补充文档：https://cloud.fynote.com/share/s/V9JIaVwAC

## JDK

https://www.oracle.com/java/technologies/downloads/

https://www.oracle.com/java/technologies/javase-jdk11-downloads.html

Java Development Kit (JDK) 是 Sun 公司（已被 Oracle 收购）针对 Java 开发员的**软件开发工具包**。

Java SE 8（LTS）、Java SE 11（LTS）、Java SE 17（LTS）企业用的比较多，长期支持版本。

JDK（Java Development Kit）是 Java 开发工具包，它是用于开发和运行 Java 程序的核心工具。JDK 包含以下组件：

1. **Java 编译器（javac）**：
   - 将 Java 源代码编译为字节码（.class 文件），这些字节码可以在 Java 虚拟机（JVM）上运行。

2. **Java 运行时环境（JRE）**：
   - 包含 JVM 和 Java 类库，允许你运行 Java 应用程序。

3. **Java 类库**：
   - 一组预定义的类和接口，提供丰富的功能供开发者使用，如数据结构、网络和文件 I/O 等。

4. **开发工具**：
   - 包括调试器（jdb）、文档生成工具（javadoc）、打包工具（jar）等，帮助开发者编写、调试和打包 Java 应用。

JDK 是 Java 开发人员的基本工具，必须安装在开发环境中以编译和运行 Java 程序。

### Mac配置JDK

1. **访问 Oracle 或其他 JDK 提供商的网站**：
   下载所需版本的 JDK 安装包。例如，访问 [Oracle JDK Archive](https://www.oracle.com/java/technologies/javase-jdk11-downloads.html) 找到旧版本。

2. **安装 JDK**：
   下载完成后，双击 `.dmg` 文件并按照安装向导进行安装。

3. **配置环境变量**：
   同样，需要在 `~/.zshrc` 或 `~/.bash_profile` 中设置 `JAVA_HOME`，例如：

   ```bash
   export JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk-11.jdk/Contents/Home
   export PATH="$JAVA_HOME/bin:$PATH"
   ```

4. **刷新配置**：
   运行以下命令以应用更改：

   ```bash
   source ~/.zshrc
   ```

完成这些步骤后，你应该能够使用所需版本的 JDK。可以通过 `java -version` 和 `javac -version` 来验证安装是否成功。

## idea

写代码的工具。

https://www.jetbrains.com/

## 快捷键

- ctrl+d：复制一行
- ctrl+y：删除一行
- sout：`System.out.println();`
- alt+Insert：类构造器，可以选择多个属性
- ctrl+i：service的imp类中，实现接口方法。
- alt+enter：为选中的ServiceImpl类，创建测试类。
- alt+shift+t：选中service接口类，会创建对应的测试文件。
- ctrl+alt+m：选中的代码，提取为方法。

## 方法重载

同一个类中，**方法名相同**，**形参列表不同**（类型不同、个数不同、顺序不同）的多个方法，构成了方法的重载。
