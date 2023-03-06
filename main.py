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
  
# Get all files and folders inside the given directory and extract all typedef
def GetAllTypedef():
    folder_typedef_list = []

    for root, dirs, files in os.walk(FolderPath, topdown=False):
        for name in files:
            
            # Read C code from a file   
            with open(os.path.join(root, name), "r") as f:
                c_code = f.readlines()

            for line in c_code:
                if "typedef"  in line:
                    line = line.replace(";", "")
                    line = line.replace("typedef", "")
                    folder_typedef_list.append(line)
    return(folder_typedef_list)
        
        

