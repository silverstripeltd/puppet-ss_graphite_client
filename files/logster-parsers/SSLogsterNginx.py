### File managed by puppet
###
###  SS logster parser to process Graphite based nginx log
###  
###  sudo ./logster --dry-run --output=ganglia SSLogsterNginx /var/log/httpd/access_log
###

import time
import re

from logster.logster_helper import MetricObject, LogsterParser
from logster.logster_helper import LogsterParsingException

class SSLogsterNginx(LogsterParser):

    def __init__(self, option_string=None):
        '''Initialize any data structures or variables needed for keeping track
        of the tasty bits we find in the log we are parsing.'''

        self.reqcnt = 0
        self.http_1xx = 0
        self.http_2xx = 0
        self.http_3xx = 0
        self.http_4xx = 0
        self.http_429 = 0
        self.http_5xx = 0
        self.http_outage = 0
        self.getreq = 0
        self.postreq = 0

        # Regular expression for matching lines we are interested in
        self.reg = re.compile('^(\S+) \S+ \S+ \[([^\]]+)\] "(?P<req_type>[A-Z]+)[^"]*" (?P<status_code>\d+) (?P<req_size>\d+) "[^"]*" "(?P<req_ua>[^"]*)"')

    def parse_line(self, line):
        '''This function should digest the contents of one line at a time, updating
        object's state variables. Takes a single argument, the line to be parsed.'''

        try:
            # Apply regular expression to each line and extract interesting bits.
            regMatch = self.reg.match(line)

            if regMatch:
                linebits = regMatch.groupdict()

                req_size = int(linebits['req_size'])
                status = int(linebits['status_code'])
                req_type = str(linebits['req_type'])

                # Always count the request (doesn't make sense to check the size, as e.g. 304 will be 0-sized, but should still be counted.
                self.reqcnt += 1

                # Process request status
                if (status < 200):
                    self.http_1xx += 1
                elif (status < 300):
                    self.http_2xx += 1
                elif (status < 400):
                    self.http_3xx += 1
                elif (status < 500):
                    self.http_4xx += 1
                else:
                    self.http_5xx += 1

                if (status == 502 or status == 503 or status == 504):
                    self.http_outage += 1

                if (status == 429):
                    self.http_429 += 1

                # Porcess request types
                if req_type == "GET":
                    self.getreq += 1
                elif req_type == "POST":
                    self.postreq += 1

            else:
                raise LogsterParsingException, "data format looks bad (no space)"

        except Exception, e:
            raise LogsterParsingException, "regmatch or contents failed with %s" % e

    def get_state(self, duration):
        '''Run any necessary calculations on the data collected from the logs
        and return a list of metric objects.'''
        self.duration = duration

        # Return a list of metrics objects
        metrics = [
            MetricObject("request.get_count", ((self.getreq  / self.duration) * 60), "Responses per min"),
            MetricObject("request.post_count", ((self.postreq / self.duration) * 60), "Responses per min"),
            MetricObject("request.req_per_min", ((self.reqcnt / self.duration) * 60), "Responses per min"),

            MetricObject("status.http_1xx", ((self.http_1xx / self.duration) * 60), "Responses per min"),
            MetricObject("status.http_2xx", ((self.http_2xx / self.duration) * 60), "Responses per min"),
            MetricObject("status.http_3xx", ((self.http_3xx / self.duration) * 60), "Responses per min"),
            MetricObject("status.http_4xx", ((self.http_4xx / self.duration) * 60), "Responses per min"),
            MetricObject("status.http_5xx", ((self.http_5xx / self.duration) * 60), "Responses per min"),

            MetricObject("status.explicit.http_429", ((self.http_429 / self.duration) * 60), "Responses per min"),
            MetricObject("status.explicit.http_outage", ((self.http_outage / self.duration) * 60), "Responses per min"),
        ]

        return metrics
