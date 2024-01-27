

def TableFromExcel(csv,outpath,outname):
   import arcpy
   import pandas as pd
   arcpy.AddMessage("---CAUTION: This script currently only automates Field Name and Field Type---")
   #CSV
   df=pd.read_csv(csv)
   Type=df['Type'].tolist()
   Name=df['Name'].tolist()
   Precision=df['Precision'].tolist()
   Scale=df['Scale'].tolist()
   length=len(Name)
   dictionary = zip(Name,Type,Precision,Scale)

   arcpy.env.workspace = out_path
   arcpy.CreateFeatureclass_management(out_path,out_name,geometry_type="POLYLINE")

   arcpy.SetProgressor("step","Adding fields...",min_range=0,max_range=length)
   for key, value, precision, scale in dictionary:
      arcpy.management.AddField(out_name,key,value,field_length=int(precision),field_precision=int(precision),field_scale=int(scale))
      arcpy.SetProgressorLabel("Added {0} | {1}".format(key,value))
      arcpy.AddMessage("--Field Added--"+key+" | "+value)
      arcpy.SetProgressorPosition()
   arcpy.conversion.FeatureClassToFeatureClass(out_name, out_path, out_name)

   arcpy.AddMessage("All Fields Add")

