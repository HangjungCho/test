# ---- Img, Tensorflow, Process, Thread import ---- #
import tensorflow as tf
from multiprocessing import Process, Queue, current_process
from threading import Thread
from PIL import Image, ImageOps

# ----- GUI import ---- #
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QPixmap

import socket
import cv2
import numpy as np
import time, datetime
import sys
import os
import RPi.GPIO as GPIO

# Machine Process global variations
Check1 = 0
Check2 = 0
Check3 = 0
running = 0
running2 = 0
Reject_Item1 = 0
Reject_Item2 = 0
Item_Dictionary = {}
Item1 = 0
Item2 = 0
count = 1

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

class NetFunc():
    def __init__( self, hostIP, hostPort ):
        self.host = hostIP
        self.port = hostPort
        self.client_sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self.server_address = ( self.host, self.port )
        self.client_sock.connect((self.host, self.port) )

    def __del__( self ):
        self.client_sock.close()
        print( "Closing connection to the server" )

    def sendData( self, stringData ):
        try:
            self.client_sock.send(str(len(stringData)).ljust(28).encode())
            self.client_sock.send(stringData)

        except socket.errno as e:
            print( "Socket error: %s" %str(e) )
        except ConnectionResetError as e:
            print( "ConnectionResetError: %s" %str(e) )
        except Exception as e:
            print( "Other exception: %s" %str(e) )
        
    def receiveData( self ):
        return self.client_sock.recv(1024)

