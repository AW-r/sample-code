'''
This module contains the LoanPool class.
'''

from loan.loan_base import Loan
from loan.mortgage import FixedMortgage
from functools import reduce
from loan.auto_loan import AutoLoan
from asset.asset_type import Car
from asset.concrete_asset import Lamborghini, Lexus, VacationHome, PrimaryHome
import numpy as np
import logging

loanNameToClass = {'AutoLoan': AutoLoan, 'FixedMortgage': FixedMortgage}
assetNameToClass = {'Lamborghini': Lamborghini, 'Lexus': Lexus, 'VacationHome': VacationHome, 'PrimaryHome': PrimaryHome, 'Car': Car}

defaultDict = {1: 0.0005, 11: 0.001, 61: 0.002, 121: 0.004, 181: 0.002, 211: 0.001}


def multiply(notional, rate):
    return notional * rate

def add(x, y):
    return x + y

class LoanPool(object):
    def __init__(self, loans):
        self._loans = loans

    def __iter__(self):
        for loan in self._loans:
            yield loan

    @property
    def loans(self):
        return self._loans
    # getter property for the loans

    @loans.setter
    def loans(self, iLoans):
        self._loans = iLoans
    # setter property for the rateDict

    def totalPrincipal(self):
        totalPrincipal = sum(getattr(i, '_notional') for i in self._loans)
        #logging.debug(
            #f'Calculating the total principal for the loans in the loan pool = sum of the principal of the loans = {totalPrincipal}')
        # Get rid of the debug to reduce time needed.
        return totalPrincipal
    # Return the total loan principal.

    def balance(self, period):
        balance = sum(Loan.balance(i, period) for i in self._loans if Loan.balance(i, period))
        #logging.debug(
            #f'Calculating the balance for the loans in the loan pool at time {period} = sum of the balance of the loans = {balance}')
        # Get rid of the debug to reduce time needed.
        return balance
    # Return the total loan balance for a given period.

    def principalDue(self, period):
        principalDue = sum(Loan.principalDue(i, period) for i in self._loans if not isinstance(i, FixedMortgage))
        principalDueFixedMortgage = sum(
            FixedMortgage.principalDue(i, period) for i in self._loans if isinstance(i, FixedMortgage))
        #logging.debug(
            #f'Calculating the principal due for the loans in the loan pool at time {period} = sum of the principal due of the loans = {principalDue + principalDueFixedMortgage}')
        # Get rid of the debug to reduce time needed.
        return principalDue + principalDueFixedMortgage
    # Return the aggregate principal due for a given period.

    def interestDue(self, period):
        interestDue = sum(Loan.interestDue(i, period) for i in self._loans)
        #logging.debug(
            #f'Calculating the interest due for the loans in the loan pool at time {period} = sum of the interest due of the loans = {interestDue}')
        # Get rid of the debug to reduce time needed.
        return interestDue
    # Return the aggregate interest due for a given period.

    def paymentDue(self, period):
        paymentDue = sum(Loan.monthlyPayment(i, period) for i in self._loans if not isinstance(i, FixedMortgage))
        paymentDueFixedMortgage = sum(FixedMortgage.monthlyPayment(i, period) for i in self._loans if isinstance(i, FixedMortgage))
        # logging.debug(
            #f'Calculating the payment due for the loans in the loan pool at time {period} = sum of the monthly payment of the loans = {paymentDue + paymentDueFixedMortgage}')
        # Get rid of the debug to reduce time needed.
        return paymentDue + paymentDueFixedMortgage
    # Return the aggregate payment due for a given period.

    def activeLoanCount(self, period):
        activeLoanCount = sum(1 for i in self._loans if Loan.balance(i, period) > 0)
        #logging.debug(
            #f'Calculating the active loans in the loan pool at time {period} = sum of the active loans = {activeLoanCount}')
        # Get rid of the debug to reduce time needed.
        return activeLoanCount
    # Count the active loan for a given period.

    def WAR(self):
        notionals = [getattr(i, '_notional') for i in self._loans]
        rates = [getattr(i, '_rate') for i in self._loans]
        total = reduce(lambda total, notional_rate: total + notional_rate[0] * notional_rate[1], zip(notionals, rates), 0)
        totalNotional = reduce(lambda totalNotional, notional: totalNotional + notional, notionals, 0)
        logging.debug(
            f'Calculating the weighted average rate for the loan pool = {total / totalNotional}')
        return total / totalNotional
    # This function calculates the weighted average rate.

    def WAM(self):
        notionals = [getattr(i, '_notional') for i in self._loans]
        terms = [getattr(i, '_term') for i in self._loans]
        total = reduce(add, map(multiply, notionals, terms))
        totalNotional = reduce(add, notionals)
        logging.debug(
            f'Calculating the weighted average maturity for the loan pool = {total / totalNotional}')
        return total / totalNotional
    # This function calculates the weighted average maturity.

    @classmethod
    def writeLoansToCSV(cls, loanPool, filename):
        lines = []
        for loan in loanPool:
            lines.append(','.join([loan.__class__.__name__, loan.asset.__class__.__name__,
                                   str(loan.asset.value), str(loan.notional),
                                   str(loan.rate), str(loan.term)]))

        outputString = '\n'.join(lines)

        with open(filename, 'w') as fp:
            fp.write(outputString)

    @classmethod
    def createLoan(cls, loanType, principal, rate, term, assetName, assetValue):
        assetCls = assetNameToClass.get(assetName)
        if assetCls:
            asset = assetCls(float(assetValue))
            loanCls = loanNameToClass.get(loanType)
            if loanCls:
                loan = loanCls(float(principal), float(rate), int(term), asset)
                return loan
            else:
                logging.error('Invalid loan type entered.')
        else:
            logging.error('Invalid asset type entered.')

    def getWaterfall(self, period):
        waterfall = [
            [loan.principalDue(period), loan.interestDue(period), loan.monthlyPayment(period), loan.balance(period)] for loan in self.loans]
        flattenedWaterfall = [item for sublist in waterfall for item in sublist]
        return flattenedWaterfall
    # Get the waterfall for the given period.

    def checkDefaults(self, period):
        if period:
            key = max(i for i in defaultDict.keys() if i <= period)
            prob = defaultDict.get(key)
            high = 1 / prob
            # Get the high parameter for randint.
            randomList = list(np.random.randint(0, high + 1, len(self._loans)))
            # Generate a random list number for each loan.
            sum = 0
            for i, loan in enumerate(self._loans):
                number = randomList[i]
                sum += loan.checkDefault(number, period)
            # logging.info(f'The recovery value of period {period} is {sum}.')
            # Get rid of the debug to reduce time needed.
            return sum
        # The function would return the recovery value for the loans.
        else:
            return 0
        # At period 0, there will be no default (no recovery value).

    def reset(self):
        for loan in self._loans:
            loan.reset()
    # Reset the loan pool to its original state.
