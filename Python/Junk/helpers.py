"""
NAME    ringPriorities

AUTHOR  jos feenstra

DESC    STATE SPACE estimation calculation

NOTE    the minimum distance to another home is represented by the name "ring",
        as its boundary representations look like square rings.

NOTE    isTouching()

"""
#import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle as mathplot_rectangle
import numpy as np
from random import randint, shuffle, random, randrange, choice, uniform

# constances general
AREA = (160, 180)
HOUSE_COUNT = [20, 40, 60]

# water (ignored for now)
WATER_PERCENTAGE = 0.20         # percentage of total area covered by water
MAX_BODIES       = 4            # maximum number of bodies
MAX_RATIO        = 4            # l/b < x AND  b/l < x

# house constances
NAME           = ["Family",  "Bungalow", "Mansion"  ]
FREQUENCY      = [0.60,      0.25,       0.15       ]
VALUE          = [285000,    399000,     610000     ]
SITE           = [(8, 8),    (10, 7.5),  (11, 10.5 )]
BASE_RING      = [2,         3,          6,         ]
RING_INCREMENT = [0.03,      0.04,       0.06       ]
COLOUR         = ["r",       'g',        'y'        ]


################################################################################
"""
Housetype Class
"""
class HouseType:

    def __init__(self, aName, aFrequency, aValue, aSite, aBaseRing, aRingIncrement, MaxRingIt, aColour):

        # base values
        self.name      = aName
        self.frequency = aFrequency
        self.value     = aValue
        self.site      = aSite
        self.baseRing  = aBaseRing
        self.ringInc   = aRingIncrement
        self.colour    = aColour

        # calculated values
        self.width     = self.site[0]
        self.height    = self.site[1]
        self.area      = self.width * self.height
        self.landValue = self.value / self.area
        self.ringValue = round(self.ringInc * self.value)

        # do not calculate rings if the basering is incorrect
        if self.baseRing - 1 < 0:
            raise print("ERROR: Ring Creation Error")

        # instanciate cummulative variables
        cumArea        = self.area
        cumValue       = self.value
        cumLandValue   = self.landValue

        # make array of rings and their weighted values
        class Ring:
            pass
        self.ring = list()

        # fill ring list with Ring objects
        # TODO rewrite so that ringwidth and ring.width is less confusing

        for ringWidth in range(self.baseRing, MaxRingIt):

            # turn r into Ring object
            r = Ring()

            # calc land value in € / m2, and calc other attributes
            r.ringWidth = ringWidth                  # synoniem
            r.x = ringWidth * 2 + self.width
            r.y = ringWidth * 2 + self.height
            r.area = r.x * r.y - cumArea

            # the first ring is part of the house, so it yields no value
            r.value = 0
            if ringWidth != self.baseRing:
                r.value = self.ringValue
            r.landValue = round(r.value / r.area, 1)

            # increase the cummilative values, and add the current values to r
            cumArea += r.area
            r.cumArea = cumArea

            cumValue += r.value
            r.cumValue = cumValue

            cumLandValue = round(cumValue / cumArea)
            r.cumLandValue = cumLandValue

            # add Ring object r to list ring
            self.ring.append(r)

    def printRingInfo(self):
        print()
        print(self.name)
        printstr = "| ring: {:2}   x: {:2}   y: {:3}   area: {:5}  landValue: {:5}  cumArea: {:6}  cumValue: {:7}   cumLandValue: {:5} |"
        print((len(printstr) - 4) * "-")
        for r in self.ring:
            print(printstr.format(r.ringWidth, r.x, r.y, r.area, r.landValue, r.cumArea, r.cumValue, r.cumLandValue ))
        print((len(printstr) - 4) * "-")

