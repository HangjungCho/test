from tensorflow.keras.models import load_model
from multiprocessing import Process, Queue
from threading import Thread
from PIL import Image, ImageOps

import tensorflow as tf
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
        global Check2, Check3
        self.conveyor_init()
        while True:
            if (Check2 or Check3) == 1 :
                self.main_conveyor_Off()
                time.sleep(2)
            else:
                self.main_conveyor_On()



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
        global Check1
        while True:
            if GPIO.input(self.port) == 0:
                Check1 = 1
                self.M2Cque.put(Check1)
                print('active Put')
                time.sleep(2)
                Check1 = 0                
            else:
                Check1 = 0 



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
        global Check2
        while True:
            if GPIO.input(self.port) == 0:
                if self.C2Mque.qsize() == 0:
                    continue
                else:
                    Check_type = self.C2Mque.get(timeout=100) # get Output value from Queue( Camera to Machine )
                    print('CheckType : {}'.format(Check_type)) # just test code
                    if Check_type == 'A':
                        Check2 = 1 # if Check type is 'A', PushMotor1 is On
                        print('Type A Sensed')
                        
                    else:
                        self.item_list.put(Check_type) # B or C case
                        print('Not Type A')
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
        global Check3
        while True:
            if GPIO.input(self.port) == 0:

                if self.item_list.qsize() == 0:
                    continue
                else:
                    Check_type = self.item_list.get(timeout=100)
                    print('CheckType : {}'.format(Check_type)) # just test code
                    print('New Check3 : {}'.format(Check3))
                    if Check_type == 'B':
                        Check3 = 1
                        print('Type B Sensed')
                    elif Check_type == 'C':
                        Check3 = 0
                        print('Type C Sensed')
                    else:
                        Check3 = 0
                        print('Error Type Sensed')

            else:
                Check3 = 0
            time.sleep(1)

class TurnOff(Conveyor_main, Conveyor1, Conveyor2, PushMotor1, PushMotor2):
    def __init__(self):
        Conveyor_main.__init__(self)
        Conveyor1.__init__(self)
        Conveyor2.__init__(self)
        PushMotor1.__init__(self)
        PushMotor2.__init__(self)
    def __del__(self):
        print('Turn Off All Motor')

    def AllOff(self):
        self.main_conveyor_Off()
        self.con1_Off()
        self.con2_Off()
        self.push_deactivate1()
        self.push_deactivate2()
        


class MachineProcess( Process, TurnOff ):
    def __init__( self, M2Cque, C2Mque):

        self.M2Cque = M2Cque
        self.C2Mque = C2Mque
        self.item_list = Queue()
        Process.__init__( self, name = "MachineProcess" )
        TurnOff.__init__(self)
        print( '[MachineProcess __init__]' )

    def __del__( self ):
        self.AllOff()
        print( '[MachineProcess __del__]' )

    def run(self):


        # make object
        conveyor_main = Conveyor_main()
        conveyor1 = Conveyor1()
        conveyor2 = Conveyor2()
        push1 = PushMotor1()
        push2 = PushMotor2()
        IR1 = IRSensor1(self.M2Cque, self.C2Mque)
        IR2 = IRSensor2(self.C2Mque, self.item_list)
        IR3 = IRSensor3(self.C2Mque, self.item_list)

        # thread start
        conveyor_main.start()
        conveyor1.start()
        conveyor2.start()
        push1.start()
        push2.start()
        IR1.start()
        IR2.start()
        IR3.start()        
        



class CameraProcess( Process, NetFunc):
    def __init__( self, host, port, M2Cque, C2Mque):
        Process.__init__(self, name='CameraProcess')
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

        # Show image
        cv2.imshow('image', img_roi)
        
        # Convert numpy array
        roi_data = np.array(imgencode)

        # Convert String for sending Data
        stringData = roi_data.tostring()

        # Send to server
        self.sendData(stringData)
        self.predictType(model, stringData)
        

    def predictType( self, model, stringData ):
        imgdata = np.frombuffer(stringData, dtype='uint8')

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

        class_1 = prediction[0][0]
        class_2 = prediction[0][1]
        class_3 = prediction[0][2]
        class_4 = prediction[0][3]
        predict_class = max(prediction[0])

        if predict_class < 0.8:
            print("[ Cannot Distinguish ]")
            predict_type = 'ERR_001'
            classification = 'E'
        else:
            if class_1 == predict_class:
                print('prediction result : Dinosaur')
                predict_type = 'DSR_001'
                classification = 'A'

            elif class_2 == predict_class:
                print('prediction result : Airplane')
                predict_type = 'APL_001'
                classification = 'C'

            elif class_3 == predict_class:
                print('prediction result : Whale')
                predict_type = 'WAL_001'
                classification = 'B'

            elif class_4 == predict_class:
                print('prediction result : Empty')
                predict_type = 'ERR_001'
                classification = 'E'

            self.C2Mque.put(classification)

        cal = 'ADD'
        now = datetime.datetime.now()
        capdate = now.strftime( '%Y-%m-%d' )
        captime = now.strftime( '%H:%M:%S' )

        product_info = predict_type + cal + capdate + captime
        product_data = product_info.encode()


        self.sendData(product_data)


    def run(self):
        np.set_printoptions(suppress=True)

        cap = cv2.VideoCapture(-1)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,480)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)

        # load model.
        model = load_model('initial_model.hdf5')
        try:
            while True:
                ret, img_color = cap.read()
                if ret == False:
                    continue
                cv2.imshow('Camera', img_color)

                cv2.waitKey(1)
                    
                if self.M2Cque.qsize() == 0:
                    continue
                else:
                    img_roi = cv2.resize(img_color, dsize=(224, 224))
                    print('MachineVision process progressed...')
                    ''' ### send image data to server ### '''
                    self.sendImg2Server(model, img_roi)

                    print(self.M2Cque.get(timeout=100))

        except KeyboardInterrupt :
            cv2.destroyAllWindows()
                
if __name__ == '__main__':
    server_ip = '192.168.0.125'
    server_port = 9000
    M2Cque = Queue() # MachineProcess to CameraProcess Queue
    C2Mque = Queue() # CameraProcess to MachineProcess Queue

    MP = MachineProcess( M2Cque, C2Mque )
    MP.start()
    CP = CameraProcess(server_ip, server_port, M2Cque, C2Mque)
    CP.start()
            
            

