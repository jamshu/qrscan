#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
author: Jamshid K
website: orchidinfosys.com 
last edited: October 2015
"""

import sys
from PyQt4 import QtGui, QtCore

from time import strftime

from sys import argv
import zbar
import xmlrpclib

def get_connection():
    return sock

class PizzaAttendance(QtGui.QMainWindow):

    def get_outlets(self):
        username = 'admin' #the user
        pwd = 'fslhggihgvplkhgvpdl'      #the password of the user
        dbname = 'yas_live'    #the database

        # Get the uid
        sock_common = xmlrpclib.ServerProxy ('http://localhost:8069/xmlrpc/common')
        uid = sock_common.login(dbname, username, pwd)

        #replace localhost with the address of the server
        sock = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/object')


        args = [] #query clause
        ids = sock.execute(dbname, uid, pwd, 'pos.config', 'search', args)

        fields = ['name','name'] #fields to read
        data = sock.execute(dbname, uid, pwd, 'pos.config', 'read', ids, fields) #ids is a list of id
        print "outlet data>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",data
        return data
        



    
    def __init__(self):
        super(PizzaAttendance, self).__init__()
        
        self.initUI()
        
    def initUI(self):      

        #Combo
        combo = QtGui.QComboBox(self)
        i = 0
        for outlet in self.get_outlets():
            if i == 0:
                inital_message = outlet.get('name') + '/' +str(outlet.get('id'))
            i =i+1
            combo.addItem(outlet.get('name') + '/' +str(outlet.get('id')))
        combo.move(50, 50)
        combo.activated[str].connect(self.onActivated)   
        

        #Calendar

        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.Time)
#Reduced update time to fasten the change from w/ secs to w/o secs
        timer.start(10)

        self.lcd = QtGui.QLCDNumber(self)
        self.lcd.move(350,50)
        self.lcd.resize(350,50)
        self.lcd.setDigitCount(8)

        #Message Label

        self.status_message = QtGui.QLabel(inital_message, self)
        self.status_message.move(350,100)
        self.status_message.resize(350,100)
        self.status_message.setStyleSheet("QWidget { background-color: yellow;color:blue ;font-size: 250%}")



#        btn1 = QtGui.QPushButton("SignIN", self)
#        btn1.move(50, 250)

#        btn2 = QtGui.QPushButton("SignOut", self)
#        btn2.move(170, 250)
#      
#        btn1.clicked.connect(self.buttonClicked)            
#        btn2.clicked.connect(self.buttonClicked)


        btn3 = QtGui.QPushButton("Check", self)
        btn3.move(50, 250)
        btn3.clicked.connect(self.buttonClicked)


        
        self.statusBar()
        
        self.setGeometry(500, 100, 800, 400)
        self.setWindowTitle('Orchid Attendance Marker')
        self.show()

    def onActivated(self, text):
      
        self.status_message.setText(text)
#        self.status_message.adjustSize() 

    def Time(self):
        self.lcd.display(strftime("%H"+":"+"%M"+":"+"%S"))


    def process_attendance(self,employee_id,outlet_id):
        username = 'admin' #the user
        pwd = 'fslhggihgvplkhgvpdl'      #the password of the user
        dbname = 'yas_live'    #the database
        action = 'sign_in'

        # Get the uid
        sock_common = xmlrpclib.ServerProxy ('http://localhost:8069/xmlrpc/common')
        uid = sock_common.login(dbname, username, pwd)

        #replace localhost with the address of the server
        sock = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/object')

        args = [('employee_id','=',employee_id)] #query clause
        ids = sock.execute(dbname, uid, pwd, 'hr.attendance', 'search', args)
        fields = ['action'] #fields to read
        data = sock.execute(dbname, uid, pwd, 'hr.attendance', 'read', ids, fields)
        if not data:
            self.onActivated(".....")
            action = 'sign_in'
        else:
            print "DDDDDD",data
            c = data[0]['action']
            if c == 'sign_in':
                action = 'sign_out'
            else:
                action = 'sign_in'
        
            
        print "********************",data


        attendance_data = {
           'employee_id': employee_id,
           'od_outlet_id':outlet_id,
           'action': action,
        }

        partner_id = sock.execute(dbname, uid, pwd, 'hr.attendance', 'create', attendance_data)


    # create a Processor
    def scann_barcode(self,outlet_id):

        proc = zbar.Processor()
        # configure the Processor
        proc.parse_config('enable')
        # initialize the Processor
        device = '/dev/video0'
        if len(argv) > 1:
            device = argv[1]
        #proc.request_size(800,480)
        proc.init(device)
        # enable the preview window
        proc.visible = True
        # read at least one barcode (or until window closed)
        proc.process_one()
        #proc.visible = True
        # hide the preview window
        proc.visible = False
        # extract results
        for symbol in proc.results:
            # do something useful with results
            print 'decoded', symbol.type, 'symbol', '"%s"' % symbol.data
            data_val=symbol.data
            data_list = data_val.split('-')
            
            employee_id = int(data_list[0])
            print "employee_id>>>>>>>>>>>>>>>>>>>>>>>",employee_id
            self.process_attendance(employee_id,outlet_id)
#            try:
#                employee_id = int(symbol.data)
#                self.process_attendance(employee_id)
#            except :
#                self.onActivated("Invalid")
                
                


        
    def buttonClicked(self):
     
        sender = self.sender()
        self.statusBar().showMessage(sender.text() + ' was pressed')
        print "combo>>>>>>>>>>>>>>>>>>",self.status_message.text()
        outlet_name = str(self.status_message.text())
       
        name_id = outlet_name.split('/')
        outlet_id = name_id[1]
        
        self.scann_barcode(int(outlet_id))

#        if sender.text() == 'SignIN':
#            self.scann_barcode('sign_in')
#        else:
#            self.scann_barcode('sign_out')


        
def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = PizzaAttendance()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
