# 基于SNMP的系统监控与分析

## 相关配置

- requirements.txt：用conda创建python=3.11的虚拟环境，然后运行`pip install -r requirements.txt`

- snmpwalk安装

## 功能测试

从mysnmp.py进入程序：

![image-20240412171358358](./resource/image-20240412171358358.png)

设置ip：![image-20240419160912573](./resource/image-20240419160912573.png)

输入oid返回结果：![image-20240412171547610](resource/image-20240412171547610.png)

点击查看信息可返回对应ip主机的CPU、内存、硬盘空间、流量值：

![image-20240412171648236](resource/image-20240412171648236.png)

设置cpu阈值：![image-20240412175316550](resource/image-20240412175316550.png)

绘制曲线:

![image-20240412175413113](resource/image-20240412175413113.png)

超过阈值弹窗：![image-20240412175519755](resource/image-20240412175519755.png)

snmptrap：测试前需要将snmp陷阱停止

![image-20240412181212498](resource/image-20240412181212498.png)

在虚拟机输入命令：![image-20240412181402280](resource/image-20240412181402280.png)

可以看到接收到如下信息：

![image-20240412181336966](resource/image-20240412181336966.png)

snmpset：

虚拟机字段初始值：

![image-20240412181806907](resource/image-20240412181806907.png)

提交如下命令：![image-20240412181720647](resource/image-20240412181720647.png)

再次查看：

![image-20240412181852489](resource/image-20240412181852489.png)

