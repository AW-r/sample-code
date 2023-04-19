'''
This program contains the doWaterfall function.
'''

from loan.loan_pool import LoanPool
from ABS.structuredSecurity import StructuredSecurity
from utils.functions import Timer
import numpy as np
import logging
import multiprocessing

ratingDict = {0.06: 'Aaa', 0.67: 'Aa1', 1.3: 'Aa2', 2.7: 'Aa3', 5.2: 'A1', 8.9: 'A2', 13: 'A3', 19: 'Baa1', 27: 'Baa2',
              46: 'Baa3', 72: 'Ba1', 106: 'Ba1', 143: 'Ba3', 183: 'B1', 231: 'B2', 311: 'B3', 2500: 'Caa', 10000: 'Ca'}

def doWaterfall(loanPool, structuredSecurity):
    if not isinstance(loanPool, LoanPool) or not isinstance(structuredSecurity, StructuredSecurity):
        logging.error('An incorrect LoanPool or StructuredSecurity type is passed into the function')
        raise TypeError('Exception: The parameter is not a LoanPool or StructuredSecurity object.')
    else:
        period = 0
        # Starts at period 0.
        loanPoolWaterfallList = []
        structuredSecurityWaterfallList = []
        # Get the initial waterfall list.

        while loanPool.activeLoanCount(period) > 0:
            cash_amount = loanPool.paymentDue(period)
            # This should be the cash we have at this period.
            prinCollections = loanPool.principalDue(period)
            # Calculate the principal due of the loanpool for principal collections for each period.
            recoveryValue = loanPool.checkDefaults(period)
            # Calculate the recovery value of the loans.
            structuredSecurity.makePayments(cash_amount, prinCollections + recoveryValue)
            # Make payments with the amount provided by the LoanPool.
            lWaterfall = loanPool.getWaterfall(period)
            # Call getWaterfall on LoanPool object.
            loanPoolWaterfallList.append(lWaterfall)
            # Append the waterfall to the list
            sWaterfall = structuredSecurity.getWaterfall()
            # Call getWaterfall on StructuredSecurity object.
            structuredSecurityWaterfallList.append(sWaterfall)
            # Append the waterfall to the list.
            structuredSecurity.increaseAllPeriod()
            # increase the time period on the StructuredSecurity object.
            period += 1
            # Update the period.

        interestPaymentA = [structuredSecurityWaterfallList[i][1] for i in range(1, len(structuredSecurityWaterfallList))]
        principalPaymentA = [structuredSecurityWaterfallList[i][3] for i in range(1, len(structuredSecurityWaterfallList))]
        interestPaymentB = [structuredSecurityWaterfallList[i][7] for i in range(1, len(structuredSecurityWaterfallList))]
        principalPaymentB = [structuredSecurityWaterfallList[i][9] for i in range(1, len(structuredSecurityWaterfallList))]
        # Save the interest payment and principal payment of each trench into the list.

        metricsA = [structuredSecurity._tranchesList[0].IRR(interestPaymentA, principalPaymentA),
                    structuredSecurity._tranchesList[0].DIRR(interestPaymentA, principalPaymentA),
                    structuredSecurity._tranchesList[0].AL(principalPaymentA)]
        # Get the list for metrics A.

        metricsB = [structuredSecurity._tranchesList[1].IRR(interestPaymentB, principalPaymentB),
                    structuredSecurity._tranchesList[1].DIRR(interestPaymentB, principalPaymentB),
                    structuredSecurity._tranchesList[1].AL(principalPaymentB)]
        # Get the list for metrics B.

        loanPool.reset()
        structuredSecurity.reset()
        # Reset the structured security and loan pool to its original state.

        return loanPoolWaterfallList, structuredSecurityWaterfallList, metricsA, metricsB

def rating(DIRR):
    DIRR = DIRR * 10000
    # Change into BPS form.
    for i in range(len(ratingDict)):
        ratingList = list(ratingDict.items())
        if DIRR <= ratingList[0][0]:
            logging.info(
                f'The rating of tranche is {ratingList[0][1]}.')
            return ratingList[0][1]
        elif DIRR > ratingList[i - 1][0] and DIRR <= ratingList[i][0] and DIRR != 10000:
            logging.info(
                f'The rating of tranche is {ratingList[0][1]}.')
            return ratingList[i][1]
        else:
            logging.info(
                f'The rating of tranche is {ratingList[len(ratingDict) - 1][1]}.')
            return ratingList[len(ratingDict) - 1][1]
    # Get the rating for the tranche.

