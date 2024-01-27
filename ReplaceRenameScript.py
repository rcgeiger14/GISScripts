import arcpy
fc = r"I:\TaskAssignments\P2PGISWorkflow_2022\20220707_PrelimData_Round2.gdb\Bridge_Projects_gResult_GeocodeProblems_Fixed"
ToReplace="_1"
Year=""

flds = arcpy.ListFields(fc)

for fld in flds:
    fld.name.endswith(ToReplace):
	 arcpy.AlterField_management(fc, fld.name, fld.name.replace(ToReplace,Year))
   elif fld.name.endswith(ToReplace):
         arcpy.AlterField_management(fc, fld.name, fld.name.replace(ToReplace,Year))
