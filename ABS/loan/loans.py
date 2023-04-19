'''
This module contains the FixedRateLoan and VariableRateLoan class.
'''

import logging
from loan.loan_base import Loan

class FixedRateLoan(Loan):
    def getRate(self, period=None):
        # Overrides the base class
        return self._rate
    # Return the rate of fixed rate loan at a given period.

class VariableRateLoan(Loan):
    def __init__(self, notional, rateDict, term):
        # Overrides the base class
        super(VariableRateLoan, self).__init__(notional, rateDict, term)

    @property
    def rateDict(self):
        return self._rate
    # getter property for the rateDict

    @rateDict.setter
    def rateDict(self, iRateDict):
        self._rate = iRateDict
    # setter property for the rateDict

    def getRate(self, period):
        sortedRateList = sorted(list(self._rate.items()), key=lambda x: x[0], reverse=False)
        for i in range(len(sortedRateList)):
            if period >= sortedRateList[i-1][0] and period < sortedRateList[i][0]:
                print('In the VariableRateLoan rate function')
                logging.debug(
                    f'get the rate for the loan at time {period} = {sortedRateList[i-1][1]}')
                return sortedRateList[i-1][1]
            elif period >= sortedRateList[len(sortedRateList)-1][0]:
                print('In the VariableRateLoan rate function')
                logging.debug(
                    f'get the rate for the loan at time {period} = {sortedRateList[len(sortedRateList)-1][1]}')
                return sortedRateList[len(sortedRateList)-1][1]
    # Return the rate of variable rate loan at a given period.
