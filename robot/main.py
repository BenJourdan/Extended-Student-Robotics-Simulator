__author__ = 'Ben'
from sr.robot import *
import time

import numpy as np

from ben.brain_render import *
from ben.data_structures import *
from ben.location_and_bearing import *
from ben.configuration import config
from math import *
from sr.robot import *
from ben.IO import *
from ben.movement import *
import itertools





# This creates the robots world

map=set_map(config)


#This is the object through which motors are controlled, pictures are taken and analysed, constants configured
#
R=Bot(Robot())


#This creates the object which holds the dictionary of marker list names and marker lists
#call its methods with no parametes to take another picture or call them with a list of markers

#uncomment this line in single player
brain_data=Scatter(R,map)


#Basic methods which use my functions in the other files to locate the robots position and move from
#one position to another

def locate(R,retdata=False):
    pos=None
    dat=None
    while pos==None:
        try:
            data=R.see()
            pos=pos_and_bearing(data)
            dat=data
        except:
            R.turn(30)
    if retdata:
        return pos,dat
    return pos

def goto(start, end,stop=0.0,tspeed=100,dspeed=100):

    angle = get_rot_to(start,end)


    R.turn(angle,speed=tspeed)

    dist=distance(start,end)-stop
    R.drive(dist,dspeed)



#Basic AI- Feel free to modify and delete!

closest=lambda tok:tok.dist


def update_targets(tokens,targets,visible=False):

    for i,t in enumerate(targets):
        targets[i].visible=False

    for tok in tokens:
        for i,t in enumerate(targets):

            if tok.info.code==t.info.code:
                targets[i]=tok
                targets[i].visible=True
                break
        else:
            targets.append(tok)
            targets[-1].visible=True



    vis=[]
    for t in targets:
        if t.visible:
            vis.append(t)
    if visible:
        return sorted(targets,key=closest),sorted(vis,key=closest)
    return sorted(targets,key=closest)

targets=[]

state="spin search"
count=0
try:
    home=brain_data.home
except:
    home=locate(R)


while True:
    brain_data.update_position_and_bearing(locate(R),draw=True)

    if state=="go to middle":
        print "in go to middle"
        pos=locate(R)
        middle=coordinate(4,4)
        goto(pos,middle,stop=2)
        state="spin search"
    elif state=="spin search":
        print "in spin search"
        pos, data=locate(R,retdata=True)
        toks=sanitize_toks(pos,data)
        targets=update_targets(toks,targets)
        if len(targets)>0:
            state="goto target"
            print "length of targets top",len(targets)
            continue
        else:
            while len(targets)<1:
                R.turn(25)
                pos.bearing=(pos.bearing+25)%360
                data=R.see()
                toks=sanitize_toks(pos,data)
                targets=update_targets(toks,targets)
            state="goto target"
            print "length of targets",len(targets)
            continue
    elif state=="goto target":
        if R.grabbed==True:
            state="go home"
            continue
        count+=1
        print "in goto target"
        print len(targets)
        pos,data=locate(R,retdata=True)
        target=targets[0]
        goto(pos,target,stop=0.3)

        R.grab()
        print R.grabbed
        if R.grabbed:
            state="go home"
            targets.remove(target)
        else:
            state="goto target"
        if count>4:
            try:
                targets.remove(target)
            except:
                pass
            count=0
            state="spin search"
    elif state=="go home":
        pos=locate(R)
        goto(pos,home)
        R.release()
        state="go to middle"





























































