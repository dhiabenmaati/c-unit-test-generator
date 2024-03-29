import os
import sys
import re
import fnmatch

FilePath = sys.argv[1]       
FolderPath = sys.argv[2]

# IF ARGS WITHOUT "/" ADD IT
pattern = re.compile(r".+/$")  
match = pattern.search(FolderPath)     
if match:
    pass
else:
    FolderPath = FolderPath + '/'

##################### extract all typedef from all files #####################
# extract all typedef from all files
def GetAllTypedef(): 
    data = []
    for root, dirs, All_files in os.walk(FolderPath, topdown=False):
        files = fnmatch.filter(All_files, '*.h')
        files += fnmatch.filter(All_files, '*.c')
        
        for name in files:
                      
            # Read C code from a file   
            with open(os.path.join(root, name), encoding='utf-8', errors='ignore') as f:
                c_code = f.read()

            #############################################################################################################
            # Find all the normal typedef declarations
            normal_typedef_pattern = re.compile(r'typedef\s+(.+?)\s+(\w+)\s*;', re.DOTALL)  
            matches = re.findall(normal_typedef_pattern, c_code)
            
            # Append Results to our list
            for match in matches:
                name = match[1]
                type = match[0]
                new_data = {"Name": name, "Additional": '', "Type": type, "keyword":"normal"}
                
                #If There is struct, enum, pointer or array we skip them 
                if 'struct' in new_data['Type'] or 'enum' in new_data['Type']:
                    pass
                else:
                    data.append(new_data)
            
            #############################################################################################################
            # Find all the struct typedef declarations
            struct_typedef_pattern = r'typedef\s+struct\s*(.*)\s*\{([^}]*)\}\s*(\w+)\s*;'
            matches = re.findall(struct_typedef_pattern, c_code)

            # Print the matches
            for match in matches:
                # Extract the name and fields
                name = match[2]
                fields = match[1]
                additional = match[0]
                
                new_data = {"Name": name, "Additional": additional ,"Type": fields, "keyword":"struct"}
                data.append(new_data)
            
            #############################################################################################################
            # Find all the enum typedef declarations
            enum_typedef_pattern = r'typedef\s+enum\s*(.*)\s*\{([^}]*)\}\s*(\w+)\s*;'
            matches = re.findall(enum_typedef_pattern, c_code)

            # Print the matches
            for match in matches:
                # Extract the name and fields
                name = match[2]
                fields = match[1]
                additional = match[0]
                
                new_data = {"Name": name, "Additional": additional, "Type": fields, "keyword":"enum"}
                data.append(new_data)
            
    return data
        
###################### extract all custom named variables from our current file #####################
def GetAllCurrentCustomVars():
    data = []

    # Open the C code file
    with open(FilePath, 'r') as file:
        c_code = file.read()
    
    c_code = comment_remover(c_code) # remove comments from our main file
    
    # RegEx pattern 
    pattern = r"\b(\w+)\s+(\w+)\s*;|\b(\w+)\s+(\w+)\s*=\s*[\'\"]?(\w+)[\'\"]?\s*;"   
    matches = re.findall(pattern, c_code)
    
    AllTypeDefs = GetAllTypedef()
    
    for item1 in matches:
        count = 0
        # TOdo changed from tuple to list do required changes here 
        for item2 in AllTypeDefs:
            if item1[2] == item2['Name']:           
                new_data = {"Variable": item1[3], "Value": item1[4], "Type": item2['Type'], 'Name': item2['Name'],'Additional': item2['Additional'] , 'Keyword': item2['keyword']} #If (char var1 = 15 ;)  !! has value
                count = count + 1
            elif item1[0] == item2['Name']:           
                new_data = {"Variable": item1[1], "Type": item2['Type'], 'Name': item2['Name'],'Additional': item2['Additional'] , 'Keyword': item2['keyword']}   # if (char var1 ;)  !! has no value
                count = count + 1

        if count == 0  :
            print('Variable with unknown type - > ' + item1[3] + item1[1]) # var name will be in [3] or [1]
        elif count == 1:
            data.append(new_data)
        elif count > 1:
            data.append(new_data)

    ### NOW WE HAVE ALL TYPEDEFS AND VARS WE CHECK IF TYPEDEF IS USING ANOTHER ONE
    for typedef in AllTypeDefs:
        for type in data:
            type = type['Type'].split() # we split this to search for exact keyword in next step
            if typedef['Name'] in type:
                new_data = {"Variable": "", "Type": typedef['Type'], 'Name': typedef['Name'], 'Additional': item2['Additional'], 'Keyword': typedef['keyword']}
                data.append(new_data)

    return data


