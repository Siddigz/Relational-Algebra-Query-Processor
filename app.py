import re

class Relation:
    def __init__(self, name, attr, tuples):
        self.name = name
        self.attr = attr
        self.tuples = tuples
        self.attrIndex = {attr:i for i, attr in enumerate(attr)}
    
    def __str__(self):
        result = f"{self.name} = {{{', '.join(self.attr)}}}\n"
        for row in self.tuples:
            value = [f'"{val}"' for val in row]
            result += f"  {', '.join(value)}\n"
        result += "}"
        return result
    
    def get_attr_val(self, row, attr):
        if(attr in self.attrIndex):
            return row[self.attrIndex[attr]]
        raise ValueError(f"Attribute '{attr} not found in relation '{self.name}'.")
    
    def get_attrs(self):
        return self.attr.copy()

    def get_tuples(self):
        return [row.copy() for row in self.tuples]

class Processor:
    
    def __init__(self):
        self.relations = {}
    
    def add_relation(self, relation: Relation):
        self.relations[relation.name] = relation
    
    def get_relation(self, name):
        if(name not in self.relations):
            raise ValueError(f"Relation '{name} not found'.")
        return self.relations[name]
    
    def selection(self, relName, condition):
        relation = self.get_relation(relName)
        result = []

        for row in relation.tuples:
            if(self._evaluate_condition(row, relation, condition)):
                result.append(row)

        return Relation(relName, relation.attr, result)
    
    def projection(self, relName, attributes):
        relation = self.get_relation(relName)
        for attr in attributes:
            if attr not in relation.attrIndex:
                raise ValueError(f"Attribute '{attr}' not found in relation '{relName}'")
        
        attrIndices = [relation.attrIndex[attr] for attr in attributes]

        result = []

        for row in relation.tuples:
            new = [row[i] for i in attrIndices]
            result.append(new)

        return Relation(f"project_{','.join(attributes)}({relName})", attributes, result)
    
    def intersection(self, rel1Name, rel2Name):
        rel1 = self.get_relation(rel1Name)
        rel2 = self.get_relation(rel2Name)
        if(rel1.attr != rel2.attr):
            raise ValueError("Relations must have the same attributes to do an intersection operation.")
        
        rel2_set = set(tuple(row) for row in rel2.tuples)
        commons = []

        for row in rel1.tuples:
            if(tuple(row) in rel2_set):
                commons.append(row)
        
        return Relation(f"{rel1Name}_intersection_{rel2Name}", rel1.attr, commons)
    
    def join(self, rel1Name, rel2Name, condition = None):
        rel1 = self.get_relation(rel1Name)
        rel2 = self.get_relation(rel2Name)
        commons = set(rel1.attr) & set(rel2.attr)
        if(not commons):
            return self._cartesian_product(rel1, rel2)

        attrResults = rel1.attr + [attr for attr in rel2.attr if attr not in commons]
        resultTuples = []

        for t1 in rel1.tuples:
            for t2 in rel2.tuples:
                bingo = True
                for attr in commons:
                    v1 = rel1.get_attr_val(t1, attr)
                    v2 = rel2.get_attr_val(t2, attr)
                    if(v1 != v2):
                        bingo = False
                        break

                if(bingo == True):
                    pair = t1.copy()
                    for attr in rel2.attr:
                        if(attr not in commons):
                            pair.append(rel2.get_attr_val(t2, attr))
                    resultTuples.append(pair)

        return Relation(f"{rel1Name}_join_{rel2Name}", attrResults, resultTuples)

    def union(self, rel1Name, rel2Name):
        rel1 = self.get_relation(rel1Name)
        rel2 = self.get_relation(rel2Name)

        if(rel1.attr != rel2.attr):
            raise ValueError("Relations must have the same attributes to do a union operations.")

        allPairs = rel1.tuples + rel2.tuples
        uniquePairs = []
        seen = set()
        for row in allPairs:
            key = tuple(row)
            if(key not in seen):
                seen.add(key)
                uniquePairs.append(row)
        
        return Relation(f"{rel1Name}_union_{rel2Name}", rel1.attr, uniquePairs)

    def difference(self, rel1Name, rel2Name):
        rel1 = self.get_relation(rel1Name)
        rel2 = self.get_relation(rel2Name)
        if(rel1.attr != rel2.attr):
            raise ValueError("Relations must have the same attributes to do an difference operation.")
    
        rel2_set = set(tuple(row) for row in rel2.tuples)
        diff = []

        for row in rel1.tuples:
            if(tuple(row) not in rel2_set):
                diff.append(row)

        return Relation(f"{rel1Name}_difference_{rel2Name}", rel1.attr, diff)

    def _evaluate_condition(self, row, relation: Relation, condition):
        condition = condition.strip()
        ops = ["<=", ">=", "=", ">", "<", "!="]
        currentOperator = None
        opLocation = -1

        for symbol in ops:
            pos = condition.find(symbol)
            if(pos != -1):
                currentOperator  = symbol
                opLocation = pos
        
        if(currentOperator == None):
            raise ValueError(f"Invalid Condition: {condition}")
        
        left = condition[:opLocation].strip()
        right = condition[opLocation + len(currentOperator):].strip()

        attrVal = relation.get_attr_val(row, left)
        try:
            rVal = float(right)
            attrVal = float(attrVal)
        except ValueError:
            rVal = right.strip('"\'')
            attrVal = str(attrVal)

        if(currentOperator == ">"):
            return attrVal > rVal
        elif(currentOperator == "<"):
            return attrVal < rVal
        elif(currentOperator == "<="):
            return attrVal <= rVal
        elif(currentOperator == ">="):
            return attrVal >= rVal
        elif(currentOperator == "="):
            return attrVal == rVal
        elif(currentOperator == "!="):
            return attrVal != rVal
        else:
            raise ValueError(f"Unsupported operator: {currentOperator}")

    def _cartesian_product(self, rel1, rel2):
        resultAttr = rel1.attr + [f"{attr}_{rel2.name}" for attr in rel2.attr]
        result = []
        for t1 in rel1.tuples:
            for t2 in rel2.tuples:
                result.append(t1 + t2)
        return Relation(f"{rel1.name}_cartesian_{rel2.name}", resultAttr, result)

