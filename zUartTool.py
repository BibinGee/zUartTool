###############################################################################################################

# coding = utf-8

# this software is modified from sweep data assistor. This software is being a uart debug tool for CO WiFi program,
# which main CO detector outputs a hexadecimal format data.

# Develop by: Daniel G.
# Initial Creatation Date: 2021-07-29

###############################################################################################################

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
import serial
import serial.tools.list_ports
import random
import time
import numpy as np
##import kalmanfilter
import string
##from Graph import Graph
##import xlwt

class Application(QWidget):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('zUartTool   Copyright @ Daniel Gee')
##        self.setWindowIcon(QIcon(r'myico.ico'))
        self.initGui()

    def initGui(self):
        # Global layout container
        layout = QVBoxLayout()
        sub_v_layout = QVBoxLayout()
        sub_h_layout = QHBoxLayout()
        
        #############################    this part is for the interface of general serial ports   ################################
        # h1 Horizontal Box to include Unit serial port, baudrate components
        h1 = QHBoxLayout()
        self.label1 = QLabel(self)
        self.label1.setText('COM')
        self.label1.setFont(QFont("Microsoft YaHei"))
        self.label1.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        h1.addWidget(self.label1) 
        self.combox1 = QComboBox(self)
        self.combox1.setFont(QFont("Microsoft YaHei"))
        h1.addWidget(self.combox1)                   


        self.label2 = QLabel(self)
        self.label2.setText('Baudrate')
        self.label2.setFont(QFont("Microsoft YaHei"))
        self.label2.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        h1.addWidget(self.label2)      
        self.bdrate_comb1 = QComboBox(self)  
        self.bdrate_comb1.setFont(QFont("Microsoft YaHei"))  
##        self.bdrate_comb1.addItem('4800')
        self.bdrate_comb1.addItem('9600')
        self.bdrate_comb1.addItem('19200')
        self.bdrate_comb1.addItem('38400')
        self.bdrate_comb1.addItem('57600')
        self.bdrate_comb1.addItem('115200')
        h1.addWidget(self.bdrate_comb1)          

        self.refreshBtn = QPushButton('Refresh', self)
        self.refreshBtn.setFont(QFont("Microsoft YaHei"))
        self.refreshBtn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.refreshBtn.clicked.connect(self.portRefresh)
        h1.addWidget(self.refreshBtn)
        
        sub_v_layout.addLayout(h1)
        # h3 Horizontal Box to include Step, Command components
        h3 = QHBoxLayout()
        
        ##############  this is for command sending of general serial ports ###########################
        self.edit4 = QLineEdit(self)
        h3.addWidget(self.edit4)                 
        self.comBtn = QPushButton('Send CMD', self)
        self.comBtn.setFont(QFont("Microsoft YaHei"))
        self.comBtn.clicked.connect(self.on_click_cmd)
        self.comBtn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        h3.addWidget(self.comBtn)
                
        ##################### this is parts for User Interface ##############################
        # h4 Horizontal Box to include Buttons components
##        h3 = QHBoxLayout()
        self.saveBtn = QPushButton('Save', self)
        self.saveBtn.setFont(QFont("Microsoft YaHei"))
        self.saveBtn.clicked.connect(self.on_click_save)
        self.saveBtn.setEnabled(False)
        h3.addWidget(self.saveBtn)

        self.startBtn = QPushButton('Start', self)
        self.startBtn.setFont(QFont("Microsoft YaHei"))
        self.startBtn.clicked.connect(self.on_click_start)
        h3.addWidget(self.startBtn)

        self.pauseBtn = QPushButton('Pause', self)
        self.pauseBtn.setFont(QFont("Microsoft YaHei"))
        self.pauseBtn.setEnabled(False)
        self.pauseBtn.clicked.connect(self.on_click_pause)
        h3.addWidget(self.pauseBtn)
        
        sub_v_layout.addLayout(h3)
        
        # include vertical layout
        sub_h_layout.addLayout(sub_v_layout)
        layout.addLayout(sub_h_layout)

        # file path display label
        self.fnfiled = QLineEdit(self)
        self.fnfiled.setEnabled(False)
        layout.addWidget(self.fnfiled)

        # Text display field 
        self.tedit = QTextEdit()
        self.tedit.setStyleSheet("background:black")
        self.tedit.setTextColor(Qt.white)
        f = self.tedit.font()
        f.setPointSize(11)
        f.setFamily('Microsoft YaHei')
        self.tedit.setFont(f)
        layout.addWidget(self.tedit)

        self.saved_text = QLineEdit(self)
        f = self.saved_text.font()
        f.setPointSize(8)
        f.setFamily('Microsoft YaHei')
        self.saved_text.setFont(f)
        self.saved_text.setStyleSheet("color: green;")
        self.saved_text.setText('......')
        self.saved_text.setEnabled(False)
        layout.addWidget(self.saved_text)
        
        self.setLayout(layout)

        #################### some basic variance need to be initialized ##################
        
        self.serPort = serial.Serial () # Global serial handler
        self.ltcSerPort = serial.Serial()
        self.file = ''
        self.timer = QBasicTimer()  # Define timer to loop events
        self.timer.start(100, self)
        self.line = ''  # Define a characters container, to store a sentence. 
        self.flag = False   # Define a flag to control serial data reading ON/OFF..
        
        # auto fill serial ports into combo box
        ports = serial.tools.list_ports.comports(include_links=False)
        for port in ports:
            self.combox1.addItem(port.device)

    def on_click_serOpenBtn(self):         
        
        # Get baudrate
        if self.bdrate_comb1.currentText() !='':
            self.serPort.baudrate =  self.bdrate_comb1.currentText()

        # Get serial port
        if self.combox1.currentText() != '':
            print(self.combox1.currentText())
            self.serPort.port  = self.combox1.currentText()
 
        if self.serPort.baudrate and self.serPort.port is not None:
            self.serPort.timeout = 0.05
            try:
                self.serPort.open()
                print(self.serPort.port, 'opened')
            except serial.serialutil.SerialException as e:
                print(e)
                QMessageBox.warning(self, 'Warning' , str(e))
                self.serPort.close()
                self.startBtn.setEnabled(True)
        else:
