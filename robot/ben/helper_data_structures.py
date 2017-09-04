import time
import numpy as np
from ben.helper_IO import load_list_from_file,write_list_to_file
from ben.helper_location_and_bearing import *


class Bot(object):


    def __init__(self,R,calib=False):
        self.grabbed=False
        self.R=R
        self.motors=R.motors
        self.location=R.location
        if calib:
            # This code can be used to calibrate the robot. This calibration information can then be accesed through
            # a Calibration object

            calibrate(R,5,100,graduation=5,samples=8,drive_turn="drive",write=True)
            calibrate(R,5,100,graduation=5,samples=8,drive_turn="turn",write=True)

        self.constants=Calibration()

    def see(self,*args,**kwargs):
        return self.R.see(*args,**kwargs)

    def drive(self,dist,speed=100,t=0.25):

        average_speed=self.constants.d_averages[speed]

        self.R.motors[0].m0.power = speed
        self.R.motors[0].m1.power = speed
        try:
            time.sleep(dist/average_speed)
        except:
            print (dist,average_speed)
            time.sleep((abs(dist/average_speed)))
        self.R.motors[0].m0.power = 0
        self.R.motors[0].m1.power = 0
        time.sleep(t)

    def turn(self,angle_right,speed=50,t=0.25):

        average_speed = self.constants.t_averages[speed]


        time.sleep(2)
        if angle_right<0:
            angle_right=abs(angle_right)
            speed=-speed

        self.R.motors[0].m0.power = speed
        self.R.motors[0].m1.power = -speed

        time.sleep(angle_right/average_speed)
        self.R.motors[0].m0.power = 0
        self.R.motors[0].m1.power = 0
        time.sleep(t)

    def drive_raw(self,speed, seconds):
        self.R.motors[0].m0.power = speed
        self.R.motors[0].m1.power = speed
        time.sleep(seconds)
        self.R.motors[0].m0.power = 0
        self.R.motors[0].m1.power = 0

    def turn_raw(self,speed, seconds):
        self.R.motors[0].m0.power = speed
        self.R.motors[0].m1.power = -speed
        time.sleep(seconds)
        self.R.motors[0].m0.power = 0
        self.R.motors[0].m1.power = 0

    def grab(self):
        self.grabbed=self.R.grab()

    def release(self):
        self.R.release()
        self.grabbed=False

    @property
    def heading(self):
        return self.R.heading

class Calibration(object):

    def __init__(self,drive_dict=None,turn_dict=None):
        if drive_dict and turn_dict:
            self.drive_dict=drive_dict
            self.turn_dict=turn_dict

        else:
            self.drive_dict,self.turn_dict=load_calibrations()

        for i in self.drive_dict.keys():
            self.drive_dict[i]=self.reject_outliers(self.drive_dict[i])

        for i in self.turn_dict.keys():
            self.turn_dict[i] = self.reject_outliers(self.turn_dict[i])

        self.update_averages()

    def update_averages(self):
        self.update_outliers()
        self.d_averages = {key: np.average(values) for (key, values) in self.drive_dict.iteritems()}
        self.t_averages = {key: np.average(values) for (key, values) in self.turn_dict.iteritems()}

    def update_outliers(self):

        for key,value in self.drive_dict.iteritems():
            self.drive_dict[key]=self.reject_outliers(value)

        for key, value in self.turn_dict.iteritems():
            self.turn_dict[key] = self.reject_outliers(value)

    def update_data(self,data,driveturn="drive"):
        if driveturn=="drive":
            for key,value in data.iteritems():
                l=len(value)
                self.drive_dict[key].append()
                del self.drive_dict[key][:l]
        elif driveturn=="turn":
            for key,value in data.iteritems():
                l=len(value)
                self.turn[key].append()
                del self.turn[key][:l]
        self.update_averages()



    def reject_outliers(self,data):

        std=np.std(data)
        mean=np.mean(data)
        low=lambda x:x>mean-2*std
        high=lambda x:x<mean+2*std

        return filter(high,filter(low,data))

    def get_average(self,drive_turn="drive",power=100):
        if drive_turn=="drive":
            return self.d_averages[power]
        elif drive_turn=="turn":
            return self.t_averages[power]



def calibrate(R,power_low,power_high,graduation=10,samples=15,drive_turn="drive",write=True):

    if drive_turn=="turn":
        R.drive_raw(100, 4)
        R.drive_raw(-100,0.1)

    powers=[]
    p=power_low

    while p<=power_high:
        powers.append(p)
        p+=graduation


    data=[]

    data.append(powers)

    for p in powers:
        consts=[]

        for i in range(samples):
            print (str(i+1)+"th sample at "+str(p)+"th power")
            pos = pos_and_bearing(R.see())
            if drive_turn=="drive":
                dtime=0.5

                #forwards


                R.drive_raw(p,dtime)
                time.sleep(0.5)
                pos2=pos_and_bearing(R.see())
                dist=distance(pos,pos2)
                speed=dist/dtime

                consts.append(speed)

                #backwards
                R.drive_raw(-p,dtime)
                time.sleep(0.5)
                pos3=pos_and_bearing(R.see())
                dist=distance(pos2,pos3)
                speed=dist/dtime

                consts.append(speed)

            if drive_turn=="turn":
                Ttime=0.5

                #right
                R.turn_raw(p,Ttime)
                time.sleep(0.5)
                pos2=pos_and_bearing(R.see())
                angle=bearing_diff(pos,pos2)

                speed=angle/Ttime

                consts.append(speed)

                #left

                R.turn_raw(-p,Ttime)
                time.sleep(0.5)
                pos3=pos_and_bearing(R.see())
                angle=bearing_diff(pos2,pos3)

                speed=abs(angle/Ttime)

                consts.append(speed)

        data.append(consts)


    if write==True:
        if drive_turn=="drive":
            write_list_to_file("ben/helper_drive_calibration.txt",data)
            print ("writing driving constants")
        elif drive_turn=="turn":
            write_list_to_file("ben/helper_turn_calibration.txt",data)
            print ("writing turning constants")

    return data



    return None


def load_calibrations(files=("helper_drive_calibration.txt","helper_turn_calibration.txt")):
    drive_constants = load_calibration(drive_turn="drive",files=(files))
    turn_constants = load_calibration(drive_turn="turn",files=(files))
    return drive_constants,turn_constants

def load_calibration(drive_turn="drive",files=("drive_calibration.txt","turn_calibration.txt")):
    ls=[]

    if drive_turn=="drive":
        ls=load_list_from_file("ben/drive_calibration.txt")
    elif drive_turn=="turn":
        ls=load_list_from_file("ben/turn_calibration.txt")
    dic={}
    for index,value in enumerate(ls[1:]):
        dic[float(ls[0][index])]=[float(v) for v in value]
    return dic