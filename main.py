import os
import sys
import re

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
    

# extract all functions from our current file 
def GetAllCurrentFunctions():
    # Open the C code file 
    with open(FilePath, 'r') as file:
        code = file.read()

    # RegEx pattern
    function_pattern = re.compile(r'\b(\w+)\s+(\w+)\s*\((.*?)\)\s*{')
    matches = function_pattern.findall(code)

    return matches

