import arcpy
fc=r"L:\_Common_GISTeam\MapAndDataRequests\Chris LaVoie\20211130_Map_ESTIPwebmapUpdates\Updated_eSTIP.gdb\Updated_eSTIP_Final"
fields = arcpy.ListFields(fc)
FieldNameList = []

for dom in fields:
   if dom.domain<>'':
     FieldNameList.append(dom.name)


for field in FieldNameList:
   arcpy.management.RemoveDomainFromField(fc,field)

