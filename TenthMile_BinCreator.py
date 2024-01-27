import arcpy
import os

in_table = arcpy.GetParameterAsText(0)
in_RouteIDFieldname = arcpy.GetParameterAsText(1)
in_fromMsFieldname = arcpy.GetParameterAsText(2)
in_toMsFieldname = arcpy.GetParameterAsText(3)
in_maxDelta = arcpy.GetParameterAsText(4)
out_table = arcpy.GetParameterAsText(5)
arcpy.env.overwriteOutput = True

row = None
rows = None
newRow = None
insertCursor = None

try:
    if (float(in_maxDelta) == 0):
        raise ValueError('The maximum measure delta cannot be a value of zero')

    arcpy.CreateTable_management(os.path.dirname(out_table), os.path.basename(out_table), '')
    arcpy.AddField_management(out_table, in_fromMsFieldname, "DOUBLE", 9, "", "", "", "NULLABLE", "NON_REQUIRED")
    arcpy.AddField_management(out_table, in_toMsFieldname, "DOUBLE", 9, "", "", "", "NULLABLE", "NON_REQUIRED")
    arcpy.AddField_management(out_table, in_RouteIDFieldname, "TEXT", 9, "", "", "", "NULLABLE", "NON_REQUIRED")
    arcpy.AddField_management(out_table, "HPMS_BinID", "TEXT", 50, "", "", "", "NULLABLE", "NON_REQUIRED")

    insertCursor = arcpy.InsertCursor(out_table)

    desc = arcpy.Describe(in_table)
    oidFieldname = desc.OIDFieldName

    arcpy.AddMessage('Finished - Creating Shell Table @ {0}..... Now beginning Segmentation.'.format(out_table))
    rowCount = int(arcpy.GetCount_management(in_table).getOutput(0))
    arcpy.SetProgressor('step','{0} by {1} feet... please wait..'.format(in_table,str(in_maxDelta)), 0, rowCount, 1)
    rows = arcpy.SearchCursor(in_table)
    
    for row in rows:
        iteration = 1 #Setup the iteration counter (to be used in HPMS Bin naming)
        oid = row.getValue(oidFieldname)
        route = row.getValue(in_RouteIDFieldname)
        fMs = row.getValue(in_fromMsFieldname)
        tMs = row.getValue(in_toMsFieldname)
        arcpy.AddMessage(str(route) + ': ' + str(fMs) + ' -> ' + str(tMs))
        incrementValue = (float(in_maxDelta)/ 5280.00)
        fromMs = fMs
        continueLooping = True  
        while continueLooping:
            toMs = fromMs + incrementValue
            if ((toMs - fMs*5280)<.11):
                toMs = tMs
            arcpy.AddMessage('     ' + str(fromMs) + ' -> ' + str(toMs))
            hpmsBin = "{0}_{1}".format(route, str(int(math.ceil(toMs * 10))))
            newRow = insertCursor.newRow()
            newRow.setValue(in_RouteIDFieldname, route)
            newRow.setValue(in_fromMsFieldname, fromMs)
            newRow.setValue(in_toMsFieldname, toMs)
            newRow.setValue("HPMS_BinID", hpmsBin)
            insertCursor.insertRow(newRow)
            iteration += 1
            fromMs = toMs
            continueLooping = fromMs < tMs if incrementValue > 0 else fromMs > tMs
        arcpy.SetProgressorPosition()
except Exception as e:
    arcpy.AddError('Exception: %s' % e)
    if row:
        arcpy.AddWarning('Offending Row: %s' % row.getValue(oidFieldname))
    if not arcpy.GetMessages() == "":
        arcpy.AddMessage(arcpy.GetMessages(2))
        print arcpy.GetMessages(2)
    else:
        #arcpy.AddMessage("Unknown Error")
        #print "Unknown Error"    
        arcpy.AddMessage(e.message)
        print e.message        
finally:
    del row
    del rows
    del newRow
    del insertCursor
    arcpy.ResetProgressor()