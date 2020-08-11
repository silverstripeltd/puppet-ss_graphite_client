import time
import re

from logster.logster_helper import MetricObject, LogsterParser
from logster.logster_helper import LogsterParsingException


class SSLogsterNginxErrors(LogsterParser):

    def __init__(self, option_string=None):
        '''Initialize any data structures or variables needed for keeping track
        of the tasty bits we find in the log we are parsing.'''
        self.errors = 0
        self.req_limit_errors = 0

        # Regular expression for matching lines we are interested in, and capturing
        # fields from the line (in this case, http_status_code).
        self.reg_req_limit = re.compile('.*limiting requests.*')

    def parse_line(self, line):
        '''This function should digest the contents of one line at a time, updating
        object's state variables. Takes a single argument, the line to be parsed.'''

        self.errors += 1

        # Apply regular expression to each line and extract interesting bits.
        regMatch = self.reg_req_limit.match(line)

        if regMatch:
            self.req_limit_errors += 1

    def get_state(self, duration):
        '''Run any necessary calculations on the data collected from the logs
        and return a list of metric objects.'''
        self.duration = duration

        # Return a list of metrics objects
        return [
            MetricObject("errors.errors", (self.errors /
                                           self.duration) * 60, "Errors per minute"),
            MetricObject("errors.req-limit-errors", (self.req_limit_errors /
                                                     self.duration) * 60, "Request limit errors per minute"),
        ]
