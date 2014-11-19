#! /usr/bin/env python

import pygame
from pygame import locals




jlist = [] # global joystick list


class Joystick:


    def __init__(self):
        pygame.init()
        self.nbJoy = pygame.joystick.get_count()

        for n in range(self.nbJoy):
            pygame.joystick.Joystick(n).init()

        try:
            for n in range(pygame.joystick.get_count()): #
                stick = pygame.joystick.Joystick(n)
                jlist.append(stick) # create a joystick instance
                stick.init() # init instance
                # report joystick charateristics #
                print '-'*20
                print 'Enabled joystick: ' + stick.get_name()
                print 'it has the following devices :'
                print '--> buttons : '+ str(stick.get_numbuttons())
                print '--> balls : '+ str(stick.get_numballs())
                print '--> axes : '+ str(stick.get_numaxes())
                print '--> hats : '+ str(stick.get_numhats())
                print '-'*20
        except pygame.error:
            print 'pygame.error, no joystick found.'





    def main(self):


    #    init() # init pygame and joystick system


        while 1: # endless loop

            for e in pygame.event.get(): # iterate over event stack


                if e.type == pygame.locals.JOYAXISMOTION: # 7
                    for j in jlist:
                        for n in range(j.get_numaxes()):
                            print 'moved axe num '+str(n)+' : ' + str(j.get_axis(n))
                            print '-'*10 # separation


                elif e.type == pygame.locals.JOYBALLMOTION: # 8
                    for j in jlist:
                        for n in range(j.get_numballs()):
                            print 'moved ball num '+str(n)+' : '+ str(j.get_ball(n))
                            print '-'*10 # separation


                elif e.type == pygame.locals.JOYHATMOTION: # 9
                    for j in jlist:
                        for n in range(j.get_numhats()):
                            print 'moved hat num '+str(n)+' : '+ str(j.get_hat(n))
                            print '-'*10 # separation


                elif e.type == pygame.locals.JOYBUTTONDOWN: # 10
                    for j in jlist:
                        for n in range(j.get_numbuttons()):
                            if j.get_button(n) : # if this is down
                                print 'down button num '+str(n)+' : '+ str(j.get_button(n))
                                print '-'*10 # separation

                elif e.type == pygame.locals.JOYBUTTONUP: # 11
                    for j in jlist:
                        for n in range(j.get_numbuttons()):
                            print 'up button num '+str(n)+' : '+ str(j.get_button(n))
                            print '-'*10 # separation


if __name__ == '__main__':
    j = Joystick()
    j.main()

