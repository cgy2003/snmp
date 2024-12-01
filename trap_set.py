


import threading
from PyQt5.QtWidgets import QWidget,QGridLayout , QTextBrowser,  QLabel, QFrame,QVBoxLayout,QMessageBox
from pysnmp.carrier.asynsock.dispatch import AsynsockDispatcher
from pysnmp.carrier.asynsock.dgram import udp, udp6
from pyasn1.codec.ber import decoder
from pysnmp.proto import api
from pysnmp.hlapi import *
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.proto import rfc1902
from qfluentwidgets import LineEdit,PrimaryPushButton
from qfluentwidgets import FluentIcon as FIF
import inspect
import ctypes

def _async_raise(tid, exctype):
    # 触发异常，执行必要的清理操作
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # 如果返回值大于 1，表示出现问题，
        # 应该再次调用该函数，将 exc 设置为 NULL 以撤销效果
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")
 
# 停止线程函数
def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)
class SNMPTrapReceiver(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.transportDispatcher = AsynsockDispatcher()
        self.flag=False

    def initUI(self):
        self.setWindowTitle('SNMP Trap&Set')
        # self.setGeometry(100, 100, 600, 400)
        self.textBrowser = QTextBrowser()
        self.startButton = PrimaryPushButton(FIF.PLAY, '开始', self)
        self.clearButton = PrimaryPushButton(FIF.DELETE, '清空', self)

        # SNMP Set UI elements
        self.ip_label = QLabel('SNMP Device IP:')
        
        self.ip_edit = LineEdit()
        self.ip_edit.setPlaceholderText('192.168.227.150')
        self.ip_edit.setClearButtonEnabled(True)
        self.oid_label = QLabel('OID:')
        self.oid_edit = LineEdit()
        self.oid_edit.setPlaceholderText('1.3.6.1.2.1.1.5.0')
        self.oid_edit.setClearButtonEnabled(True)
        self.com_label = QLabel('Community:')
        self.com_edit = LineEdit()
        self.com_edit.setPlaceholderText('private')
        self.com_edit.setClearButtonEnabled(True)
        self.value_label = QLabel('Value:')
        self.value_edit = LineEdit()
        self.value_edit.setPlaceholderText('SNMPv2R2')
        self.value_edit.setClearButtonEnabled(True)
        
        self.submit_btn = PrimaryPushButton(FIF.SEND, '提交', self)
        self.trap = QLabel('SNMP Trap Window')
        layout = QGridLayout()
        layout.addWidget(self.startButton,3,9,1,1)
        layout.addWidget(self.clearButton,10,0,1,1)
        layout.addWidget(self.textBrowser,5,0,5,10)

        # Add SNMP Set UI elements to layout
        layout.addWidget(self.ip_label,0,0,1,1)
        layout.addWidget(self.ip_edit,0,1,1,4)
        layout.addWidget(self.oid_label,0,5,1,1)
        layout.addWidget(self.oid_edit,0,6,1,4)
        layout.addWidget(self.com_label,1,0,1,1)
        layout.addWidget(self.com_edit,1,1,1,4)
        layout.addWidget(self.value_label,1,5,1,1)
        layout.addWidget(self.value_edit,1,6,1,4)
        layout.addWidget(self.trap,3,0,1,1)
        layout.addWidget(self.submit_btn,2,9,1,1)

        self.setLayout(layout)

        self.startButton.clicked.connect(self.start)
        self.clearButton.clicked.connect(self.clear)
        self.submit_btn.clicked.connect(self.submit)

    def start(self):
        if self.flag==False:
            self.flag=True
            self.trap_thread = threading.Thread(target=self.TrapReceiver)
            self.trap_thread.start()
            self.show_success_message("SNMP Trap 启动！")
            # self.startButton.setText('停止')
        # else:
        #     self.flag=False
        #     stop_thread(self.trap_thread)
        #     self.startButton.setText('开始')

    def clear(self):
        self.textBrowser.clear()

    def submit(self):
        ip = self.ip_edit.text()
        oid = self.oid_edit.text()
        value = self.value_edit.text()
        community= self.com_edit.text()
        

        cmdGen = cmdgen.CommandGenerator()
        errorIndication, errorStatus, errorindex, varBinds = cmdGen.setCmd(
        cmdgen.CommunityData(community),#写入Community
        cmdgen.UdpTransportTarget((ip,161)),#IP地址和端口号
        (oid,rfc1902.OctetString(value))#OID和写入的内容，需要进行编码！
    )

        if errorIndication:
            print(errorIndication)
        elif errorStatus:
            print('%s at %s' % (
                    errorStatus.prettyPrint(),
                    errorindex and varBinds[int(errorindex)-1][0] or '?'
                ))
        else:
            self.show_success_message("snmp set成功！")
    # def Trap(self):
    #     command="snmputil trap"
    #     print(command)
    #     p = subprocess.Popen(command, stdout=subprocess.PIPE,  shell=True, text=True)
    #     while True:
    #         # time.sleep(0.5)
    #         result = p.stdout.readline()
    #         print(result)
    #         if result != '':
    #             print(result.strip('\r\n'))  # 对结果进行UTF-8解码以显示中文
    #             self.textBrowser.insertPlainText(result.strip('\r\n')+'\n')
    #                     # 通过信号/槽或其他方式将结果传递给用户界面
    #         else:
    #             break
    #         p.stdout.close()
                
    #         p.wait()
    def TrapReceiver(self):
        def cbFun(transportDispatcher, transportDomain, transportAddress, wholeMsg):
            
                while wholeMsg:
                    msgVer = int(api.decodeMessageVersion(wholeMsg))#提取版本信息
                    if msgVer in api.protoModules:#如果版本兼容
                        pMod = api.protoModules[msgVer]
                    else:#如果版本不兼容，就打印错误
                        self.textBrowser.insertPlainText('Unsupported SNMP version %s' % msgVer)
                        return
                    reqMsg, wholeMsg = decoder.decode(
                        wholeMsg, asn1Spec=pMod.Message(),#对信息进行解码
                        )
                    self.textBrowser.insertPlainText('Notification message from %s:%s: ' % (
                        transportDomain, transportAddress#打印发送TRAP的源信息
                        )
                    )
                    reqPDU = pMod.apiMessage.getPDU(reqMsg)
                    #self.textBrowser.insertPlainText(reqPDU)

                    if reqPDU.isSameTypeWith(pMod.TrapPDU()):
                        if msgVer == api.protoVersion1:# SNMPv1的特殊处理方法,可以提取更加详细的信息
                            self.textBrowser.insertPlainText('Enterprise: %s' % (
                                pMod.apiTrapPDU.getEnterprise(reqPDU).prettyPrint()
                                )
                                +"\n"
                            )
                            self.textBrowser.insertPlainText('Agent Address: %s' % (
                                pMod.apiTrapPDU.getAgentAddr(reqPDU).prettyPrint()
                                )
                                +"\n"
                            )
                            self.textBrowser.insertPlainText('Generic Trap: %s' % (
                                pMod.apiTrapPDU.getGenericTrap(reqPDU).prettyPrint()
                                )
                                +"\n"
                            )
                            self.textBrowser.insertPlainText('Specific Trap: %s' % (
                                pMod.apiTrapPDU.getSpecificTrap(reqPDU).prettyPrint()
                                )
                                +"\n"
                            )
                            self.textBrowser.insertPlainText('Time-Stamp: %s' % (
                                pMod.apiTrapPDU.getTimeStamp(reqPDU).prettyPrint()
                                )
                                +"\n"
                            )
                            varBinds = pMod.apiTrapPDU.getVarBindList(reqPDU)
                        else:# SNMPv2c的处理方法
                            varBinds = pMod.apiPDU.getVarBindList(reqPDU)
                        #result_dict = {}  # 每一个Trap信息,都会整理返回一个字典
                        # 定义一个空字符串来存储转换后的内容
                        varBinds_str = ""

                        # 遍历 varBinds 中的每个 VarBind
                        for varBind in varBinds:
                            # 获取 VarBind 中的 name 和 value
                            name = varBind['name']
                            value = varBind['value']
                            
                            # 将 name 和 value 转换为字符串并添加到 varBinds_str 中
                            varBinds_str += f"VarBind:\nname={name}\nvalue={value}"

                        # 打印转换后的字符串
                        print(varBinds_str)

                        self.textBrowser.insertPlainText(varBinds_str)
                        self.textBrowser.insertPlainText("===== End =====\n")
                        
                return wholeMsg

        # Register callback function
        self.transportDispatcher.registerRecvCbFun(cbFun)

        # UDP/IPv4
        self.transportDispatcher.registerTransport(udp.domainName, udp.UdpSocketTransport().openServerMode(('0.0.0.0', 162)))

        # UDP/IPv6
        self.transportDispatcher.registerTransport(udp6.domainName, udp6.Udp6SocketTransport().openServerMode(('::1', 162)))

        self.transportDispatcher.jobStarted(1)

        try:
            # Dispatcher will never finish as job#1 never reaches zero
            self.transportDispatcher.runDispatcher()
        except:
            self.transportDispatcher.closeDispatcher()
            raise
    def show_success_message(self, message):
        msg = QMessageBox()
        msg.setWindowTitle("Success")
        msg.setText(message)
        msg.setIcon(QMessageBox.Information)
        msg.exec_()

    def show_error_message(self, message):
        msg = QMessageBox()
        msg.setWindowTitle("Error")
        msg.setText(message)
        msg.setIcon(QMessageBox.Critical)
        msg.exec_()
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     trap_receiver = SNMPTrapReceiver()
#     trap_receiver.show()
#     sys.exit(app.exec_())

class Trap(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.ui = SNMPTrapReceiver()
        self.setObjectName("Snmp Trap and Set")
        layout = QVBoxLayout(self)
        layout.addWidget(self.ui)  # 将 Ui_Form 中的 widget 添加到布局中
        self.setLayout(layout)