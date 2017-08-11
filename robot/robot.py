__author__ = 'Ben'

from math import *

from sr.robot import *
import time
import numpy
from matplotlib.pyplot import *



R=Robot()

print(R.location)
print R.heading



def drive(speed, seconds):
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = speed
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0


turning_values=[]
driving_values=[]
turning_constant=0
turning_r_squared=0
driving_constant=0
driving_r_squared=0
def turn(speed, seconds):
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = -speed
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0


def calibrate(tspeed,dspeed,iterations,deltat):

    for a in range(1,3):
        for b in range(iterations):
            start=locate_bearing_and_position().bearing

            turn(tspeed*((a*2)-3),deltat)
            time.sleep(0.5)
            end=locate_bearing_and_position().bearing
            if a==1:
                if end>start:
                    end=end-360
                difference=start-end

            elif a==2:
                if start>end:
                    start=1-360
                difference=end-start

            const_val=deltat/difference

            if const_val<1.5*max(turning_values):
                turning_values.append(const_val)
            else:
                print (const_val, " to high a turning constant to be true",start,end,deltat)
    for a in range(2):
        turning_values.remove(max(turning_values))
        turning_values.remove(min(turning_values))

    for a in range(1,3):
        for b in range(iterations):
            start=locate_bearing_and_position()

            drive(-dspeed*((a*2)-3),deltat)
            time.sleep(0.5)
            end=locate_bearing_and_position()
            d=distance(start,end)
            drive_val=deltat/d
            driving_values.append(drive_val)

        for a in range(1,3):
            driving_values.remove(max(driving_values))
            driving_values.remove(max(driving_values))


    return numpy.average(turning_values),(1-numpy.std(turning_values, dtype=np.float64))**2,numpy.average(driving_values),(1-numpy.std(driving_values, dtype=np.float64))**2


token_filter = lambda m: m.info.marker_type in (MARKER_TOKEN_GOLD, MARKER_TOKEN_SILVER)
arena_filter = lambda m: m.info.marker_type in (MARKER_ARENA)

North=range(0,7)
East=range(7,14)
South=range(14,21)
West=range(21,28)

Northwest=((0.0,4.1),(4.1,8.0))
Northeast=((4.1,8.0),(4.1,8.0))
Southeast=((4.1,8.0),(0.0,4.1))
Southwest=((0.0,4.1),(0.0,4.1))

middle_size=0.4
saftey=middle_size+1
middle=((4-middle_size,4+middle_size),(4-middle_size,4+middle_size))
safteyzone=((4-saftey,4+saftey),(4-saftey,4+saftey))

c=(safteyzone[0][0],safteyzone[1][0])
d=(safteyzone[0][1],safteyzone[1][0])
a=(safteyzone[0][0],safteyzone[1][1])
b=(safteyzone[0][1],safteyzone[1][1])
SAFE=(a,b,c,d)
corners={str(a):(b,c),str(b):(a,d),str(c):(a,d),str(d):(b,c)}

#list containing target tokens and their locations and timestamp
TARGETS=[]
SUBTARGETS=[]
SEEN=[]
#bearing pile up cases error constants:


class coordinate(object):
    def __init__(self,x,y):
        self.x=x
        self.y=y
        self.bearing=None #bearing gets created later
    def __str__(self):
        return "coordinate at ({},{}),bearing {} degrees from North".format(str(self.x),str(self.y),str(self.bearing))

#hard coded waypoints:
fromtopbottom=2.5
fromsides=2.5
waypoints=[]
waypoints.append(coordinate(fromtopbottom,fromsides))
waypoints.append(coordinate(fromtopbottom,8-fromsides))
waypoints.append(coordinate(8-fromtopbottom,8-fromsides))
waypoints.append(coordinate(8-fromtopbottom,fromsides))


class wall_coordinate(object):
    def __init__(self,x,y,dist):
        self.x=x
        self.y=y
        self.dist=dist
        def __str__(self):
            return "({},{}),distance={}".format(str(self.x),str(self.y),self.dist)

