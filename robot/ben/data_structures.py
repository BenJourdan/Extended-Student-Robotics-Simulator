from movement import calibrate,Calibration
import time


MARKER_TOKEN_GOLD   = 'token_gold'
MARKER_TOKEN_SILVER = 'token_silver'
MARKER_ARENA = 'arena'
MARKER_ROBOT = 'robot'

token_filter = lambda m: m.info.marker_type in (MARKER_TOKEN_GOLD, MARKER_TOKEN_SILVER)
silver_filter = lambda m:m.info.marker_type in (MARKER_TOKEN_SILVER)
gold_filter = lambda m:m.info.marker_type in (MARKER_TOKEN_GOLD)
arena_filter = lambda m: m.info.marker_type in (MARKER_ARENA)
robot_filter = lambda m: m.info.marker_type in (MARKER_ROBOT)


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
            print dist,average_speed
            time.sleep((abs(dist/average_speed)))
        self.R.motors[0].m0.power = 0
        self.R.motors[0].m1.power = 0
        time.sleep(t)

    def turn(self,angle_right,speed=100,t=0.25):

        average_speed = self.constants.t_averages[speed]
        if angle_right<0:
            angle_right=abs(angle_right)
            speed=-speed

        self.R.motors[0].m0.power = speed
        self.R.motors[0].m1.power = -speed

        time.sleep(angle_right/average_speed)
        self.R.motors[0].m0.power = 0
        self.R.motors[0].m1.power = 0
        time.sleep(t)

    def grab(self):
        self.grabbed=self.R.grab()

    def release(self):
        self.R.release()
        self.grabbed=False

    @property
    def heading(self):
        return self.R.heading

def coords_to_data(name,coords,dic,destroyOld=False):
    res=[]
    for coord in coords:
        res.append([coord.x,coord.y])
    old=dic[name]

    if destroyOld:
        dic[name]=res
        return dic
    else:
        res+=old

        res_set = set(map(tuple,res))
        res=map(list,res_set)
        dic[name]=res
        return dic




class coordinate(object):
    def __init__(self,x,y):
        self.x=x
        self.y=y
        self.bearing=None #bearing gets created later
    def __str__(self):
        return "coordinate at ({},{}),bearing {} degrees from North".format(str(self.x),str(self.y),str(self.bearing))
    def __repr__(self):
        return self.__str__()