################################################################################
"""
House Class
"""
class House:

    def __init__(self, aType, aCoord, addRings):
        self.type = aType
        self.additionalRings = addRings

        # select current ring
        self.ring = self.type.ring[self.additionalRings]

        # calc house's lower- and upperbounds of x and y coordinates
        self.xLower = self.ring.ringWidth
        print(self.xLower)
        self.yLower = self.ring.ringWidth
        print(self.yLower)
        self.xUpper = AREA[0] - self.ring.ringWidth - self.type.width
        print(self.xUpper)
        self.yUpper = AREA[1] - self.ring.ringWidth - self.type.height
        print(self.yUpper)

        # assign either a random coordinate, or assign given coordinate
        if aCoord == "random":
            # randomize numbers, with 0.5 precision
            random_x = round(uniform(self.xLower, self.xUpper) * 2) / 2
            random_y = round(uniform(self.yLower, self.yUpper) * 2) / 2

            self.origin = (random_x, random_y)
        else:
            self.origin = aCoord

        # update geometic info
        self.update()

    def update(self):
        # calculate additional geometric information, based on init's current value
            # EXAMPLE a fam.house with 3 add.rings gives a ringWidth of 5.

        # house geometry rep. boundary
        self.boundary = Rectangle(self.origin, self.type.width, self.type.height)

        # move houseOrigin diagonal to create ringOrigin
        vector = (-1 * self.ring.ringWidth, -1 * self.ring.ringWidth)
        ringOrigin = moveCoord(self.origin, vector)

        # house ring rep. boundary
        self.ringboundary = Rectangle(ringOrigin, self.ring.x, self.ring.y)

        # make some synonimes for lazy use
        self.coord = self.origin

    def move(self, vector):

        # add vector and origin coordinate, and update other values accordingly
        self.origin = moveCoord(self.origin, vector)
        self.update()

    def moveTo(self, newCoord):

        # replace origin coordinate, and update other values accordingly
        self.origin = newCoord
        self.update()

###############################################################################

"""
square class
"""
class Rectangle:

    def __init__(self, OriginCoord, width, height):

        self.width = width
        self.height = height

        self.x1 = OriginCoord[0]
        self.y1 = OriginCoord[1]
        self.coord1 = (self.x1, self.y1)

        self.x2 = self.x1 + width
        self.y2 = self.y1 + height
        self.coord2 = (self.x2, self.y2)

    def toString(self):
        return ("Rectangle.coord1: {} \n Rectangle.coord2: {} \n".format(
               self.coord1,
               self.coord2)
               )

    # TODO make method of comparissons:

    def isTouching(self, obj2):

        # find out if object is coordinate or square
        checkCoords = []
        if isinstance(obj2, Rectangle):
            print("its an rectangle")

            [checkCoords.append((x, y)) for x in obj2.coord1 for y in obj2.coord2]
            print(checkCoords)

        elif isinstance(obj2, tuple):
            print("its an coord")
            checkCoords.append(obj2)
        else:
            print("ERROR: secondObject is not of valid type")

        for checkCoord in checkCoords:
            print(checkCoord)
        # return True / False

###############################################################################