def parse_text(text) -> tuple[list[str], list[Relation]]:
    relations = []
    queryList = []
    
    lines = text.split("\n")
    
    currentRelation = None
    currentAttr = None
    currentTuples = []

    lineNum = 0
    while lineNum < len(lines):
        line = lines[lineNum].strip() 
        
        #accounts for comments
        if((not line) or line.startswith("//")):
            lineNum += 1
            continue
        
        #relation def
        if( ("(" in line) and (")" in line) and ("=" in line)):
            parts = line.split("=")
        
            if(len(parts) == 2):
                left = parts[0].strip()
                right = parts[1].strip()

                if(right == "{"):
                    paren_pos = left.find("(")

                    if(paren_pos != -1):
                        currentRelation = left[:paren_pos].strip()
                        attrPart = left[paren_pos+1 : left.rfind(")")].strip()
                        currentAttr = [attr.strip() for attr in attrPart.split(",")]
                        currentTuples = []

        #end of def
        elif(line == "}"):
            if(currentRelation and currentAttr != None):
                relation = Relation(currentRelation, currentAttr, currentTuples)
                relations.append(relation)
                currentRelation = currentAttr = None
                currentTuples = []
    
        elif(currentRelation and currentAttr):
            if(line and (not line.startswith("//")) and (not line.startswith("Query:"))): 
                tupleDetails = [val.strip().strip('"\'') for val in line.split(",")]

                if(len(tupleDetails) == len(currentAttr)):
                    currentTuples.append(tupleDetails)
            elif(line.startswith("Query:")):
                query = line[6:].strip()
                queryList.append(query)

        if(line.startswith("Query:") and (not (currentRelation and currentAttr))):
            query = line [6:].strip()
            queryList.append(query)

        lineNum += 1

    return queryList, relations

def run_query(processor, query):
    query = query.strip()
    return _parse_and_run(processor, query)