# GUI setting
class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1550, 510)
        self.btn_1 = QtWidgets.QPushButton(Dialog)
        self.btn_1.setGeometry(QtCore.QRect(510, 420, 105, 30))
        self.btn_1.setObjectName("btn_1")
        self.btn_2 = QtWidgets.QPushButton(Dialog)
        self.btn_2.setGeometry(QtCore.QRect(635, 420, 105, 30))
        self.btn_2.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.btn_2.setObjectName("btn_2")
        self.btn_2.setEnabled(False)
        self.textEdit = QtWidgets.QTextEdit(Dialog)
        self.textEdit.setGeometry(QtCore.QRect(510, 250, 230, 160))
        self.textEdit.setObjectName("textEdit")
        # self.textEdit.setEnabled(False)
        self.btn_3 = QtWidgets.QPushButton(Dialog)
        self.btn_3.setGeometry(QtCore.QRect(510, 460, 230, 30))
        self.btn_3.setObjectName("btn_3")
        self.img = QtWidgets.QLabel(Dialog)
        self.img.setGeometry(QtCore.QRect(510, 10, 224, 224))
        self.img.setText("")
        self.img.setObjectName("img")
        self.cam = QtWidgets.QLabel(Dialog)
        self.cam.setGeometry(QtCore.QRect(10, 10, 480, 480))
        self.cam.setText("")
        self.cam.setObjectName("cam")
        self.conveyor = QtWidgets.QLabel(Dialog)
        self.conveyor.setGeometry(QtCore.QRect(760, 10, 580, 440))
        self.conveyor.setText("")
        self.conveyor.setObjectName("conveyor")
        self.type_1 = QtWidgets.QComboBox(Dialog)
        self.type_1.setEnabled(True)
        self.type_1.setGeometry(QtCore.QRect(880, 470, 140, 30))
        self.type_1.setIconSize(QtCore.QSize(40, 20))
        self.type_1.setObjectName("type_1")
        self.type_1.addItem("")
        self.type_1.addItem("")
        self.type_1.addItem("")
        self.type_1.addItem("")
        self.type_1.addItem("")
        self.type_2 = QtWidgets.QComboBox(Dialog)
        self.type_2.setEnabled(True)
        self.type_2.setGeometry(QtCore.QRect(1100, 470, 140, 30))
        self.type_2.setMinimumSize(QtCore.QSize(94, 0))
        self.type_2.setIconSize(QtCore.QSize(40, 20))
        self.type_2.setDuplicatesEnabled(False)
        self.type_2.setFrame(True)
        self.type_2.setObjectName("type_2")
        self.type_2.addItem("")
        self.type_2.addItem("")
        self.type_2.addItem("")
        self.type_2.addItem("")
        self.type_2.addItem("")
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(1360, 100, 180, 30))
        self.pushButton.setObjectName("pushButton")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(1360, 20, 180, 30))
        self.label.setMouseTracking(False)
        self.label.setTabletTracking(False)
        self.label.setScaledContents(False)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.pushButton_2 = QtWidgets.QPushButton(Dialog)
        self.pushButton_2.setGeometry(QtCore.QRect(1360, 220, 180, 30))
        self.pushButton_2.setObjectName("pushButton_2")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(1360, 140, 180, 30))
        self.label_2.setMouseTracking(False)
        self.label_2.setTabletTracking(False)
        self.label_2.setScaledContents(False)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.Add_item = QtWidgets.QTextEdit(Dialog)
        self.Add_item.setGeometry(QtCore.QRect(1360, 60, 180, 30))
        self.Add_item.setObjectName("Add_item")
        self.Delete_combobox = QtWidgets.QComboBox(Dialog)
        self.Delete_combobox.setEnabled(True)
        self.Delete_combobox.setGeometry(QtCore.QRect(1360, 180, 180, 30))
        self.Delete_combobox.setMinimumSize(QtCore.QSize(94, 0))
        self.Delete_combobox.setIconSize(QtCore.QSize(40, 20))
        self.Delete_combobox.setDuplicatesEnabled(False)
        self.Delete_combobox.setFrame(True)
        self.Delete_combobox.setObjectName("Delete_combobox")
        self.Delete_combobox.addItem("")
        self.Delete_combobox.addItem("")
        self.Delete_combobox.addItem("")
        self.Delete_combobox.addItem("")
        self.Delete_combobox.addItem("")

        self.retranslateUi(Dialog)
        self.type_1.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.btn_1.setText(_translate("Dialog", "Start"))
        self.btn_2.setText(_translate("Dialog", "Stop"))
        self.btn_3.setText(_translate("Dialog", "Exit"))
        self.type_1.setItemText(0, _translate("Dialog", "--None--"))
        self.type_1.setItemText(1, _translate("Dialog", "Car"))
        self.type_1.setItemText(2, _translate("Dialog", "Airplane"))
        self.type_1.setItemText(3, _translate("Dialog", "Dinosaur"))
        self.type_1.setItemText(4, _translate("Dialog", "Whale"))
        self.type_2.setItemText(0, _translate("Dialog", "--None--"))
        self.type_2.setItemText(1, _translate("Dialog", "Car"))
        self.type_2.setItemText(2, _translate("Dialog", "Airplane"))
        self.type_2.setItemText(3, _translate("Dialog", "Dinosaur"))
        self.type_2.setItemText(4, _translate("Dialog", "Whale"))
        self.pushButton.setText(_translate("Dialog", "Add Item"))
        self.label.setText(_translate("Dialog", "Add Item"))
        self.pushButton_2.setText(_translate("Dialog", "Delete Item"))
        self.label_2.setText(_translate("Dialog", "Delete Item"))
        self.Delete_combobox.setItemText(0, _translate("Dialog", "--None--"))
        self.Delete_combobox.setItemText(1, _translate("Dialog", "Car"))
        self.Delete_combobox.setItemText(2, _translate("Dialog", "Airplane"))
        self.Delete_combobox.setItemText(3, _translate("Dialog", "Dinosaur"))
        self.Delete_combobox.setItemText(4, _translate("Dialog", "Whale"))

class Conveyor_main(Thread):
    def __init__(self):
        Thread.__init__(self, name='Conveyor_main')
        self.con1_port = 5 # 29
        self.con2_port = 6 # 31

        GPIO.setup(self.con1_port, GPIO.OUT)
        GPIO.setup(self.con2_port, GPIO.OUT)

    def __del__( self ):
        print( "Closing Conveyor_main" )

    def conveyor_init(self):
        GPIO.output(self.con1_port, True)
        GPIO.output(self.con2_port, True)

    def main_conveyor_On(self):
        GPIO.output(self.con1_port, False)
        GPIO.output(self.con2_port, False)
        
    def main_conveyor_Off(self):
        GPIO.output(self.con1_port, True)
        GPIO.output(self.con2_port, True)

    def run(self):
        global Check2, Check3, running2
        self.conveyor_init()
        while True:
            if running2 == 1:
                if (Check2 or Check3) == 1 :
                    self.main_conveyor_Off()
                    time.sleep(2)
                else:
                    self.main_conveyor_On()
            else:
                self.main_conveyor_Off()

