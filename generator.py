import platform
from jinja2 import Template
from datetime import date

###################### Function calls goes here #######################
Export_Date = date.today().strftime("%B %d, %Y")    # GEt Date
Author_Pc_Name = platform.node()                    # Get laptop Name


# open the unit test template
with open('template.c', 'r') as file:
        file_contents = file.read()

#Create a Jinja2 template
template = Template(file_contents)


# required data will be passed here
data = {'File_Name': 'file1.c', 'Author': Author_Pc_Name,'Export_Date': Export_Date }
template = template.render(data)

# export final unit test file
with open('output.c', 'w') as f:
    f.write(template)