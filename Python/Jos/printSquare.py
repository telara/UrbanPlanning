"""
NAME    printSquare

AUTHORS Christiaan Wewer
        Tara Elsen
        jos feenstra        1196 95

DESC    STATE SPACE estimation calculation

NOTE    this thing is an example of how to use helpers
"""


# TODO turn main into hillclimber
# TODO save all values generated in .txt file
# TODO make an algoritm which determines which ring is the most valuable to add, with value in price / m2


from helpers import *

# choose 0, 1 or 2 to get 20, 40 or 60 houses
SELECTED_HOUSE_COUNT = HOUSE_COUNT[0]


"""
build a correct random map
"""
def main():
    housetypes = initHouseTypes(100)

    # generate correct type parameters
    housetypelist = []
    for ht in reversed(housetypes):
        n = round(ht.frequency * SELECTED_HOUSE_COUNT)
        housetypelist += [ht] * n

    # make a map
    map1 = Map()

    # add a number of houses to map
    for i in range(SELECTED_HOUSE_COUNT):

        # get current housetype
        ht = housetypelist[i]

        # the add house function which i want
        map1.addHouse(ht, (0,0), 0, "random_positions", "non_colliding")

    # add water to the map (TODO)
    map1.addWater()

    map1.plot()

    map1.expandRings()
    #
    # # keep increasing the best house
    # for i in range(100):
    #     selected = map1.findHouseWithMostLandValueRingIncrease()
    #     map1.house[selected].changeRingsBy(1)
    #     # if that house does not fit
    #     if not map1.house[selected].fit()
    #         # make it fit
    #         map1.house[selected]

    # print value of map
    value = map1.calculateValue()
    print()
    print("Total map value:", value)

    # draw the map a second time
    map1.plot()

if __name__ == "__main__":
    main()
