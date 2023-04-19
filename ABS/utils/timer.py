'''
This module contains the Timer class.
'''

import time
import logging

class Timer(object):
    timer = False
    config = 'seconds'
    # The default configuration is seconds.
    warnThreshold = 60
    # class level warnThreshold (defaults to 1 minute (60 secs))

    def __init__(self, timerName):
        self.timerName = timerName

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.end()

    def start(self):
        if not Timer.timer:
            Timer.timer = True
            self._start = time.time()
            return self._start
        else:
            logging.info('Error (Timer is already started.)')
    # The timer starts.

    def end(self):
        if Timer.timer:
            Timer.timer = False
            self._end = time.time()
            timeTaken = self._end - self._start
            config = Timer.config
            divDict = {'hours': 3600, 'minutes': 60, 'seconds': 1}
            logFunc = logging.info if timeTaken <= Timer.warnThreshold else logging.warning
            return logFunc(f'{self.timerName}: {timeTaken / divDict.get(config)} {config}')
        else:
            logging.info('Error (Timer is not currently running.)')
    # The timer ends.

    def configureTimerDisplay(self, configuration):
        unit = {'s': 'seconds', 'mins': 'minutes', 'hrs': 'hours'}
        Timer.config = unit.get(configuration)
        return Timer.config
        # This will enable us to choose the configuration we want to display.

    def retrieveLastResult(self):
        timeTaken = self._end - self._start
        config = Timer.config
        divDict = {'hours': 3600, 'minutes': 60, 'seconds': 1}
        logFunc = logging.info if timeTaken <= Timer.warnThreshold else logging.warning
        return logFunc(f'{self.timerName}: {timeTaken / divDict.get(config)} {config}')
    # Use this to retrieve the last result.