def simulateWaterfall(loanPool, structuredSecurity, NSIM):
    metricsListA = []
    metricsListB = []

    for i in range(NSIM):
        lists = doWaterfall(loanPool, structuredSecurity)
        metricsA = lists[2]
        # Get all the metrics for tranche A.
        metricsListA.append(metricsA)
        metricsB = lists[3]
        # Get all the metrics for tranche B.
        metricsListB.append(metricsB)

    DIRRA = np.average([metricsListA[i][1] for i in range(NSIM)])
    logging.info(f'The DIRR of tranche A is {DIRRA}.')
    DIRRB = np.average([metricsListB[i][1] for i in range(NSIM)])
    logging.info(f'The DIRR of tranche B is {DIRRB}.')
    # Calculate the DIRR for each tranche.
    WALA = np.average([metricsListA[i][2] for i in range(NSIM) if metricsListA[i][2]])
    logging.info(f'The WAL of tranche A is {WALA}.')
    WALB = np.average([metricsListB[i][2] for i in range(NSIM) if metricsListB[i][2]])
    logging.info(f'The WAL of tranche B is {WALB}.')
    # Calculate the WAL for each tranche. (And exclude those with no AL)
    return DIRRA, DIRRB, WALA, WALB

@Timer
def runMonte(loanPool, structuredSecurity, tolerance, NSIM, numProcesses):
    while True:
        # This is an infinite loop.
        oldTrancheRateList = [structuredSecurity._tranchesList[i].rate for i in range(2)]
        notionalList = [structuredSecurity._tranchesList[i].notional for i in range(2)]

        result = runSimulationParallel(loanPool, structuredSecurity, NSIM, numProcesses)
        DIRRA = result[0]
        DIRRB = result[1]
        WALA = result[2]
        WALB = result[3]
        # Get the DIRR and WAL for both tranche.
        yieldA = calculateYield(DIRRA, WALA)
        yieldB = calculateYield(DIRRB, WALB)
        # Calculate the yield
        yieldList = [yieldA, yieldB]
        coeff = [1.2, 0.8]
        newTrancheRateList = []
        for i, tranche in enumerate(structuredSecurity._tranchesList):
            newTrancheRate = tranche.rate + coeff[i] * (yieldList[i] - tranche.rate)
            # Calculate the new rate for both tranche.
            newTrancheRateList.append(newTrancheRate)

        diff = (notionalList[0] * np.abs((oldTrancheRateList[0] - newTrancheRateList[0]) / oldTrancheRateList[0]) +
            notionalList[1] * np.abs((oldTrancheRateList[1] - newTrancheRateList[1]) / oldTrancheRateList[1])) / sum(notionalList)
        # Calculate if the new rate differs from the old one.

        if diff < tolerance:
            break
            # Break from the loop.
        else:
            for i, tranche in enumerate(structuredSecurity._tranchesList):
                tranche._rate = newTrancheRateList[i]
            # Modify the tranche rates.

    return DIRRA, DIRRB, WALA, WALB, structuredSecurity._tranchesList[0]._rate, structuredSecurity._tranchesList[1]._rate

def calculateYield(DIRR, WAL):
    Yield = (7 / (1 + .08 * np.exp((-.19) * WAL / 12)) + .019 * np.sqrt(WAL / 12 * DIRR * 100)) / 100
    return Yield
# Calculate the yield.

def doWork(input, output):
    while True:
        try:
            f, args = input.get(timeout=1)
            res = f(*args)
            output.put(res)
        except:
            break

def runSimulationParallel(loanPool, structuredSecurity, NSIM, numProcesses):
    input_queue = multiprocessing.Queue()
    output_queue = multiprocessing.Queue()
    # Use two queues.

    for i in range(numProcesses):
        input_queue.put((simulateWaterfall, (loanPool, structuredSecurity, int(NSIM / numProcesses))))

    processes = []
    for i in range(numProcesses):
        p = multiprocessing.Process(target=doWork, args=(input_queue, output_queue))
        processes.append(p)
        p.start()
    # Create and initialize processes.

    res = []
    while True:
        if len(res) != numProcesses:
            r = output_queue.get()
            res.append(r)
        else:
            break

    for process in processes:
        process.terminate()
    # terminate the processes
    DIRRA = np.average([res[i][0] for i in range(numProcesses) if res[0]])
    DIRRB = np.average([res[i][1] for i in range(numProcesses) if res[1]])
    WALA = np.average([res[i][2] for i in range(numProcesses) if res[2]])
    WALB = np.average([res[i][3] for i in range(numProcesses) if res[3]])
    # Get the result for average DIRR and WAL.

    return DIRRA, DIRRB, WALA, WALB