def distance(A_real,real_or_tuple):
    A=A_real
    B=real_or_tuple
    try:
        return sqrt(((B.x-A.x)**2)+((B.y-A.y)**2))
    except:
        return sqrt(((B[0]-A.x)**2)+((B[1]-A.y)**2))


def marker_to_coordinate(marker):
    id=int(marker.info.offset)
    if 0<=id<7 :
        "in north"
        marker.x=(marker.info.offset+1)
        marker.y=8
        marker.wall="north"
    elif 0<=id<14:
        "in east"
        marker.x=8
        marker.y=8-(marker.info.offset-6)
        marker.wall="east"
    elif 14<=id<21:
        "in south"
        marker.x=8-(marker.info.offset-13)
        marker.y=0
        marker.wall="south"
    elif 21<=id<28:
        "in west"
        marker.x=0
        marker.y=(marker.info.offset-20)
        marker.wall="west"

def get_glob_loc(A,B):




    a=float(A.x)
    b=float(A.y)
    c=float(B.x)
    d=float(B.y)
    r_1=float(A.dist)
    r_2=float(B.dist)
    D=distance(A,B)
    x1=y1=x2=y2=0
    D=distance(A,B)
    if (D <= (r_1+r_2))and(D>=abs(r_1-r_2)):
        #circles intersect
        #herons formula
        a1=D+r_1+r_2
        a2=D+r_1-r_2
        a3=D-r_1+r_2
        a4=-D+r_1+r_2
        area=sqrt(a1*a2*a3*a4)/4
        #X coordinates
        val1=(a+c)/2+(c-a)*(r_1*r_1-r_2*r_2)/(2*D*D)
        val2=2*(b-d)*area/(D*D)
        x1=val1+val2
        x2=val1-val2

        #y coordinates
        val1=(b+d)/2+(d-b)*(r_1*r_1-r_2*r_2)/(2*D*D)
        val2=2*(a-c)*area/(D**2)
        y1=val1-val2
        y2=val1+val2

        pos=coordinate(x1,y1)
        neg=coordinate(x2,y2)

        if(0<=pos.x<=8 and 0<=pos.y<=8):
            return pos
        else:
            return neg

    else:
        print "circles do not intersect"

def locate_position(datum=0):
    if(datum==0):
        data=R.see(res=(1920,1080))
    else:
        data=datum
    arenatokens=filter(arena_filter,data)

    while(len(arenatokens)<2):
        print "can't see, turning"
        turn(15,1)
        data=R.see(res=(1920,1080))
        arenatokens=filter(arena_filter,data)
    for coord in arenatokens:
        marker_to_coordinate(coord)
    x=0
    y=0
    vals=0
    if len(arenatokens)%2!=0:
        temp =get_glob_loc(arenatokens[0],arenatokens[-1])
        x+=temp.x
        y+=temp.y
        vals+=1
        del arenatokens[-1]

    for i in range(0,len(arenatokens),2):
        temp=get_glob_loc(arenatokens[i],arenatokens[i+1])
        x+=temp.x
        y+=temp.y
        vals+=1

    x=x/vals
    y=y/vals
    return coordinate(x,y)

