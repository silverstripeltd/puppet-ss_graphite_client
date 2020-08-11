### File managed by puppet
###
###  SS logster parser to process Graphite based apache log
###  
###  sudo ./logster --dry-run --output=ganglia SSLogster /var/log/httpd/access_log
###

import time
import re
import math
import functools
import socket

from logster.logster_helper import MetricObject, LogsterParser
from logster.logster_helper import LogsterParsingException

class SSLogster(LogsterParser):

    def __init__(self, option_string=None):
        '''Initialize any data structures or variables needed for keeping track
        of the tasty bits we find in the log we are parsing.'''
        self.reqtime_high = 0
        self.reqsize_high = 0
        self.reqtime_low = 0
        self.reqsize_low = 0

        self.reqsize_tot = 0
        self.reqtime_tot = 0
        self.reqcnt = 0

        self.reqtime_list = []
        self.reqsize_list = []

        self.http_1xx = 0
        self.http_2xx = 0
        self.http_3xx = 0
        self.http_4xx = 0
        self.http_5xx = 0

        self.getreq = 0
        self.postreq = 0
        self.dynreq = 0

        self.uacombined = {}
        self.uabrowser = {}
        self.uaos = {}

        # Regular expression for matching lines we are interested in, and capturing
        # fields from the line (each value split by space).

        self.reg = re.compile('^(\S+) \S+ \S+ \[([^\]]+)\] "(?P<req_type>[A-Z]+)(?P<req_string>[^"]*)" (?P<status_code>\d+) (?P<req_size>\d+) "[^"]*" "(?P<req_ua>[^"]*)" (?P<req_time>\d+)')



    def parse_line(self, line):
        '''This function should digest the contents of one line at a time, updating
        object's state variables. Takes a single argument, the line to be parsed.'''

        try:
            # Apply regular expression to each line and extract interesting bits.
            regMatch = self.reg.match(line)

            if regMatch:
                linebits = regMatch.groupdict()

                req_size = int(linebits['req_size'])
                req_time = int(linebits['req_time'])

                status = int(linebits['status_code'])

                req_type = str(linebits['req_type'])
                req_ua   = str(linebits['req_ua'])

                req_string = str(linebits['req_string'])

                # Process request string to determine dynamic request
                if (req_string.find("/assets/") == -1) and (req_string.find("/themes/") == -1) and (req_string.find(".css") == -1) and (req_string.find(".js") == -1) and (req_string.find(".jpg") == -1) and (req_string.find(".gif") == -1) and (req_string.find(".png") == -1):
                    self.dynreq += 1

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

                # Process request time and size
                if (req_size != 0) and (req_time != 0):
                    
                    if req_size > self.reqsize_high:
                        self.reqsize_high = req_size

                    if req_time > self.reqtime_high:
                        self.reqtime_high = req_time

                    if (req_size < self.reqsize_low) or (self.reqsize_low == 0):
                        self.reqsize_low = req_size

                    if (req_time < self.reqtime_low) or (self.reqtime_low == 0):
                        self.reqtime_low = req_time

                    self.reqcnt += 1
                    self.reqsize_tot = self.reqsize_tot + req_size
                    self.reqtime_tot = self.reqtime_tot + req_time
                    self.reqtime_list.append(req_time)
                    self.reqsize_list.append(req_size)

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

        if self.reqcnt > 0:
            reqtime_avg = (self.reqtime_tot / self.reqcnt)
            reqsize_avg = (self.reqsize_tot / self.reqcnt)
        else:
            reqtime_avg = 0
            reqsize_avg = 0

        # Return a list of metrics objects
        metrics = [
            MetricObject("request.time_avg",  (reqtime_avg / 1000), "ms"),
            MetricObject("request.time_high", (self.reqtime_high / 1000), "ms"),
            MetricObject("request.time_low",  (self.reqtime_low / 1000), "ms"),
            MetricObject("request.time_95",   (self.percentile(self.reqtime_list, 0.95) / 1000), "ms"),
            MetricObject("request.time_05",   (self.percentile(self.reqtime_list, 0.05) / 1000), "ms"),

            MetricObject("request.size_avg",  (reqsize_avg), "B"),
            MetricObject("request.size_high", (self.reqsize_high), "B"),
            MetricObject("request.size_low",  (self.reqsize_low), "B"),
            MetricObject("request.size_95",   (self.percentile(self.reqsize_list, 0.95)), "B"),
            MetricObject("request.size_05",   (self.percentile(self.reqsize_list, 0.05)), "B"),
            MetricObject("request.size_total",  (self.reqsize_tot), "B"),

            MetricObject("request.get_count", ((self.getreq  / self.duration) * 60), "Responses per min"),
            MetricObject("request.post_count", ((self.postreq / self.duration) * 60), "Responses per min"),
            MetricObject("request.dyn_count", self.dynreq, "requests"),
            MetricObject("request.req_per_min", ((self.reqcnt / self.duration) * 60), "Responses per min"),

            MetricObject("status.http_1xx", ((self.http_1xx / self.duration) * 60), "Responses per min"),
            MetricObject("status.http_2xx", ((self.http_2xx / self.duration) * 60), "Responses per min"),
            MetricObject("status.http_3xx", ((self.http_3xx / self.duration) * 60), "Responses per min"),
            MetricObject("status.http_4xx", ((self.http_4xx / self.duration) * 60), "Responses per min"),
            MetricObject("status.http_5xx", ((self.http_5xx / self.duration) * 60), "Responses per min"),
        ]

        return metrics



    def percentile(self, N, percent, key=lambda x:x):
        """
        Find the percentile of a list of values.

        @parameter N - is a list of values. Note N MUST BE already sorted.
        @parameter percent - a float value from 0.0 to 1.0.
        @parameter key - optional key function to compute value from each element of N.

        @return - the percentile of the values
        """

        if not N:
            return 0

        N.sort()

        k = (len(N)-1) * percent
        f = math.floor(k)
        c = math.ceil(k)

        if f == c:
            return key(N[int(k)])

        d0 = key(N[int(f)]) * (c-k)
        d1 = key(N[int(c)]) * (k-f)

        return d0+d1
