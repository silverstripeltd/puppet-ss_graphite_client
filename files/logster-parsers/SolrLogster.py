# File managed by puppet
###
# SS logster parser to process Graphite based apache log
###
# sudo logster --dry-run --output=graphite --graphite-host=localhost:2003 SolrLogster /sites/solrproxy/logs/apache.access.log
###

import time
import re
import math
import functools
import socket

from logster.logster_helper import MetricObject, LogsterParser
from logster.logster_helper import LogsterParsingException


class SolrLogster(LogsterParser):

    def __init__(self, option_string=None):
        '''Initialize any data structures or variables needed for keeping track
        of the tasty bits we find in the log we are parsing.'''
        self.solrstats = {}

        # Regular expression for matching lines we are interested in, and capturing
        # fields from the line (each value split by space).

        self.reg = re.compile(
            '^(\S+) \S+ (?P<req_env>\S+) \[([^\]]+)\] "(?P<req_type>[A-Z]+)(?P<req_string>[^"]*)" (?P<status_code>\d+) (?P<req_size>\d+) "[^"]*" "\S+" (?P<req_time>\d+)')

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
                req_env = str(linebits['req_env'])

                req_string = str(linebits['req_string'])

                # Set up new key if not exist
                if req_env not in self.solrstats:
                    self.solrstats[req_env] = {
                        'select_per_min': 0,
                        'select_time_total': 0,
                        'select_time_max': 0,
                        'select_time_min': 9999999999,
                        'update_per_min': 0,
                        'update_time_total': 0,
                        'update_time_max': 0,
                        'update_time_min': 9999999999,
                        'http_2xx': 0,
                        'http_4xx': 0,
                        'http_5xx': 0,
                    }

                # SOLR Index Update
                myre = '^\s*\/v4\/(.*)\/update.*'

                if re.search(myre, req_string):
                    # Count update queries and SOLR Index
                    self.solrstats[req_env]["update_per_min"] += 1
                    self.solrstats[req_env]["update_time_total"] = self.solrstats[req_env]["update_time_total"] + req_time

                    if req_time > self.solrstats[req_env]["update_time_max"]:
                        self.solrstats[req_env]["update_time_max"] = req_time
                    if req_time < self.solrstats[req_env]["update_time_min"]:
                        self.solrstats[req_env]["update_time_min"] = req_time

                # SOLR Index Select
                myre = '^\s*\/v4\/(.*)\/select.*'

                if re.search(myre, req_string):
                    # Count update queries and SOLR Index
                    self.solrstats[req_env]["select_per_min"] += 1
                    self.solrstats[req_env]["select_time_total"] = self.solrstats[req_env]["select_time_total"] + req_time

                    if req_time > self.solrstats[req_env]["select_time_max"]:
                        self.solrstats[req_env]["select_time_max"] = req_time
                    if req_time < self.solrstats[req_env]["update_time_min"]:
                        self.solrstats[req_env]["select_time_min"] = req_time

                # Process request status
                if (status >= 200 and status < 300):
                    self.solrstats[req_env]["http_2xx"] += 1
                elif (status >= 400 and status < 500):
                    self.solrstats[req_env]["http_4xx"] += 1
                elif (status >= 500 and status < 600):
                    self.solrstats[req_env]["http_5xx"] += 1

            else:
                raise LogsterParsingException, "data format looks bad (no space)"

        except Exception, e:
            raise LogsterParsingException, "regmatch or contents failed with %s" % e

    def get_state(self, duration):
        '''Run any necessary calculations on the data collected from the logs
        and return a list of metric objects.'''
        self.duration = duration
        metrics = []

        for key, value in self.solrstats.iteritems():

            if value["select_per_min"] > 0:
                metrics.append(MetricObject(
                    key + ".select_time_avg", (value["select_time_total"] / value["select_per_min"])))
                metrics.append(MetricObject(
                    key + ".select_per_min",  (value["select_per_min"])))
                metrics.append(MetricObject(
                    key + ".select_time_max", (value["select_time_max"])))
                metrics.append(MetricObject(
                    key + ".select_time_min", (value["select_time_min"])))

            if value["update_per_min"] > 0:
                metrics.append(MetricObject(
                    key + ".update_time_avg", (value["update_time_total"] / value["update_per_min"])))
                metrics.append(MetricObject(
                    key + ".update_per_min",  (value["update_per_min"])))
                metrics.append(MetricObject(
                    key + ".update_time_max", (value["update_time_max"])))
                metrics.append(MetricObject(
                    key + ".update_time_min", (value["update_time_min"])))

            metrics.append(MetricObject(
                key + ".http_2xx", (value["http_2xx"])))
            metrics.append(MetricObject(
                key + ".http_4xx", (value["http_4xx"])))
            metrics.append(MetricObject(
                key + ".http_5xx", (value["http_5xx"])))

        return metrics

    def percentile(self, N, percent, key=lambda x: x):
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