class Conveyor1(Thread):
    def __init__(self):
        Thread.__init__(self, name='Conveyor1')
        self.con3_port = 13 # 33
        GPIO.setup(self.con3_port, GPIO.OUT)

    def __del__( self ):
        print( "Closing Conveyor1" )

    def conveyor_init(self):
        GPIO.output(self.con3_port, True)

    def con1_On(self):
        GPIO.output(self.con3_port, False)

    def con1_Off(self):
        GPIO.output(self.con3_port, True)

    def run(self):
        global Check2
        self.conveyor_init()
        while True:
            if Check2 == 1:
                self.con1_On()
                time.sleep(8)
            elif Check2 == 0:
                self.con1_Off()

class Conveyor2(Thread):
    def __init__(self):
        Thread.__init__(self, name='Conveyor2')
        self.con4_port = 19 # 35
        GPIO.setup(self.con4_port, GPIO.OUT)

    def __del__( self ):
        print( "Closing Conveyor2" )

    def conveyor_init(self):
        GPIO.output(self.con4_port, True)

    def con2_On(self):
        GPIO.output(self.con4_port, False)

    def con2_Off(self):
        GPIO.output(self.con4_port, True)

    def run(self):
        global Check3
        self.conveyor_init()
        while True:
            if Check3 == 1:
                self.con2_On()
                time.sleep(8) 
            elif Check3 == 0:
                self.con2_Off()

class PushMotor1(Thread):
    def __init__(self):
        Thread.__init__(self, name='PushMotor1')
        self.ports = 23 # 16
        GPIO.setup(self.ports, GPIO.OUT)

    def __del__( self ):
        print( "Closing PushMotor1" )

    def push_activate1(self):
        GPIO.output(self.ports, False)
        time.sleep(5.73)
        GPIO.output(self.ports, True)
    
    def push_deactivate1(self):
        GPIO.output(self.ports, True)
    
    def run(self):
        global Check2
        while True:
            if Check2 == 1:
                self.push_activate1()
                Check2 = 0
                print('PushMotor1 is On')
            else:
                self.push_deactivate1()

class PushMotor2(Thread):
    def __init__(self):
        Thread.__init__(self, name='PushMotor2')
        self.ports = 24 # 18
        GPIO.setup(self.ports, GPIO.OUT)

    def __del__( self ):
        print( "Closing PushMotor2" )

    def push_activate2(self):
        GPIO.output(self.ports, False)
        time.sleep(5.73)
        GPIO.output(self.ports, True)

    def push_deactivate2(self):
        GPIO.output(self.ports, True)
    
    def run(self):
        global Check3
        while True:
            if Check3==1:
                self.push_activate2()
                print('PushMotor2 is On')
                Check3 = 0
                
            else:
                self.push_deactivate2()

class IRSensor1(Thread):
    def __init__(self, M2Cque, C2Mque):
        Thread.__init__(self, name='IRSensor1')
        self.port = 16 # 36

        self.C2Mque = C2Mque
        self.M2Cque = M2Cque
        GPIO.setup(self.port, GPIO.IN)

    def __del__( self ):
        print( "Closing IRSensor1" )

    def run(self):
        global Check1, running
        while True: 
            if running == 1:
                if GPIO.input(self.port) == 0:
                    Check1 = 1
                    self.M2Cque.put(Check1)
                    print('active Put')
                    time.sleep(2)
                    Check1 = 0                
                else:
                    Check1 = 0
            else:
                continue

