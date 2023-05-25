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

#################### Custom Variables & Deftypes ######################
Custom_Vars_list    = main.GetAllCurrentCustomVars() 
Var_Stubs = ''
Type_Stubs = ''
for element in Custom_Vars_list:
    Var_Val_If_Exist = ' = ' + str(element.get('Value')) if element.get('Value') is not None else ''
        
    Var_Stubs += element['Name'] + ' ' + element['Variable'] + Var_Val_If_Exist + ' ' + ';' +'\n'
        
    if element['Keyword'] == 'normal':
        Type_Stubs += 'typedef' + ' ' + element['Type'] + ' ' +element['Name'] + ' ' +';' + '\n'
    elif element['Keyword'] == 'struct':
        Type_Stubs += 'typedef struct { ' + element['Type'] + ' }' + element['Name'] + ' ;' + '\n'
    elif element['Keyword'] == 'enum':
        Type_Stubs += 'typedef enum { ' + element['Type'] + ' }' + element['Name'] + ' ;' + '\n'



####################### Export File ################################
text = '''
/* 
 * $Source: {{File_Name}} $
 * $Author: {{Author}} $
 * $Date: {{Export_Date}} $
 */


/*   TYPE & vars STUBS   */

// Deftypes Stubs
{{Deftypes}}

// Vars Stubs
{{Vars}}
'''
#Create a Jinja2 template
template = Template(text)

# required data will be passed here
data = {'File_Name': file_name, 
        'Author': Author_Pc_Name,
        'Export_Date': Export_Date, 
        'Deftypes': Type_Stubs,
        'Vars': Var_Stubs
        }

template = template.render(data)

# export final unit test file
with open(file_path_no_ext + '-vars-deftypes.c.test', 'w') as f:
    f.write(template)
    

