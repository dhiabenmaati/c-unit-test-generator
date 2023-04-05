import platform
from jinja2 import Template
from datetime import date
import main

###################### Get Date And Laptop Name #######################
Export_Date         = date.today().strftime("%B %d, %Y")          
Author_Pc_Name      = platform.node()                             
#######################################################################


####################### Get All DEFINE CONSTS #########################
DEFINE_CONSTS_STUBS_list    = main.ReplaceAllDefine()
Define_Consts = ''

for element in DEFINE_CONSTS_STUBS_list:
    Define_Consts += element 
#######################################################################


#################### Get All Custom Variables & Deftypes ##############
Custom_Vars_list    = main.GetAllCurrentCustomVars() 
Var_Stubs = ''
Type_Stubs = ''
for element in Custom_Vars_list:
    Var_Val_If_Exist = ' = ' + str(element.get('Value')) if element.get('Value') is not None else ''
    
    Var_Stubs += element['Custom_Name'] + ' ' + element['Variable'] + Var_Val_If_Exist + ' ' + ';' +'\n'
    Type_Stubs += 'typedef' + ' ' + element['Type'] + ' ' +element['Custom_Name'] + ' ' +';' + '\n'
#######################################################################


####################### Get AllFunctions To Mock ######################
Functions_To_Mock_List    = main.FunctionsToStub()
Function_Mocks = ''
rett = ''
for element in Functions_To_Mock_List:
    Function_Mocks += 'MOCK ' + element['Return Type'] + ' ' + element['Function Name'] + ' ' + '(!!!!!! TBD !!!!!)' + ' ; \n'
#######################################################################


# open the unit test template
with open('template.c', 'r') as file:
        file_contents = file.read()

#Create a Jinja2 template
template = Template(file_contents)


# required data will be passed here
data = {'File_Name': 'file1.c', 
        'Author': Author_Pc_Name,
        'Export_Date': Export_Date, 
        'Define_Consts': Define_Consts,
        'Type_Stubs': Type_Stubs, 
        'Var_Stubs': Var_Stubs, 
        'Function_Mocks': Function_Mocks 
        }

template = template.render(data)

# export final unit test file
with open('output.c.test', 'w') as f:
    f.write(template)