#!/usr/bin/python

## Generate PDF report

from subprocess import call
import os
import re
import sys
import argparse
from fpdf import FPDF


class ReportGenerator():
  """
  Class for generating a pdf report for the mutation profile of a single sample
  """
  def __init__(self, reportTitle):
    self.reportTitle = reportTitle
    self.profile = {
      "protease": [],
      "reverse_transcriptase": [],
      "integrase": []
    }
    self.drugDict = {'3TC': 'lamivudine', 'ABC': 'abacavir', 'APV': 'amprenavir',
                     'ATV': 'atazanavir', 'BIC': 'bictegravir', 'COBI': 'cobicistat',
                     'd4T': 'stavudine', 'ddI': 'didanosine','DLV': 'delavirdine',
                     'DOR': 'doravirine', 'DRV': 'darunavir', 'DTG': 'dolutegravir',
                     'EFV': 'efavirenz', 'ETR': 'etravirine', 'EVG': 'elvitegravir',
                     'FPV': 'fosamprenavir', 'FTC': 'emtricitabine', 'IBA': 'ibalizumab',
                     'IDV': 'indinavir', 'LPV': 'lopinavir', 'MVC': 'maraviroc',
                     'NFV': 'nelfinavir', 'NVP': 'nevirapine', 'RAL': 'raltegravir',
                     'RPV': 'rilpivirine', 'RTV': 'ritonavir ', 'SQV': 'saquinavir',
                     'T20': 'enfuvirtide', 'TAF': 'tenofovir alafenamide',
                     'TDF': 'tenofovir disoproxil fumarate', 'TPV': 'tipranavir',
                     'ZDV': 'zidovudine', 'D4T': 'stavudine', 'AZT': 'zidovudine',
                     'DDI': 'didanosine', 'LMV': 'lamivudine'
    }

  def parseFile(self, filename):
    with open(filename, 'r') as infile:
      for line in infile:
        lineparts = line.split()
        if len(lineparts) > 0:
          drugClass = lineparts[0]
          if drugClass == "PR":
            self.profile['protease'].append(lineparts)
          elif drugClass == "NRTI" or drugClass == "NNRTI":
            self.profile['reverse_transcriptase'].append(lineparts)
          elif drugClass == "IN":
            self.profile['integrase'].append(lineparts)



  def generateReport(self):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="GENOTYPIC HIV-1 RESISTANCE PROFILE", ln=1, align="C")
    pdf.cell(200, 10, txt=self.reportTitle, ln=1, align="C")
    pdf.set_font("Arial", size=10)
    pdf.cell(100, 10, txt="DRUG RESISTANCE INTERPRETATION", ln=1)
    pdf.set_font("Arial", size=9)
    pdf.cell(150, 10, txt="1) Resistance to Reverse transcriptase Inhibitors (RTI)", ln=1)
    pdf.set_font("Arial", size=8)


    pdf.cell(150, 10, txt="Resistance to Nucleoside / Nucleotide RTI (NRTI)", ln=1)
    for resistance in self.profile['reverse_transcriptase']:
      drugAbbrv = resistance[1]
      if resistance[0] == "NRTI":
        drugName = ""
        if drugAbbrv in self.drugDict:
          drugName = self.drugDict[drugAbbrv] + " (" + drugAbbrv + ")"
        else:
          drugName = drugAbbrv
        res = resistance[3] + " " + resistance[4]
        pdf.cell(50, 5, txt=drugName)
        pdf.cell(50, 5, txt=res, ln=1)
    pdf.cell(150, 10, txt="Resistance to Non-Nucleoside RTI (NNRTI)", ln=1)
    for resistance in self.profile['reverse_transcriptase']:
      drugAbbrv = resistance[1]
      if resistance[0] == "NNRTI":
        drugName = ""
        if drugAbbrv in self.drugDict:
          drugName = self.drugDict[drugAbbrv] + " (" + drugAbbrv + ")"
        else:
          drugName = drugAbbrv
        res = resistance[3] + " " + resistance[4]
        pdf.cell(50, 5, txt=drugName)
        pdf.cell(50, 5, txt=res, ln=1)


    pdf.cell(10, 10, txt="", ln=1)
    pdf.set_font("Arial", size=9)
    pdf.cell(150, 10, txt="2) Resistance to Protease Inhibitors (PI)", ln=1)
    pdf.set_font("Arial", size=8)
    ## do the for each
    pdf.cell(10, 10, txt="", ln=1)
    pdf.set_font("Arial", size=9)
    pdf.cell(150, 10, txt="3) Resistance to Integrase inhibitors (II)", ln=1)
    pdf.set_font("Arial", size=8)
    ## do the for each
    pdf.cell(10, 10, txt="", ln=1)
    pdf.output("simple_demo.pdf")

if __name__ == "__main__":
  reporter = ReportGenerator('SAMPLE1')
  reporter.parseFile('one_profile.txt')
  reporter.generateReport()
  #print(reporter.profile)