def _parse_and_run(cpu: Processor, query):
    ops = ["select ", "project ", " join ", " union ", " intersection ", " difference "]
    query = query.strip()
    if(query.startswith("(") and query.endswith(")")):
        return _parse_and_run(cpu, query[1:-1].strip())
    
    if(query.startswith("select ")):
        match = re.match(r"select\s+(.+?)\s+\((.+)\)", query)
        if(match):
            condition = match.group(1)
            rORq = match.group(2).strip()
            if(rORq.startswith("(") or any(op in rORq for op in ops)):
                nestedResult = _parse_and_run(cpu, rORq)
                temp = f"temp_{len(cpu.relations)}"
                cpu.add_relation(Relation(temp, nestedResult.attr, nestedResult.tuples))
                result = cpu.selection(temp, condition)
                del cpu.relations[temp]
                return result
            else:
                return cpu.selection(rORq, condition)

    elif(query.startswith("project")):
        match = re.match(r"project\s+(.+?)\s+\((.+)\)", query)
        if(match):
            attrs = [attr.strip() for attr in match.group(1).split(",")]
            rORq = match.group(2).strip()
            if(rORq.startswith("(") or any(op in rORq for op in ops)):
                nestedResult = _parse_and_run(cpu, rORq)
                temp = f"temp_{len(cpu.relations)}"
                cpu.add_relation(Relation(temp, nestedResult.attr, nestedResult.tuples))
                result = cpu.projection(temp, attrs)
                del cpu.relations[temp]
                return result
            else:
                return cpu.projection(rORq, attrs)

    elif(" join " in query):
        parts = query.split(" join ")
        if(len(parts) == 2):
            r1 = parts[0].strip()
            r2 = parts[1].strip()
            if(r1.startswith("(") or any(op in r1 for op in ops)):
                result1 = _parse_and_run(cpu, r1)
                temp1 = f"temp1_{len(cpu.relations)}"
                cpu.add_relation(Relation(temp1, result1.attr, result1.tuples))
                r1 = temp1
            else:
                result1 = None

            if(r2.startswith("(") or any(op in r2 for op in ops)):
                result2 = _parse_and_run(cpu, r2)
                temp2 = f"temp1_{len(cpu.relations)}"
                cpu.add_relation(Relation(temp2, result2.attr, result2.tuples))
                r2 = temp2
            else:
                result2 = None

            result = cpu.join(r1, r2)
            if(result1 is not None):
                del cpu.relations[r1]
            if(result2 is not None):
                del cpu.relations[r2]
            return result
        
    elif(" union " in query):
        parts = query.split(" union ")
        if(len(parts) == 2):
            r1 = parts[0].strip()
            r2 = parts[1].strip()
            if(r1.startswith("(") or any(op in r1 for op in ops)):
                result1 = _parse_and_run(cpu, r1)
                temp1 = f"temp1_{len(cpu.relations)}"
                cpu.add_relation(Relation(temp1, result1.attr, result1.tuples))
                r1 = temp1
            else:
                result1 = None

            if(r2.startswith("(") or any(op in r2 for op in ops)):
                result2 = _parse_and_run(cpu, r2)
                temp2 = f"temp1_{len(cpu.relations)}"
                cpu.add_relation(Relation(temp2, result2.attr, result2.tuples))
                r2 = temp2
            else:
                result2 = None

            result = cpu.union(r1, r2)
            if(result1 is not None):
                del cpu.relations[r1]
            if(result2 is not None):
                del cpu.relations[r2]
            return result

    elif(" intersection " in query):
        parts = query.split(" intersection ")
        if(len(parts) == 2):
            r1 = parts[0].strip()
            r2 = parts[1].strip()
            if(r1.startswith("(") or any(op in r1 for op in ops)):
                result1 = _parse_and_run(cpu, r1)
                temp1 = f"temp1_{len(cpu.relations)}"
                cpu.add_relation(Relation(temp1, result1.attr, result1.tuples))
                r1 = temp1
            else:
                result1 = None

            if(r2.startswith("(") or any(op in r2 for op in ops)):
                result2 = _parse_and_run(cpu, r2)
                temp2 = f"temp1_{len(cpu.relations)}"
                cpu.add_relation(Relation(temp2, result2.attr, result2.tuples))
                r2 = temp2
            else:
                result2 = None

            result = cpu.intersection(r1, r2)
            if(result1 is not None):
                del cpu.relations[r1]
            if(result2 is not None):
                del cpu.relations[r2]
            return result

    elif(" difference " in query):
        parts = query.split(" difference ")
        if(len(parts) == 2):
            r1 = parts[0].strip()
            r2 = parts[1].strip()
            if(r1.startswith("(") or any(op in r1 for op in ops)):
                result1 = _parse_and_run(cpu, r1)
                temp1 = f"temp1_{len(cpu.relations)}"
                cpu.add_relation(Relation(temp1, result1.attr, result1.tuples))
                r1 = temp1
            else:
                result1 = None

            if(r2.startswith("(") or any(op in r2 for op in ops)):
                result2 = _parse_and_run(cpu, r2)
                temp2 = f"temp1_{len(cpu.relations)}"
                cpu.add_relation(Relation(temp2, result2.attr, result2.tuples))
                r2 = temp2
            else:
                result2 = None

            result = cpu.difference(r1, r2)
            if(result1 is not None):
                del cpu.relations[r1]
            if(result2 is not None):
                del cpu.relations[r2]
            return result

    else:
        if(query in cpu.relations):
            return cpu.get_relation(query)
        else:
            raise ValueError(f"Unsupported query format: {query}")

def main():
    maker = Processor()

    try:
        #loads input.txt to text
        with open("input.txt", "r") as inputFile:
            text = inputFile.read()

    except FileNotFoundError:
        #prints error if file cant be opened
        print(f"ERROR - input.txt not found.")    
        quit()
    
    #parses text to relations and list of queries
    queryList, relations = parse_text(text)
    print(f"Program has parsed {len(relations)} relations and {len(queryList)} queries.")

    for rel in relations:
        maker.add_relation(rel)

    results = []
    for query in queryList:
        try:
            result = run_query(maker, query)
            results.append(result)
        except Exception as e:
            results.append(f"Error running query '{query}': {str(e)}.")

    with open("output.txt", "w") as outputFile:
        for line in results:
            outputFile.write(str(line) + "\n\n")
    
    print(f"SUCCESSFUL - output.txt has been filled with results.")
    
if __name__ == "__main__":
    main()