def locate_bearing_and_position(datum=0,TURN=True):
    if(datum==0):
        data=R.see(res=(1920,1080))
    else:
        data=datum
    pos=locate_position(data)
    #print pos
    arenatokens=filter(arena_filter,data)

    while(len(arenatokens)<1):
        if(TURN==False):
            return False
        else:#print "can't see, turning"
            turn(speedt,turning_constant*15)
            data=R.see(res=(1920,1080))
            arenatokens=filter(arena_filter,data)

    for coord in arenatokens:
        marker_to_coordinate(coord)
       #print coord.x,coord.y,coord.wall
    #print "transforms:"

    #transform global coordinates to local coordinates:
    for coord in arenatokens:
        if(coord.wall=="south"):
            pass
        if(coord.wall=="west"):
            temp=coord.x
            coord.x=8-coord.y
            coord.y=temp
        if(coord.wall=="north"):
            coord.x=8-coord.x
            coord.y=8-coord.y
        if(coord.wall=="east"):
            temp=coord.x
            coord.x=coord.y
            coord.y=8-temp
       #print coord.x,coord.y,coord.wall
        #transforms complete
    #print "beginning conditioning:"
    #begin conditioning!!!!!
    for coord in arenatokens:
        temp_rot=0
        temp_rot_count=0
        #print "global position:",pos
        #translate global position to selected wall local position
        loc_pos=coordinate(0,0)
        if(coord.wall=="south"):
            loc_pos.x=pos.x
            loc_pos.y=pos.y
        elif(coord.wall=="west"):
            temp=pos.x
            loc_pos.x=8-pos.y
            loc_pos.y=temp
        elif(coord.wall=="north"):
            loc_pos.x=8-pos.x
            loc_pos.y=8-pos.y
        elif(coord.wall=="east"):
            temp=pos.x
            loc_pos.x=pos.y
            loc_pos.y=8-temp
        #print "no wall"

        #calculate wall offset:

        if(coord.wall=="north"):
            offset=0
        elif(coord.wall=="east"):
            offset=1
        elif(coord.wall=="south"):
            offset=2
        elif(coord.wall=="west"):
            offset=3

        #initiate pile up conditions to false
        r=coord.rot_y
        delta_x=abs(coord.x-loc_pos.x)
        delta_y=abs(coord.y-loc_pos.y)


        try:
            ratio=delta_x/delta_y
            theta_rads=atan(ratio)
            theta=theta_rads*180/pi
        except:
            delta_x+=0.001




        #print "after ratio/theta calculated:"

        #print "ratio: {}".format(ratio)
        #print "delta_x: {}".format(delta_x)
        #print "delta_y: {}".format(delta_y)
        #print "localposition: {}".format(loc_pos)
        #print "coordinate_position: ({},{})".format(coord.x,coord.y)
        #print "end of input, begin cases"



        #case == CPA
        if(coord.x>loc_pos.x and r<0 and abs(r)>theta):
            #print " in CPA"
            #print theta,r,coord.x,coord.y,loc_pos,ratio,coord.wall
            bearing=(offset*90)+(-r-theta)
            if bearing<0:
                bearing+=360
            pos.bearing=bearing
            #print "bearing: {}".format(bearing)
        #case == PCA
        elif (coord.x>loc_pos.x and r<0):
            #print " in PCA"
            #print theta,r,coord.x,coord.y,loc_pos,ratio,coord.wall
            bearing=(offset*90)+(-r-theta)
            if bearing<0:
                bearing+=360
            pos.bearing=bearing
            #print "bearing: {}".format(bearing)
        #case == PAC
        elif(coord.x>loc_pos.x and r>0):
            #print " in PAC"
            #print theta,r,coord.x,coord.y,loc_pos,ratio,coord.wall
            bearing=(offset*90)+(-r-theta)
            if bearing<0:
                bearing+=360
            pos.bearing=bearing
            #print "bearing: {}".format(bearing)
        #case == APC
        elif(coord.x<loc_pos.x and r>0 and r>theta):
            #print " in APC"
            #print theta,r,coord.x,coord.y,loc_pos,ratio,coord.wall
            bearing=(offset*90)+(theta-r)
            if bearing<0:
                bearing+=360
            pos.bearing=bearing
            #print "bearing: {}".format(bearing)
        #case == ACP
        elif(coord.x<loc_pos.x and r>0 and r<theta):
            #print " in ACP"
            #print theta,r,coord.x,coord.y,loc_pos,ratio,coord.wall
            bearing=(offset*90)+(theta-r)
            if bearing<0:
                bearing+=360
            pos.bearing=bearing
            #print "bearing: {}".format(bearing)
        #case == CAP
        elif(coord.x<loc_pos.x and r<0):
            #print " in CAP"
            #print theta,r,coord.x,coord.y,loc_pos,ratio,coord.wall
            bearing=(offset*90)+(theta-r)
            if bearing<0:
                bearing+=360
            pos.bearing=bearing
            #print "bearing: {}".format(bearing)
        else:
            print "didn't enter a condition"
            #print theta,r,coord.x,coord.y,loc_pos,ratio,coord.wall
        temp_rot+=pos.bearing
        temp_rot_count+=1
    pos.bearing=temp_rot/temp_rot_count
    pos.data=data
    return pos

