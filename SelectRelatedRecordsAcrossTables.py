
def SelectTable(Table,Field,targetTable,targetField):
#import modules needed
  import arcpy, string

  # Add DBMS-specific field delimiters
  fieldDelimited = arcpy.AddFieldDelimiters(arcpy.Describe(Table).path, Field)

  # Determine field type
  fieldType = arcpy.ListFields(Table, Field)[0].type

  # Set the SearchCursor to look through the selection of the sourceTable
  sourceIDs = set([row[0] for row in arcpy.da.SearchCursor(Table, Field)])

  # Add single-quotes for string field values
  if str(fieldType) == 'String' or str(fieldType) == 'Guid':
    sourceIDs = ["'%s'" % value for value in sourceIDs]

  # Format WHERE clause in the form of an IN statement
  whereClause = "%s IN(%s)" % (fieldDelimited, ', '.join(map(str, sourceIDs)))


  # Process: Select Layer By Attribute
  arcpy.SelectLayerByAttribute_management(targetTable, "NEW_SELECTION", whereClause)

  # Set output parameters
  arcpy.SetParameterAsText(4, whereClause)
  arcpy.SetParameterAsText(5, True)
  arcpy.SetParameter(6, targetTable)
