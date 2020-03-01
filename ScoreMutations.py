import json
import requests
import re
import time
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-file", help="Specify a drug resistance called mutations file", type=str)
args = parser.parse_args()

geneClassDict = {}

# read in the mutation table and make a gene class lookup dict
with open('HIV_DR_ANNO_REVISED.txt', 'r') as mutationsFile:
  for line in mutationsFile:
    lineparts = line.split()

    geneClass = lineparts[4]
    if lineparts[4] == "P":
      geneClass = "PR"
    elif lineparts[4] == "I":
      geneClass = "IN"
    geneClassDict[lineparts[0]] = geneClass

query = """
        query score($mutations:[String]!){
          viewer {
            mutationsAnalysis(mutations: $mutations) {
              drugResistance {
                gene { name },
                drugScores {
                  drugClass { name },
                  drug {name, displayAbbr},
                  SIR,
                  score,
                  level,
                  text,
                  partialScores {
                    mutations {
                      text
                    },
                    score
                  }

                }

              }

            }

          }
        }
        """

#"mutations": [
#      "PR:V32I",
#      "PR:L76V",
#      "RT:69Insertion"
#    ]

def makeRequest(mutations):
  resp = requests.post(
      'https://hivdb.stanford.edu/graphql',
      data=json.dumps({
          'query': query,
          'variables': {
            "mutations": mutations
          }
      }),
      headers={
          'Content-Type': 'application/json'
      }
  )
  return resp

# convert the called mutations into the mutation string for API query
def apiMutationString(row):
  barcode = row[0]
  mutation = row[1]
  readcount = re.sub('[[,]', '', row[3])
  aachange = re.sub('[]\']', '', row[4])
  aachange = re.sub(':MUT/RESISTANT', '', aachange)
  frequency = row[5]
  mutationBase = re.sub(r'\D+$', '', mutation)
  mutationString = ""
  if mutationBase == "T69":
    mutationString = "RT:69Insertion" # API generic name for T69dDNG
  else:
    mutationString = geneClassDict[mutation] + ':' + mutationBase + aachange
  return mutationString

def unpackResponse(json):
  outputLines = []
  for gene in json:
    outputLines.append("\n")
    outputLines.append(gene['gene']['name'] + "\n")
    for drugDef in gene['drugScores']:
      drugClass = drugDef['drugClass']['name']
      drugName = drugDef['drug']['name']
      score = drugDef['score']
      text = drugDef['text']

      outputLines.append(drugClass + "  " + drugName + "   " + str(score) + "   " + text + "  ")
      if len(drugDef['partialScores']) > 0:
        #print("(", end="")
        outputLines.append("(")
      for score in drugDef['partialScores']:
        outputLines.append(score['mutations'][0]['text'] + ':' + str(score['score']) + ",")
        #print(score['mutations'][0]['text'], ':', score['score'], sep="", end=",")
      if len(drugDef['partialScores']) > 0:
        outputLines.append(")\n")
        #print(")")
      else:
        outputLines.append("\n")
        #print()
  return "".join(outputLines)

mutationsDict = {}

with open(args.file, 'r') as mutationsFile:
  for line in mutationsFile:
    lineparts = line.split()
    mutString = apiMutationString(lineparts)
    #print(mutString)
    barcode = lineparts[0]
    if not barcode in mutationsDict:
      mutationsDict[barcode] = [mutString]
    else:
      mutationsDict[barcode].append(mutString)

errorBarcodes = []

for barcode in mutationsDict:
  with open('output/' + barcode + '_scores.txt', 'w') as outfile:
    outfile.write('barcode: ' + barcode)
    outfile.write("\n")
    if len(mutationsDict[barcode]) > 0:
      response = makeRequest(mutationsDict[barcode])
      if response.status_code == 200:
        output = unpackResponse(response.json()['data']['viewer']['mutationsAnalysis']['drugResistance'])
        outfile.write(output)
      else:
        outfile.write("Error with query!")
        errorBarcodes.append(barcode)
    else:
      outfile.write("No mutations called for barcode")
    time.sleep(2)

    outfile.write("\n")
    outfile.write("barcodes with errors:")
    for barcode in errorBarcodes:
      outfile.write(barcode)
  sys.stderr.write("barcode " + barcode + " scored\n")