########################################### Get All Define ######################################
def Get_Define_Consts():
    define_list = []
    data = []
    
    for root, dirs, All_files in os.walk(FolderPath, topdown=False):
        files = fnmatch.filter(All_files, '*.h')
        files += fnmatch.filter(All_files, '*.c')

        for name in files:                      
            # Read C code from a file   
            with open(os.path.join(root, name), encoding='utf-8', errors='ignore') as f:
                c_code = f.read()

            ###### GET NORMAL DEFINES  #######
            # Find all the define declarations with regex pattern
            define_pattern = re.compile(r'^#define\s+\w+\s*.*$', flags=re.MULTILINE)
            defines = re.findall(define_pattern, c_code)

            # Append Results to our list
            for define in defines:
                define.replace('\t',' ') # Change tab to space for issue
                define_list.append(define)
                
    
    # Open our main c code and search for used defines
    with open(FilePath, 'r') as file:
        c_code = file.read()

    c_code = comment_remover(c_code) # remove comments from our main file
    
    for define in define_list: 
        define_with_space = define.replace("(", " (")  # we add space if "(" found just for macro (ex macro(x,y)  --> macro (x ,y) )    
        define_splitted = define_with_space.split(' ') # we plit it by space to get the first value (define name)
        
        
        if define_splitted[1] in c_code:
            # We remove all unwanted data and append to the final list like comments
            cleaning_pattern = r'\s*//.*$'
            define = re.sub(cleaning_pattern, '', define) # remove the //
            define = define.split('/*')[0].strip()        # remove the /*

            data.append(define) 

    # we search if define is using another define
    for define in define_list:    
        define_splitted = define.split(' ') # we plit it by space to get the first value (define name)
        
        for define2 in data:
            if define_splitted[1] in define2: 
                if define not in data:
                    data.append(define)
                     
              
    return data



#################### EXTRACT ALL FUNCTIONS + BODY FROM MAIN FILE ##########################
def GetAllMainFunctions():
  with open(FilePath, 'r') as f:
      content = f.readlines()

  count = 0
  pattern = r"\w*\s*\w+\s+\w+\s*\(.*?\)\s*"
  correction_pattern = r"\w*\s*\w+\s+\w+\s*\(.*?\)\s*;$"

  Functions_list = []

  for line in content:
    count += 1

    if re.match(pattern, line) and not re.match(correction_pattern, line) :
        Full_Function = ''
        opened_union = 0
        closed_union = 0
        count2 = count-1
        
        while (opened_union == 0 or opened_union != closed_union):
            opened_union += content[count2].strip().count('{')
            closed_union += content[count2].strip().count('}')
            
            Full_Function += content[count2].strip() + '\n'

            count2 += 1
        
        Functions_list.append(Full_Function) 
    
  data = []
  for match in Functions_list:
      func_body = match
      # filter and remove empty lines
      match = "\n".join(filter(lambda x: x.strip(), match.split("\n")))
         
      # EXTRACT NAME, RETURN_TYPE, ARGS
      pattern = r"(\w+)\s+(\w+)\s*\((.*?)\)\s*{.*}"
      match = re.search(pattern, match, re.DOTALL)
      
      func_name = match.group(2)
      return_type = match.group(1)
      args = match.group(3)
      args_list = [arg.strip() for arg in args.split(',')] # split args
      
      new_data = {"Function Name": func_name, "Return Type": return_type, "Arguments": args_list, "Body": func_body}
      data.append(new_data)

  return data

