import sys
from collections import defaultdict
from symbol import parameters
import copy



#Method to eliminate all biconditional and implication operators in the sentence
def removeBiConditional(sentence):
    
    if(type(sentence) is not list):
        return sentence
    
    operator = sentence[0]
    
    if(operator == "not"):
        return ["not",removeBiConditional(sentence[1])]
    elif(operator == "implies"):
        return removeBiConditional(["or",removeBiConditional(["not",sentence[1]]),removeBiConditional(sentence[2])])
    elif(operator == "iff"):
        return removeBiConditional(["and",removeBiConditional(["implies",sentence[1],sentence[2]]),removeBiConditional(["implies",sentence[2],sentence[1]])])
    elif(operator == "and" or operator == "or"):
        newSentence = [operator]
        for term in sentence[1:]:
            newSentence.append(removeBiConditional(term))
        return newSentence
        
#Method to evaluate terms in sentence based on de Morgan's laws    
def deMorganLaws(sentence):
    if(type(sentence) is not list):
        return sentence

    operator = sentence[0]
    
    if(operator != "not"):
        newSentence = [operator]
        for term in sentence[1:]:
            newSentence.append(deMorganLaws(term))
        return newSentence
    
    term = sentence[1]
    
    if(type(term) is not list):
        return ["not",term]
    
    #negation of a Negative literal -> Positive Literal
    if(term[0] == "not"):
        return deMorganLaws(term[1])
    
    if(term[0] == "and"):
        newSentence = ["or"]
        for operand in term[1:]:
            newSentence.append(deMorganLaws(["not",operand]))
        return newSentence
    elif(term[0] == "or"):
        newSentence = ["and"]
        for operand in term[1:]:
            newSentence.append(deMorganLaws(["not",operand]))
        return newSentence
    

#Method to distribute or over two conjunctions or two literals or a literal and a conjunction 
def evaluate(term1,term2):
    
    if((type(term1) is list) and (type(term2) is not list)): #Performing OR operation on a list and a literal
        if(term1[0] == "or"):
            term1.append(term2)
            return term1
        elif(term1[0] == "and"):
            newList = ["and"]
            for term in term1[1:]:
                newList.append(["or",term,term2])
            return newList
        elif(term1[0] == "not"):
            return ["or",term1,term2]
    elif((type(term1) is list) and (type(term2) is list)): #Performing OR operation on two lists
        if(term1[0] == "or" and term2[0] == "or"):
            for term in term2[1:]:
                term1.append(term)
            return term1
        elif(term1[0] == "or" and term2[0] == "and"):
            newList = ["and"]
            for term in term2[1:]:
                newTerm = list(term1)
                newTerm.append(term)
                newList.append(newTerm)
            return newList
        elif(term1[0] == "and" and term2[0] == "or"):
            newList = ["and"]
            for term in term1[1:]:
                newTerm = list(term2)
                newTerm.insert(1,term)
                newList.append(newTerm)
            return newList
        elif(term1[0] =="and" and term2[0] == "and"):
            newList = ["and"]
            for firstTerm in term1[1:]:
                for secondTerm in term2[1:]:
                    newList.append(["or",firstTerm,secondTerm])
            return newList
        elif(term1[0] == "and" and term2[0] == "not"):
            newList=["and"]
            for term in term1[1:]:
                newList.append(["or",term,term2])
            return newList            
        elif(term1[0] == "or" and term2[0] == "not"):
            term1.append(term2)
            return term1
        elif(term1[0] == "not" and term2[0] == "or"):
            term2.append(term1)
            return term2
        elif(term1[0] == "not" and term2[0] == "and"):
            newList=["and"]
            for term in term2[1:]:
                newList.append(["or",term1,term])      
            return newList
        elif(term1[0] == "not" and term2[0] == "not"):
            return ["or",term1,term2]
    elif((type(term1) is not list) and (type(term2) is list)): #Performing OR operation on a literal and a list
        if(term2[0] == "or"):
            term2.append(term1)
            return term2
        elif(term2[0] == "and"):
            newList = ["and"]
            for term in term2[1:]:
                newList.append(["or",term1,term])
            return newList
        elif(term2[0] == "not"):
            return ["or",term1,term2]
    else:
        return ["or",term1,term2] #Returning Clause that has two literals as disjuncts
        
      
