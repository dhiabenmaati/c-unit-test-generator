import os
import sys
import re
import fnmatch

############################################################################################################
# Open the C code file funct in every def will be replaced with only one read at the baginning of the script
############################################################################################################

## Get Given args and check if they are correct
n = len(sys.argv)
if n == 3 :
    FilePath = sys.argv[1]       
    FolderPath = sys.argv[2]      
else :
    print("###  PLEASE CHECK YOUR ARGS ###")
    print("#### AUTOMATIC EXIT ####")
    sys.exit()

############################################################################################################  

# extract all typedef from all files
def GetAllTypedef():
    folder_typedef_list = []

    for root, dirs, files in os.walk(FolderPath, topdown=False):
        for name in files:
            
            # Regular expression pattern to match typedef declarations
            typedef_pattern = re.compile(r'typedef\s+(.+?)\s+(\w+)\s*;', re.DOTALL)
            
            # Read C code from a file   
            with open(os.path.join(root, name), "r") as f:
                c_code = f.read()

            # Find all the typedef declarations
            typedefs = re.findall(typedef_pattern, c_code)
            # Append Results to our list
            for typedef in typedefs:
                folder_typedef_list.append(typedef)

    return(folder_typedef_list)
        

# extract all custom named variables from our current file 
def GetAllCurrentCustomVars():
    # Open the C code file
    with open(FilePath, 'r') as file:
        c_code = file.read()
    
    # RegEx pattern 
    pattern = r"\b(\w+)\s+(\w+)\s*;\s*$|\b(\w+)\s+(\w+)\s*=\s*[\'\"]?(\w+)[\'\"]?\s*;"   
    matches = re.findall(pattern, c_code)
  
    AllTypeDefs = GetAllTypedef()
    
    for item1 in matches:
        count = 0
        for item2 in AllTypeDefs:
            if item1[2] == item2[1]:           
                results = item1[3] + ' Is ' + item2[0] 
                count = count + 1

        if count == 0  :
            print(item1[3] + ' Has no Type')
        elif count == 1:
            print(results)
        elif count > 1:
            print('Too Many Types')

    return matches

############################################################################################################ 


# Replace All #Define (add define at the beginning of the file)
def ReplaceAllDefine():
    define_list = []
    
    for root, dirs, files in os.walk(FolderPath, topdown=False):
        files = fnmatch.filter(files, '*.c')
        for name in files:
            # Regular expression pattern to match typedef declarations
            typedef_pattern = re.compile(r'^#define\s+\w+\s*.*$', flags=re.MULTILINE)
            
            # Read C code from a file   
            with open(os.path.join(root, name), "rb") as f:
                c_code = f.read().decode('utf-8')

            # Find all the typedef declarations
            defines = re.findall(typedef_pattern, c_code)

            # Append Results to our list
            for define in defines:
                define_list.append(define)
    print(define_list)

    # Open the C code file Replace All Define Then Save To .c.test file
    with open(FilePath, 'r') as file:
        c_code = file.read()
    
    for define in define_list:
        define.replace('\t',' ') # Chnage tab to space for issue
        define_splitted = define.split(' ') 
        if define_splitted[1] in c_code:
            c_code = define + '\n' + c_code
            

    #with open(FilePath + ".test", "w") as file:
    #    file.write(c_code)
    
    return True


#################################### FUNC EXTRACTOR #############################################################     

import sys
import re
import json

n = len(sys.argv)
if n == 3 :
    FilePath = sys.argv[1]       
    FolderPath = sys.argv[2] 
    
    # IF ARGS WITHOUT "/" ADD IT
    pattern = re.compile(r".+/$")  
    match = pattern.search(FolderPath)     
    if match:
      pass
    else:
        FolderPath = FolderPath + '/'

else :
    print("###  PLEASE CHECK YOUR ARGS ###")
    print("#### AUTOMATIC EXIT ####")
    sys.exit()


#################### EXTRACT ALL FUNCTIONS + BODY FROM MAIN FILE ##########################
def GetAllMainFunctions():
  with open(FilePath, 'r') as f:
      content = f.read()

  pattern = r'\w+\s+\w+\s*\([^)]*\)\s*\{(?:[^{}]*{(?:[^{}]*{[^{}]*}[^{}]*|[^{}])*}[^{}]*|[^{}])*?\}'
  matches = re.findall(pattern, content, re.DOTALL)

  data = []
  for match in matches:
      func_body = match
      # filter and remove empty lines
      match = "\n".join(filter(lambda x: x.strip(), match.split("\n")))

      # EXTRACT NAME, RETURN_TYPE, ARGS
      pattern = r"(\w+)\s+(\w+)\((.*?)\)\s*{.*}"
      match = re.search(pattern, match, re.DOTALL)
      
      func_name = match.group(2)
      return_type = match.group(1)
      args = match.group(3)
      args_list = [arg.strip() for arg in args.split(',')] # split args
      
      new_data = {"Function Name": func_name, "Return Type": return_type, "Arguments": args_list, "Body": func_body}
      data.append(new_data)

  return data

############## EXTRACT ALL FUNCTIONS + BODY FROM HEADERS INCLUDED IN MAIN FILE ############

def GetAllFunctionsFromHeaders():
  data = []
  with open(FilePath, 'r') as f:
      content = f.read()

  pattern = r'#include\s*[<"]([^>"]+)[>"]'
  matches = re.findall(pattern, content, re.DOTALL)

  # list of standard C headers to exclude
  exclude_headers = ['stdio.h', 'stdlib.h', 'string.h']

  for match in matches:
    if match not in exclude_headers:

        ##### NOW WE LOOP ON ALL FOUND HEADERS AND EXTRACT ALL FUNCTIONS
        with open(FolderPath + match, 'r') as f:
          content = f.read()
                  
        pattern = r'\w+\s+\w+\s*\([^)]*\)\s*\{(?:[^{}]*{(?:[^{}]*{[^{}]*}[^{}]*|[^{}])*}[^{}]*|[^{}])*?\}'
        matches = re.findall(pattern, content, re.DOTALL)

        for match in matches:
            # filter and remove empty lines
            match = "\n".join(filter(lambda x: x.strip(), match.split("\n")))

            # EXTRACT NAME, RETURN_TYPE, ARGS
            pattern = r"(\w+)\s+(\w+)\((.*?)\)\s*{.*}"
            match = re.search(pattern, match, re.DOTALL)
            
            func_name = match.group(2)
            return_type = match.group(1)
            args = match.group(3)
            args_list = [arg.strip() for arg in args.split(',')] # split args
            
            new_data = {"Function Name": func_name, "Return Type": return_type, "Arguments": args_list}
            data.append(new_data)

  return data

def FunctionsToMock():
   HeaderFuncs = GetAllFunctionsFromHeaders()
   MainFuncs = GetAllMainFunctions()
   for header in HeaderFuncs:
      for main in MainFuncs:
        if header['Function Name'] in main['Body']:
          print(header['Function Name'] + '       is used in       ' + main['Function Name'])
        
   