def block_to_coord(A,d,r):
    b=(A.bearing + r)*(pi/180)
    e=d*sin(b)
    f=d*cos(b)
    return coordinate(A.x+e,A.y+f)

def update_targets(position=0,datum=0,Flush=False):
    global TARGETS
    global SUBTARGETS
    global SEEN
    if Flush==True:
        SEEN=[]
        SUBTARGETS=[]
        TARGETS=[]
    if position==0 or datum==0:
        position=locate_bearing_and_position()
        datum=position.data

    home.rot=get_rot_to(position,home)

    for a in waypoints:
        a.rot=get_rot_to(position,a)

    for a in turning_values:
        if a>1:
            print ("turning const removed")
            del a

    for a in driving_values:
        if a>10:
            print ("driving const removed")
            del a

    if len(turning_values)>20:
        for a in range(2):
            turning_values.remove(max(turning_values))
            turning_values.remove(min(turning_values))
        del turning_values[0:3]
    global turning_constant
    turning_constant=sum(turning_values)/len(turning_values)

    if len(driving_values)>20:
        for a in range(2):
            driving_values.remove(max(driving_values))
            driving_values.remove(min(driving_values))
        del driving_values[0:3]
    global driving_constant
    driving_constant=sum(driving_values)/len(driving_values)

    closest_waypoint=waypoints[0]
    for c,a in enumerate(waypoints):
        if distance(position,a)<distance(position,closest_waypoint):
            closest_waypoint=a
            closest_waypoint.id=c

    visible_targets=filter(token_filter,datum)
    print visible_targets
    for seen in visible_targets:
        for targ in TARGETS:
            if seen.info.code==targ.code:
                temp=block_to_coord(position,seen.dist,seen.rot_y)
                temp.code=seen.info.code
                temp.col=seen.info.marker_type
                temp.rot=get_rot_to(position,temp)
                temp.seen=True
                targ=temp
                if (home.zone[0][0]<temp.x<home.zone[0][1])==False and (home.zone[1][0]<temp.y<home.zone[1][1])==False:
                        if (middle[1][0]<temp.y<middle[1][1])==False and (middle[0][0]<temp.y<middle[0][1])==False:
                            print "temp appended"
                            SEEN.append(temp)
                break
        else:
            print "in else"
            temp=block_to_coord(position,seen.dist,seen.rot_y)
            temp.code=seen.info.code
            temp.col=seen.info.marker_type
            temp.rot=get_rot_to(position,temp)
            temp.seen=True
            TARGETS.append(temp)
            if (home.zone[0][0]<temp.x<home.zone[0][1])==False and (home.zone[1][0]<temp.y<home.zone[1][1])==False:
                        if (middle[1][0]<temp.y<middle[1][1])==False and (middle[0][0]<temp.y<middle[0][1])==False:
                            print "temp appended"
                            SEEN.append(temp)

    print SEEN


    for a in SEEN:
        a.rot=get_rot_to(position,a)




def show_targets():
    for t in TARGETS:
        print t, ". Colour: ",t.col, ". Timestamp: ",t.timestamp,". code: ",t.code, " rotation to: ",t.rot_y

def intersect(a1,b1,a2,b2,a3,b3,a4,b4):
    try:m12=(b2-b1)/(a2-a1)
    except:pass

    try:m34=(b4-b3)/(a4-a3)
    except:pass
    if a1==a2:
        xi=a1
        yi=m34*(xi-a4)+b4
        return(xi,yi)
    elif a3==a4:
        xi=a3
        yi=m12*(xi-a2)+b2
        return(xi,yi)
    elif b1==b2:
        yi=b1
        xi=((yi-b3)/m34)+a3
        return(xi,yi)
    elif b3==b4:
        yi=b3
        xi=((yi-b1)/m12)+a1
        return(xi,yi)

"""def check_intersect(start,end):
    print("in intersect")
    intersectionab=intersect(start.x,start.y,end.x,end.y,a[0],a[1],b[0],b[1])
    intersectionbd=intersect(start.x,start.y,end.x,end.y,b[0],b[1],d[0],d[1])
    print(intersectionab,intersectionbd)
    if a[0]<=intersectionab[0]<=b[0]:
        if d[1]<=intersectionbd[1]<=b[0]:
            return True
        else:
            return False
    else:
        return False
"""

