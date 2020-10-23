"""
A simple class for interfacing with a Black Cat Systems GM-10 radiation detector.
The GM-10 operates using a serial port interface, and the number of counts of radiation
are determined purely by the number of bytes read from the serial port.
This means that you need to continuously poll the sensor and perform your own
computation of radiation levels based off of CPS and the documented calibration for
the tube.
"""

import serial
from threading import Thread
from time import sleep

class GM10Sensor():

    def __init__(self, serialport, cpslimit, mrhr_calibration, avgsample, alertlevel):
        self.serialport = serialport
        self.cpslimit = cpslimit
        self.calibration = mrhr_calibration
        self.readings = []
        self.cancelled = False
        self.avgsample = avgsample
        self.alertlevel = alertlevel
        self.radiation_level = {
            "CPS": 0,
            "mRhr": 0,
            "AvgmRhr": 0,
            "Alert": False,
            "Average over seconds": 0
        }

    def _read_worker(self):
        try:
            ser = serial.Serial(self.serialport,57600,timeout=1)
        except Exception as e:
            LOGGER.error("Can't open serial port: {}".format(e))
            return()
        while(not self.cancelled):
            count = len(ser.read(self.cpslimit))
            self.readings.append(count)
            if len(self.readings) > self.avgsample:
                self.readings.pop(0)
            ticks = len(self.readings)
            cpssum = sum(self.readings)
            cps = self.readings[ticks-1]
            if ticks < 10:
                a = 0
            else:
                a = ticks - 10
            cpmshort = (sum(self.readings[a:ticks]) * 6)
            if cps > self.alertlevel:
                alert = True
            else:
                alert = False
            mrhrshort = cpmshort / self.calibration
            mrhrlong = (cpssum / (ticks / 60)) / self.calibration
            self.radiation_level = {
                "CPS": cps,
                "mR/hr": mrhrshort,
                "Avg mR/hr": mrhrlong,
                "Alert": alert,
                "Average over seconds": ticks
            }

    def GetCurrentReading(self):
        return self.radiation_level

    def StartSurvey(self):
        survey_thread = Thread(target=self._read_worker)
        survey_thread.start()
        return survey_thread

    def StopSurvey(self):
        self.cancelled = True
      
    def GetReadings(self):
        return self.readings
