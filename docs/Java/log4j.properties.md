# log4j.properties

log4j.properties加入：

```properties
# log4j中定义的级别：fatal(致命错误) > error(错误) >warn(警告) >info(普通信息) >debug(调试信息)>trace(跟踪信息)
log4j.rootLogger=ERROR , console , D 

# log4j.logger是固定的，a.b.c是命名空间的名字可以只写一部分。
log4j.logger.a.b=TRACE
# log4f.logger是固定的，com.hh.mapper.BookMapper是命名空间的名字。
# log4j.logger.com.hh.mapper.BookMapper=TRACE

### console ###
log4j.appender.console=org.apache.log4j.ConsoleAppender
log4j.appender.console.Target=System.out
log4j.appender.console.layout=org.apache.log4j.PatternLayout
log4j.appender.console.layout.ConversionPattern=[%p] [%-d{yyyy-MM-dd HH\:mm\:ss}] %C.%M(%L) | %m%n
### log file ###
log4j.appender.D=org.apache.log4j.DailyRollingFileAppender
log4j.appender.D.File=D:/log4j.log
log4j.appender.D.Append=true
# 只能生级别，不能降
log4j.appender.D.Threshold=INFO
log4j.appender.D.layout=org.apache.log4j.PatternLayout
log4j.appender.D.layout.ConversionPattern=[%p] [%-d{yyyy-MM-dd HH\:mm\:ss}] %
```
