import platform
import sys
from jinja2 import Template
from datetime import date
import main
import os 
import re

  
###################### Starting The Script & checking ##########################

## Get Given args and check if they are correct
n = len(sys.argv)
if n == 8 :
    FilePath = sys.argv[1]       
    FolderPath = sys.argv[2]

    Defines_Condition = sys.argv[3]
    Vars_Deftype_Condition = sys.argv[4]
    FuncMock_Condition = sys.argv[5]
    FuncPrototype_Condition = sys.argv[6]
    FuncTests_Condition = sys.argv[7]

    # IF ARGS WITHOUT "/" ADD IT
    pattern = re.compile(r".+/$")  
    match = pattern.search(FolderPath)     
    if match:
      pass
    else:
        FolderPath = FolderPath + '/'
    
    file_name = main.GetFileName()    
    file_name_no_ext = file_name.rsplit(".", 1)[0]    

elif n == 3 :
    FilePath = sys.argv[1]       
    FolderPath = sys.argv[2]

    Defines_Condition = '1'
    Vars_Deftype_Condition = '1'
    FuncMock_Condition = '1'
    FuncPrototype_Condition = '1'
    FuncTests_Condition = '1'

    # IF ARGS WITHOUT "/" ADD IT
    pattern = re.compile(r".+/$")  
    match = pattern.search(FolderPath)     
    if match:
      pass
    else:
        FolderPath = FolderPath + '/'
    
    file_name = main.GetFileName()    
    file_name_no_ext = file_name.rsplit(".", 1)[0]    

else :
    print("###  PLEASE CHECK YOUR ARGS ###")
    print("#### AUTOMATIC EXIT ####")
    sys.exit()

# This Path Technique Is used for the vs code extension to call the template.c correctly
current_path = current_path = os.path.abspath(__file__)   
current_path = os.path.dirname(current_path) + '/'


#################################################################
#               THE GENERATOR STARTS FROM HERE                  #
#                   GENERATE FULL SWATT TEST                    #
#################################################################

###################### Date And Laptop Name ##########################
Export_Date         = date.today().strftime("%B %d, %Y")          
Author_Pc_Name      = platform.node() 

####################### DEFINE CONSTS ################################
if Defines_Condition == '1':
    print('Extracting Defines')
    DEFINE_CONSTS_STUBS_list    = main.Get_Define_Consts()
    Define_Consts = ''

    for element in DEFINE_CONSTS_STUBS_list:
        Define_Consts += element + '\n'

    # To remove duplicated DEFINE
    Define_Consts = list(set(Define_Consts.split('\n')))
    Define_Consts = '\n'.join(Define_Consts)
else:
    Define_Consts = '/*=== BYPASSED ===*/'
#######################################################################


#################### Custom Variables & Deftypes ######################
if Vars_Deftype_Condition == '1' :
    print('Extracting Vars & Deftypes')
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
else:
    Var_Stubs = '/*=== BYPASSED ===*/'
    Type_Stubs = '/*=== BYPASSED ===*/'
######################################################################

####################### Functions Mocks ###############################
if FuncMock_Condition == '1' :
    print('Generating Func Mocks')
    Functions_To_Stub_List    = main.FunctionsToStub()
    Function_Mocks = ''
    for element in Functions_To_Stub_List:
        
        Arguments = element['Arguments']
        Temp_Args = ''
        for i, Argument in enumerate(Arguments):
            if i == len(Arguments) - 1:
                Temp_Args += Argument
            else:
                Temp_Args += Argument + ', '  
        
        Function_Mocks += '\nMOCK ' + element['Return Type'] + ' ' + element['Function Name'] + ' (' + Temp_Args + ') ;  ' + element['Comment'] + '\n'

        # To remove duplicated DEFINE
        Function_Mocks = list(set(Function_Mocks.split('\n')))
        Function_Mocks = '\n'.join(Function_Mocks)
else:
    Function_Mocks = '/*=== BYPASSED ===*/'        
#######################################################################

####################### Functions Prototypes #########################
if FuncPrototype_Condition == '1' :
    print('Generating Func Prototypes')
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
else:
    Function_Prototypes = '/*=== BYPASSED ===*/'  
#######################################################################

####################### Functions Test skeleton ######################
if FuncTests_Condition == '1' :
    print('Generating Func Test')
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
else:
    Function_To_Test = '/*=== BYPASSED ===*/' 
#######################################################################


# open the unit test template
with open(current_path + 'template.c', 'r') as file:
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
with open(FilePath + '.test', 'w') as f:
    f.write(template)