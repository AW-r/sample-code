'''
This module contains the Asset class.
'''

import logging

class Asset(object):
    def __init__(self, value):
        self._value = float(value)
    # initialize the input

    @property
    def value(self):
        return self._value
    # getter property for the initial value

    @value.setter
    def value(self, ivalue):
        self._value = ivalue
    # setter property for the initial value

    def annualDeprRate(self, period):
        raise NotImplementedError()
    # Make sure not to directly instantiate an Asset object.

    def monthlyDeprRate(self, period):
        logging.debug(
            f'Calculating the monthLy depreciation rate for the asset at time {period} = {self.annualDeprRate(period) / 12}')
        return self.annualDeprRate(period) / 12
    # Convert the yearly depreciation rate to monthly depreciation rate.

    def currentValue(self, period):
        totalDepr = (1 - self.monthlyDeprRate(period)) ** period
        logging.debug(
            f'Calculating the current value for the asset at time {period} = {self._value * totalDepr}')
        return self._value * totalDepr
    # Calculate the current value.