class IRSensor2(Thread):
    def __init__(self, C2Mque, item_list):
        Thread.__init__(self, name='IRSensor2')

        self.port = 21 # 40
        self.C2Mque = C2Mque
        self.item_list = item_list
        GPIO.setup(self.port, GPIO.IN)

    def __del__( self ):
        print( "Closing IRSensor2" )

    def run(self):
        global Check2,Reject_Item1
        while True:
            if GPIO.input(self.port) == 0:
                if self.C2Mque.qsize() == 0:
                    continue
                else:
                    Check_type = self.C2Mque.get(timeout=100) # get Output value from Queue( Camera to Machine )
                    print('CheckType : {}'.format(Check_type)) # just test code
                    if Check_type == Reject_Item1:
                        Check2 = 1 # if Check type is 'A', PushMotor1 is On
                        print('Reject_Item1 Sensed')
                        
                    else:
                        self.item_list.put(Check_type) # B or C case
                        print('Not Type Reject_Item1')
                        Check2 = 0
            else:
                Check2 = 0
            time.sleep(1)

class IRSensor3(Thread):
    def __init__(self, C2Mque, item_list):
        Thread.__init__(self, name='IRSensor3')

        self.port = 20 # 38
        self.C2Mque = C2Mque
        self.item_list = item_list
        GPIO.setup(self.port, GPIO.IN)

    def __del__( self ):
        print( "Closing IRSensor3" )

    def run(self):
        global Check3, Reject_Item2
        while True:
            if GPIO.input(self.port) == 0:

                if self.item_list.qsize() == 0:
                    continue
                else:
                    Check_type = self.item_list.get(timeout=100)
                    print('CheckType : {}'.format(Check_type)) # just test code
                    print('New Check3 : {}'.format(Check3))
                    if Check_type == Reject_Item2:
                        Check3 = 1
                        print('Reject_Item2 Sensed')
                    else:
                        Check3 = 0
                        print('Error Type Sensed')

            else:
                Check3 = 0
            time.sleep(1)


