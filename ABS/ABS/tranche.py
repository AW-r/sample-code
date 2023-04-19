'''
This module contains the abstract base class Tranche.
'''

import logging
import numpy_financial as npf
from functools import reduce

class Tranche(object):
    def __init__(self, notional, rate, subordination):
        self._notional = notional
        self._rate = rate

        if subordination not in ('A', 'B'):
            logging.error('An incorrect subordination value is passed-into the initialization function.')
            raise ValueError('Exception: The value of the subordination parameter should be "A" or "B".')
        else:
            self._subordination = subordination
        # Initialize the inputs.

    @property
    def notional(self):
        return self._notional
    # getter property for the notional

    @notional.setter
    def notional(self, inotional):
        self._notional = inotional
    # setter property for the notional

    @property
    def rate(self):
        return self._rate
    # getter property for the rate

    @rate.setter
    def rate(self, irate):
        self._rate = irate
    # setter property for the rate

    @property
    def subordination(self):
        return self._subordination
    # getter property for the subordination

    @subordination.setter
    def subordination(self, isubordination):
        self._subordination = isubordination
    # setter property for the subordination

    def increaseTimePeriod(self):
        raise NotImplementedError()
        # Make sure not to directly instantiate a Tranche object.

    def notionalBalance(self):
        raise NotImplementedError()
    # Make sure not to directly instantiate a Tranche object.

    def interestDue(self):
        raise NotImplementedError()
    # Make sure not to directly instantiate a Tranche object.

    def makePrincipalPayment(self, cash_amount, principalDue):
        raise NotImplementedError()
    # Make sure not to directly instantiate a Tranche object.

    def makeInterestPayment(self, cash_amount):
        raise NotImplementedError
    # Make sure not to directly instantiate a Tranche object.

    def IRR(self, interestPayment, principalPayment):
        totalPayment = [x + y for x, y in zip(interestPayment, principalPayment)]
        IRR = round(npf.irr([-self.notional] + totalPayment) * 12, 6)
        # Round the IRR to the 6th decimal.
        logging.info(f'The IRR of the investment is {IRR}.')
        return IRR
    # Calculate the IRR of the investment.

    def DIRR(self, interestPayment, principalPayment):
        DIRR = round(self._rate - self.IRR(interestPayment, principalPayment), 6)
        logging.info(f'The DIRR of the investment is {DIRR}.')
        return DIRR
    # Calculate the DIRR.

    def AL(self, principalPayment):
        if not round(sum(principalPayment) - self.notional):
            period = [i + 1 for i in range(len(principalPayment))]
            AL = reduce(lambda total, period_payment: total + period_payment[0] * period_payment[1], zip(period, principalPayment), 0) / self._notional
            logging.info(f'The AL of the investment is {AL}.')
            return AL
        else:
            logging.info(f'The AL of the investment is infinite.')
            return None

    # Calculate the AL.