############## EXTRACT ALL FUNCTIONS + BODY FROM HEADERS ############

def GetAllFunctionsFromHeaders():
    data = []
    Functions_list = []
        
    # search for the full path of the file
    for root, dirs, files in os.walk(FolderPath):
        files = fnmatch.filter(files, '*.h')
        for name in files:
                   
            ##### NOW WE LOOP ON ALL FOUND HEADERS AND EXTRACT ALL FUNCTIONS
            with open(os.path.join(root, name), encoding='utf-8', errors='ignore') as f:
                content = f.readlines()
                    
            count = 0
            pattern = r"\w*\s*\w+\s+\w+\s*\(.*?\)\s*"
            correction_pattern = r"\w*\s*\w+\s+\w+\s*\(.*?\)\s*;$"

            for line in content:
                count += 1

                if re.match(pattern, line) and not re.match(correction_pattern, line) :
                    Full_Function = ''
                    opened_union = 0
                    closed_union = 0
                    count2 = count-1
                    
                    while (opened_union == 0 or opened_union != closed_union):
                        opened_union += content[count2].strip().count('{')
                        closed_union += content[count2].strip().count('}')
                        
                        Full_Function += content[count2].strip() + '\n'

                        count2 += 1
                    
                    Functions_list.append(Full_Function) 

            for match in Functions_list:

                # filter and remove empty lines
                match = "\n".join(filter(lambda x: x.strip(), match.split("\n")))

                # EXTRACT NAME, RETURN_TYPE, ARGS
                pattern = r"(\w+)\s+(\w+)\s*\((.*?)\)\s*{.*}"
                match = re.search(pattern, match, re.DOTALL)
                
                return_type = match.group(1)
                func_name = match.group(2)
                args = match.group(3)
                args_list = [arg.strip() for arg in args.split(',')] # split args
                
                new_data = {"Function Name": func_name, "Return Type": return_type, "Arguments": args_list}
                data.append(new_data)

    return data

def FunctionsToStub():
    data = []
    HeaderFuncs = GetAllFunctionsFromHeaders()
    MainFuncs = GetAllMainFunctions()
    # Function to mock found in main file and in header file
    for header in HeaderFuncs:
      for main in MainFuncs:
        if header['Function Name'] in main['Body']:
          print('Verified Function Mock Found')
          new_data = {"Function Name": header['Function Name'], "Return Type": header['Return Type'], "Arguments": header['Arguments'], "Comment": '// Verified Mock'}
          data.append(new_data)

    # Unverified Function to mock found in main only
    for main in MainFuncs:
        UnverifiedFuncToStub = re.findall(r'\b([a-zA-Z_]\w*)\s*\(([^)]*)\);', main['Body'])
        for Function in UnverifiedFuncToStub:
            new_data = {"Function Name": Function[0], "Return Type": 'void', "Arguments": [Function[1]], "Comment": '// This Mock Return Type Is Not verified'}
            data.append(new_data)
         
    return data    

# This will get our main function body as param -> check if there is functions to mock 
def GetFunctionsCallsFromArgs(FctBody):
    data = []
    function_calls = re.findall(r"\b([a-zA-Z_]\w*)\s*\(([^)]*)\);", FctBody)

    for function_call in function_calls:
        new_data = {"Function Name": function_call[0], "Arguments": function_call[1]}
        data.append(new_data)

    return data   

## GET FILE NAME
def GetFileName():
    file_name = os.path.basename(FilePath)
    return file_name

## REMOVE COMMENTS
def comment_remover(text):
    def replacer(match):
        s = match.group(0)
        if s.startswith('/'):
            return " " # note: a space and not an empty string
        else:
            return s
    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE
    )
    return re.sub(pattern, replacer, text)
