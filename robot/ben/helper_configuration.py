
import inspect

class Devarena():
    def __init__(self):
        self.point_lists_list = []
        self.x = 8
        self.y = 8


        # markers which are being considered for grabbing and where it thinks they are
        self.targets = ("targets", {"color": "g","facecolors":"none","s":300})
        # the position that the robot thinks it is at
        self.pos = ("pos", {"color": "b", "marker": "o", "s":1000,"facecolors":"none"})
        #The position of the arena tokens which it can currently see
        self.arena_now = ("arena_now",{"color": "black","marker": "o"})
        #The home position:
        self.home=("home",{"color":"black","marker":"s"})

        #tokens:
        self.silver_toks=("silver_toks",{"color":"silver","marker":"D","s":100})
        self.gold_toks = ("gold_toks", {"color": "gold", "marker": "D", "s": 100})

        #Non-physical points of interest, e.g. Waypoints:

        self.waypoints=("way_points",{"color": "black","marker":"o","s":500,"facecolors":"none"})


    def load_lists(self,dev):
        attributes=inspect.getmembers(dev,lambda a:not inspect.isroutine(a))

        clean=[c for c in attributes if not(c[0].startswith("__") and c[0].endswith("__"))]


        lists=[ls for ls in clean if (ls[1]!=8)and ls[0]!="point_lists_list" ]

        for ls in lists:
            self.point_lists_list.append(ls[1])







dev=Devarena()
dev.load_lists(dev)

configurations={"development": dev,"default":dev}

config=configurations["development"]