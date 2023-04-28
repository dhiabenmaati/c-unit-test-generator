import platform
from jinja2 import Template
from datetime import date
import main

###################### Date And Laptop Name ##########################
Export_Date         = date.today().strftime("%B %d, %Y")          
Author_Pc_Name      = platform.node()   

file_name = main.GetFileName()    
file_name_no_ext = file_name.rsplit(".", 1)[0]            
######################################################################


####################### DEFINE CONSTS ################################
DEFINE_CONSTS_STUBS_list    = main.ReplaceAllDefine()
Define_Consts = ''

for element in DEFINE_CONSTS_STUBS_list:
    Define_Consts += element 
#######################################################################


#################### Custom Variables & Deftypes ######################
Custom_Vars_list    = main.GetAllCurrentCustomVars() 
Var_Stubs = ''
Type_Stubs = ''
for element in Custom_Vars_list:
    Var_Val_If_Exist = ' = ' + str(element.get('Value')) if element.get('Value') is not None else ''
    
    Var_Stubs += element['Custom_Name'] + ' ' + element['Variable'] + Var_Val_If_Exist + ' ' + ';' +'\n'
    Type_Stubs += 'typedef' + ' ' + element['Type'] + ' ' +element['Custom_Name'] + ' ' +';' + '\n'

# To remove duplicated typedefs
Type_Stubs = list(set(Type_Stubs.split('\n')))
Type_Stubs = '\n'.join(Type_Stubs)
######################################################################

####################### Functions Mocks ###############################
Functions_To_Stub_List    = main.FunctionsToStub()
Function_Mocks = ''
for element in Functions_To_Stub_List:
    
    Arguments = element['Arguments']
    Temp_Args = ''
    for i, Argument in enumerate(Arguments):
        if i == len(Arguments) - 1:
            Temp_Args += Argument
        else:
            Temp_Args += f"{Argument}, "  
    
    Function_Mocks += 'MOCK ' + element['Return Type'] + ' ' + element['Function Name'] + ' (' + Temp_Args + ') ; \n'
#######################################################################

####################### Functions Prototypes #########################
Functions_Prototypes_List    = main.GetAllMainFunctions()
Function_Prototypes = ''
for element in Functions_Prototypes_List:
    
    Arguments = element['Arguments']
    Temp_Args = ''
    for i, Argument in enumerate(Arguments):
        if i == len(Arguments) - 1:
            Temp_Args += Argument
        else:
            Temp_Args += f"{Argument}, "

    Function_Prototypes += element['Return Type'] + ' ' + element['Function Name'] + ' (' + Temp_Args + ') ; \n'
#######################################################################

####################### Functions Test skeleton ######################
Function_To_Test_List    = main.GetAllMainFunctions()
Function_To_Test = ''
for element in Function_To_Test_List:
    
    Arguments = element['Arguments']
    Temp_Args = ''
    
    # STAGE 1
    Function_To_Test += '\n\n\n'
    Function_To_Test += '/* test function ' + element['Function Name'] + ' */ \n'
    Function_To_Test += 'TEST(' + file_name_no_ext + '__'+ element['Function Name'] + ') {\n\n'
    Function_To_Test += '\t/* trace information to indicate what the test covers */ \n'
    Function_To_Test += '\tTRACE(" TBD "); \n\n'
    Function_To_Test += '\t/* description information of what the test does */ \n'
    Function_To_Test += '\tDESCRIPTION(" TBD "); \n\n'

    # STAGE 2
    if len(Arguments) > 0 : 
        Function_To_Test += '\t/* to be set the function input parameter values with proper values before the call */ \n'           
        for i, Argument in enumerate(Arguments):
            Function_To_Test +=  f"\t{Argument}; \n" 

    # STAGE 3
    function_call = main.GetFunctionsCallsFromArgs(element['Body'])
    for element in function_call:
        Function_To_Test += '\tmock_' + element['Function Name'] + '_Return()' + '; \n'

    # STAGE 4
    if len(Arguments) > 0 : 
        Function_To_Test += '\t/* to be set the function input parameter values with proper values before the call */ \n'           
        for i, Argument in enumerate(Arguments):
            Temp_Args += f"{Argument}, "  
            Temp_Args = Temp_Args[:-1]
            
    Function_To_Test += '\t/* the function call */ \n'
    Function_To_Test +='\t' + element['Function Name'] + '(' + Temp_Args + ') ; \n'

    # STAGE 5
    Function_To_Test += '\n'
    Function_To_Test += '\tassert( TBD ); \n'

    Function_To_Test += '}'
#######################################################################


# open the unit test template
with open('template.c', 'r') as file:
        file_contents = file.read()

#Create a Jinja2 template
template = Template(file_contents)


# required data will be passed here
data = {'File_Name': file_name, 
        'Author': Author_Pc_Name,
        'Export_Date': Export_Date, 
        'Define_Consts': Define_Consts,
        'Type_Stubs': Type_Stubs, 
        'Var_Stubs': Var_Stubs, 
        'Function_Mocks': Function_Mocks,
        'Function_Prototypes': Function_Prototypes,
        'Function_To_Test': Function_To_Test
        }

template = template.render(data)

# export final unit test file
with open(file_name + '.test', 'w') as f:
    f.write(template)