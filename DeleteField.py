def RemoveField(fc,flds,todelete):
    import arcpy
    fieldtoremove = []
    flds = arcpy.ListFields(fc)
    for field in flds:
        if field.name.endswith(todelete):
            fieldtoremove.append(field.name)
    for fld in fieldtoremove:
      arcpy.management.DeleteField(fc,fieldtoremove)