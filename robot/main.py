from __future__ import print_function
__author__ = 'Ben'

from sr.robot import *

from ben.helper_configuration import config
from ben.helper_initialise import initialise_helper
from ben.helper_location_and_bearing import coordinate,sanitize_toks,get_rot_to,distance,locate,goto,silver_filter,gold_filter


import time





#This AI is very dodge and makes remarkably stupid  but makes use of all of the inbuilt functionality such as:
# -> Positioning code
# -> The extened Robot class Bot
# -> Matpltotlib Graphing functionality
#feel free to copy/delete etc

class Basic_AI(object):
    def __init__(self):

        #Robot() is defined at runtime so even though it is underlined in red by IDEs don't panic
        self.R,self.brain_data=initialise_helper(config,Robot(),calibrate=False)



        self.closest=lambda tok:tok.dist

        self.targets=[]
        self.gold=[]
        self.silver=[]
        self.state = "initialise"
        self.count = 0
        try:
            self.home = self.brain_data.home
        except:
            self.home = locate(self.R)

        self.pos=None
        self.data=None

        #makes show do nothing instead of print to console
        self.show=print
        if self.R.R.render==False:
            self.show=self.print_nothing_when_others(self.show)

    def print_nothing_when_others(self,function):

        from functools import wraps

        @wraps(function)
        def decorated_func(*args,**kwargs):
            return None
        return decorated_func


    def start(self):
        # This code starts off the AI
        return self.spin_search()



    def draw_self(function):
        from functools import wraps
        @wraps(function)
        def decorated_func(self,*args,**kwargs):
            temp_pos=locate(self.R)
            self.brain_data.update_position_and_bearing(temp_pos)
            self.brain_data.update_visible_arena(draw=True)
            return function(self,*args,**kwargs)

        return decorated_func

    def draw_targets_before(function):
        from functools import wraps

        @wraps(function)
        def decorated_function(self,*args,**kwargs):
            self.pos,self.data=locate(self.R,retdata=True)
            toks=sanitize_toks(self.pos,self.data)
            golds=[t for t in toks if gold_filter(t)]
            silvers=[s for s in toks if silver_filter(s)]

            for j in golds:

                marked=True
                for c,i in enumerate(self.gold):

                    if i.info.code==j.info.code:
                        self.gold[c]=j

                        marked=False
                if marked:
                    self.gold.append(j)

            for j in silvers:

                marked=True
                for c,i in enumerate(self.silver):

                    if i.info.code==j.info.code:
                        self.silver[c]=j

                        marked=False
                if marked:
                    self.silver.append(j)



            self.brain_data.update_visible_tokens_and_all_targets(targets=self.targets,silvers=self.silver,golds=self.gold,draw=True)
            return function(self,*args,**kwargs)
        return decorated_function

    #Declare all AI functions here. This is necessary because a few AI functions have to be called before they are
    #Initialised
    def spin_search(self):
        pass
    def go_to_middle(self):
        pass
    def goto_target(self):
        pass
    def go_home(self):
        pass


    def update_targets(self,tokens,targets,visible=False):

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
            return sorted(targets,key=self.closest),sorted(vis,key=self.closest)
        return sorted(targets,key=self.closest)



    @draw_self
    @draw_targets_before
    def go_to_middle(self):
        self.show ("In go to middle function")
        self.pos=locate(self.R)
        middle=coordinate(4,4)
        goto(self.pos,middle,self.R,2)
        return self.spin_search()

    @draw_self
    @draw_targets_before
    def spin_search(self):
        self.show ("in spin search function")
        self.pos,self.data = locate(self.R,retdata=True)
        toks=sanitize_toks(self.pos,self.data)
        self.targets=self.update_targets(toks,self.targets)

        if len(self.targets)>0:
            self.show ("length of targets top",len(self.targets))
            return self.goto_target()
        else:
            while len(self.targets)<1:
                self.R.turn(30)
                self.pos.bearing=(self.pos.bearing+30)%360
                self.data=self.R.see()
                toks=sanitize_toks(self.pos,self.data)
                self.targets=self.update_targets(toks,self.targets)
            self.show ("length of targets",len(self.targets))
            return self.goto_target()

    @draw_self
    @draw_targets_before
    def goto_target(self):
        if self.R.grabbed==True:
            return self.go_home()
        self.count+=1
        self.show ("in goto target")
        self.show (len(self.targets))
        self.pos,self.data=locate(self.R,retdata=True)
        target=self.targets[0]
        goto(self.pos,target,self.R,stop=0.3)
        self.R.grab()

        if self.R.grabbed:
            state="go home"
            self.targets.remove(target)
            return self.go_home()

        if self.count>4:
            try:
                self.targets.remove(target)
            except:
                pass
            self.count=0
            state="spin search"
            return self.spin_search()
        self.goto_target()

    @draw_self
    @draw_targets_before
    def go_home(self):
        self.show ("in go home function")
        self.pos=locate(self.R)
        goto(self.pos,self.home,self.R)
        self.R.release()
        return self.go_to_middle()


bob=Basic_AI()



bob.start()
