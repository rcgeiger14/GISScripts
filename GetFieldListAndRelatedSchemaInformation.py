
def GetSchemaInfo(mydir):
   import arcpy
   import pandas as pd
   import os
   os.chdir(mydir)
   arcpy.env.workspace = mydir
   
   desc=arcpy.Describe(r'I:\TaskAssignments\P2PGISWorkflow_2022\20220808_DataBTable_Review\P2P2022_Bridge_Final.gdb\P2P2022_Bridge_Input_FC_Lines')
   fields=desc.fields
   fieldlist=[]
   for field in fields:
      fieldlist.append(str(field.name) + ',' + field.aliasName + ',' + field.type + ',' + str(field.length) + ',' + str(field.precision) + ',' + str(field.scale) + ',' + str(field.required) + ',' + str(field.isNullable) + ',' + str(field.domain) + ',' + str(field.editable))
   DF=pd.DataFrame(fieldlist)
   DF.to_csv(r"I:\Data\ArcView_ft\X_Custom\Reid\test.csv")
