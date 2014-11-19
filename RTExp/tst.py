#!/usr/bin/env python
"""A moving target."""

############################
#  Import various modules  #
############################

import VisionEgg
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

from VisionEgg.Core import *
from VisionEgg.FlowControl import Presentation, Controller, FunctionController
from VisionEgg.MoreStimuli import *
from math import *

#################################
#  Initialize the various bits  #
#################################

# Initialize OpenGL graphics screen.
screen = get_default_screen()

# Set the background color to white (RGBA).
screen.parameters.bgcolor = (1.0,1.0,1.0,1.0)

# Create an instance of the Target2D class with appropriate parameters.

def dots(number):
	color = (0.5,0.5,0.5,1.0)
	position=(10, 10)
	targets = []
	for i in range(0, number):
		target = FilledCircle(color = color, position=(position[0]+i*10, position[1])) 
		targets.append(target)
	return targets

# Create a Viewport instance
dots = dots(10)
dots[2].parameters.color = (1,0,0,1)
dots[4].parameters.color = (0,1,0,1)
viewport = Viewport(screen=screen, stimuli=dots)

# Create an instance of the Presentation class.  This contains the
# the Vision Egg's runtime control abilities.
p = Presentation(go_duration=(10.0,'seconds'),viewports=[viewport])

#######################
#  Define controller  #
#######################

# calculate a few variables we need
mid_x = screen.size[0]/2.0
mid_y = screen.size[1]/2.0
max_vel = min(screen.size[0],screen.size[1]) * 0.4

# define position as a function of time
def get_target_position(t):
    global mid_x, mid_y, max_vel
    #return ( max_vel*sin(0.1*2.0*pi*t) + mid_x , # x
    #         max_vel*sin(0.1*2.0*pi*t) + mid_y ) # y
    return (10, 10)

# Create an instance of the Controller class
target_position_controller = FunctionController(during_go_func=get_target_position)

#############################################################
#  Connect the controllers with the variables they control  #
#############################################################

#p.add_controller(target,'position', target_position_controller )

#######################
#  Run the stimulus!  #
#######################

p.go()

