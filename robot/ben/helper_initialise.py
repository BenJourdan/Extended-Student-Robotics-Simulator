from ben.helper_data_structures import Bot
from ben.helper_brain_render import set_map,Scatter




def initialise_helper(config,robot):

    #This is the object through which motors are controlled, pictures are taken and analysed, constants configured
    #and objects grabbed
    R=Bot(robot)


    # This creates the robots world

    if R.R.render:
        map=set_map(config)

        # This creates the object which holds the dictionary of marker list names and marker lists
        # call its methods with no parametes to take another picture or call them with a list of markers

        brain_data=Scatter(R,map)
    else:
        brain_data=Scatter(R,False)

    return R,brain_data
