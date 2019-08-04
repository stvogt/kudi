#! /usr/bin/python

import sys, os
import kudi.operations as op
import kudi.singlePoint as sp
from optparse import OptionParser

rev = sys.argv[1]
forw = sys.argv[2]

irc_rev_lines = op.read_lines(rev)
irc_forw_lines = op.read_lines(forw)

f = open('output.log', 'w')

for line in irc_rev_lines:
  f.write(line)
for line in irc_forw_lines:
  f.write(line)
f.close()