"""
Map class which holds houses and has a method of printing them

METHODS AND THEIR USE:
self.addHouse(type, coord, rings)
self.plot()
"""
class Map:

    def __init__(self, coord1=(0,0), coord2=AREA):
        self.coord1 = coord1
        self.coord2 = coord2
        self.width  = coord2[0] - coord1[0]
        self.height = coord2[1] - coord1[1]

        # init houselist
        self.house = []

        # init a boundary for collision testing
        self.boundary = Rectangle(self.coord1, self.width, self.height)


    """
    add a [aType] house to the map at [aCoord], with [addrings] rings
    """
    def addHouseStupid(self, aType, aCoord, addRings):
        # simple way of creating a house
        self.house.append(House(aType, aCoord, addRings))

    """
    add a [aType] house to the map at [aCoord], with [addrings] rings
    the following options are usable:
        ["non_colliding"]
            pick random house locations until the position is valid.
        ["random_positions"]
            place house at a random location
        ["Tactical_fit"]
            TODO
    """
    def addHouse(self, aType, aCoord, addRings, *options):

        # apply options
        LoopUntilValid = False
        if any(option == "non_colliding" for option in options):
            print("make a house without colliding")
            LoopUntilValid = True
        if any(option == "random_positions" for option in options):
            print("make house at a random location")
            h = (House(aType, "random", addRings))
        else:
            print("make a house in ordinary fashion")
            h = (House(aType, aCoord, addRings))


        if not LoopUntilValid:
            # directly append h if we dont need to check for valid position
            self.house.append(h)
        else:
            # if we do need to check if placement is valid
            while(True):

                # get h's 4 boundary coordinates
                bound_coords = [(x, y) for x in [h.boundary.x1, h.boundary.x2]
                                       for y in [h.boundary.y1, h.boundary.y2]]

                # # calculate per boundary coordinate
                # for bound_coord in bound_coords:
                #     # per house in embedded houses
                #     for ring in self.house.ringboundary:
                #         # clear names
                #         x = bound_coord[0]
                #         y = bound_coord[1]
                #
                #         if ring.x1 < x < ring.x2:
                #             print("GOED")
                #         if ring.y1 < y < ring.y2:
                #             print("goed")
                #
                # # placement is incorrect, try again at different position
                #
                # h = (House(aType, "random", addRings)
                # go into loop again
                #
                self.house.append(h)
                break


    """
    plot the full map with all houses. This code is hard to understand
    without understanding the mathplot.py libaries
    """
    def plot(self):

        # init figure and axes
        fig = plt.figure()
        ax = fig.add_subplot(111, aspect='equal')

        # get rectangle information out of houses
        houseBound_list = []
        ringBound_list  = []
        for house in self.house:
            rec1 = mathplot_rectangle(house.boundary.coord1, house.boundary.width, house.boundary.height, 0, fc=house.type.colour)
            rec2 = mathplot_rectangle(house.ringboundary.coord1, house.ringboundary.width, house.ringboundary.height, 0, fc=house.type.colour, alpha=0.2)
            ax.add_patch(rec1)
            ax.add_patch(rec2)

        # EXAMPLE FOR PROPERTIES
        # rect = patches.Rectangle((50,100),40,30,linewidth=1,edgecolor='r',facecolor='none')

        # determines how axis are drawn
        ax.set_xticks(np.arange(0, self.width, 10))
        ax.set_yticks(np.arange(0, self.height, 10))
        ax.set_xlim([0, self.width])
        ax.set_ylim([0, self.height])

        # draw the board
        plt.show()




###############################################################################
"""
This area is for functions with are no part of classes
"""


"""
instantiate the 3 housetype objects
"""
def initHouseTypes(IterationMax=20):
    # determines how many rings will be added and calculated
    maximumRingIterations = IterationMax

    # make a list of House objects
    houseTypeList = list()
    for i,s in enumerate(NAME):
        houseTypeList.append(
            HouseType(NAME[i], FREQUENCY[i], VALUE[i], SITE[i], BASE_RING[i],
                RING_INCREMENT[i], maximumRingIterations, COLOUR[i])
        )
    return houseTypeList



"""
add a coordinate and a vector (movement representative) together
- make a coordinate class/?????
"""
def moveCoord(coordinate, vector):
    return tuple(sum(x) for x in zip(coordinate, vector))



# is coord within boundary?
# is square within square?



# FOUND ON THE INTERNETZZ
"""
class Coord(tuple):

    def __new__(cls, width, height):
        return tuple.__new__(cls, (width, height)) # create tuple with 2 items

    def __init__(self, x, y):
        self.x = y # width is the first argument passed
        self.y = y # height is the next



# or WAAAAYYY easier

from collections import namedtuple

Coord = namedtuple("Coord", ('x', 'y'))

# does not allow additional stuff like
coord1.move
coord1.moveto
coord1.plot


# example
coord1 = Coord(20, 40)
print(coord1)
>>> (20, 40)
print(coord1.x)
>>> 20
print(coord1.y)
>>> 40




onze case/????////// na 2e college
we moeten depth first gaan!!!!!!!
daarom eerst 1 groot apparaat maken, dan kleinere
[9][3][2][1]
[9][][][]




        # make clearer var names
        x = h.origin[0]
        y = h.origin[1]

        # push the house within bounds if the house is outside of bounds
        if x <  h.xLower:
            x = h.xLower
        if y <  h.yLower:
            y = h.yLower
        if x >= h.xUppers:
            x = h.xUpper
        if y >= h.yUpper:
            y = h.yUpper

"""