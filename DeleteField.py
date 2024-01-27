import arcpy
fc = r"I:\TaskAssignments\FUGRO_2021\FUGRO_2021_PavementAudit\FUGRO_2021_PavementAudit.gdb\I40_2021_Base"
flds = arcpy.ListFields(fc)
ToDelete="19"

fieldNameList = []

for field in flds:
    if field.name.endswith(ToDelete):
        fieldNameList.append(field.name)

for fld in fieldNameList:
      arcpy.management.DeleteField(fc,fieldNameList)impo