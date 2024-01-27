# ---------------------------------------------------------------------------
# Geocode_PreProcessing_1118.py
# Created on: 2021-11-18 08:44:20.00000
# Usage: To prepare spreadsheet of modernization and expansion projects for 
#        processing in GIS
# Description:
#   Inputs:
#       1. Excel spreadsheet of modernization and expansion projects
#	2. Selection of Excel workbook sheet(s) for pre-processing
#       3. Workspace (i.e., output gdb)
#   Outputs: 
#       1. File geodatabase table of modernization and expansion projects
# ---------------------------------------------------------------------------

import arcpy
arcpy.env.overwriteOutput = True

# Script arguments
project_wb = arcpy.GetParameterAsText(0)
wb_sheet = arcpy.GetParameterAsText(1)
ws = arcpy.GetParameterAsText(2)

# Local variables
output_project_tables = []

# ---------------------------------------------------------------------------
# Convert Excel spreadsheet to file geodatabase table
# ---------------------------------------------------------------------------

project_type_list = wb_sheet.split(";")
for i in project_type_list:
    output_project_table = ws + "\\" + i + "_Projects"
    arcpy.ExcelToTable_conversion(project_wb, output_project_table, i)
    output_project_tables.append(output_project_table)

arcpy.AddMessage("Created file geodatabase tables")

# ---------------------------------------------------------------------------
# Concatenate route ID into a single field
# ---------------------------------------------------------------------------

for i in output_project_tables:
    arcpy.AddField_management(i, "Route_Concat", "TEXT", "", "", "32", "", "NULLABLE", "NON_REQUIRED", "")
    arcpy.CalculateField_management(i, "Route_Concat", "[F_Route_Name] & [F_Route__]", "VB", "")

arcpy.AddMessage("Concatenated route ID into single field")

# ---------------------------------------------------------------------------
# Parse mileposts into mileposts and milepost offsets
# ---------------------------------------------------------------------------

for i in output_project_tables:
    arcpy.AddField_management(i, "FromMP_MP", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
    arcpy.CalculateField_management(i, "FromMP_MP", "calcFromMP( !F_From_Milepost! )", "PYTHON_9.3", "def calcFromMP(fromMP):\\n\\n  if str(fromMP) == None:\\n    return None\\n\\n  elif str(fromMP) == \"\":\\n    return None\\n\\n  elif str(fromMP)[0].isdigit():\\n    return math.floor(float(fromMP))\\n\\n  else:\\n    return None")
    arcpy.AddField_management(i, "FromMP_Offset", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
    arcpy.CalculateField_management(i, "FromMP_Offset", "calcFromMP( !F_From_Milepost! )", "PYTHON_9.3", "def calcFromMP(fromMP):\\n\\n  if str(fromMP) == None:\\n    return None\\n\\n  elif (fromMP) == \"\":\\n    return None\\n\\n  elif str(fromMP)[0].isdigit():\\n    return float(fromMP) - math.floor(float(fromMP))\\n\\n  else:\\n    return None")

    arcpy.AddField_management(i, "ToMP_MP", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
    arcpy.CalculateField_management(i, "ToMP_MP", "calcToMP( !F_To_Milepost! )", "PYTHON_9.3", "def calcToMP(toMP):\\n\\n  if str(toMP) == None:\\n    return None\\n\\n  elif str(toMP) == \"\":\\n    return None\\n\\n  elif str(toMP)[0].isdigit():\\n    return math.floor(float(toMP))\\n\\n  else:\\n    return None")
    arcpy.AddField_management(i, "ToMP_Offset", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
    arcpy.CalculateField_management(i, "ToMP_Offset", "calcToMP( !F_To_Milepost! )", "PYTHON_9.3", "def calcToMP(toMP):\\n\\n  if str(toMP) == None:\\n    return None\\n\\n  elif str(toMP) == \"\":\\n    return None\\n\\n  elif str(toMP)[0].isdigit():\\n    return float(toMP) - math.floor(float(toMP))\\n\\n  else:\\n    return None")

arcpy.AddMessage("Parsed mileposts")

# ---------------------------------------------------------------------------
# Create unique ID for processing purposes
# ---------------------------------------------------------------------------

for i in output_project_tables:
    arcpy.AddField_management(i, "UniqueIDCalced", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
    arcpy.CalculateField_management(i, "UniqueIDCalced", "str(!Unique_ID!)+ \"_\" + str(!Route_Concat!) + \"_\" + str( !F_From_Milepost!)+ \"_\" + str( !F_To_Milepost!)", "PYTHON_9.3", "")

arcpy.AddMessage("Created Unique ID for geocoding GIS processing")