class MachineProcess(Process):
    def __init__( self, M2Cque, C2Mque):
        # Process.__init__(self, name='MachineProcess')
        self.M2Cque = M2Cque
        self.C2Mque = C2Mque
        self.item_list = Queue()
        self.conveyor_main = Conveyor_main()
        self.conveyor1 = Conveyor1()
        self.conveyor2 = Conveyor2()
        self.push1 = PushMotor1()
        self.push2 = PushMotor2()
        self.IR1 = IRSensor1(self.M2Cque, self.C2Mque)
        self.IR2 = IRSensor2(self.C2Mque, self.item_list)
        self.IR3 = IRSensor3(self.C2Mque, self.item_list)
        print( '[MachineProcess __init__]' )

    def __del__( self ):
        print( '[MachineProcess __del__]' )

    def run(self):
        # thread start
        self.conveyor_main.start()
        self.conveyor1.start()
        self.conveyor2.start()
        self.push1.start()
        self.push2.start()
        self.IR1.start()
        self.IR2.start()
        self.IR3.start()

    def change_running(self, a):
        global running
        running = a

    def change_running2(self, a):
        global running2
        running2 = a

    def Get_Reject_Item1(self, a):
        global Reject_Item1
        Reject_Item1 = a
       
    def Get_Reject_Item2(self, a):
        global Reject_Item2
        Reject_Item2 = a
        

    #화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, Ui_Dialog) :
    def __init__(self, M2Cque, C2Mque) :
        super().__init__()
        self.setupUi(self)
        self.initUI()
        self.start = 0
        self.setting = 0
        self.M2Cque = M2Cque
        self.C2Mque = C2Mque
        self.item_list = Queue()
        self.running = False
        self.TMP = MachineProcess(self.M2Cque, self.C2Mque)
        Process(target=self.TMP.run())
        # self.TMP.start()

        print( '[WindowClass __init__]' )
        
        #버튼에 기능을 연결하는 코드
        self.btn_1.clicked.connect(self.button1Function)
        self.btn_2.clicked.connect(self.button2Function)
        self.btn_3.clicked.connect(self.button3Function)
        
        self.type_1.currentIndexChanged.connect(self.combo1Function)
        self.type_2.currentIndexChanged.connect(self.combo2Function)
        
        self.qPixmapFileVar = QPixmap()
        self.qPixmapFileVar.load("conveyor1.png")
        self.qPixmapFileVar = self.qPixmapFileVar.scaled(580,440)
        self.conveyor.setPixmap(QtGui.QPixmap(self.qPixmapFileVar))#image path
        
        self.pushButton.clicked.connect(self.addComboBoxItem)
        self.pushButton_2.clicked.connect(self.deleteComboBoxItem)
        
    def __del__( self ):
        print( '[WindowClass __del__]' )
        os._exit(0)
        
    def initUI(self):
        self.setWindowTitle('ARAF')
        self.setWindowIcon(QIcon('raspi.png'))
        self.show()

    #btn_1이 눌리면 작동할 함수
    def button1Function(self) :
        self.textEdit.append('Start')
        self.btn_1.setEnabled(False)
        self.type_1.setEnabled(False)
        self.type_2.setEnabled(False)
        self.running = 1
        self.TMP.change_running(self.running)
        self.TMP.change_running2(self.running)
        self.btn_2.setEnabled(True)

    #btn_2가 눌리면 작동할 함수
    def button2Function(self) :
        self.btn_2.setEnabled(False)
        self.running = 0
        self.TMP.change_running(self.running)
        time.sleep(0.1)
        self.textEdit.append('It stops in five seconds.')
        for i in range (5,-1,-1):
            self.textEdit.append('{}'.format(i))
            QApplication.processEvents()
            time.sleep(1)
        self.TMP.change_running2(self.running)
        self.btn_1.setEnabled(True)
        self.type_1.setEnabled(True)
        self.type_2.setEnabled(True)
        self.btn_2.setEnabled(False)
        self.conveyor.setPixmap(QtGui.QPixmap(self.qPixmapFileVar))#image path
       
        #btn_3가 눌리면 작동할 함수
    def button3Function(self) :
        print("exit")
        self.running = 0
        self.TMP.change_running(self.running)
        self.TMP.change_running2(self.running)
        # self.mp.close()
        os._exit(0)

    def combo1Function(self) :
        global Item_Dictionary, Item1
        Item1 = self.type_1.currentIndex()
        Item1_1 = self.type_1.currentText()
        self.textEdit.append('{}_Select'.format(Item1_1))
        self.TMP.Get_Reject_Item1(Item1)
        Item_Dictionary[Item1] = Item1_1

    def combo2Function(self) :
        global Item_Dictionary, Item2
        Item2 = self.type_2.currentIndex()
        Item2_1 = self.type_2.currentText()
        self.textEdit.append('{}_Select'.format(Item2_1))
        self.TMP.Get_Reject_Item2(Item2)
        Item_Dictionary[Item2] = Item2_1
        
    def addComboBoxItem(self) :
        self.type_1.addItem(self.Add_item.toPlainText())
        self.type_2.addItem(self.Add_item.toPlainText())
        self.Delete_combobox.addItem(self.Add_item.toPlainText())
        self.textEdit.append("Item Added")

    def deleteComboBoxItem(self) :
        self.delidx = self.Delete_combobox.currentIndex()
        self.type_1.removeItem(self.delidx)
        self.type_2.removeItem(self.delidx)
        self.Delete_combobox.removeItem(self.delidx)
        self.textEdit.append("Item Deleted")