##            print('Cannot open Unit Serial Port!!!')
            QMessageBox.warning(self, 'Warning', 'Port is not available.')

    def on_click_save(self):
        try:
            self.file, _ = QFileDialog.getSaveFileName(self, 'Save file', '','Text(*.txt)')
            if self.file is not None:
                self.fnfiled.setText(self.file)                          
                with open(self.file, "a+", encoding = "utf-8") as f :   # writing title information to txt file.
                    f.write("Log data of Uart: ")
                    f.write("\n")                          
                self.saveBtn.setEnabled(False)
        except Exception as e:
            print(e)
            QMessageBox.warning(self, 'Warning', str(e))

    def on_click_start(self):
        self.startBtn.setEnabled(False)
        if not self.serPort.isOpen ():
                self.on_click_serOpenBtn()
                
        self.saveBtn.setEnabled(True)
        self.pauseBtn.setEnabled(True)
#        enable timer
        self.flag = True
    
    def on_click_pause (self):
        try:          
            self.saved_text.setText('')  # clear saved text label
            if self.serPort.isOpen ():  # close unit serial port, enable open button
                self.serPort.close()
                
            self.flag = False   # disable event loop
            self.startBtn.setEnabled(True)  # enable start button
            self.saveBtn.setEnabled(True)   # enable save button
            self.pauseBtn.setEnabled(False)
            self.file = ''  # Clear file path
            self.fnfiled.setText('')
        except Exception as e:
            print(e)
            QMessageBox.warning(self, 'Warning', str(e))

    def on_click_cmd (self):
        if self.serPort.isOpen ():
            cmd = self.edit4.text() + '\r'
            print(cmd.encode())
            # send command through serial port
            self.serPort.write(cmd.encode())
            t = time.strftime ('[%H:%M:%S]:>', time.localtime ())
            self.tedit.append(t + self.edit4.text())
      
    def portRefresh(self):
        self.combox1.clear()
        ports = serial.tools.list_ports.comports(include_links=False)    # auto fill serial ports into combo box
        for port in ports:
            self.combox1.addItem(port.device)
    
    def timerEvent(self, event):
        # Read String from Main Serial Port
        hexstring = []
        if self.flag:
            try:
                if self.serPort.isOpen():
                    serial_data = self.serPort.readline()
##                    print(serial_data)                    
                    if serial_data != b'':   # remove all null serial_data.                    
                        t = time.strftime ('[%H:%M:%S]: ', time.localtime ())
                        hexstring.append(t)
                        for byte in serial_data:
                            hexstring.append("{:02X}".format(byte))
                            hexstring.append(' ')
                        self.tedit.append(''.join(hexstring))                                  
                        self.tedit.moveCursor(QTextCursor.End)  # move cursor to the end.
            except Exception as e:
                    print('error caught when reading serial_data from serial port', e)
                    QMessageBox.warning(self, 'Warning', str(e))
                    self.on_click_pause()                             
            if hexstring != []: #  Ready to save file into Excel.    
                try:
                    if self.file != '':    # check file pat if validated.                          
                        with open(self.file, "a+", encoding = "utf-8") as f:
                            f.write(''.join(hexstring))
                            f.write("\n")                                                           
                        self.saved_text.setText('Saving:'+ ''.join(hexstring)) 
                except Exception as e:
                    print('error:', e) 
                    QMessageBox.warning(self, 'Warning', str(e))               
     
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Application()
    ex.show()
    sys.exit(app.exec_())
