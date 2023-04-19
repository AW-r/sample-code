'''
This module contains the basic Loan class.
'''

from asset.asset import Asset
import logging

defaultDict = {1: 0.0005, 11: 0.001, 60: 0.002, 120: 0.004, 180: 0.002, 210: 0.001, 360: 0}

class Loan(object):
    def __init__(self, notional, rate, term, asset):
        self._notional = float(notional)
        self._rate = rate
        self._term = term
        if not isinstance(asset, Asset):
            logging.error('An incorrect Asset type is passed-into the initialization function')
            raise TypeError('Exception: The asset parameter does not contain an Asset object(or any of its derived classed).')
        else:
            self._asset = asset
    # initialize the inputs

        self._default = False
        # The initial status of the default is False. (No default at the beginning)

    @staticmethod
    def monthlyRate(annualRate):
        # logging.debug(f'Calculating the monthly rate of {annualRate} (annual rate) = {annualRate / 12}')
        # Get rid of the debug to reduce time needed.
        return annualRate / 12
    # Convert the annual rate to the monthly rate.

    @staticmethod
    def annualRate(monthlyRate):
        # logging.debug(f'Calculating the annual rate of {monthlyRate} (monthly rate) = {monthlyRate * 12}')
        # Get rid of the debug to reduce time needed.
        return monthlyRate * 12
    # Convert the monthly rate to the annual rate.

    @property
    def asset(self):
        return self._asset
    # getter property for the asset

    @asset.setter
    def asset(self, iasset):
        self._asset = iasset
    # setter property for the asset

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
    def term(self):
        return self._term
    # getter property for the term

    @term.setter
    def term(self, iterm):
        self._term = iterm
    # setter property for the term

    def totalPayments(self):
        totalPayments = sum(self.monthlyPayment(period) for period in range(self._term))
        # logging.debug(f'Calculating the total payments of the loan = sum of the monthly payments of the loan = {totalPayments}')
        # Get rid of the debug to reduce time needed.
        return totalPayments
    # Calculate the total payment for a given loan.

    def totalInterest(self):
        totalInterest = self.totalPayments() - self._notional
        # logging.debug(f'Calculating the total interest of the loan = total payments - notional = {totalInterest}')
        # Get rid of the debug to reduce time needed.
        return totalInterest
    # Calculate the total interest for a given loan.

    def balanceRecursive(self, t):
        logging.warn('This function may take a long time with large t')
        return self.balanceRecursive2(t)

    def balanceRecursive2(self, t):
        if t <= self._term:
            if not t:
                logging.debug(f'Calculating the balance at time {t} = {self._notional} (notional)')
                return self._notional
            else:
                balanceRecursive2 = self.balanceRecursive2(t-1) - (self.monthlyPayment(t) - self.balanceRecursive2(t-1) * self.monthlyRate(self.getRate()))
                logging.debug(f'Calculating the balance at time {t} = balance at time {t-1} - (monthly payment at time {t} - balance at time {t-1} * monthly rate) = {balanceRecursive2}')
                return balanceRecursive2
        else:
            logging.info(f'period is greater than term')
            raise ValueError('Exception: The period should not exceed the term of the loan.')
    # Calculate the balance at a given period using recursive method.

    def interestDue(self, t):
        if t <= self._term:
            interestDue = self.balance(t-1) * self.monthlyRate(self.getRate())
            # logging.debug(
                # f'Calculating the interest due at time {t} = balance at time {t - 1} * monthly rate = {interestDue}')
            # Get rid of the debug to reduce time needed.
            return interestDue if t != 0 else 0
        else:
            return 0
    # Calculate the interest amount due at a given period using the formula.

    def interestDueRecursive(self, t):
        logging.warn('This function may take a long time with large t')
        return self.interestDueRecursive2(t)

    def interestDueRecursive2(self, t):
        if t <= self._term:
            interestDueRecursive2 = self.balanceRecursive2(t-1) * self.monthlyRate(self.getRate())
            logging.debug(
                f'Calculating the interest due at time {t} = balance at time {t - 1} * monthly rate = {interestDueRecursive2}')
            return interestDueRecursive2
        else:
            logging.info(f'period is greater than term')
            raise ValueError('Exception: The period should not exceed the term of the loan.')
    # Calculate the interest amount due at a given period using recursive method.

    def principalDue(self, t):
        if t <= self._term:
            principalDue = self.monthlyPayment(t) - self.interestDue(t)
            # logging.debug(
                # f'Calculating the principal due at time {t} = monthly payment at time {t} - interest due at time {t} = {principalDue}')
            # Get rid of the debug to reduce time needed.
            return principalDue if t != 0 else 0
        else:
            return 0
    # Calculate the principal amount due at a given period using the formula.

    def principalDueRecursive(self, t):
        logging.warn('This function may take a long time with large t')
        return self.principalDueRecursive2(t)

    def principalDueRecursive2(self, t):
        if t <= self._term:
            principalDueRecursive2 = self.monthlyPayment(t) - self.interestDueRecursive2(t)
            logging.debug(
                f'Calculating the principal due at time {t} = monthly payment at time {t} - interest due at time {t} = {principalDueRecursive2}')
            return principalDueRecursive2
        else:
            logging.info(f'period is greater than term')
            raise ValueError('Exception: The period should not exceed the term of the loan.')
        # Calculate the principal amount due at a given period using recursive method.

    @classmethod
    def calcMonthlyPmt(cls, face, rate, term, period=None):
        pmt = (Loan.monthlyRate(rate) * face) * (1 + Loan.monthlyRate(rate)) ** term / ((1 + Loan.monthlyRate(rate)) ** term - 1)
        # logging.debug(
            # f'Calculating the monthly payment at time {period} = (monthly rate * notional) * (1 + monthly rate) ^ (term) / ((1 + monthly rate) ^ (term) - 1) = {pmt}')
        # Get rid of the debug to reduce time needed.
        return pmt
    # Calculate the monthly payment using the class-level method.

    @classmethod
    def calcBalance(cls, face, rate, term, period):
        if period <= term:
            pmt = ((Loan.monthlyRate(rate) * face) * (1 + Loan.monthlyRate(rate)) ** term) / ((1 + Loan.monthlyRate(rate)) ** term - 1)
            bal = (face * (1 + Loan.monthlyRate(rate)) ** period) - (pmt * (((1 + Loan.monthlyRate(rate)) ** period - 1) / Loan.monthlyRate(rate)))
            # logging.debug(
                # f'Calculating the balance at time {period} = ((notional) * (1 + monthly rate) ^ {period})) - (payment * ((1 + monthly rate) ^ {period} - 1) / monthly rate) = {bal}')
            # Get rid of the debug to reduce time needed.
            return bal
        else:
            # logging.debug(
                # f'Calculating the balance at time {period} = 0')
            # Get rid of the debug to reduce time needed.
            return 0
    # Calculate the balance using the class-level method.

    def monthlyPayment(self, period):
        if 0 < period <= self._term:
            monthlyPayment = self.calcMonthlyPmt(self._notional, self.getRate(), self._term, period)
            # logging.debug(
                # f'Calculating the monthly payment at time {period} = {monthlyPayment}')
            # Get rid of the debug to reduce time needed.
            return monthlyPayment if not self._default else 0
            # If the default is True, the monthly payment will be 0.
        else:
            # logging.debug(
                # f'Calculating the monthly payment at time {period} = 0')
            # Get rid of the debug to reduce time needed.
            return 0
    # Calculate the monthly payment for a given loan using the delegation and object-level method.

    def balance(self, period):
        balance = self.calcBalance(self._notional, self.getRate(), self._term, period)
        # logging.debug(
                # f'Calculating the balance at time {period} = {balance}')
        # Get rid of the debug to reduce time needed.
        return balance if not self._default else 0
    # If the default is True, the balance will be 0.
    # Calculate the balance at a given period using the delegation and object-level method.

    def getRate(self, period=None):
        # Should be overriden by derived classes.
        # logging.debug(
            # f'get the rate for the loan at time {period} = {self.rate()}')
        # Get rid of the debug to reduce time needed.
        return self.rate()
    # Return the result of the rate property.

    def recoveryValue(self, period):
        recoveryValue = 0.6 * self._asset.currentValue(period)
        # logging.debug(
            # f'Calculating the recovery value for the asset at time {period} = {recoveryValue}')
        # Get rid of the debug to reduce time needed.
        return recoveryValue
    # Return the current asset value for the given period.

    def equity(self, period):
        equity = getattr(self._asset, '_value') - self.balance(period)
        # logging.debug(
            # f'Calculating the equity for the asset at time {period} = {equity}')
        # Get rid of the debug to reduce time needed.
        return equity

    def checkDefault(self, number, period):
        if number:
            return 0
        # The status is still no default.
        else:
            self._default = True
            # If the passed-in number is 0, the status of default would be True.
            return self.recoveryValue(period)

    def reset(self):
        self._default = False
    # Reset the loan to its original state.
