# -*- coding: utf-8 -*-

# Copyright (C) 2009-2010 Max Arnold <lwarxx@gmail.com>.
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.

# 3. Neither the name of copyright holder nor the names of contributors may
# be used to endorse or promote products derived from this software without
# specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""Python module for programmatic event scheduling using cron-like syntax with
seconds precision.

get_matched_jobs() method should be called periodically and will return list of
tasks to execute if their time has arrived. Latency can be specified if strict
calling periodicity (at least once per second) can not be guaranteed. Protection
against time jitter also implemented.

Each job is described using extended cron-like syntax with six fields:

Field            Allowed values
------------     --------------
Second           0 - 59
Minute           0 - 59
Hour             0 - 23
Day of month     1 - 31
Month            1 - 12 (jan - dec)
Day of week      1 - 7  (mon - sun)

Fields are separated with space and can contain ranges, comma separated lists
or asterisk symbol (*) which is expanded as full range. Ranges also can be used
with step value, for example 0-59/10 or */2. For more examples refer to crontab
manual page.

Cron record is matched when all fields match current date/time (logical AND).

Job itself is specified using arbitrary python object or data structure. Its
interpretation and execution is up to calling program.
"""

import re
import time
from datetime import datetime
from operator import itemgetter

class pycron(object):
    """Main cron class
    """

    # enums are declared as lists in order to use .index method
    month_enum = ['jan', 'feb', 'mar', 'apr', 'may', 'jun',
                              'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    wday_enum = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    f_ranges = [
            { 'name': 'Second',        'min': 0, 'max': 59 },
            { 'name': 'Minute',        'min': 0, 'max': 59 },
            { 'name': 'Hour',          'min': 0, 'max': 23 },
            { 'name': 'Day of month',  'min': 1, 'max': 31 },
            { 'name': 'Month',         'min': 1, 'max': 12, 'enum': month_enum },
            { 'name': 'Day of week',   'min': 1, 'max': 7,  'enum': wday_enum } # TODO: 0 - sunday
    ]

    cron_split_re = re.compile('(?<![/,\-\s])\s+(?![/,\-\s])')
    cron_int_re = re.compile('^0*\d{1,2}$')

    def __init__(self, latency=10):
        self.tlast = None
        self.latency = abs(int(latency))
        self.jobs = []
        self.jobrecs = {}
        self.taskhist = set()

    def add_job(self, cronrecord, job, jobinfo=""):
        """Add cron job

        cronrecord - string in form of 'SS MM HH DD MO DW', with crontab-like syntax
        job - job identifier, string or callable (calling is not performed)
        jobinfo - optional string (for debugging purposes)

        Return False if error, True if job already exists, total job count if success
        """

        j = pycron.parse_record(cronrecord)
        if j is False: return False
        j = (j, job)
        if j in self.jobs: return True
        self.jobs.append(j)
        self.jobrecs[j] = (cronrecord, jobinfo)

        return len(self.jobs)

    def print_jobs(self):
        for j in self.jobs:
            print self.jobrecs[j]

    def del_job(self):
        # Do something with task history!
        pass

    def wayback(self, jobs=None, wbtime=86400, tnow=None, stopfirst=True):
        """Look back in time (wbtime seconds maximum) and find last matching jobs

        Useful right after instantiation if previous task should be executed again.
        Does not affect internal state
        """
        wbtasks = set()
        if tnow is None: tnow = int(time.mktime(datetime.today().timetuple()))
        if jobs == None: jobs = self.jobs

        if stopfirst:
            for ts in xrange(tnow, tnow-wbtime-1, -1):
                for j in jobs:
                    if pycron.match_job(j[0], ts):
                        return tuple((j[1],))
            return tuple()
        else:
            for j in jobs:
                for ts in xrange(tnow, tnow-wbtime-1, -1):
                    if pycron.match_job(j[0], ts):
                        wbtasks.add((j[1], ts))
                        break

        return tuple([t[0] for t in sorted(wbtasks, key=itemgetter(1), reverse=True)])

    def get_matched_jobs(self, tnow=None):
        """Return tuple of matched task identifiers
        """
        tasks = set()
        if tnow is None: tnow = int(time.mktime(datetime.today().timetuple()))
        if self.tlast is None:
            self.tlast = tnow-1
            firstrun = True
        else:
            firstrun = False
        tdiff = tnow-self.tlast
        if tdiff == 0:
            # time not changed
            return tuple(tasks)
        elif firstrun or abs(tdiff) > self.latency:
        # time jumped back or forward too much
            self.clear_taskhist()
            for j in self.jobs:
                th = (j[0], j[1], tnow)
                if pycron.match_job(j[0], tnow):
                    self.taskhist.add(th)
                    tasks.add((j[1], tnow))
        else:
            # time jumped back or forward, but still within latency window
            t1 = min(self.tlast, tnow)
            t2 = max(self.tlast, tnow)
            for ts in xrange(t1, t2+1):
                for j in self.jobs:
                    th = (j[0], j[1], ts)
                    if pycron.match_job(j[0], ts) and th not in self.taskhist:
                        self.taskhist.add(th)
                        tasks.add((j[1], ts))
            self.purge_taskhist(tnow)

        self.tlast = tnow
        return tuple([t[0] for t in sorted(tasks, key=itemgetter(1))])

    def clear_taskhist(self):
        self.taskhist = set()

    def purge_taskhist(self, tnow=None):
        """Iterate over task history (previously matched jobs) and drop everything
        not within latency window
        """
        if tnow is None: tnow = int(time.mktime(datetime.today().timetuple()))
        thist = self.taskhist
        # tuple is necessary since we are modifying set in place:
        for th in tuple(self.taskhist):
            if th[2] < tnow - self.latency:
                self.taskhist.remove(th)

    @staticmethod
    def parse_fnum(nfield, num):
        """Parse and validate field value (also accepts weekday/month enums)

        nfield - field number (0-5)
        num - field value (string)

        Return integer value or False if error
        """
        if pycron.cron_int_re.match(num):
            n = int(num)
            if pycron.f_ranges[nfield]['min'] <= n <= pycron.f_ranges[nfield]['max']: return n
        elif 'enum' in pycron.f_ranges[nfield] and num in pycron.f_ranges[nfield]['enum']:
            return pycron.f_ranges[nfield]['enum'].index(num)+pycron.f_ranges[nfield]['min']
        return False

    @staticmethod
    def parse_step(step):
        """Parse and validate step value

        step - step value (string)

        Return integer value or False if error
        """
        if pycron.cron_int_re.match(step):
            n = int(step)
            if n > 0: return n
        return False

    @staticmethod
    def parse_range(nfield, frange):
        """Parse and validate range/step value

        nfield - field number (0-5)
        frange - field value

        Return tuple (range_start, range_end, step) or False if error
        """
        # split range into value and step
        frange = frange.split('/')
        if len(frange) > 2:
            # too many "/" symbols
            return False

        # split value into range start and end
        rparts = frange[0].split('-')
        if len(rparts) > 2:
            # too many "-" symbols
            return False

        # parse step
        if len(frange) == 2:
            step = pycron.parse_step(frange[1])
            if step is False: return False
        else:
            # default step value
            step = 1

        # parse range
        if len(rparts) == 2:
            r1 = pycron.parse_fnum(nfield, rparts[0])
            r2 = pycron.parse_fnum(nfield, rparts[1])
            if r1 is False or r2 is False or r1 > r2: return False
        else:
            if rparts[0] == '*':
                r1 = pycron.f_ranges[nfield]['min']
                r2 = pycron.f_ranges[nfield]['max']
            else:
                r1 = pycron.parse_fnum(nfield, rparts[0])
                if r1 is False: return False
                r2 = r1

        return (r1, r2, step)

    @staticmethod
    def parse_field(nfield, field):
        """Parse and validate field

        nfield - field number (0-5)
        field - field value

        Return tuple with unrolled range values or False if error
        """
        # remove all whitespaces
        field = ''.join(field.split())
        rangeset = []
        for frange in field.split(','):
            r = pycron.parse_range(nfield, frange)
            if r is False: return False

            for i in xrange(r[0], r[1]+1, r[2]): # TODO: optimize
                # uroll all range values
                rangeset.append(i)

        # return only unique values
        return tuple(sorted(set(rangeset)))

    @staticmethod
    def parse_record(record):
        """Parse and validate cron record

        Return six unrolled ranges as a tuple, or False if error
        """
        # split record into six fields
        fields = pycron.cron_split_re.split(record.strip())
        if len(fields) != 6: return False

        # parse and validate each field and build unrolled tuple
        rec = []
        for nfield, field in enumerate(fields):
            f = pycron.parse_field(nfield, field)
            if f is False: return False
            rec.append(f)

        return tuple(rec)

    @staticmethod
    def match_job(r, ts):
        """Check if parsed cron record equals timestamp
        """
        t = datetime.fromtimestamp(ts)
        if t.second in r[0] and t.minute in r[1] \
                and t.hour in r[2] and t.day in r[3] \
                and t.month in r[4] and t.isoweekday() in r[5]:
            return True
        return False

if __name__ == '__main__':
    c = pycron()
    c.add_job('*/5 * * * * *', 'job_id1', 'job_info1')
    c.add_job('* * 0 * * *', 'job_id2', 'job_info2')
    print c.wayback()

    while True:
        time.sleep(1)
        print datetime.today(), c.get_matched_jobs()
