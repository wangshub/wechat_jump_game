# -*- coding: utf-8 -*-
import sys

if sys.version_info.major != 3:
    class UnicodeStreamFilter:

        def __init__(self, target):
            self.target = target
            self.encoding = 'utf-8'
            self.errors = 'replace'
            self.encode_to = self.target.encoding


    def write(self, s):
        if type(s) == str:
            s = s.decode("utf-8")
        s = s.encode(self.encode_to, self.errors).decode(self.encode_to)
        self.target.write(s)


    if sys.stdout.encoding == 'cp936':
        sys.stdout = UnicodeStreamFilter(sys.stdout)
else:
    pass
