#!/usr/bin/python

## Generate PDF report

from subprocess import call
import os
import re
import sys
import argparse
from fpdf import FPDF
import xlsxwriter


class ReportGenerator():
  """
  Class for generating a pdf report for the mutation profile of a single sample
  """
  def __init__(self, reportTitle, profileFile):
    self.reportTitle = reportTitle
    self.profile = {
      "protease": [],
      "reverse_transcriptase": [],
      "integrase": []
    }
    self.barcode = ""
    self.profileFile = profileFile
    self.brandDict = {'ABC': "Ziagenu\u00AE", 'ddI': "Videx\u00AE", 'FTC': "Emtriva\u00AE",
                      '3TC': "Epivir\u00AE", 'd4T': "Zerit\u00AE", 'AZT': "Retrovir\u00AE",
                      'TDF': "Viread\u00AE", 'EFV': "Sustiva\u00AE", 'ETR': "Intelence\u00AE", 'NVP': "Viramune\u00AE", 'RPV': "Edurant\u00AE",
                      'ATV': "Reyataz\u00AE", 'FPV': "Lexiva\u00AE", 'DRV': "Prezista\u00AE",
                      'IDV': "Crixivan\u00AE", 'LPV': "Kaletra\u00AE", 'NFV': "Viracept\u00AE", 'SQV': "Invirase\u00AE", 'TPV': "Aptivus\u00AE",
                      'RAL': "Isentress\u00AE", 'DTG': "Tivicay\u00AE",
                      'DDI': "Videx\u00AE", 'D4T': "Zerit\u00AE", 'LMV': "Epivir\u00AE",
                      'DOR': "Pifeltro\u00AE"}
    self.drugDict = {'3TC': 'Lamivudine', 'ABC': 'Abacavir', 'APV': 'Amprenavir',
                     'ATV': 'Atazanavir', 'BIC': 'Bictegravir', 'COBI': 'Cobicistat',
                     'd4T': 'Stavudine', 'ddI': 'Didanosine','DLV': 'Delavirdine',
                     'DOR': 'Doravirine', 'DRV': 'Darunavir', 'DTG': 'Dolutegravir',
                     'EFV': 'Efavirenz', 'ETR': 'Etravirine', 'EVG': 'Elvitegravir',
                     'FPV': 'Fosamprenavir', 'FTC': 'Emtricitabine', 'IBA': 'Ibalizumab',
                     'IDV': 'Indinavir', 'LPV': 'Lopinavir', 'MVC': 'Maraviroc',
                     'NFV': 'Nelfinavir', 'NVP': 'Nevirapine', 'RAL': 'Raltegravir',
                     'RPV': 'Rilpivirine', 'RTV': 'Ritonavir ', 'SQV': 'Saquinavir',
                     'T20': 'Enfuvirtide', 'TAF': 'Tenofovir alafenamide',
                     'TDF': 'Tenofovir disoproxil fumarate', 'TPV': 'Tipranavir',
                     'ZDV': 'Zidovudine', 'D4T': 'Stavudine', 'AZT': 'Zidovudine',
                     'DDI': 'Didanosine', 'LMV': 'Lamivudine'}

    self.fixed = { 'NRTI': {'ABC': 'Abacavir', 'DDI': 'Didanosine','ddI': 'Didanosine',
                  'FTC': 'Emtricitabine', '3TC': 'Lamivudine', 'D4T': 'Stavudine', 'LMV': 'Lamivudine',
                  'd4T': 'Stavudine', 'AZT': 'Zidovudine', 'TDF':'Tenofovir disoproxil fumarate'},
                  'NNRTI': {'EFV': 'Efavirenz', 'ETR': 'Etravirine', 'NVP': 'Nevirapine',
                            'RPV': 'Rilpivirine'},
                  'PI': {'ATV': 'Atazanavir', 'FPV': 'Fosamprenavir', 'DRV': 'Darunavir',
                     'IDV': 'Indinavir', 'LPV': 'Lopinavir', 'NFV': 'Nelfinavir',
                     'SQV': 'Saquinavir', 'TPV': 'Tipranavir'},
                  'IN': {'RAL': 'Raltegravir', 'EVG': 'Elvitegravir', 'DTG': 'Dolutegravir'} }

  def parseFile(self, filename):
    with open(filename, 'r') as infile:
      for line in infile:
        lineparts = line.split()
        if len(lineparts) > 0:
          drugClass = lineparts[0]
          if lineparts[0] == 'barcode:':
            self.barcode = lineparts[1]

          if drugClass == "PI":
            self.profile['protease'].append(lineparts)
          elif drugClass == "NRTI" or drugClass == "NNRTI":
            self.profile['reverse_transcriptase'].append(lineparts)
          elif drugClass == "INSTI":
            self.profile['integrase'].append(lineparts)

  def drugName(self, drugAbbrv):
    drugName = ""
    if drugAbbrv in self.drugDict:
      drugName = self.drugDict[drugAbbrv] + " (" + drugAbbrv + ")"
    else:
      drugName = drugAbbrv
    return drugName

  def generatePDFReport(self):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.image('CFAR-logo.jpg', x = 5, y = 5, h = 36, w = 30)
    pdf.image('jcrc_logo-1.jpg', x = 170, y = 5, h = 36, w = 30)
    pdf.cell(200, 10, txt="GENOTYPIC HIV-1 RESISTANCE PROFILE", ln=1, align="C")
    pdf.cell(200, 10, txt=self.reportTitle, ln=1, align="C")
    pdf.set_font("Arial", size=10)
    pdf.cell(100, 10, txt="DRUG RESISTANCE INTERPRETATION", ln=1)
    pdf.set_font("Arial", style='B', size=9)
    pdf.cell(150, 10, txt="1) Resistance to Reverse transcriptase Inhibitors (RTI)", ln=1)
    pdf.set_font("Arial", style='B', size=8)
    pdf.cell(5, 5)
    pdf.cell(150, 10, txt="Resistance to Nucleoside / Nucleotide RTI (NRTI)", ln=1)
    pdf.set_font("Arial", size=8)

    for resistance in self.profile['reverse_transcriptase']:
      drugAbbrv = resistance[1]
      if resistance[0] == "NRTI":
        drugName = ""
        if drugAbbrv in self.drugDict:
          drugName = self.drugDict[drugAbbrv] + " (" + drugAbbrv + ")"
        else:
          drugName = drugAbbrv
        res = ""
        if resistance[3] == "Susceptible":
          res = resistance[3]
        else:
          res = resistance[3] + " " + resistance[4]
        pdf.cell(5, 5)
        pdf.cell(50, 5, txt=drugName)
        pdf.cell(50, 5, txt=res, ln=1)
    pdf.set_font("Arial", style='B', size=8)
    pdf.cell(5, 5)
    pdf.cell(150, 10, txt="Resistance to Non-Nucleoside RTI (NNRTI)", ln=1)
    pdf.set_font("Arial", size=8)

    for resistance in self.profile['reverse_transcriptase']:
      drugAbbrv = resistance[1]
      if resistance[0] == "NNRTI":
        drugName = ""
        if drugAbbrv in self.drugDict:
          drugName = self.drugDict[drugAbbrv] + " (" + drugAbbrv + ")"
        else:
          drugName = drugAbbrv
        res = ""
        if resistance[3] == "Susceptible":
          res = resistance[3]
        else:
          res = resistance[3] + " " + resistance[4]
        pdf.cell(5, 5)
        pdf.cell(50, 5, txt=drugName)
        pdf.cell(50, 5, txt=res, ln=1)
    if len(self.profile['reverse_transcriptase']) == 0:
      pdf.cell(5, 5)
      pdf.cell(50, 5, txt="Reverse transcriptase mutations not detected")

    pdf.cell(10, 10, txt="", ln=1)
    pdf.set_font("Arial", style='B', size=9)
    pdf.cell(150, 10, txt="2) Resistance to Protease Inhibitors (PI)", ln=1)
    pdf.set_font("Arial", size=8)
    ## do the for each
    for resistance in self.profile['protease']:
      drugName = self.drugName(resistance[1])
      res = ""
      if resistance[3] == "Susceptible":
        res = resistance[3]
      else:
        res = resistance[3] + " " + resistance[4]
      pdf.cell(5, 5)
      pdf.cell(50, 5, txt=drugName)
      pdf.cell(50, 5, txt=res, ln=1)
    if len(self.profile['protease']) == 0:
      pdf.cell(5, 5)
      pdf.cell(50, 5, txt="Protease mutations not detected")
    pdf.cell(10, 10, txt="", ln=1)
    pdf.set_font("Arial", style='B', size=9)
    pdf.cell(150, 10, txt="3) Resistance to Integrase inhibitors (II)", ln=1)
    pdf.set_font("Arial", size=8)
    ## do the for each
    if len(self.profile['integrase']) == 0:
      pdf.cell(5, 5)
      pdf.cell(50, 5, txt="Integrase mutations not detected")
    for resistance in self.profile['integrase']:
      drugName = self.drugName(resistance[1])
      res = ""
      if resistance[3] == "Susceptible":
        res = resistance[3]
      else:
        res = resistance[3] + " " + resistance[4]
      pdf.cell(5, 5)
      pdf.cell(50, 5, txt=drugName)
      pdf.cell(50, 5, txt=res, ln=1)
    pdf.cell(10, 10, txt="", ln=1)
    pdf.output("pdfs/" + self.barcode + ".pdf")

  def generateExcelReport(self):
    workbook = xlsxwriter.Workbook('demo.xlsx')
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({'bold': True})
    brand_header = workbook.add_format({'font_color': 'blue', 'bold': True})
    report = workbook.add_format({'font_color': 'red', 'bold': True})
    metadata_header = workbook.add_format({'bg_color': '#F1C096', 'bold': True})
    green = workbook.add_format({'bg_color': '#397d22', 'font_color': '#FFFFFF'})
    grey = workbook.add_format({'bg_color': '#c9d2d6'})
    blue = workbook.add_format({'bg_color': '#2e0cb3', 'font_color': '#FFFFFF'})
    red = workbook.add_format({'bg_color': '#8f1507', 'font_color': '#FFFFFF'})
    main_table_header = workbook.add_format({'bg_color': '#000000', 'font_color': '#FFFFFF',
                                             'bold': True, 'center_across': True})
    psub_header = workbook.add_format({'font_color': 'purple', 'center_across': True, 'font_size': 8})
    # set columns widths
    worksheet.set_column('A:A', 6.17)  # pixels to *width* unitss
    worksheet.set_column('B:B', 4)
    worksheet.set_column('C:C', 22.6)
    worksheet.set_column('D:D', 9.33)
    worksheet.set_column('E:E', 1)
    worksheet.set_column('F:F', 24.5)
    worksheet.set_column('G:G', 0.7)
    worksheet.set_column('H:H', 12.5)
    worksheet.set_column('I:I', 9.17)
    worksheet.set_column('J:J', 7)
    worksheet.set_column('K:K', 8.5)
    worksheet.set_column('L:L', 0.7)
    worksheet.set_column('M:M', 7)
    worksheet.set_column('N:N', 11.5)


    worksheet.write('A1', 'JOINT CLINICAL RESEARCH CENTER', brand_header)
    worksheet.write('A2', 'CWRU/CFAR LABORATORY', brand_header)
    worksheet.write('A4', 'HIV-1 DRUG RESISTANCE REPORT', report)
    worksheet.write_row("A6:I6", ['Patient / Sample Information','','','','','','','',''], metadata_header)
    #worksheet.write('A6', 'Patient / Sample Information', bold)
    worksheet.write('A7', 'MRN:', bold)
    worksheet.write('A8', 'Name:', bold)
    worksheet.write('A9', 'DOB:', bold)
    worksheet.write('A10', 'Gender:', bold)
    worksheet.write('H7', 'Sample ID:', bold)
    worksheet.write('H8', 'Lab ID:', bold)
    worksheet.write('H9', 'Date Collected:', bold)
    worksheet.write('H10', 'Date Received:', bold)
    worksheet.write('H11', 'Date Reported:', bold)
    worksheet.write_row("K6:N6", ['Physician / Project Information','','',''], metadata_header)
    worksheet.write('K7', 'Name:', bold)
    worksheet.write('K8', 'Institution:', bold)
    worksheet.write('K9', 'Address:', bold)
    worksheet.write_row("A13:F13", ['Subtyping information','','','','',''], metadata_header)
    worksheet.write_row("I13:N13", ['Codons Analyzed','','','','',''], metadata_header)
    ## MAIN TABLE
    worksheet.write_row("B19:D19", ['ANTIRETROVIRAL DRUG','',''], main_table_header)
    worksheet.write('F19', 'RESISTANCE INTERPRETATION *', main_table_header)
    worksheet.write_row("H19:N19", ['DRUG RESISTANCE ASSOCIATED MUTATIONS','','','','','',''], main_table_header)
    worksheet.write('C20', 'Generic Name', psub_header)
    worksheet.write('D20', 'Brand Name', psub_header)
    worksheet.write('F20', 'Assessment', psub_header)
    worksheet.write_row("H20:K20", ['MUTATIONS DETECTED AT ≥ 20%','','',''], psub_header)
    worksheet.write_row("M20:N20", ['MUTATIONS DETECTED AT < 20%',''], psub_header)
    rowNum = 21
    ## NRTI
    first_nrti = 0
    first_nnrti = 0
    first_pi = 0
    first_in = 0
    title = ""

    for resistance in self.profile['reverse_transcriptase']:
      if resistance[0] == "NRTI":
        if first_nrti == 0:
          title = "NRTI"
        else:
          title = ""
        self.writeResistance(worksheet, resistance, rowNum, grey, green, title)
        rowNum += 1
        first_nrti += 1
    for fixed in self.fixed['NRTI']:
      # write out the fixed drugs with susceptible if not found
      found = False
      for res in self.profile['reverse_transcriptase']:
        if res[1].upper() == fixed.upper():
          found = True
      if not found:
        self.writeResistance(worksheet, ['NRTI', fixed, '', 'Susceptible', '', ''], rowNum, grey, green, title)
        rowNum += 1
        first_nrti += 1
    ## NNRTI
    rowNum += 1
    for resistance in self.profile['reverse_transcriptase']:
      if resistance[0] == "NNRTI":
        if first_nnrti == 0:
          title = "NNRTI"
        else:
          title = ""
        self.writeResistance(worksheet, resistance, rowNum, grey, green, title)
        rowNum += 1
        first_nnrti += 1
    for fixed in self.fixed['NNRTI']:
      # write out the fixed drugs with susceptible if not found
      found = False
      for res in self.profile['reverse_transcriptase']:
        if res[1].upper() == fixed.upper():
          found = True
      if not found:
        self.writeResistance(worksheet, ['NNRTI', fixed, '', 'Susceptible', '', ''], rowNum, grey, green, title)
        rowNum += 1
        first_nnrti += 1
    ## PI
    rowNum += 1
    for resistance in self.profile['protease']:
      if resistance[0] == "PI":
        if first_pi == 0:
          title = "PI"
        else:
          title = ""
        self.writeResistance(worksheet, resistance, rowNum, grey, blue, title)
        rowNum += 1
        first_pi += 1
    for fixed in self.fixed['PI']:
      # write out the fixed drugs with susceptible if not found
      found = False
      for res in self.profile['protease']:
        if res[1].upper() == fixed.upper():
          found = True
      if not found:
        self.writeResistance(worksheet, ['PI', fixed, '', 'Susceptible', '', ''], rowNum, grey, blue, title)
        rowNum += 1
        first_pi += 1
    ## IN
    rowNum += 1
    for resistance in self.profile['integrase']:
      if resistance[0] == "IN":
        if first_in == 0:
          title = "IN"
        else:
          title = ""
        self.writeResistance(worksheet, resistance, rowNum, grey, red, title)
        rowNum += 1
        first_in += 1
    for fixed in self.fixed['IN']:
      # write out the fixed drugs with susceptible if not found
      found = False
      for res in self.profile['integrase']:
        if res[1].upper() == fixed.upper():
          found = True
      if not found:
        self.writeResistance(worksheet, ['IN', fixed, '', 'Susceptible', '', ''], rowNum, grey, red, title)
        rowNum += 1
        first_in += 1

    workbook.close()

  def writeResistance(self, worksheet, resistance, rowNum, grey, green, title):
    drugAbbrv = resistance[1]
    resistanceClass = resistance[0]
    drugName = ""
    brandName = ""
    if drugAbbrv in self.drugDict:
      drugName = self.drugDict[drugAbbrv]
    else:
      drugName = drugAbbrv

    if drugAbbrv in self.brandDict:
      brandName = self.brandDict[drugAbbrv]

    res = ""
    if resistance[3] == "Susceptible":
      res = resistance[3]
    else:
      res = resistance[3] + " " + resistance[4]
    worksheet.write('A' + str(rowNum), title, green)
    if rowNum % 2 == 0:
       worksheet.write('B' + str(rowNum), drugAbbrv)
       worksheet.write('C' + str(rowNum), drugName)
       worksheet.write('D' + str(rowNum), brandName)
       worksheet.write('F' + str(rowNum), res)
    else:
      worksheet.write('B' + str(rowNum), drugAbbrv, grey)
      worksheet.write('C' + str(rowNum), drugName, grey)
      worksheet.write('D' + str(rowNum), brandName, grey)
      worksheet.write('F' + str(rowNum), res, grey)


if __name__ == "__main__":
  reporter = ReportGenerator('SAMPLE1', 'output/CGAGGCTG+TCTCTCCG_scores.txt')
  reporter.parseFile(reporter.profileFile)
  #reporter.generatePDFReport()
  reporter.generateExcelReport()
  #print(reporter.profile)






