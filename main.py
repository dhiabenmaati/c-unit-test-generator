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
    data = []
    # Open the C code file
    with open(FilePath, 'r') as file:
        c_code = file.read()
    
    # RegEx pattern 
    pattern = r"\b(\w+)\s+(\w+)\s*;|\b(\w+)\s+(\w+)\s*=\s*[\'\"]?(\w+)[\'\"]?\s*;"   
    matches = re.findall(pattern, c_code)
  
    AllTypeDefs = GetAllTypedef()
    
    for item1 in matches:
        count = 0
        for item2 in AllTypeDefs:
            # why we used this method !!! If (char var1 = 15 ;) Elif (char var1 ;) !!!
            if item1[2] == item2[1]:           
                new_data = {"Variable": item1[3], "Value": item1[4], "Type": item2[0], 'Custom_Name': item2[1]}
                count = count + 1
            elif item1[0] == item2[1]:           
                new_data = {"Variable": item1[1], "Type": item2[0], 'Custom_Name': item2[1]}
                count = count + 1

        if count == 0  :
            print(item1[3] + ' Has no Type' + '----------> Error In GetAllCurrentCustomVars()')
        elif count == 1:
            data.append(new_data)
        elif count > 1:
            print('Too Many Types' + '----------> Error In GetAllCurrentCustomVars()')

    return data

############################################################################################################ 


# Replace All #Define (add define at the beginning of the file)
def ReplaceAllDefine():
    define_list = []
    data = []
    
    for root, dirs, files in os.walk(FolderPath, topdown=False):
        files = fnmatch.filter(files, '*.h')
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
    
    # Open the C code file Replace All Define Then Save To .c.test file
    with open(FilePath, 'r') as file:
        c_code = file.read()
    
    for define in define_list:
        define.replace('\t',' ') # Chnage tab to space for issue
        define_splitted = define.split(' ') 
        if define_splitted[1] in c_code:
            data.append(define)
            
              
    return data



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

def FunctionsToStub():
    data = []
    HeaderFuncs = GetAllFunctionsFromHeaders()
    MainFuncs = GetAllMainFunctions()
    for header in HeaderFuncs:
      for main in MainFuncs:
        if header['Function Name'] in main['Body']:
          new_data = {"Function Name": header['Function Name'], "Return Type": header['Return Type'], "Arguments": header['Arguments']}
          data.append(new_data)
    
    return data    