
import numpy as np
from data_structures import coordinate
from math import *
from data_structures import arena_filter,token_filter
from itertools import combinations
import time


def distance(A_real,real_or_tuple):
    A=A_real
    B=real_or_tuple
    try:
        return sqrt(((B.x-A.x)**2)+((B.y-A.y)**2))
    except:
        return sqrt(((B[0]-A.x)**2)+((B[1]-A.y)**2))

def get_glob_loc(A,B,map_size=8):


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

        if(0<=pos.x<=map_size and 0<=pos.y<=map_size):
            return pos
        else:
            return neg

    else:
        raise EnvironmentError("circles do not intersect")


def get_location_from_world(data):

    #take in arena tokens straight from R.see()
    #if there are more than 1 arena tokens on screen find the average of the positions
    #otherwise raise an EnvironmentError
    arena_tokens=filter(arena_filter,data)

    if len(arena_tokens)<2:
        raise EnvironmentError("Not enough tokens to locate position")


    #if non-arena tokens are passed then they will not be assigned an x,y or wall attribute
    tokens_with_positions=[]
    for tok in arena_tokens:
        tokens_with_positions.append(marker_to_coordinate(tok))



    coordinate_pairs=list(combinations(tokens_with_positions,2))

    possible_locations=[]

    for A,B in coordinate_pairs:
        possible_locations.append(get_glob_loc(A,B))

    #generate average x and y coordinate
    x=0
    y=0
    n=0
    for i in possible_locations:
        x+=i.x
        y+=i.y
        n+=1
    x/=n
    y/=n
    pos=coordinate(x,y)
    return pos


def marker_to_coordinate(old_marker):
    marker=old_marker

    id=int(marker.info.offset)
    if 0<=id<7 :
        marker.x=(marker.info.offset+1)
        marker.y=8
        marker.wall="north"
    elif 0<=id<14:
        marker.x=8
        marker.y=8-(marker.info.offset-6)
        marker.wall="east"
    elif 14<=id<21:
        marker.x=8-(marker.info.offset-13)
        marker.y=0
        marker.wall="south"
    elif 21<=id<28:
        marker.x=0
        marker.y=(marker.info.offset-20)
        marker.wall="west"
    return marker


def select_home(coord):
    home=None
    homepos=coordinate(0,0)
    if coord.x<=3:
        if coord.y<=3:
            home="bottomleft"
            homepos.x=1.5
            homepos.y=1.5
        elif coord.y>=5:
            home="topleft"
            homepos.x = 1.5
            homepos.y = 6.5
    elif coord.x>=5:
        if coord.y<=3:
            home="bottomright"
            homepos.x = 6.5
            homepos.y = 1.5
        elif coord.y>=5:
            home="topright"
            homepos.x = 6.5
            homepos.y = 6.5
    if home==None:
        raise EnvironmentError("robot not in a homezone")
    return homepos,home

def sanitize_arena_toks(data):

    if type(data[0])==coordinate:
        return data
    a_toks=filter(arena_filter,data)
    s_toks=[marker_to_coordinate(i) for i in a_toks]
    return s_toks


def theta_to_bearing(theta):
    bearing=0
    theta=theta*(180/pi)

    bearing=(90-theta)
    if bearing<0:
        bearing+=360

    return bearing


def get_theta_AB(A,B):
    theta=atan2(B.y-A.y,B.x-A.x)
    return theta

def get_bearing_AB(A,B):
    theta=get_theta_AB(A,B)

    bearing=theta_to_bearing(theta)
    return bearing


def get_bearing(pos,marker,offset=True):
    initial_bearing=get_bearing_AB(pos,marker)

    if offset:
        bearing=(initial_bearing-marker.rot_y)%360
    else:
        bearing=initial_bearing%360
    return bearing

def pos_and_bearing(data):

    arena_toks = sanitize_arena_toks(data)

    if len(arena_toks)<2:
        raise EnvironmentError("can't see enough arean tokens")

    position = get_location_from_world(data)






    position.bearing=get_bearing(position,arena_toks[0])

    return position





def bearing_diff(B,A):
    raw_diff=B.bearing-A.bearing
    wrapped_neg=raw_diff%360
    if wrapped_neg>=180:
        wrapped_neg-=360
    return wrapped_neg


def x_y_At(pos,token):

    bearing=pos.bearing

    polar_bearing=bearing*pi/180

    if polar_bearing>pi:
        polar_bearing=-(2*pi-polar_bearing)


    mapped_bearing=0
    if polar_bearing>0 and polar_bearing<=pi/2:
        mapped_bearing=(pi/2)-polar_bearing
    elif polar_bearing>pi/2:
        mapped_bearing=-(polar_bearing-pi/2)
    elif polar_bearing<0 and polar_bearing>=-pi/2:
        mapped_bearing=pi/2-polar_bearing
    elif polar_bearing<-pi/2:
        mapped_bearing=-pi*3/2 -polar_bearing


    if mapped_bearing<-pi:
        mapped_bearing+=2*pi


    offset=token.rot_y*pi/180


    mapped_combined=mapped_bearing-offset


    if mapped_combined<-pi:
        mapped_combined+=2*pi
    elif mapped_combined>pi:
        mapped_combined-=2*pi


    x=cos(mapped_combined)*token.dist
    y=sin(mapped_combined)*token.dist
    token.x=pos.x+x
    token.y=pos.y+y


    return token

def sanitize_toks(pos,data):
    data=filter(token_filter,data)
    for tok in data:
        tok=x_y_At(pos,tok)
    return data


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











