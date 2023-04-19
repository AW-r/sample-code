'''
This module contains the derived-class StandardTranche.
'''

import logging
from ABS.tranche import Tranche

class StandardTranche(Tranche):

    def __init__(self, notional, rate, subordination, period=0):
        self._period = period
        super(StandardTranche, self).__init__(notional, rate, subordination)
        # Overrides the base class.

        self._principalPayment = 0
        self._principalShortfall = 0
        self._interestPayment = 0
        self._interestDue = 0
        self._interestShortfall = 0
        # The initial principal payment, principal shortfall, principal due, interest payment, interest due and interest shortfall at period 0 are all 0 by default.
        self._notionalBalance = self.notional
        # The initial balance is notional itself.

        self._principal_Payment = True
        self._interest_Payment = True

# Create the following getter property in order to implement getWaterfall in the StructuredSecurities Class.
    @property
    def period(self):
        return self._period
    # getter property for the period

    @period.setter
    def period(self, iperiod):
        self._period = iperiod
    # setter property for the period

    @property
    def interestPayment(self):
        return self._interestPayment
    # getter property for the interest payment

    @property
    def interestShortfall(self):
        return self._interestShortfall
    # getter property for the interest shortfall

    @property
    def principalPayment(self):
        return self._principalPayment
    # getter property for the principal payment

    def increaseTimePeriod(self):
        logging.debug(f'Increase the time period by 1: {self._period} (last period) + 1 = {self._period + 1}')
        self._period += 1
        # Increase the time period.

        self._interestDue = self._notionalBalance * self._rate / 12 + self._interestShortfall
        # Update the interest due.
        self._interestShortfall = 0
        self._interestPayment = 0
        self._principalPayment = 0
        # At a new period, reset the interest shortfall, interest payment and principal payment to 0.

        self._principal_Payment = True
        self._interest_Payment = True
        # We can call the makePrincipalPayment and makeInterestPayment again.
        return self._period
    # Increase the current time period of the object by 1 (starts from 0).

    def notionalBalance(self):
        # The notional balance is the notional itself when the period is 0, otherwise calculated based on principal payment.
        logging.info(f'The notional balance of the period {self._period} is {self._notionalBalance}.')
        return self._notional if not self._period else self._notionalBalance
    # Calculate the notional balance for the current time period.

    def interestDue(self):
        logging.info(f'The interest due of the period {self._period} is {self._interestDue}.')
        return self._interestDue
    # Return the interest due for the current period.

    def makePrincipalPayment(self, cash_amount, principalDue):
        if not self._notionalBalance:
            logging.info('The notional balance is 0, the function should not accept the principal payment.')
            # Should be an error, but each loan has different terms. (To make the output cleaner)
            return cash_amount
        else:
            if self._principal_Payment:
                principalDue += self._principalShortfall
                self._principalShortfall = 0
                # Reset the principal shortfall to 0, after added to the principal due.
                self._principalPayment = min(cash_amount, principalDue)
            # The smaller one is the principal payment made for this period.
                self._principalShortfall = principalDue - self._principalPayment
                logging.info(f'The principal payment of {self._principalPayment} has been made.')
                logging.info(f'After payment, there is {cash_amount - self._principalPayment} cash left.')
                self._principal_Payment = False
                # The principal payment is already made, you cannot call it again for this period.
                self._notionalBalance -= self._principalPayment
                # Update the notional balance with the principal payment.
                return cash_amount - self._principalPayment
                # The cash is used to pay off the principal.
            else:
                logging.error(f'The function has been called before at this period {self._period}.')
                raise Exception('Exception: You should make the interest payment for a new period.')

    def makeInterestPayment(self, cash_amount):
        if not self._interestDue:
            logging.info('The notional balance is 0, the function should not accept the interest payment.')
            # Should be an error, but each loan has different terms. (To make the output cleaner)
            return cash_amount
        else:
            if self._interest_Payment:
                self._interestPayment = min(cash_amount, self._interestDue)
                # The smaller one is the interest payment made for this period.
                self._interestShortfall = self._interestDue - self._interestPayment
                # Update the interest shortfall.
                logging.info(f'The interest payment of {self._interestPayment} has been made.')
                logging.info(f'The interest shortfall at period{self._period} is {self._interestShortfall}.')
                logging.info(f'After payment, there is {cash_amount - self._interestPayment} cash left.')
                self._interest_Payment = False
                # The interest payment is already made, you cannot call it again for this period.
                return cash_amount - self._interestPayment
                # The cash is used to pay off the interest.
            else:
                logging.error(f'The function has been called before at this period {self._period}.')
                raise Exception('Exception: You should make the interest payment for a new period.')

    def reset(self):
        self._period = 0
        # The period is reset to 0.

        self._principalPayment = 0
        self._principalShortfall = 0
        self._interestPayment = 0
        self._interestDue = 0
        self._interestShortfall = 0
        # The initial principal payment, principal shortfall, interest payment, interest due and interest shortfall are reset to 0.
        self._notionalBalance = self.notional
        # The notional balance is reset to the notional.

        self._principal_Payment = True
        self._interest_Payment = True
        # We can call the makePrincipalPayment and makeInterestPayment again.
    # Reset the tranche to its original state.