def avoid_the_middle(start,end):
    pass



def goto(start,end,stop=0,finish=True):
    print "heading game ", -R.heading*180/pi
    time.sleep(2)
    update_targets()

    dist=distance(end,start)
    dist=dist-stop
    rotation=end.rot
    print rotation,"rot"
    startb=start.bearing


    if(rotation<0):
        if abs(-rotation*turning_constant)>100:
            print turning_constant
            print turning_values
        print (-speedt,-rotation*turning_constant)
        turn(-speedt,-rotation*turning_constant)
    elif rotation>0:
        if abs(-rotation*turning_constant)>100:
            print turning_constant
            print turning_values
        print (speedt,rotation*turning_constant)
        turn(speedt,rotation*turning_constant)
    time.sleep(0.5)
    endpos=locate_bearing_and_position(TURN=False)
    if endpos!=False:
        endb=endpos.bearing

        if rotation<0:
            if endb>startb:
                d=(360-endb)+startb
            else:
                d=startb-endb
        elif rotation>0:
            if endb<startb:
                d=(360-startb)+endb
            else:
                d=endb-startb
        elif rotation==0:
            d=0
        difference=d


        try:
            turning_const=(abs(rotation)*turning_constant)/difference
            print "turning const:",turning_const
            if turning_const<1.5*max(turning_values):
                turning_values.append(turning_const)
            else:
                print "out or range"
        except:
            pass
    else:
        endpos=locate_bearing_and_position()




    time.sleep(0.5)
    try:
        drive(speedd,dist*driving_constant)
    except:
        drive(-speedd,-dist*driving_constant)
    time.sleep(0.5)
    if finish==True:
        endend=locate_bearing_and_position()
        dr=distance(endend,endpos)
        try:
            drive_val=(dist*driving_constant)/dr
            if abs(drive_val)<10:
                driving_values.append(drive_val)
        except:
            pass


def get_rot_to(A,B):

    bearing=90-(180/pi)*atan2(B.y-A.y,B.x-A.x)
    if bearing<0:
        bearing+=360


    right_turn=bearing-A.bearing
    left_turn=360-bearing + A.bearing
    #print "before"
    #print left_turn
    #print right_turn
    if left_turn>360:
        left_turn=left_turn-360
        right_turn=360-left_turn
    val=0
    if right_turn==left_turn:
        val=right_turn
    elif abs(right_turn)<abs(left_turn):
        #print left_turn,right_turn
        val=right_turn
    elif abs(left_turn)<abs(right_turn):
        #print left_turn,right_turn
        val=-left_turn
    #print "turn selected: ",val
    return val

def get_home_pos(datum=0):

    homepos=locate_bearing_and_position(datum)
    print("In get_home_pos with position",homepos.x,homepos.y)

    homezone=None
    if(Northwest[0][0]<homepos.x<Northwest[0][1] and Northwest[0][1]<homepos.y<Northwest[1][1]):
        print("northwest home")
        homezone=Northwest
    if (Northeast[0][0]<homepos.x<Northeast[0][1] and Northeast[0][1]<homepos.y<Northeast[1][1]):
        print("northeast home")
        homezone=Northeast
    if (Southeast[0][0]<homepos.x<Southeast[0][1] and Southeast[0][1]<homepos.y<Southeast[1][1]):
        print("southeast home")
        homezone=Southeast
    if (Southwest[0][0]<homepos.x<Southwest[0][1] and Southwest[0][1]<homepos.y<Southwest[1][1]):
        print("southwest home")
        homezone=Southwest
    if homezone==None:

        print(" No homezone, In get_home_pos with position", homepos.x, homepos.y)
        homezone=Northeast
    home=coordinate((homezone[0][0]+homezone[0][1])/2.0,(homezone[1][0]+homezone[1][1])/2.0)

    home.zone=homezone
    return home