#Method to distribute or over disjunctions or literals in the sentence    
def distributeOr(sentence):
    
    if(type(sentence) is not list):
        return sentence
    
    operator = sentence[0]
    
    if(operator == "or"):
        newSentence = []
        firstTerm = sentence[1]
        for term in sentence[2:]:
            firstTerm = evaluate(distributeOr(firstTerm),distributeOr(term))
        return firstTerm
    elif(operator == "not"):
        return sentence
    
    elif(operator =="and"):
        newSentence = [operator]
        for term in sentence[1:]:
            newSentence.append(distributeOr(term)) #Distribute OR over all conjuncts of the sentence
        return distributeAnd(newSentence)
        
        
#Method to format sentence such that ["and",["and","A","B"],"C"] is converted to ["and","A","B","C"]    
def distributeAnd(sentence):
    
    if(type(sentence) is not list):
        return sentence
    
    operator = sentence[0]
    
    if(operator == "and"):
        newSentence = ["and"]
        for term in sentence[1:]:
            if(type(term) is list):
                if(term[0] =="and"):
                    for subterm in term[1:]:
                        newSentence.append(distributeAnd(subterm)) #Append all conjuncts into a single conjunction
                else:
                    newSentence.append(distributeOr(term)) #Evaluate the clauses and append to the conjunction
            else:
                newSentence.append(term)
        return newSentence
    elif(operator == "or"):
        return distributeOr(sentence)
    else:
        return sentence
    
#Method to eliminate duplicate terms from the sentence
def eliminateDuplicates(sentence):
       
    if(type(sentence) is not list):
        return sentence
    
    operator = sentence[0]
    
    toRemove = []
    if (operator != "not"):
        for i in range(1,len(sentence)):
            parameters = copy.deepcopy(sentence[i+1:])
            
            for parameter in parameters:
                if(parameter in toRemove):
                    continue
                if(equals(eliminateDuplicates(sentence[i]),eliminateDuplicates(parameter))):
                    toRemove.append(parameter)
                           
        for parameter in toRemove:
            sentence.remove(parameter)
        if(len(sentence) == 2):
            returnValue = sentence[1]
            return eliminateDuplicates(returnValue)
    return sentence
    
#Method to check if two lists or literals are equal    
def equals(term1,term2):
    
    returnValue = False
    if( term1 == term2) :
        returnValue = True
    else:
        if(type(term1) == type(term2) and type(term1) is list):
            if(len(term1) == len(term2)):
                if(sorted(term1) == sorted(term2)):
                    returnValue = True
    return returnValue
                    
                
#Method to format output        
def convertResult(sentence):
    result="["
    termCount = 0
    for term in sentence:
        if termCount == 0 :
            termCount+=1
        else:
            result+=", "
        if(type(term) is not list):
            result+="\""+term+"\""
        else:
            returnResult =convertResult(term) 
            result+=returnResult 
    result+="]"
    return result



# Read input file and invoke methods to create output

inputFile = open(sys.argv[2])
lines=inputFile.readlines()
sentenceCount = lines[0]

#print sentenceCount

outputfile = "sentences_CNF.txt"

outputFile = open(outputfile,"w")

#for index in range(1,len(lines)):
for index in range(1,int(sentenceCount)+1):
    sList = eval(lines[index])
    if type(sList) is list:
        # Conversion to CNF
        
        #Biconditional Elimination
        result = removeBiConditional(sList)
        
        #Application of DeMorgan Laws on the sentences
        result = deMorganLaws(result)
        
        #Distribute the OR evaluation
        result = distributeOr(result)
        
        #Format the sentence to convert to CNF
        result = distributeAnd(result)
        
        #Remove duplicate literals and clauses from the sentence
        result = eliminateDuplicates(result)
        
        #Format the output sentence
        result = convertResult(result)
        
        #Print the result CNF to the output File
        outputFile.write(str(result)+"\n")
        
outputFile.close()
  
