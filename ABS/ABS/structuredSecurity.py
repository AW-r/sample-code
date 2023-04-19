'''
This module contains the StructuredSecurity Class.
'''

import logging
from ABS.standardTranche import StandardTranche

class StructuredSecurity(object):

    def __init__(self, totalNotional):
        self._totalNotional = totalNotional
        # Initialize the input.

        self._tranchesList = []
        # The list will have items after addTranche is called.
        self._reserveAccount = 0
        # The initial reserve account is empty at first.
        self._mode = 'Sequential'
        # Set the initial mode as sequential.
        self._cumPrinCollections = 0
        # The original cumulative principal collections is 0.

    def __iter__(self):
        for tranche in self._tranchesList:
            yield tranche

    @property
    def tranches(self):
        return self._tranches
    # getter property for the tranches

    @tranches.setter
    def tranches(self, itranches):
        self._tranches = itranches
    # setter property for the tranches

    @property
    def totalNotional(self):
        return self._totalNotional
    # getter property for the total notional

    @totalNotional.setter
    def totalNotional(self, itotalNotional):
        self._totalNotional = itotalNotional
    # setter property for the total notional

    def addTranche(self, percent, rate, subordination, trancheClass=StandardTranche):
        tranche = trancheClass(self._totalNotional * percent, rate, subordination)
        self._tranchesList.append(tranche)
        logging.info(f'A new tranche is add to the list.')
        return self._tranchesList
    # Append the new tranche into the tranche list.

    def mode(self, mode='Sequential'):
        self._mode = mode
        return self._mode if mode in ('Sequential', 'Pro Rata') else logging.error('An incorrect mode is passed-into the function.')
    # Set the mode for the structured securities. (The default mode is 'Sequential'.)

    def increaseAllPeriod(self):
        for tranche in self._tranchesList:
            tranche.increaseTimePeriod()
            logging.info(f'The time period for {tranche} has increased.')
        # Call the increaseTimePeriod on each tranche.

    def makePayments(self, cash_amount, prinCollections):
        self._tranchesList = sorted(self._tranchesList, key=lambda x: x.subordination)
        # This means that tranche A is paid first.
        self._cumPrinCollections += prinCollections
        # Save the cumulative principal collections for each period.
        cash = cash_amount + self._reserveAccount
        # The initial cash for every period is the cash_amount and the money in the reserve account.
        self._reserveAccount = 0
        # The reserve account is reset to 0.

        for tranche in self._tranchesList:
            cash = tranche.makeInterestPayment(cash)

        # logging.info(f'The remaining cash after the interest payment is {cash}') (to reduce the time for function)
        # Make the interest payment for the tranches first.
        # If there is shortfall, it will be added to the interest of next period.
        if cash > 0:
            if self._mode == 'Sequential':
                # If there is still balance in prior tranche, make payment first.
                principalDueA = min(self._tranchesList[0].notionalBalance(), prinCollections + self._tranchesList[0]._principalShortfall)
                # When the mode is 'Sequential', the principal due is the smaller one between the balance and principal collections.
                cash = self._tranchesList[0].makePrincipalPayment(cash, principalDueA)
                # Make the principal payment for tranche A.

                principalDueB = min(self._tranchesList[1].notionalBalance(),
                                            max(0, min(prinCollections,
                                                       self._cumPrinCollections - self._tranchesList[0]._notional)) +
                                            self._tranchesList[1]._principalShortfall)
                    # According to the Excel, cumulative principal payment of this period should deduct the bigger one between the tranche A notional and
                    # cumulative principal payment of last period. Convert it to the smaller one between the principal collections for this period, and
                    # cumulative principal collections minus the original notional of tranche A.
                cash = self._tranchesList[1].makePrincipalPayment(cash, principalDueB)
                    # Make payments to the subordinate tranche.

            # Make the principal payment for the tranches afterward.
            # If there is shortfall, it will be added to the principal of next period.

            else:
                for tranche in self._tranchesList:
                    percentOfNotional = tranche.notional / self._totalNotional
                    # Get the percentage for the tranche.
                    principalDue = min(tranche.notionalBalance(), prinCollections * percentOfNotional + tranche._principalShortfall)
                    # When the mode is 'Pro Rata', the principal due is the smaller one between the percent * balance and principal collections.
                    cash = tranche.makePrincipalPayment(cash, principalDue)
            # Make the principal payment for the tranches afterward.
            # If there is shortfall, it will be added to the principal of next period.
        # logging.info(f'The remaining cash after the principal payment is {cash}')

        self._reserveAccount = cash
        return self._reserveAccount
        # The extra cash goes into the reserve account.

    def getWaterfall(self):
        waterfall = [
            [tranche.interestDue(), tranche.interestPayment, tranche.interestShortfall, tranche.principalPayment,
             tranche.notionalBalance(), self._reserveAccount] for tranche in self._tranchesList]
        flattenedWaterfall = [item for sublist in waterfall for item in sublist]
        return flattenedWaterfall
    # Get the waterfall for the current period.

    def reset(self):
        for tranche in self._tranchesList:
            tranche.reset()
    # Reset the structured security to its original state.
        self._reserveAccount = 0
        self._cumPrinCollections = 0
    # The reserve account and the cumulative principal collections is reset to 0.
