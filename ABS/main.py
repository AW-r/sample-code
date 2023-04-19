'''
This program illustrates the functionality of the project.
'''

import logging
import pandas as pd

from loan.loan_pool import LoanPool
from ABS.structuredSecurity import StructuredSecurity
from waterfall import doWaterfall, rating, simulateWaterfall, runMonte, runSimulationParallel, calculateYield

def main():
    '''
    The following code demonstrates the part 1.
    '''

    loanPool = LoanPool([])
    with open('Loans.csv', 'r', encoding='utf-8') as fp:
        cnt = 0
        for line in fp:
            cnt += 1
            vals = line.lstrip('\ufeff').rstrip('\n').replace(' ', '').split(',')
            loan = LoanPool.createLoan(*vals)
            if loan:
                loanPool.loans.append(loan)
                logging.info('{0} loans loaded: '.format(cnt))
    # Use the provided csv to create LoanPool objects.
    totalNotional = loanPool.balance(0)
    # This is the total notional for the StructuredSecurity.
    structuredSecurity = StructuredSecurity(totalNotional)
    # Instantiate the StructuredSecurity object.
    structuredSecurity.addTranche(0.8, 0.05, 'A')
    structuredSecurity.addTranche(0.2, 0.08, 'B')
    # Tranche A and B are added into the structured security. (B is the subordinate tranche)
    structuredSecurity.mode('Sequential')
    # The mode is set to sequential.
    lists = doWaterfall(loanPool, structuredSecurity)
    # Call the doWaterfall function.

    assets = lists[0]
    liabilities = lists[1]
    loanNum = int(len(assets[0]) / 4)
    columnsAsset = []
    for i in range(loanNum):
        columnsAsset.append(f'Principal Payment of Loan {i + 1}')
        columnsAsset.append(f'Interest Payment of Loan {i + 1}')
        columnsAsset.append(f'Total Payment of Loan {i + 1}')
        columnsAsset.append(f'Balance of Loan {i + 1}')
    assetdf = pd.DataFrame(assets, columns=columnsAsset)
    # save the info into a dataframe
    assetdf.index.name = 'Period'
    assetdf.to_csv('assets.csv', index=True)
    # Save the info to the csv.
    # We can acquire the assets CSV.

    columnsLiabilities = ['Interest Due of Tranche A', 'Interest Paid of Tranche A',
                                 'Interest Shortfall of Tranche A', 'Principal Paid of Tranche A',
                                 'Balance of Tranche A', 'Reserve', 'Interest Due of Tranche B',
                                 'Interest Paid of Tranche B', 'Interest Shortfall of Tranche B',
                                 'Principal Paid of Tranche B', 'Balance of Tranche B', 'Reserve Account Balance']
    liabilitiesdf = pd.DataFrame(liabilities, columns=columnsLiabilities)
    # save the info into a dataframe
    liabilitiesdf.index.name = 'Period'
    liabilitiesdf.drop(columns='Reserve', inplace=True)
    # drop the redundant reserve column
    liabilitiesdf.to_csv('liabilities.csv', index=True)
    # Save the info to the csv.
    # We can acquire the liabilities CSV.

    '''
    The following code demonstrates the part 2.
    '''

    metricsA = lists[2]
    print(f'The IRR of tranche A is {metricsA[0]}, the DIRR of tranche A is {metricsA[1]}, and the AL of tranche A is {metricsA[2]}.\n'
          f'The rating of tranche A is {rating(metricsA[1])}.\n')
    # Output the metrics and the letter rating of tranche A.

    metricsB = lists[3]
    print(f'The IRR of tranche B is {metricsB[0]}, the DIRR of tranche B is {metricsB[1]}, and the AL of tranche B is {metricsB[2]}.\n'
          f'The rating of tranche B is {rating(metricsB[1])}.')
    # Output the metrics and the letter rating of tranche B.

    '''
    The following code demonstrates the part 3.
    '''

    res = simulateWaterfall(loanPool, structuredSecurity, 20)
    # The simulation of 200 needs 326 seconds. (before multiprocessing, after using it 3x faster on my computer.)
    print(f'The average DIRR of tranche A is {res[0]}, the average DIRR of tranche B is {res[1]}, '
          f'the WAL of tranche A is {res[2]}, and the WAL of tranche B is {res[3]}.')

    print(runSimulationParallel(loanPool, structuredSecurity, 2000, 8))
    # The simulation of 2000 needs 1325 seconds.

    res = runMonte(loanPool, structuredSecurity, 0.005, 2000, 8)
    # Run the simulation with 8 processors.
    print(f'The average DIRR of tranche A is {res[0]}, and the average DIRR of tranche B is {res[1]}.\n'
          f'The rating of tranche A is {rating(res[0])}, and the rating of tranche B is {rating(res[1])}.\n'
          f'The WAL of tranche A is {res[2]}, and the WAL of tranche B is {res[3]}.\n'
          f'The rate of tranche A is {res[4]}, and the rate of tranche B is {res[5]}')
    # The total time of simulation is 5000 seconds.
    # The WAL of tranche A is 28.674089182095933, and the WAL of tranche B is 58.0885658996603.
    # The rate of tranche A is 0.06674843814715704, and the rate of tranche B is 0.06809269445489097


if __name__ == '__main__':
    main()
