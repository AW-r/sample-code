'''
This module contains the Car and HouseBase class.
'''

from asset.asset import Asset

class Car(Asset):
    def annualDeprRate(self, period):
        return 0.1
    # I modify the annual depreciation rate here for that the provided csv only has Car type.

class HouseBase(Asset):
    def annualDeprRate(self, period):
        raise NotImplementedError()
    # Make sure not to directly instantiate a house base object.
