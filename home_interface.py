
from PyQt5.QtWidgets import QApplication, QMainWindow, QFrame, QLabel, QTextEdit, QVBoxLayout, QTextBrowser, QGridLayout, QWidget,QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import os, sys



from PyQt5.QtCore import QTimer,pyqtSignal
import numpy as np  
from qfluentwidgets import LineEdit,PrimaryPushButton
from qfluentwidgets import FluentIcon as FIF
import threading
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
def snmpWalk(host, oid):
    try:
        result = os.popen('snmpwalk -v 2c -c public ' + str(host) + '  ' + oid).read().split('\n')[:-1]
        return result
    except Exception as e:
        error_message = f"An error occurred in SNMP walk: {str(e)}"
        # 弹出错误提示框
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Error")
        msg.setInformativeText(error_message)
        msg.setWindowTitle("SNMP Walk Error")
        msg.exec_()
        return None
class main_window(QWidget):
    warning_signal = pyqtSignal()
    def __init__(self, parent=None):
        super(main_window, self).__init__(parent)
          
        # super(main_window,self).__init__(self.drawPicf) 
        # super(main_window,self).__init__(self.drawPicfC) 
        
        self._timer = QTimer(self)
        self.warning_signal.connect(self.show_warning)
        self.createWidgets()
        self.pro=0
        self.boolcurve = False
        self.host='192.168.227.150'
    def show_warning(self):
        # 在主线程中弹出警告对话框
        QMessageBox.warning(self, 'Threshold Warning', 'CPU exceeds threshold')
    def createWidgets(self):
        self.drawPicf = Figure(figsize=(10,2), dpi=50)  
        self.drawPicfC = Figure(figsize=(10,2), dpi=50)
        self.CPU_threshhold = 100.0
        layout = QGridLayout()
        
        self.Label1 = QLabel('oid:', self)
        layout.addWidget(self.Label1, 0, 0, 1, 1)
        
        # self.Text1Var = QLineEdit('1.3.6.1.2.1.1.1.0', self)
        self.Text1Var = LineEdit(self)

        self.Text1Var.setPlaceholderText('例如：1.3.6.1.2.1.1.1.0')
        self.Text1Var.setClearButtonEnabled(True)
        layout.addWidget(self.Text1Var, 0, 1, 1, 3)
        
        self.Command1 = PrimaryPushButton(FIF.SEND, '结果', self)
        layout.addWidget(self.Command1, 1, 0, 1, 1)
        self.Command1.clicked.connect(lambda: self.Command1_Cmd())
        
        self.Text2 = QTextEdit(self)
        layout.addWidget(self.Text2, 1, 1, 7, 3)
        
        self.Textip = LineEdit(self)
        # self.Text1Var.setPlaceholderText('192.168.227.150')
        self.Textip.setClearButtonEnabled(True)
        # self.Textip.setFixedHeight(20)
        layout.addWidget(self.Textip, 8, 1, 1, 3)

        
        self.ip = PrimaryPushButton(FIF.WIFI, '设置ip', self)
        layout.addWidget(self.ip, 8, 0, 1, 1)
        self.ip.clicked.connect(self.Command_ip)

        self.Textcpu = LineEdit(self)
        self.Textcpu.setClearButtonEnabled(True)
        layout.addWidget(self.Textcpu, 9, 1, 1, 3)
        
        self.cpu = PrimaryPushButton(FIF.SETTING, '设置cpu阈值', self)
        layout.addWidget(self.cpu, 9, 0, 1, 1)
        self.cpu.clicked.connect(self.Command_cpu)

        self.Label2 = QLabel('CPU', self)
        layout.addWidget(self.Label2, 0, 5, 1, 1)
        
        self.Text3 = QTextBrowser(self)
        layout.addWidget(self.Text3, 0, 6, 2, 6)
        
        self.Label3 = QLabel('内存', self)
        layout.addWidget(self.Label3, 2, 5, 1, 1)
        
        self.Text4 = QTextBrowser(self)
        layout.addWidget(self.Text4, 2, 6, 2, 6)
        
        self.Label4 = QLabel('流量', self)
        layout.addWidget(self.Label4, 4, 5, 1, 1)
        
        self.Text5 = QTextBrowser(self)
        layout.addWidget(self.Text5, 4, 6, 2, 6)
        
        self.Label5 = QLabel('硬盘信息', self)
        layout.addWidget(self.Label5, 7, 5, 1, 1)
        
        self.Text6 = QTextBrowser(self)
        layout.addWidget(self.Text6, 7, 6, 2, 6)
        self.Command2 = PrimaryPushButton(FIF.SEARCH_MIRROR, '查看信息', self)
        layout.addWidget(self.Command2, 0, 4, 1, 1)
        self.Command2.clicked.connect(self.Command2_Cmd)
        
       
        
        self.Command3 = PrimaryPushButton(FIF.UPDATE, '开始/停止绘制', self)
        layout.addWidget(self.Command3, 10, 0, 2, 1)
        self.Command3.clicked.connect(self.Command3_Cmd)
        
        
        self.drawPiccanvas = FigureCanvas(self.drawPicf)
        #self.drawPicf.suptitle("CPU CURVE", fontsize=22)
        self.drawPiccanvas.draw()
       
        layout.addWidget(self.drawPiccanvas, 10, 1, 30, 12)
        
        
        self.drawPiccanvasC = FigureCanvas(self.drawPicfC)
        #self.drawPicfC.suptitle("MEMORY CURVE", fontsize=22)
        self.drawPiccanvasC.draw()
        
        layout.addWidget(self.drawPiccanvasC, 40, 1, 30, 12)  # 使用 drawPiccanvasC
        
        
        self.setLayout(layout)
    def Command_ip(self):
        try:
            self.host = self.Textip.text()
            print(self.host)
            #self.refresh()
            if self.boolcurve:
                stop_thread(self.thread)
                self.boolcurve=False
            
            # 如果没有异常，执行成功，显示成功消息框
            self.show_success_message("ip设置成功！")
        except Exception as e:
            # 如果出现异常，显示错误消息框
            self.show_error_message(f"出现异常：{str(e)}")

    
    def Command_cpu(self):
        try:
            self.CPU_threshhold=float(self.Textcpu.text())
            print(self.CPU_threshhold)
            if self.boolcurve:
                stop_thread(self.thread)
                self.boolcurve=False
            
            #self.refresh()
            self.show_success_message("cpu阈值设置成功！")
        except Exception as e:
            self.show_error_message(f"出现异常：{str(e)}")
    def Command1_Cmd(self):
        self.Text2.clear()
        oid_result = snmpWalk(self.host,self.Text1Var.text())
        print(self.Text1Var.text())
        self.Text2.insertPlainText(str(oid_result))
    
    def Command2_Cmd(self):
        # CPU信息
        self.Text3.clear()

        pro = os.popen('snmpwalk -v 2c -c public ' + self.host + ' ' + '.1.3.6.1.4.1.2021.11.9.0').read()
        # 截取后面需要读的部分
        index = pro.rfind(":") + 2
        pro = pro[index:]
        pro = pro.strip('\n')
        self.Text3.insertPlainText("CPU使用率：" + pro + '%\n')
        # 内存信息
        self.Text4.clear()
        mem_total = snmpWalk(self.host, 'HOST-RESOURCES-MIB::hrMemorySize.0')[0].split(' ')[3]
        print(snmpWalk(self.host, 'HOST-RESOURCES-MIB::hrStorageUsed.7'))
        mem_sto_used = snmpWalk(self.host, 'HOST-RESOURCES-MIB::hrStorageUsed.7')[0].split(' ')[3]
        print(snmpWalk(self.host, 'HOST-RESOURCES-MIB::hrStorageAllocationUnits.7'))
        mem_sto_unit = snmpWalk(self.host, 'HOST-RESOURCES-MIB::hrStorageAllocationUnits.7')[0].split(' ')[3]
        mem_used=str(round(float(mem_sto_used)*float(mem_sto_unit)/1024/1024/1024,2))
        mem_used_total=float(mem_total)
        mem_used_rate=str(round(float(mem_sto_used)*float(mem_sto_unit)/1024/mem_used_total*100,2))+'%'
        self.Text4.insertPlainText("总内存 : "+str(round(float(mem_total)/1024/1024,2))+" GB\n"+"内存使用："+mem_used+"GB\n"+"内存使用率："+mem_used_rate)

        # 硬盘空间
        self.Text6.clear()
        disk_total = snmpWalk(self.host, '.1.3.6.1.4.1.2021.9.1.3')
        disk_num=sum('/' in entry.split(': ')[1] for entry in disk_total)
        print(disk_num)
        tmp=1
        diskstr=''
        while tmp<=disk_num:
            if snmpWalk(self.host, '.1.3.6.1.4.1.2021.9.1.6.'+str(tmp))[0].split(' ')[3]!="Such":

                storge=snmpWalk(self.host, '.1.3.6.1.4.1.2021.9.1.6.'+str(tmp))[0].split(' ')[3]
                print(storge)
                diskstr=diskstr+snmpWalk(self.host, '.1.3.6.1.4.1.2021.9.1.3.'+str(tmp))[0].split(' ')[3]+' '+str(storge)+'GB'+'\n'
                tmp+=1
        
        self.Text6.insertPlainText("硬盘数："+str(disk_num)+'\n'+diskstr)

        # 流量信息
        device_mib = snmpWalk(self.host, 'RFC1213-MIB::ifDescr')
        device_list = []
        for item in device_mib:
            device_list.append(item.split(':')[3].strip())
        # 流入流量
        data_mib = snmpWalk(self.host, 'IF-MIB::ifInOctets')
        data = []
        for item in data_mib:
            byte = float(item.split(':')[3].strip())
            data.append(str(round(byte / 1024, 2)))
        inside = data
        # 流出流量
        data_mib = snmpWalk(self.host, 'IF-MIB::ifOutOctets')
        data = []
        for item in data_mib:
            byte = float(item.split(':')[3].strip())
            data.append(str(round(byte / 1024, 2)))
        outside = data
        rxsum=0.0
        txsum=0.0
        for i, item in enumerate(device_list):
            rxsum+=float(inside[i])
            txsum+=float(outside[i])
        rxsum=round(rxsum/1024,2)
        txsum=round(txsum/1024,2)
        self.Text5.clear()
        self.Text5.insertPlainText("发送流量："+str(txsum)+'MB'+'\n'+"接收流量："+str(rxsum)+'MB'+'\n')
    def Command3_Cmd(self):
        self.boolcurve=not self.boolcurve
        print(self.boolcurve)
        #print(self.boolcurve)
        if self.boolcurve:
            self.thread = threading.Thread(target=self.refresh)
            self.thread.start()
        else:
            stop_thread(self.thread)
    def refresh(self):
        self.ydataM = []
        #print(1)
        for i in range(20):
            self.ydataM.append(0)
        self.xdataM = np.linspace(0,19, 20)
        self.ydataC = []
        for i in range(20):
            self.ydataC.append(0)
        self.xdataC = np.linspace(0,19, 20)
        while True:
            self.drawPicC() 
            if float(self.pro)>self.CPU_threshhold:
                self.warning_signal.emit()
                self.boolcurve=False
                break
            
        # self._timer.timeout.connect(self.drawPicC)
        # self._timer.start(1000) 
    def drawPicC(self):             
        self.drawPicfC.clf() 
        self.drawPicf.clf()  

        self.drawPicaC=self.drawPicfC.add_subplot(111) 
        self.drawPica=self.drawPicf.add_subplot(111) 
        if not self.boolcurve:
            return
        pro = os.popen('snmpwalk -v 2c -c public ' + self.host + ' ' + '.1.3.6.1.4.1.2021.11.9.0').read()
        index = pro.rfind(":") + 2
        pro = pro[index:]
        pro = pro.strip('\n')
        self.pro = float(pro)
        #阈值告警
        # if float(self.pro)>self.CPU_threshhold:
        #     QMessageBox.warning(None, '阈值警告', 'CPU超过阈值')
            
        self.ydataC.append(pro)
        del self.ydataC[0] 

        mem_total = snmpWalk(self.host, 'HOST-RESOURCES-MIB::hrMemorySize.0')[0].split(' ')[3]
        mem_sto_unit = snmpWalk(self.host, 'HOST-RESOURCES-MIB::hrStorageAllocationUnits.7')[0].split(' ')[3]
                    
        mem_sto_used = snmpWalk(self.host, 'HOST-RESOURCES-MIB::hrStorageUsed.7')[0].split(' ')[3]
        mem_used_total=float(mem_total)
        mem_used_rate=round(float(mem_sto_used)*float(mem_sto_unit)/1024/mem_used_total*100,2)
        #print(mem_used_rate)
        del self.ydataM[0]
        self.ydataM.append(mem_used_rate)
             
        self.drawPicaC.plot(self.xdataC,self.ydataC,color='r')  
        #print(self.xdataC,self.ydataC)
        self.drawPicaC.set_title('cpu curve',fontsize=22)  
        self.drawPiccanvasC.draw()

        self.drawPica.plot(self.xdataM,self.ydataM,color='r') 
        #print(self.xdataM,self.ydataM)
        self.drawPica.set_title('memory curve',fontsize=22)  
        self.drawPiccanvas.draw()
        
        #self.drawPicC(self.xdataC,self.ydataC,self.xdataM,self.ydataM)
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

class Walk(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.ui = main_window()
        self.setObjectName("Snmp walk")
        layout = QVBoxLayout(self)
        layout.addWidget(self.ui)  # 将 Ui_Form 中的 widget 添加到布局中
        self.setLayout(layout)
       
# if __name__ == '__main__':
#     host='192.168.227.150'
#     app = QApplication(sys.argv)
#     ex = main_window()
#     ex.show()
#     sys.exit(app.exec_())
