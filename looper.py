#!/usr/bin/python

import glob
from ReportGenerator import ReportGenerator

files = glob.glob('output/*.txt')
for file in files:
  reporter = ReportGenerator('SAMPLE1', file)
  reporter.parseFile(reporter.profileFile)
  reporter.generateReport()
