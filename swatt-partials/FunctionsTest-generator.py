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

####################### Functions Test skeleton ######################

Function_To_Test_List    = main.GetAllMainFunctions()
Function_To_Test = ''
for element in Function_To_Test_List:
        
    if element['Return Type'] == 'define':
        pass
    else:

        Arguments = element['Arguments']
        Temp_Args = ''
            
        # STAGE 1
        Function_To_Test += '\n\n\n'
        Function_To_Test += '/* test function ' + element['Function Name'] + ' */ \n'
        Function_To_Test += 'TEST(' + file_name_no_ext + '__'+ element['Function Name'] + ') {\n\n'
        Function_To_Test += '\t/* trace information to indicate what the test covers */ \n'
        Function_To_Test += '\tTRACE(" TBD "); \n\n'
        Function_To_Test += '\t/* description information of what the test does */ \n'
        Function_To_Test += '\tDESCRIPTION(" TBD "); \n'
        Function_To_Test += '\t' + element['Return Type'] + ' ret_expected = TBD ;\n\n' 

        # STAGE 2
        if len(Arguments) > 0 : 
            Function_To_Test += '\t/* to be set the function input parameter values with proper values before the call */ \n'           
            for i, Argument in enumerate(Arguments):
                if Argument != 'void':
                    Function_To_Test +=  f"\t{Argument}; \n" 

        # STAGE 3
        function_call = main.GetFunctionsCallsFromArgs(element['Body'])
        for element_body in function_call:
            Function_To_Test += '\tmock_' + element_body['Function Name'] + '_Return()' + '; \n'

        # STAGE 4
        if len(Arguments) > 0 :           
            for i, Argument in enumerate(Arguments):
                if i == len(Arguments) - 1:
                    Temp_Args += Argument
                else:
                    Temp_Args += f"{Argument}, "
                    
        Function_To_Test += '\n\t/* the function call */ \n'
        Function_To_Test +='\t'+ element['Return Type'] + ' ' +element['Function Name'] + '_ret = ' + element['Function Name'] + '(' + Temp_Args + ') ; \n'

        # STAGE 5
        Function_To_Test += '\n'
        Function_To_Test += '\tassert( ' + element['Function Name'] + '_ret' + ' == ret_expected ); \n'

        Function_To_Test += '}'

####################### Export File ################################
text = '''
/* 
 * $Source: {{File_Name}} $
 * $Author: {{Author}} $
 * $Date: {{Export_Date}} $
 */


/*   Functions Test   */

{{Content}}
'''
#Create a Jinja2 template
template = Template(text)

# required data will be passed here
data = {'File_Name': file_name, 
        'Author': Author_Pc_Name,
        'Export_Date': Export_Date, 
        'Content': Function_To_Test
        }

template = template.render(data)

# export final unit test file
with open(file_path_no_ext + '-FunctionsTest.c.test', 'w') as f:
    f.write(template)
    

