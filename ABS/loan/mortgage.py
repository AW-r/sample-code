'''
This module contains the MortgageMixin class.
'''

import logging
from loan.loans import VariableRateLoan, FixedRateLoan

class MortgageMixin(object):
    def __init__(self, notional, rate, term, asset):
        super(MortgageMixin, self).__init__(notional, rate, term, asset)

    def PMI(self, period):
        if super(MortgageMixin, self).balance(period) >= 0.8 * self._notional:
            logging.debug(
                f'Calculating the PMI for the mortgage at time {period} = {0.000075 * self._notional}')
            return 0.000075 * self._notional
        else:
            logging.debug(
                f'Calculating the PMI for the mortgage at time {period} = 0')
            return 0
    # Since we assume the initial loan amount is for 100% of the asset value.

    def monthlyPayment(self, period):
        monthlyPayment = super(MortgageMixin, self).monthlyPayment(period) + self.PMI(period)
        logging.debug(
            f'Calculating the monthly payment for the mortgage at time {period} = monthly payment of a normal loan + PMI = {monthlyPayment}')
        return monthlyPayment
    # Overrides the base class monthlyPayment functions.

    def principalDue(self, period):
        principalDue = super(MortgageMixin, self).principalDue(period) - self.PMI(period)
        logging.debug(
            f'Calculating the principal due for the mortgage at time {period} = principal due of a normal loan - PMI = {principalDue}')
        return principalDue
    # Overrides the base class principalDue functions.

    def principalDueRecursive(self, period):
        principalDueRecursive = super(MortgageMixin, self).principalDueRecursive(period) - self.PMI(period)
        logging.debug(
            f'Calculating the principal due for the mortgage at time {period} = principal due of a normal loan - PMI = {principalDueRecursive}')
        return principalDueRecursive
    # Overrides the base class principalDueRecursive functions.

class VariableMortgage(MortgageMixin, VariableRateLoan):
    pass

class FixedMortgage(MortgageMixin, FixedRateLoan):
    pass