def get_closest_target(pos=0,datum=0,list=SUBTARGETS):
    if pos==0:
        pos=locate_bearing_and_position(datum=0)

    update_targets(pos,datum)
    closest=list[0]
    for a in list:
        if distance(a,pos)<distance(closest,pos):
            closest=a
    return closest

def test_for_area(zone,target):
    if(zone[0][0]<target.x<zone[0][1]):
        if (zone[1][0]<target.y<zone[1][1]):
            #print "in area x any y"
            return True
        else:
            #print "in area x"
            return False
    else:
        #print "not in area"
        return False



speedt=50
speedd=70
dtime=0.15


turning_constant=0.00640690967217
driving_constant=1.0760111099
turning_values=[0.005914946064323486, 0.0059140954336470335, 0.005914048171491407, 0.007392486363725085, 0.005914095433646191, 0.0073919373434798066, 0.005914095489481625, 0.007392486363725095, 0.0059140954336461965, 0.005914048171491414, 0.007392486363725084, 0.005914095433646198]
driving_values=[1.0761866299470262, 1.0757150364475043, 1.0761828730608143, 1.0757150304790029, 1.0762047393966916, 1.0757150652171632, 1.0761866299194003, 1.0761828747071605]


#turning_constant,turning_r_squared,driving_constant,driving_r_squared=calibrate(speedt,speedd,8,dtime)


state="1"
closest_sub=None
target=None
way=0
stamp=int(time.time())
end=int(time.time())
print stamp
while state!=None:
    if state=="1":
        print "in state 1"
        home=get_home_pos()
        update_targets()
        print "outside get to"
        state="2"

    elif state=="2":
        print "in state 2"
        pos=locate_bearing_and_position()
        update_targets(Flush=True)
        state="3"
    elif state=="3":
        print "in state 3"
        update_targets()
        if len(SEEN)>0:
            pass
        else:
            for a in range(12):
                turn(speedt,turning_constant*30)
                time.sleep(0.5)
                update_targets()
                if len(SEEN)>0:
                    break
        state="4"
    elif state=="4":
        print "in state 4"
        pos=locate_bearing_and_position()
        update_targets()
        try:
            closest_sub=get_closest_target(pos,pos.data,SEEN)
        except:
            way+=1
            state="7"
            print "can't see, going to next waypoint"
            continue
        update_targets(Flush=True)
        pos=locate_bearing_and_position()
        print closest_sub.code
        #print ("check:",check_intersect(pos,closest_sub))
        goto(pos,closest_sub,distance(pos,closest_sub)/2,finish=False)
        state="5"
    elif state=="5":
        print "in state 5"
        id=closest_sub.code
        print id
        target=[]
        while True:
            data=R.see(res=(1920,1080))
            target=[a for a in data if a.info.code==id]

            if(len(target)>0):
                target=target[0]
                break
            else:
                turn(speedt,30*turning_constant)

        while abs(target.rot_y)>2:
            target=[a for a in data if a.info.code==id]
            target=target[0]
            if(target.rot_y<0):
                turn(-speedt,turning_constant*-target.rot_y)
            elif target.rot_y>0:
                turn(speedt,turning_constant*target.rot_y)
            data = R.see(res=(1920, 1080))

        target=[a for a in data if a.info.code==id]
        target=target[0]
        drive(speedd,driving_constant*(target.dist-0.1))
        grabbed=R.grab()
        if grabbed==False:
            state="5"
            for a in TARGETS:
                if a.code==id:
                    del a
            continue
        state="6"
    elif state=="6":
        pos=locate_bearing_and_position()
        #avoid_the_middle(pos,home,SAFE,0,False)
        goto(pos,home,finish=False)

        pos=locate_bearing_and_position()

        dist=distance(pos,home)

        while(dist>1):
            goto(pos,home,finish=False)
            pos = locate_bearing_and_position()
            dist = distance(pos, home)

        R.release()
        turn(speedt,180*turning_constant)
        drive(speedd,2*driving_constant)
        update_targets(Flush=True)
        state="3"
    elif state=="7":
     goto(locate_bearing_and_position(),waypoints[way%4])
     state="3"
    end=int(time.time())
    if (end-stamp)>2500:
        break

goto(locate_bearing_and_position(),home,finish=False)
R.release()