class CameraProcess( Process, WindowClass, NetFunc):
    def __init__( self, host, port, M2Cque, C2Mque):
        Process.__init__(self, name='CameraProcess')
        WindowClass.__init__(self, M2Cque, C2Mque)
        NetFunc.__init__( self, host, port )
        
        self.M2Cque = M2Cque
        self.C2Mque = C2Mque
        print( '[CameraProcess __init__]' )

    def __del__( self ):
        print( '[CameraProcess __del__]' )

    def sendImg2Server( self, model, img_roi ):
        # set imencode parameter. set image quality 0~100 (100 is the best quality). default is 95
        encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),100]

        # image encoding,  encode_param is composed of [1, 100]
        result, imgencode = cv2.imencode('.jpg', img_roi, encode_param)
        if result==False:
            print("Error : result={}".format(result))
        
        
        # Convert numpy array
        roi_data = np.array(imgencode)

        # Convert String for sending Data
        bytesData = roi_data.tobytes()

        # Send to server
        self.sendData(bytesData)
        self.predictType(model, bytesData)
        

    def predictType( self, model, bytesData ):
        global Item_Dictionary, Item1, Item2
        imgdata = np.frombuffer(bytesData, dtype='uint8')

        # img decode
        decimg=cv2.imdecode(imgdata,1)
        img_location = './img_file/buf.png'

        cv2.imwrite(img_location, decimg)

        """
        Create an array of the shape to supply to the Keras model
        The number of 'lengths' or images that can be placed in an array...
        ..determined by the first position of the tuple, in this case '1'
        """
        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
        image = Image.open(img_location)
        size = (224, 224)
        image = ImageOps.fit(image, size, Image.ANTIALIAS)


        #turn the image into a numpy array
        image_array = np.asarray(image)

        # Normalize the image
        normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1

        # Load the image into the array
        data[0] = normalized_image_array

        prediction = model.predict(data)
        predict_class = max(prediction[0])
        if predict_class < 0.8:
            print("[ Cannot Distinguish ]")
            predict_type = 'ERR_001'
            classification = '0'
        else:
            for i in range(len(prediction[0])):
                if prediction[0][i] == predict_class:
                    classification = i
                    predict_type = Item_Dictionary[i]
                    print(classification)
                    print(predict_type)
                    break
        
        if Item1 == classification:
            self.count = 2
        elif Item2 == classification:
            self.count = 3
        else:
            self.count = 4
        
        img = "conveyor"+str(count)+".png"
        self.qPixmapFileVar.load(img)
        self.qPixmapFileVar = self.qPixmapFileVar.scaled(580,440)
        self.conveyor.setPixmap(QtGui.QPixmap(self.qPixmapFileVar))#image path
        self.C2Mque.put(classification)

        cal = 'ADD'
        now = datetime.datetime.now()
        capdate = now.strftime( '%Y-%m-%d' )
        captime = now.strftime( '%H:%M:%S' )

        product_info = predict_type + cal + capdate + captime
        product_data = product_info.encode()

        self.textEdit.append('Predict Type : ' + predict_type)
        self.textEdit.append('Date : {}'.format(capdate))
        self.textEdit.append('Time : {}'.format(captime))
        self.textEdit.append('Product ADD Complete')
        self.textEdit.append('')

        self.sendData(product_data)


    def run(self):
        print('cam start')
        np.set_printoptions(suppress=True)

        cap = cv2.VideoCapture(-1)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,480)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)

        model = tf.keras.models.load_model("initial_model.hdf5")

        try:
            while True:
                ret, img_color = cap.read()
                if ret == False:
                    continue
                img = cv2.cvtColor(img_color, cv2.COLOR_BGR2RGB) 
                h,w,c = img.shape
                qImg = QtGui.QImage(img.data, w, h, w*c, QtGui.QImage.Format_RGB888)
                pixmap = QtGui.QPixmap.fromImage(qImg)
                self.cam.setPixmap(pixmap)
                cv2.waitKey(1)
                QApplication.processEvents()

                if self.M2Cque.qsize() == 0:
                    continue
                else:

                    img_roi = cv2.resize(img_color, dsize=(224, 224))
                    print('MachineVision process progressed...')

                    # Open GUI
                    img = cv2.cvtColor(img_roi, cv2.COLOR_BGR2RGB) 
                    h,w,c = img.shape
                    qImg = QtGui.QImage(img.data, w, h, w*c, QtGui.QImage.Format_RGB888)
                    pixmap = QtGui.QPixmap.fromImage(qImg)
                    self.img.setPixmap(pixmap)

                    ''' ### send image data to server ### '''
                    self.sendImg2Server(model, img_roi)
    
                    print(self.M2Cque.get(timeout=100))
                    
            cap.release()

        except KeyboardInterrupt :
            # os._exit(0)
            # cv2.destroyAllWindows()
            print('KeyboardInterrupt')
        finally:
            # os._exit(0)
            print('Finally Closed')
                
if __name__ == '__main__':
    server_ip = '192.168.0.84'
    server_port = 9000
    M2Cque = Queue() # MachineProcess to CameraProcess Queue
    C2Mque = Queue() # CameraProcess to MachineProcess Queue

    app = QApplication(sys.argv)
    CP = CameraProcess(server_ip, server_port, M2Cque, C2Mque)
    CP.show()
    CP.run()
    app.exec_()    