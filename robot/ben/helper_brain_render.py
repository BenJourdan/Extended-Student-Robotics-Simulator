from matplotlib import pyplot as plt
import matplotlib.patches as patches


from ben.helper_location_and_bearing import *
from ben.helper_configuration import config
from ben.helper_data_structures import *


def none(*args, **kwargs):
    return None

class Map(object):
    def __init__(self,config,plt,fig,ax,mng,point_sets,line_sets):
        self.plt=plt
        self.fig=fig
        self.ax=ax
        self.mng=mng
        self.point_sets=point_sets
        self.line_sets=line_sets




def redraw_figure(map):
    map.plt.draw()
    map.fig.show()
    map.plt.pause(0.0001) #set this higher if things don't plot

def namestr(obj, namespace):
    return [name for name in namespace if namespace[name] is obj]

def add_point_set(name,map,**kwargs):
    #I'm not proud of this function but it works very well
    #It takes a string as well as keyword arguments and creates a scatter object with the variable name of the string
    #as well as passing the scatter object constructor the keyword arguments
    stri='map.point_sets["'+name+'"]=ax.scatter([],[])'

    if kwargs:
        str2=""
        for key,value in kwargs.iteritems():

            try:
                str2+=','+key+'='+'"'+value+'"'
            except:
                str2+=','+key+'='+ str(value)




        stri='map.point_sets["'+name+'"]=map.ax.scatter([],[]' +str2+ ')'
    exec(stri)


def set_map(config):
    fig, ax = plt.subplots(num=None, figsize=(6.5, 6.5), facecolor="w")

    # turn off x and y axes
    ax.axes.get_xaxis().set_visible(False)
    ax.axes.get_yaxis().set_visible(False)

    mng = plt.get_current_fig_manager()

    point_sets = {}

    line_sets = {}
    line_sets["bearing"] = ax.plot([], [], color="blue")[0]
    line_sets["fov_left"] = ax.plot([], [], color="grey")[0]
    line_sets["fov_right"] = ax.plot([], [], color="grey")[0]


    plt.axis("scaled")

    ax.set_xlim([0, config.x])
    ax.set_ylim([0, config.y])
    #ax.grid(which="major")
    plt.tight_layout()

    middlezone = patches.Circle((4,4),0.5,facecolor="none",edgecolor="g",linewidth=2)
    ax.add_patch(middlezone)


    return Map(config,plt,fig,ax,mng,point_sets,line_sets)


def add_home(area,map):
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
    map.ax.add_patch(homezone)

    for Ehome in homes:
        enemy_home = patches.Rectangle(Ehome,3,3,facecolor="none",edgecolor="r",linewidth=1)
        map.ax.add_patch(enemy_home)
    return map


def update_brain(data,map):
    #data is a dicitonary containing the string names of the point lists to be updated
    #scat is the scatter data  in the format:
    #scat=[[x1,y1],[x2,y2],[x3,y3],...]
    for name,scat in data.iteritems():

        if scat!=[]:
            map.point_sets[name].set_offsets(scat)

    redraw_figure(map)

class Scatter(object):
    def __init__(self,R,map):
        self.R=R
        self.map=map
        self.scatter_data_dict={}

        if self.map:
            for name, dic in config.point_lists_list:
                add_point_set(name,self.map, **dic)
                self.scatter_data_dict[name] = []

        # select home zone and pick home coordinate
        posi = get_location_from_world(self.R.see())
        self.home, area = select_home(posi)

        if self.map:
            self.map=add_home(area,self.map)

            self.scatter_data_dict = coords_to_data("home", [self.home], self.scatter_data_dict)
            self.map.ax.annotate("home",(self.home.x+0.05,self.home.y+0.05))
            update_brain(self.scatter_data_dict,self.map)

    def run_on_single(function):
        from functools import wraps

        @wraps(function)
        def decorated_function(self,*args, **kwargs):
            if self.map:
                return function(self,*args, **kwargs)
            else:

                return none(self,*args,**kwargs)

        return decorated_function


    def draw_logic(function):
        from functools import wraps

        @wraps(function)
        def decorated_function(self,*args,**kwargs):
            if "draw" in kwargs.keys():
                if kwargs["draw"]==True:
                    del kwargs["draw"]
                    val=function(self,*args,**kwargs)
                    update_brain(self.scatter_data_dict,self.map)
                    return val
                else:
                    del kwargs["draw"]
                    return function(self,*args,**kwargs)
            else:
                return function(self,*args,**kwargs)
        return decorated_function


    @run_on_single
    def test_single(self):
        print "this should only print in single player"

    @run_on_single
    def generate_xy_from_heading(self, pos, length=12, offset=0):

        bearing_with_offset = (pos.bearing - offset)


        if bearing_with_offset >= 360:
            bearing_with_offset -= 360
        elif bearing_with_offset < 0:
            bearing_with_offset += 360

        raw_x =  cos((bearing_with_offset) * (pi / 180)) * length
        raw_y =  sin(bearing_with_offset * (pi / 180)) * length



        return pos.x + raw_y, pos.y + raw_x

    @draw_logic
    @run_on_single
    def update_list(self,name,data,flush=True):
        self.scatter_data_dict=coords_to_data(name,data,self.scatter_data_dict,destroyOld=flush)

    # update home positon on map
    @draw_logic
    @run_on_single
    def update_position_and_bearing(self,pos):


        self.scatter_data_dict = coords_to_data("pos", [pos], self.scatter_data_dict,destroyOld=True)
        #draw bearing
        x,y=self.generate_xy_from_heading(pos)

        self.map.line_sets["bearing"].set_xdata([pos.x,x])
        self.map.line_sets["bearing"].set_ydata([pos.y,y])

        #draw left fov:

        left_x,left_y=self.generate_xy_from_heading(pos,offset=-30)
        self.map.line_sets["fov_left"].set_xdata([pos.x,left_x])
        self.map.line_sets["fov_left"].set_ydata([pos.y,left_y])

        #draw right fov
        right_x, right_y = self.generate_xy_from_heading(pos, offset=30)
        self.map.line_sets["fov_right"].set_xdata([pos.x, right_x])
        self.map.line_sets["fov_right"].set_ydata([pos.y, right_y])



    # update the arena tokens that are visible to the robot

    @run_on_single
    @draw_logic
    def update_visible_arena(self, data=None,coords=None):
        if not data and not coords:
            data=self.R.see()
        if not coords:
            coords = [marker_to_coordinate(i) for i in filter(arena_filter, data)]
        self.scatter_data_dict = coords_to_data("arena_now", coords, self.scatter_data_dict,destroyOld=True)

    @run_on_single
    @draw_logic
    def update_visible_tokens_and_all_targets(self,golds=None,silvers=None,targets=None):
        self.scatter_data_dict["gold_toks"]=[]
        self.scatter_data_dict["silver_toks"]=[]
        self.scatter_data_dict["targets"]=[]

        if golds:
            self.scatter_data_dict=coords_to_data("gold_toks",golds,self.scatter_data_dict,destroyOld=True)

        if silvers:
            self.scatter_data_dict=coords_to_data("silver_toks",silvers,self.scatter_data_dict,destroyOld=True)

        if targets:
            self.scatter_data_dict=coords_to_data("targets",targets,self.scatter_data_dict,destroyOld=True)










