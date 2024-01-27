def FindReplace(fc,toreplace,insert):
    import arcpy
    flds = arcpy.ListFields(fc)
    for fld in flds:
        if fld.name.endswith(toreplace):
	        arcpy.AlterField_management(fc, fld.name, fld.name.replace(toreplace,insert))
