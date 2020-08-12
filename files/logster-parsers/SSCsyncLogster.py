# File managed by puppet

import time
import re

from logster.logster_helper import MetricObject, LogsterParser
from logster.logster_helper import LogsterParsingException


class SSCsyncLogster(LogsterParser):

    def __init__(self, option_string=None):
        self.errors = 0
        self.dirtied = 0
        self.changed = 0
        self.maxProctime = 0

        self.errorLineRE = re.compile(
            '.*Finished with (?P<errors>[0-9]*) errors')
        self.statusLineRE = re.compile(
            '.*Done, files dirtied: (?P<dirtied>[0-9]*), updated: (?P<updated>[0-9]*), deleted: (?P<deleted>[0-9]*). Processing time: (?P<proctime>[0-9]*)s')

    def parse_line(self, line):
        try:
            errorLine = self.errorLineRE.match(line)
            if errorLine:
                errorBits = errorLine.groupdict()
                self.errors += int(errorBits['errors'])

            statusLine = self.statusLineRE.match(line)
            if statusLine:
                statusBits = statusLine.groupdict()
                self.dirtied += int(statusBits['dirtied'])
                self.changed += int(statusBits['updated']) + \
                    int(statusBits['deleted'])

                proctime = int(statusBits['proctime'])
                if proctime > self.maxProctime:
                    self.maxProctime = proctime

        except Exception, e:
            raise LogsterParsingException, "regmatch or contents failed with %s" % e

    def get_state(self, duration):
        return [
            MetricObject("sum_errors", self.errors, "Errors"),
            MetricObject("max_proctime", self.maxProctime,
                         "Max processing time"),
            # Don't send those for now, to preserve carbon bandwidth.
            #MetricObject("sum_dirtied", self.dirtied, "Dirtied"),
            #MetricObject("sum_changing", self.changed, "Changing"),
        ]
