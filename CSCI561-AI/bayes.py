import os
from fileinput import close
import sys
import collections
from __builtin__ import str
import copy

diseases = collections.defaultdict(lambda: collections.defaultdict())
patients = collections.defaultdict(lambda: collections.defaultdict(dict))

def addDisease(line1,findings,prob_Present,prob_Not_Present,dNumber):
    (diseaseName,fCount,dProb)=line1.split(" ")
    diseases[dNumber]["probability"]=dProb
    diseases[dNumber]["findings"]=findings
    diseases[dNumber]["positive"]=prob_Present
    diseases[dNumber]["negative"]=prob_Not_Present
    diseases[dNumber]["name"]=diseaseName
    diseases[dNumber]["count"]=fCount
     
    
def evaluateProbability(pName,inputLine,dNumber):
    
    dName = diseases[dNumber]["name"]
    
    presentP = diseases[dNumber]["positive"]
    absentP = diseases[dNumber]["negative"]
    
    dProbability = diseases[dNumber]["probability"]
    findingsCount = diseases[dNumber]["count"]
    findings = diseases[dNumber]["findings"]
    
    #Compute the probability for question 1
    initialProb ="{0:.4f}".format(compute(inputLine, dProbability, presentP, absentP))
    patients[pName]["q1"][dName] = initialProb
    
    
    #Compute the maximum and minimum probabilities for question 2
    probList = []
    undefinedCount = 0
    for term in inputLine:
        if(term == "U"):
            undefinedCount += 1
    
    for index in range(2**undefinedCount):
        possibility = str("{0:b}".format(index)).zfill(undefinedCount)
        updatedInput = updateInputList(copy.deepcopy(inputLine), list(possibility))
        prob = compute(updatedInput, dProbability, presentP, absentP)
        probList.append(prob)
    
    patients[pName]["q2"][dName]=["{0:.4f}".format(min(probList)),"{0:.4f}".format(max(probList))]
    
    #Determine the substitution for Maximum and Minimum probabilities for question 3
    maxProb = minProb = float(initialProb)
    maxProbList = minProbList = []
    
    for index,term in enumerate(inputLine):
        if(term == "U"):
            #Setting the finding to be True for the disease
            updatedInput = copy.deepcopy(inputLine)
            updatedInput[index] = "T"
            prob = compute(updatedInput, dProbability, presentP, absentP)
            if(prob > maxProb):
                maxProb = prob
                maxProbList=[findings[index],"T"]
            elif(prob == maxProb):
                if(( len(maxProbList)!= 0 ) and (maxProbList[0].lower() > findings[index].lower())):
                    maxProb = prob
                    maxProbList=[findings[index],"T"]
            if(prob < minProb):
                minProb = prob
                minProbList=[findings[index],"T"]
            elif(prob == minProb):
                if(( len(minProbList)!= 0 ) and (minProbList[0].lower() > findings[index].lower())):
                    minProbList = prob
                    minProbList=[findings[index],"T"]
                
            
            
            #Setting the finding to be False for the disease
            updatedInput = copy.deepcopy(inputLine)
            updatedInput[index] = "F"
            prob = compute(updatedInput, dProbability, presentP, absentP)
            if(prob > maxProb):
                maxProb = prob
                maxProbList=[findings[index],"F"]
            elif(prob == maxProb):
                if(( len(maxProbList)!= 0 ) and (maxProbList[0].lower() > findings[index].lower())):
                    maxProb = prob
                    maxProbList=[findings[index],"F"]
            if(prob < minProb):
                minProb = prob
                minProbList=[findings[index],"F"]
            elif(prob == minProb):
                if(( len(minProbList)!= 0 ) and (minProbList[0].lower() > findings[index].lower())):
                    minProbList = prob
                    minProbList=[findings[index],"F"]
            
    
    if((maxProb == float(initialProb)) and (minProb == float(initialProb))):
        patients[pName]["q3"][dName]=["none","N","none","N"]
    elif(maxProb == float(initialProb)):
        patients[pName]["q3"][dName]=["none","N",minProbList[0],minProbList[1]]
    elif(minProb == float(initialProb)):
        patients[pName]["q3"][dName]=[maxProbList[0],maxProbList[1],"none","N"]
    else:
        patients[pName]["q3"][dName]=[maxProbList[0],maxProbList[1],minProbList[0],minProbList[1]]
        
        
            
        
     
    
    
            
        
def updateInputList(inputList,subsList):
    count =0;
    for index,term in enumerate(inputList):
        if term == "U":
            if(subsList[count] == "1"):
                inputList[index] = "T"
            else:
                inputList[index] = "F"
            count += 1;
    
    return inputList
            
            
                        
        
def compute(input,dProbability,presentP,absentP):
    
    numerator = float(dProbability)
    denominator = 1 - numerator
    for index,fExist in enumerate(input):
        if fExist == "T":
            numerator *= presentP[index]
            denominator *= absentP[index]
        elif fExist == "F":
            numerator *= 1 - presentP[index]
            denominator *= 1 - absentP[index]
    
    probability = round(numerator/(numerator+denominator),4)
    
    return probability
    
    
    


#Read input file and process all lines
inputFileName = os.path.basename(sys.argv[2])
inputFile = open(inputFileName)

lines=inputFile.readlines()

(diseaseCount,patientCount) = lines[0].split(" ")
diseaseLines = int(diseaseCount)*4
patientLines = int(diseaseCount) * int(patientCount)
dNumber = 0


outputFile = (inputFileName).rsplit(".")[0]+"_inference.txt"
outFile = open(outputFile,"w")

#Parse all diseases' info
for i in range(1,diseaseLines,4):
    dNumber += 1
    line1 = lines[i]
    i+= 1
    line2 = eval(lines[i])
    i+= 1
    line3 = eval(lines[i])
    i+= 1
    line4 = eval(lines[i])
    addDisease(line1.rstrip("\n"), line2, line3, line4,dNumber)

#Parse all Patient Info and compute probabilities
patientNumber = 1
for j in range(diseaseLines+1,len(lines),int(diseaseCount)):
    dNumber = 1
    patientName = "Patient-"+str(patientNumber)
    while(dNumber <= int(diseaseCount)):
        evaluateProbability(patientName,eval(lines[j]),dNumber)
        j += 1
        dNumber += 1
        
    outFile.write(patientName+":\n")
    outFile.write(str(patients[patientName]["q1"])+"\n")
    outFile.write(str(patients[patientName]["q2"])+"\n")
    outFile.write(str(patients[patientName]["q3"])+"\n")
    print str(patients[patientName]["q1"])
    print str(patients[patientName]["q2"])
    print str(patients[patientName]["q3"])
    patientNumber += 1
    
outFile.close()
    
    
    
    
    
    

inputFile.close()

