'''
This module contains the AutoLoan class.
'''

from loan.loans import FixedRateLoan

class AutoLoan(FixedRateLoan):
    def __init__(self, notional, rate, term, car):
        super(AutoLoan, self).__init__(notional, rate, term, car)
        self._car = car

    @property
    def car(self):
        return self._car
    # getter property for the car

    @car.setter
    def car(self, icar):
        self._car = icar
    # setter property for the car
