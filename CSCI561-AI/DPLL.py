import sys
import copy



#Method to get list of symbols in the sentence    
def getSymbols(sentence):
    
    symbols = []
    if((sentence[0] != "or") and (sentence[0] != "and") and (sentence[0] != "not")):
        return [sentence[0]]
    for term in sentence[1:]:
        if(type(term) is not list):
            symbols.append(term)
        elif(term[0] == "or"):
            for subTerm in term[1:]:
                if(type(subTerm) is not list):
                    symbols.append(subTerm)
                else:
                    symbols.append(subTerm[1])
        else:
            symbols.append(term[1])
    
    return list(set(symbols))

#Method to get the list of clauses in the sentence
def getClauses(sentence):
    
    if(type(sentence) is list and sentence[0] == "and"):
        clauseList = []
        for term in sentence[1:]:
            if(type(term) is list):
                if(term[0] == "or"):
                    term.pop(0)
            clauseList.append(term)
        return clauseList
    else:
        return [sentence]
    
 
#Method to execute the DPLL algorithm on the given sentence    
def evaluate(sentence,symbols,model):
    
    #Invoke Method to check if sentence contains unit clauses and remove them.
    (sentence,model) = eliminateUnitClause(sentence,model)
    

    if(emptyList in sentence):
        return (False,model)
    elif(len(sentence) == 0):
        return (True,model)

    #Invoke method to check for pure symbols in a sentence and remove them
    (sentence,model) = eliminatePureSymbols(sentence,symbols,model)
    
    if(emptyList in sentence):
        return(False,model)
    elif(len(sentence) == 0):
        return (True,model)
    
    #Once Pure symbols and Unit Clauses are eliminated, assume values for remaining literals and check satisfiability
    oldSentence = copy.deepcopy(sentence)
    for symbol in symbols:
        if(symbol not in model.keys()):
            #assume symbol to be True in model
            model[symbol] = True
            removeIndices = []
            removeTerms = []
            for index,term in enumerate(sentence):
                if(symbol in term):
                    removeIndices.append(index)
                elif(['not',symbol] in term):
                    sentence[index].remove(['not',symbol])
                    if(len(sentence[index]) ==1):
                            sentence[index] = (sentence[index])[0]
                    
            for index in set(removeIndices):
                removeTerms.append(sentence[index])
            for term in removeTerms:
                sentence.remove(term)
            (satisfiable,model) = evaluate(sentence, symbols, model)
            if(satisfiable == True):
                return (satisfiable,model)
            
            #assume symbol to be False in model
            sentence = copy.deepcopy(oldSentence)
            model[symbol] = False
            removeIndices = []
            removeTerms = []
            for index,term in enumerate(sentence):
                if(['not',symbol] in term):
                    removeIndices.append(index)
                elif(symbol in term):
                    sentence[index].remove(symbol)
                    if(len(sentence[index]) ==1):
                            sentence[index] = (sentence[index])[0]
                    
            for index in removeIndices:
                removeTerms.append(sentence[index])
            for term in removeTerms:
                sentence.remove(term)
            (satisfiable,model) = evaluate(sentence, symbols, model)
            if(satisfiable == True):
                return (satisfiable,model)
            
    return (False,model)
    
#Method to identify all the pure symbols in the sentence and remove them.
def eliminatePureSymbols(sentence,symbols,model):
    
    for symbol in symbols:
        pure = None
        removeIndices = []
        removeTerms = []
        
        for term in sentence:
            if (symbol in term):
                if(pure == None):
                    pure = True
                elif(pure == False):
                    pure = "Not Pure"
                    break
                
            if(['not',symbol] in term):
                if(pure ==None):
                    pure = False
                elif(pure == True):
                    pure = "Not Pure"
                    break
        
        if(pure == True or pure == False):
            
            model[symbol] = pure
        
            for index,term in enumerate(sentence):
                if(pure == True):
                    if(symbol in term):
                        removeIndices.append(index)
                if(pure == False):
                    if(['not',symbol] in term):
                        removeIndices.append(index)
        
            for index in set(removeIndices):
                removeTerms.append(sentence[index])
            for term in removeTerms:
                sentence.remove(term)
            
    return (sentence,model)
            
                    
                
    
    
#Method to eliminate all unit clauses recursively from the given sentence    
def eliminateUnitClause(sentence,model):
    

    unitClauses = getUnitClauses(sentence)
    
    if(len(unitClauses) == 0):
        return (sentence,model)
    
    else:
        for literal in unitClauses:
            if(type(literal) is not list):
                if (['not',literal] in unitClauses):
                    return ([[]],model)
    
    for literal in unitClauses:
        sentence.remove(literal)


    for literal in unitClauses:
        removeIndices = []
        removeTerms = []
        
        if(type(literal) is not list):
            model[literal]= True
        else:
            model[literal[1]] = False
    
        for index,term in enumerate(sentence):
            
            if literal in term:
                removeIndices.append(index) # Remove the clause from the sentence
            else:
                if(type(literal) is list):
                    if(literal[1] in term):
                        (sentence[index]).remove(literal[1])
                        if(len(sentence[index]) ==1):
                            sentence[index] = (sentence[index])[0]
                else:
                    negativeTerm = ["not",literal]
                    if(negativeTerm in term):
                        (sentence[index]).remove(negativeTerm)
                        if(len(sentence[index]) ==1):
                            sentence[index] = (sentence[index])[0]
        
        for index in set(removeIndices):
            removeTerms.append(sentence[index])
        for term in removeTerms:
            sentence.remove(term)        
    
    return eliminateUnitClause(sentence,model)

            
#Method to get the list of all unit clauses that can be found in the input sentence
def getUnitClauses(sentence):
    unitClauses = []
    
    
    for term in sentence:
        if(type(term) is not list):
            unitClauses.append(term) 
        else:
            if(len(term)!=0 and term[0] == "not"):
                unitClauses.append(term)
    return unitClauses 

#Method to print result in the required format 
def convertResult(satisfiable,model):
    result = "["
    if (satisfiable is False):
        result += "\"false\"]"
    else:
        result += "\"true\""
        for symbol in symbols:
            result += ", \""+str(symbol)+"="
            if(symbol in model.keys()):
                if(model[symbol] is True):
                    result += "true\""
                else:
                    result += "false\""
            else:
                result += "true\""
        
        result += "]"
    
    return result
       

#Read input file and evaluate satisfiability of sentences

input = open(sys.argv[2])

sentences = input.readlines()
lineCount = sentences[0]

emptyList = []

outputFile = "CNF_satisfiability.txt"
output = open(outputFile,"w")
for line in sentences[1:int(lineCount)+1]:
    symbols = []
    model = {}
    satisfiable = None
    try:
        sentence = eval(line) #Convert the input to list representation
        symbols = getSymbols(sentence) #Get the list of symbols in the sentence
        sentence = getClauses(sentence) #Get the list of clauses in the given CNF
    
        (satisfiable,model)= evaluate(sentence,symbols,model) #Evaluate the sentence to check satisfiability
        output.write(convertResult(satisfiable, model)+"\n") #Format the output sentence and print to output file
    except (SyntaxError) as detail:
        print "Syntax Error in Input File",detail

output.close()

        
    