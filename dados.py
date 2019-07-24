#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the DADOS repository; a Cortix module.
# https://cortix.org

import time, os, datetime, serial
import numpy as np
from cortix.src.module import Module
from vault.rs_232 import RS_232

class Dados(Module):
    '''
    DADOS is a Cortix module for data acquistion.

    Ports
    =====
    rs-232:
    mcc-118:
    '''

    def __init__(self):

        super().__init__()

        self.initial_time = 0.0
        self.end_time     = np.inf
        self.time_step    = 0.1

        # RS-232 default configuration
        self.rs232_filename = 'rs-232'
        self.rs232_wrk_dir = '/tmp/dados/rs-232'
        home = os.path.expanduser('~')
        self.db_dir=os.path.join(home,'IR_7040_database')
        for f in [self.rs232_wrk_dir,self.db_dir]:
            if not os.path.isdir(f):
                os.makedirs(f)
        tmp_file = self.rs232_wrk_dir+'/'+self.rs232_filename
        if os.path.exists(tmp_file):
            os.remove(tmp_file)
        self.rs232_dev = '/dev/ttyUSB0'
        self.rs232_baud_rate = 9600
        self.rs232_timeout = 5
        self.rs232_request_string = 'rs232-null-request-string'
        self.rs232_request_string_encoding = 'ascii'

        # MCC 118 configuration

    def run(self):

        # Access module's ports
        rs_232_port  = self.get_port('rs_232')
        mcc_118_port = self.get_port('mcc_118')

        # Start RS-232 interface
        if rs_232_port:
            rs_232 = serial.Serial( port=self.rs232_dev, 
                                    baudrate=self.rs232_baud_rate,
                                    timeout=5,
                                    stopbits=serial.STOPBITS_ONE,
                                    parity=serial.PARITY_NONE,
                                    bytesize=serial.EIGHTBITS )

        # Start MCC 118 interface
        if mcc_118_port:
            pass
        daq_time=0
        # Evolve daq_time    
        oldline=''
        while daq_time < self.end_time:

            if rs_232_port:

                # Send request string to the rs-232
                rs_232.write(self.rs232_request_string.encode(self.rs232_request_string_encoding))
                line = rs_232.readline()
                line = str(line.decode('utf-8', errors='replace').strip())
                if line == oldline:
                    time.sleep(0.2)
                    continue
                oldline = line
                try:
                    timestamp = str(datetime.datetime.now())[:-7]
                    minutes = timestamp[14:16]
                    filetime = str(datetime.datetime.now())[:10]
                    self.filename = os.path.join(self.db_dir,self.rs232_filename+filetime+'.csv')
                    splitline = line.split()

                    for n in range(3,25):
                        splitline[n] = splitline[n][0]+'.'+splitline[n][1:3]+'e'+splitline[n][3:]
                    line = timestamp+', '+', '.join(splitline)+'\n'
                except Exception as e:
                    print('------Error-------')
                    print(e)
                    continue
                print(line)
                if not os.path.isfile(self.filename):
                    with open(self.filename,'w') as f:
                        f.write('Date and Time, Type, Callback, Status Group, ch1_rate_filtered, ch1_rate_unfiltered, ch1_dose, ch1_alarm_high, ch1_alarm_low, ch2_rate_filtered, ch2_rate_unfiltered, ch2_dose, ch2_alarm_high, ch2_alarm_low, Leak Rate: Gallons/Day, Leak Rate: %Power Level, ch3_rate_filtered, ch3_rate_unfiltered, ch3_dose, ch3_alarm_high, ch3_alarm_low, ch4_rate_filtered, ch4_rate_unfiltered, ch4_dose, ch4_alarm_high, ch4_alarm_low, Probe_status, Checksum\n')
                
                with open(self.filename,'a') as f:
                    f.write(line)

