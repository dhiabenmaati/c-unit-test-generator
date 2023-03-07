import os
import sys
import re

## Get Given args and check if they are correct
n = len(sys.argv)
if n < 4 :
    FilePath = sys.argv[1]       
    FolderPath = sys.argv[2]      
else :
    print("### Too Many Args Given ###")
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
                temp = typedef[1] + ' : ' + typedef[0]
                folder_typedef_list.append(temp)

    return(folder_typedef_list)
        


# extract all standard variables from our current file 
def GetAllCurrentVars():
    with open(FilePath, 'r') as f:
        c_code = f.read()
    
    # RegEx pattern template to find ( type - name - value )
    pattern = r'\b(int|char|float|double)\b\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*([a-zA-Z0-9_]*)\s*;'   
    matches = re.findall(pattern, c_code)
    
    for match in matches:
        print( '  ------->  ' + match[0] + ' : ' + match[1] + ' : ' +  match[2])


# extract all functions from our current file 
def GetAllCurrentFunctions():
    # Open the C code file for reading
    with open(FilePath, 'r') as f:
        code = f.read()

    # Define a regular expression to match function definitions
    pattern = r'(?:^|\n)[a-zA-Z_][a-zA-Z0-9_]*\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\([^;]*\)'

    # Find all matches of the pattern in the code
    matches = re.findall(pattern, code)
    
    for match in matches:
        print(match)

