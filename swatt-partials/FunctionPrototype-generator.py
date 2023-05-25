import platform
import sys
from datetime import date
from jinja2 import Template
import os 
import re

# Add the root directory to the system path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
import main

  
###################### Starting The Script ##########################

## Get Given args and check if they are correct
n = len(sys.argv)
if n == 3 :
    FilePath = sys.argv[1]       
    FolderPath = sys.argv[2]
    
    file_name = main.GetFileName()    
    file_name_no_ext = file_name.rsplit(".", 1)[0] 
    
    file_path_no_ext = FilePath.rsplit(".", 1)[0]  
    
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

# This Path Technique Is used for the vs code extension to call the template.c correctly
current_path = current_path = os.path.abspath(__file__)   
current_path = os.path.dirname(current_path) + '/'


    
#################################################################
#               THE GENERATOR STARTS FROM HERE                  #
#              GENERATE All Define Const In CSV                 #
#################################################################

###################### Date And Laptop Name ##########################
Export_Date         = date.today().strftime("%B %d, %Y")          
Author_Pc_Name      = platform.node() 

####################### Functions Prototypes #########################
    
Functions_Prototypes_List    = main.GetAllMainFunctions()
Function_Prototypes = ''
for element in Functions_Prototypes_List:
        
    if element['Return Type'] == 'define':
        pass
    else:    
        Arguments = element['Arguments']
        Temp_Args = ''
        for i, Argument in enumerate(Arguments):
            if i == len(Arguments) - 1:
                Temp_Args += Argument
            else:
                Temp_Args += f"{Argument}, "

        Function_Prototypes += element['Return Type'] + ' ' + element['Function Name'] + ' (' + Temp_Args + ') ; \n'

####################### Export File ################################
text = '''
/* 
 * $Source: {{File_Name}} $
 * $Author: {{Author}} $
 * $Date: {{Export_Date}} $
 */


/*   FUNCTION PROTOTYPES   */

{{Content}}
'''
#Create a Jinja2 template
template = Template(text)

# required data will be passed here
data = {'File_Name': file_name, 
        'Author': Author_Pc_Name,
        'Export_Date': Export_Date, 
        'Content': Function_Prototypes
        }

template = template.render(data)

# export final unit test file
with open(file_path_no_ext + '-FunctionsPrototype.c.test', 'w') as f:
    f.write(template)
    

