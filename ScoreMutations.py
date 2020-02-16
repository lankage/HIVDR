"""
A simple script to initial a request to Sierra GraphQL service and
then print out current HIVDB version.
"""
from __future__ import print_function
import json
import requests
import re
import time

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
  #print(mutations)
  return resp
  #return resp.json()['data']['viewer']['mutationsAnalysis']['drugResistance']
#print(resp.json()['data']['viewer']['mutationsAnalysis']['drugResistance'])

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
  for gene in json:
    print(gene['gene']['name'])
    for drugDef in gene['drugScores']:
      drugClass = drugDef['drugClass']['name']
      drugName = drugDef['drug']['name']
      score = drugDef['score']
      text = drugDef['text']
      print(drugClass, drugName, score, text, sep="\t")

mutationsDict = {}

#with open('called_mutations.txt', 'r') as mutationsFile:
with open('one_sample.txt', 'r') as mutationsFile:
#with open('bad_sample.txt', 'r') as mutationsFile:
  for line in mutationsFile:
    lineparts = line.split()
    mutString = apiMutationString(lineparts)
    print(mutString)
    barcode = lineparts[0]
    if not barcode in mutationsDict:
      mutationsDict[barcode] = [mutString]
    else:
      mutationsDict[barcode].append(mutString)

errorBarcodes = []

for barcode in mutationsDict:
  print(barcode)
  #print(len(mutationsDict[barcode]))
  print()
  if len(mutationsDict[barcode]) > 0:
    response = makeRequest(mutationsDict[barcode])
    if response.status_code == 200:
      #print(response)
      output = unpackResponse(response.json()['data']['viewer']['mutationsAnalysis']['drugResistance'])
      print(output)
    else:
      print("Error with query!")
      errorBarcodes.append(barcode)
  else:
    print("No mutations called for barcode")
  time.sleep(2)

print()
print()
print("barcodes with errors:")
for barcode in errorBarcodes:
  print(barcode)
# TODO
# handle single called mutations file, break out into data structure of samples
# run loop and call makeRequest with a sleep to prevent hammering api



