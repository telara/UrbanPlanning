"""
NAME    ringPriorities

AUTHOR  jos feenstra

DESC    STATE SPACE estimation calculation

NOTE    the minimum distance to another home is represented by the name "ring",
        as its boundary representations look like square rings.
"""
#import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle as create_rectangle
import numpy as np

# constances general
AREA = (160, 180)
HOUSE_COUNT = [20, 40, 60]

# water (ignored for now)
WATER_PERCENTAGE = 0.20         # percentage of total area covered by water
MAX_BODIES       = 4            # maximum number of bodies
MAX_RATIO        = 4            # l/b < x AND  b/l < x

# house constances
NAME           = ["Family",  "Bungalow", "Mansion"  ]
FREQUENCY      = [60,        25,         15         ]
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
            r.width = ringWidth
            r.ring = ringWidth                  # synoniem
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
            print(printstr.format(r.ring, r.x, r.y, r.area, r.landValue, r.cumArea, r.cumValue, r.cumLandValue ))
        print((len(printstr) - 4) * "-")



"""
House Class
"""
class House:

    def __init__(self, aType, aCoord, ExtraRings):
        self.type = aType
        self.origin = aCoord
        self.additionalRings = ExtraRings
        self.update()

    def update(self):
        # calculate additional geometric information, based on init's current value
            # EXAMPLE a fam.house with 3 add.rings gives a ringWidth of 5.
        self.ring = self.type.ring[self.additionalRings]

        # house geometry rep. boundary
        self.boundary = Rectangle(self.origin, self.type.width, self.type.height, fc=self.type.colour)

        # move houseOrigin diagonal to create ringOrigin
        vector = (-1 * self.ring.ring, -1 * self.ring.ring)
        ringOrigin = moveCoord(self.origin, vector)

        # house ring rep. boundary
        self.ringboundary =  Rectangle(ringOrigin, self.ring.x, self.ring.y, fc=self.type.colour, alpha=0.2)

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



"""
square class
"""
class Rectangle:

    def __init__(self, OriginCoord, width, height, **kwargs):

        self.x1 = OriginCoord[0]
        self.y1 = OriginCoord[1]
        self.coord1 = (self.x1, self.y1)

        self.x2 = self.x1 + width
        self.y2 = self.y1 + height
        self.coord2 = (self.x2, self.y2)

        # self.printAll()

        # embed mathplot object in this object
        self.mathplot = create_rectangle(self.coord1, width, height, 0, **kwargs)

    def printAll(self):
        print("Rectangle.coord1: {} \n"
              "Rectangle.coord2: {} \n".format(
               self.coord1,
               self.coord2)
             )


# TODO make a map class
# WIP

class map:
    pass
    # def __init__()

"""
- TODO this function should become a method of the house class when it is ready
    - Then 'houses' should be replaced with 'self.houses', as a class can remember
      all the houses on it.
    -

"""
def drawAll(houses):

    # init figure and axes
    fig = plt.figure()
    ax = fig.add_subplot(111, aspect='equal')

    # get rectangle information out of houses
    houseBound_list = []
    ringBound_list  = []
    for house in houses:
        ax.add_patch(house.boundary.mathplot)
        ax.add_patch(house.ringboundary.mathplot)

    # EXAMPLE FOR PROPERTIES
    # rect = patches.Rectangle((50,100),40,30,linewidth=1,edgecolor='r',facecolor='none')

    # determines how axis are drawn
    ax.set_xticks(np.arange(0, AREA[0], 10))
    ax.set_yticks(np.arange(0, AREA[1], 10))
    ax.set_xlim([0, AREA[0]])
    ax.set_ylim([0, AREA[1]])

    # draw the board
    plt.show()


###############################################################################


"""
instantiate all house objects
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

"""
