'''
This module contains the Lamborghini, Lexus, PrimaryHome and VacationHome class.
'''

import logging
from asset.asset_type import Car, HouseBase

class Lamborghini(Car):
    def annualDeprRate(self, period):
        logging.debug(
            f'Calculating the annual depreciation rate for the Lamborghini at time {period} = {0.2}')
        return 0.2
    # Depreciation rate for a Lamborghini is 0.2.
    # This overrides the base class.

class Lexus(Car):
    def annualDeprRate(self, period):
        logging.debug(
            f'Calculating the annual depreciation rate for the Lexus at time {period} = {0.1}')
        return 0.1
    # Depreciation rate for a Lexus is 0.1.
    # This overrides the base class.

class PrimaryHome(HouseBase):
    def annualDeprRate(self, period):
        logging.debug(
            f'Calculating the annual depreciation rate for the primary home at time {period} = {0.05}')
        return 0.05
    # Depreciation rate for a primary home is 0.05.
    # This overrides the base class.

class VacationHome(HouseBase):
    def annualDeprRate(self, period):
        logging.debug(
            f'Calculating the annual depreciation rate for the vacation home at time {period} = {0.02}')
        return 0.02
    # Depreciation rate for a vacation home is 0.02.
    # This overrides the base class.
