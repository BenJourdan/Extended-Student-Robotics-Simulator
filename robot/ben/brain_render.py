from matplotlib import pyplot as plt
import matplotlib.patches as patches

import numpy as np

from tornado.util import timedelta_to_seconds

from location_and_bearing import *
from configuration import config
from data_structures import *
import time
import random
from threading import Thread
from threading import Lock

#create figure and plot

#Remove the triple quote paranthesis in single player
"""
fig,ax = plt.subplots(num=None,figsize=(6.5,6.5),facecolor="w")

#turn off x and y axes
ax.axes.get_xaxis().set_visible(False)
ax.axes.get_yaxis().set_visible(False)

mng = plt.get_current_fig_manager()



point_sets={}


line_sets={}
line_sets["bearing"]=ax.plot([],[],color="blue")[0]
line_sets["fov_left"]=ax.plot([],[],color="grey")[0]
line_sets["fov_right"]=ax.plot([],[],color="grey")[0]


"""


def redraw_figure():
    plt.draw()
    fig.show()
    plt.pause(0.1) #set this higher if things don't plot

def namestr(obj, namespace):
    return [name for name in namespace if namespace[name] is obj]

def add_point_set(name,**kwargs):
    #I'm not proud of this function but it works very well
    #It takes a string as well as keyword arguments and creates a scatter object with the variable name of the string
    #as well as passing the scatter object constructor the keyword arguments
    stri='point_sets["'+name+'"]=ax.scatter([],[])'

    if kwargs:
        str2=""
        for key,value in kwargs.iteritems():

            try:
                str2+=','+key+'='+'"'+value+'"'
            except:
                str2+=','+key+'='+ str(value)




        stri='point_sets["'+name+'"]=ax.scatter([],[]' +str2+ ')'
    exec(stri)


def set_map(config):

    plt.axis("scaled")

    ax.set_xlim([0, config.x])
    ax.set_ylim([0, config.y])
    #ax.grid(which="major")
    plt.tight_layout()

    middlezone = patches.Circle((4,4),0.5,facecolor="none",edgecolor="g",linewidth=2)
    ax.add_patch(middlezone)
    redraw_figure()


def add_home(area):
    coord=None
    homes=[(0,5),(5,5),(0,0),(5,0)]
    if area=="topleft":
        coord=(0,5)
    elif area=="topright":
        coord=(5,5)
    elif area=="bottomleft":
        coord=(0,0)
    elif area=="bottomright":
        coord=(5,0)

    homes.remove(coord)

    homezone = patches.Rectangle(coord,3,3,facecolor="none",edgecolor="b",linewidth=1)
    ax.add_patch(homezone)

    for Ehome in homes:
        enemy_home = patches.Rectangle(Ehome,3,3,facecolor="none",edgecolor="r",linewidth=1)
        ax.add_patch(enemy_home)
    redraw_figure()


def update_brain(data):
    #data is a dicitonary containing the string names of the point lists to be updated
    #scat is the scatter data  in the format:
    #scat=[[x1,y1],[x2,y2],[x3,y3],...]
    for name,scat in data.iteritems():
        point_sets[name].set_offsets(scat)

    redraw_figure()

class scatter(object):
    def __init__(self,R,render=False):
        self.R=R
        self.scatter_data_dict={}

        for name, dic in config.point_lists_list:
            add_point_set(name, **dic)
            self.scatter_data_dict[name] = []

        # select home zone and pick home coordinate
        posi = get_location_from_world(self.R.see())
        self. home, area = select_home(posi)
        add_home(area)
        self.scatter_data_dict = coords_to_data("home", [self.home], self.scatter_data_dict)
        update_brain(self.scatter_data_dict)

    def generate_xy_from_heading(self, pos, length=12, offset=0):

        bearing_with_offset = (pos.bearing - offset)


        if bearing_with_offset >= 360:
            bearing_with_offset -= 360
        elif bearing_with_offset < 0:
            bearing_with_offset += 360





        raw_x =  cos((bearing_with_offset) * (pi / 180)) * length
        raw_y =  sin(bearing_with_offset * (pi / 180)) * length



        return pos.x + raw_y, pos.y + raw_x


    def update_list(self,name,data,flush=True,draw=False):
        self.scatter_data_dict=coords_to_data(name,data,self.scatter_data_dict,destroyOld=flush)
        if draw:
            update_brain(self.scatter_data_dict)

    # update home positon on map
    def update_position_and_bearing(self,pos,draw=False):


        self.scatter_data_dict = coords_to_data("pos", [pos], self.scatter_data_dict,destroyOld=True)
        #draw bearing
        x,y=self.generate_xy_from_heading(pos)

        line_sets["bearing"].set_xdata([pos.x,x])
        line_sets["bearing"].set_ydata([pos.y,y])

        #draw left fov:

        left_x,left_y=self.generate_xy_from_heading(pos,offset=-30)
        line_sets["fov_left"].set_xdata([pos.x,left_x])
        line_sets["fov_left"].set_ydata([pos.y,left_y])

        #draw right fov
        right_x, right_y = self.generate_xy_from_heading(pos, offset=30)
        line_sets["fov_right"].set_xdata([pos.x, right_x])
        line_sets["fov_right"].set_ydata([pos.y, right_y])

        if draw:
            update_brain(self.scatter_data_dict)




    # update the arena tokens that are visible to the robot
    def update_visible_arena(self, data=None,coords=None,draw=False):
        if not data and not coords:
            data=self.R.see()
        if not coords:
            coords = [marker_to_coordinate(i) for i in filter(arena_filter, data)]
        self.scatter_data_dict = coords_to_data("arena_now", coords, self.scatter_data_dict,destroyOld=True)

        if draw:
            update_brain(self.scatter_data_dict)

    def update_visible_tokens_and_all_targets(self,golds=None,silvers=None,targets=None,draw=False):
        self.scatter_data_dict["gold_toks"]=[]
        self.scatter_data_dict["silver_toks"]=[]
        self.scatter_data_dict["targets"]=[]

        if golds:
            self.scatter_data_dict=coords_to_data("gold_toks",golds,self.scatter_data_dict,destroyOld=True)
        if silvers:
            self.scatter_data_dict=coords_to_data("silver_toks",silvers,self.scatter_data_dict,destroyOld=True)
        if targets:
            self.scatter_data_dict=coords_to_data("targets",targets,self.scatter_data_dict,destroyOld=True)



        if draw:
            update_brain(self.scatter_data_dict)



    def dont_render(self,function):
        from functools import wraps
        if self.render:

            @wraps
            def decorated_function(*args,**kwargs):
                return function(*args,**kwargs)
            return decorated_function
        else:
            @wraps
            def decorated_function(*args,**kwargs):
                return None
            return decorated_function





