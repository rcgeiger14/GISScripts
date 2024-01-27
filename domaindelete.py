def DeleteDomain(fc):
   import arcpy
   fields = arcpy.ListFields(fc)
   FieldNameList = []
   for dom in fields:
      if dom.domain<>'':
      FieldNameList.append(dom.name)
   for field in FieldNameList:
      arcpy.management.RemoveDomainFromField(fc,field)

