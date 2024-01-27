# ---------------------------------------------------------------------------
# Geocode_UpdateProjects_1108.py
# Created on: 2021-11-08 16:26:24.00000
# Usage: To endow geocoded modernization and expansion projects with weighted
#        AADT values, dominant functional classification, and calculated
#        T-Factor
# Description:
#   Inputs:
#       1. Overlay of AADT, Traffic Section, and Functional Classification
#       2. ADOT T-Factor AADT Publication spreadsheet
#       3. Feature class of geocoded modernization or expansion projects
#       4. Workspace (i.e., output gdb)
#   Outputs: Columns for
#       1. Weighted_AADT
#       2. Weighted_AADT_Single
#       3. Weighted_AADT_Combo
#       4. TrafficSectionId
#       5. FunctionalClass
#       6. FunctionalClass_Description
#       7. TFactor_Rounded_Avg
# ---------------------------------------------------------------------------

import arcpy
arcpy.env.overwriteOutput = True

# Script arguments
Overlay = arcpy.GetParameterAsText(0)
if Overlay == '#' or not Overlay:
    Overlay = "I:\\TaskAssignments\\P2PGISWorkflow_2021\\Geocode_DataItemsForSteven_20210817\\EndowedGeocodedLayers_20210827\\EndowedGeocodedLayers_20210827.gdb\\Overlay_AADT_Single_Combo_Traffic_Func_Table_0827" 
# provide a default value if unspecified

TFactor_AADT_Publication = arcpy.GetParameterAsText(1)
if TFactor_AADT_Publication == '#' or not TFactor_AADT_Publication:
    TFactor_AADT_Publication = "I:\\TaskAssignments\\P2PGISWorkflow_2021\\Geocode_UpdatedProjects_20210930\\Geocode_UpdatedProjects_20210930.gdb\\TFactor_AADTPublication" 
# provide a default value if unspecified

geocode_projects = arcpy.GetParameterAsText(2)
ws = arcpy.GetParameterAsText(3)

# Local variables
Overlay_Geocode_Intersect = ws + "\Overlay_Geocode_Intersect"
Output_Event_Table_Properties = "geocode_onRoad_ATIS LINE geocode_fromRoutePoint_M geocode_toRoutePoint_M"
SummaryStats_Geocode = ws + "\SummaryStats_Geocode"
SummaryStats_Geocode_TrafficSection_1 = ws + "\SummaryStats_Geocode_TrafficSection_1"
SummaryStats_Geocode_TrafficSection_2 = ws + "\SummaryStats_Geocode_TrafficSection_2"
SummaryStats_Geocode_TrafficSection_Table = "SummaryStats_Geocode_TrafficSection"
SummaryStats_Geocode_FuncClass_1 = ws + "\SummaryStats_Geocode_FuncClass_1"
SummaryStats_Geocode_FuncClass_2 = ws + "\SummaryStats_Geocode_FuncClass_2"
SummaryStats_FuncClass_Table = "SummaryStats_Geocode_FuncClass"
FuncClass_Description = "FuncClass_Description"
SummaryStats_TFactor = ws + "\SummaryStats_TFactor"

# ---------------------------------------------------------------------------
# Endow all weighted AADT values
# ---------------------------------------------------------------------------

# Process: Table to Table
Geocode_UpdatedProjects_TabletoTable = arcpy.TableToTable_conversion(geocode_projects, ws, "Geocode_UpdatedProjects_TabletoTable")

# Process: Overlay Route Events
arcpy.OverlayRouteEvents_lr(Geocode_UpdatedProjects_TabletoTable, "geocode_onRoad_ATIS LINE geocode_fromRoutePoint_M geocode_toRoutePoint_M", Overlay, "route_id LINE from_measure to_measure", "INTERSECT", Overlay_Geocode_Intersect, Output_Event_Table_Properties, "ZERO", "FIELDS", "INDEX")

# Process: Add Field
arcpy.AddField_management(Overlay_Geocode_Intersect, "Overlay_Length", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

# Process: Calculate Field
arcpy.CalculateField_management(Overlay_Geocode_Intersect, "Overlay_Length", "( [geocode_toRoutePoint_M] - [geocode_fromRoutePoint_M] ) * 5280", "VB", "")

# Process: Add Field (2)
arcpy.AddField_management(Overlay_Geocode_Intersect, "Weighted_AADT", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

# Process: Calculate Field (2)
arcpy.CalculateField_management(Overlay_Geocode_Intersect, "Weighted_AADT", "( [Overlay_Length] / [Shape_Length] ) * [AADT]", "VB", "")

# Process: Add Field (3)
arcpy.AddField_management(Overlay_Geocode_Intersect, "Weighted_AADT_Single", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

# Process: Calculate Field (3)
arcpy.CalculateField_management(Overlay_Geocode_Intersect, "Weighted_AADT_Single", "( [Overlay_Length] / [Shape_Length] ) * [AADTSingleUnit]", "VB", "")

# Process: Add Field (4)
arcpy.AddField_management(Overlay_Geocode_Intersect, "Weighted_AADT_Combo", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

# Process: Calculate Field (4)
arcpy.CalculateField_management(Overlay_Geocode_Intersect, "Weighted_AADT_Combo", "( [Overlay_Length] / [Shape_Length] ) * [AADTCombination]", "VB", "")

# Process: Summary Statistics
arcpy.Statistics_analysis(Overlay_Geocode_Intersect, SummaryStats_Geocode, "Weighted_AADT SUM;Weighted_AADT_Single SUM;Weighted_AADT_Combo SUM", "UniqueIDCalced")

# Process: Join Field
arcpy.JoinField_management(geocode_projects, "UniqueIDCalced", SummaryStats_Geocode, "UniqueIDCalced", "SUM_Weighted_AADT;SUM_Weighted_AADT_Single;SUM_Weighted_AADT_Combo")

# Process: Add Field (5)
arcpy.AddField_management(geocode_projects, "Weighted_AADT", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

# Process: Calculate Field (5)
arcpy.CalculateField_management(geocode_projects, "Weighted_AADT", "[SUM_Weighted_AADT]", "VB", "")

# Process: Add Field (6)
arcpy.AddField_management(geocode_projects, "Weighted_AADT_Single", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

# Process: Calculate Field (6)
arcpy.CalculateField_management(geocode_projects, "Weighted_AADT_Single", "[SUM_Weighted_AADT_Single]", "VB", "")

# Process: Add Field (7)
arcpy.AddField_management(geocode_projects, "Weighted_AADT_Combo", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

# Process: Calculate Field (7)
arcpy.CalculateField_management(geocode_projects, "Weighted_AADT_Combo", "[SUM_Weighted_AADT_Combo]", "VB", "")

# Process: Delete Field
arcpy.DeleteField_management(geocode_projects, "SUM_Weighted_AADT;SUM_Weighted_AADT_Single;SUM_Weighted_AADT_Combo")

arcpy.AddMessage("Weighted AADT values added")

# ---------------------------------------------------------------------------
# Endow traffic section and functional classification
# ---------------------------------------------------------------------------

# Process: Summary Statistics
arcpy.Statistics_analysis(Overlay_Geocode_Intersect, SummaryStats_Geocode_TrafficSection_1, "Overlay_Length SUM", "UniqueIDCalced;TrafficSectionId")

# Process: Add Field
arcpy.AddField_management(SummaryStats_Geocode_TrafficSection_1, "TEMP_JOIN_ID", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

# Process: Calculate Field
arcpy.CalculateField_management(SummaryStats_Geocode_TrafficSection_1, "TEMP_JOIN_ID", "[UniqueIDCalced] & [SUM_Overlay_Length]", "VB", "")

# Process: Make Table View
arcpy.MakeTableView_management(SummaryStats_Geocode_TrafficSection_1, SummaryStats_Geocode_TrafficSection_Table, "", "", "UniqueIDCalced UniqueIDCalced VISIBLE NONE;TrafficSectionId TrafficSectionId VISIBLE NONE;FREQUENCY FREQUENCY VISIBLE NONE;SUM_Overlay_Length SUM_Overlay_Length VISIBLE NONE;TEMP_JOIN_ID TEMP_JOIN_ID VISIBLE NONE")

# Process: Summary Statistics (2)
arcpy.Statistics_analysis(SummaryStats_Geocode_TrafficSection_1, SummaryStats_Geocode_TrafficSection_2, "SUM_Overlay_Length MAX", "UniqueIDCalced")

# Process: Add Field (2)
arcpy.AddField_management(SummaryStats_Geocode_TrafficSection_2, "TEMP_JOIN_ID", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

# Process: Calculate Field (2)
arcpy.CalculateField_management(SummaryStats_Geocode_TrafficSection_2, "TEMP_JOIN_ID", "[UniqueIDCalced] & [MAX_SUM_Overlay_Length]", "VB", "")

# Process: Add Join
arcpy.AddJoin_management(SummaryStats_Geocode_TrafficSection_Table, "TEMP_JOIN_ID", SummaryStats_Geocode_TrafficSection_2, "TEMP_JOIN_ID", "KEEP_COMMON")

# Process: Join Field
tempEnvironment0 = arcpy.env.transferDomains
arcpy.env.transferDomains = "false"
arcpy.JoinField_management(geocode_projects, "UniqueIDCalced", SummaryStats_Geocode_TrafficSection_Table, "SummaryStats_Geocode_TrafficSection_1.UniqueIDCalced", "SummaryStats_Geocode_TrafficSection_1.TrafficSectionId")
arcpy.env.transferDomains = tempEnvironment0

arcpy.AddMessage("Traffic Section ID added")

# Process: Summary Statistics (3)
arcpy.Statistics_analysis(Overlay_Geocode_Intersect, SummaryStats_Geocode_FuncClass_1, "Overlay_Length SUM", "UniqueIDCalced;FunctionalClass")

# Process: Add Field (3)
arcpy.AddField_management(SummaryStats_Geocode_FuncClass_1, "TEMP_JOIN_ID", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

# Process: Calculate Field (3)
arcpy.CalculateField_management(SummaryStats_Geocode_FuncClass_1, "TEMP_JOIN_ID", "[UniqueIDCalced] & [SUM_Overlay_Length]", "VB", "")

# Process: Make Table View (2)
arcpy.MakeTableView_management(SummaryStats_Geocode_FuncClass_1, SummaryStats_FuncClass_Table, "", "", "UniqueIDCalced UniqueIDCalced VISIBLE NONE;FunctionalClass FunctionalClass VISIBLE NONE;FREQUENCY FREQUENCY VISIBLE NONE;SUM_Overlay_Length SUM_Overlay_Length VISIBLE NONE;TEMP_JOIN_ID TEMP_JOIN_ID VISIBLE NONE")

# Process: Summary Statistics (4)
arcpy.Statistics_analysis(SummaryStats_Geocode_FuncClass_1, SummaryStats_Geocode_FuncClass_2, "SUM_Overlay_Length MAX", "UniqueIDCalced")

# Process: Add Field (4)
arcpy.AddField_management(SummaryStats_Geocode_FuncClass_2, "TEMP_JOIN_ID", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

# Process: Calculate Field (4)
arcpy.CalculateField_management(SummaryStats_Geocode_FuncClass_2, "TEMP_JOIN_ID", "[UniqueIDCalced] & [MAX_SUM_Overlay_Length]", "VB", "")

# Process: Add Join (2)
tempEnvironment0 = arcpy.env.transferDomains
arcpy.env.transferDomains = "false"
tempEnvironment1 = arcpy.env.qualifiedFieldNames
arcpy.env.qualifiedFieldNames = "true"
arcpy.AddJoin_management(SummaryStats_FuncClass_Table, "TEMP_JOIN_ID", SummaryStats_Geocode_FuncClass_2, "TEMP_JOIN_ID", "KEEP_COMMON")
arcpy.env.transferDomains = tempEnvironment0
arcpy.env.qualifiedFieldNames = tempEnvironment1

# Process: Join Field (2)
tempEnvironment0 = arcpy.env.transferDomains
arcpy.env.transferDomains = "false"
tempEnvironment1 = arcpy.env.qualifiedFieldNames
arcpy.env.qualifiedFieldNames = "true"
arcpy.JoinField_management(geocode_projects, "UniqueIDCalced", SummaryStats_FuncClass_Table, "SummaryStats_Geocode_FuncClass_1.UniqueIDCalced", "SummaryStats_Geocode_FuncClass_1.FunctionalClass")
arcpy.env.transferDomains = tempEnvironment0
arcpy.env.qualifiedFieldNames = tempEnvironment1

# Process: Alter Field
tempEnvironment0 = arcpy.env.transferDomains
arcpy.env.transferDomains = "false"
tempEnvironment1 = arcpy.env.qualifiedFieldNames
arcpy.env.qualifiedFieldNames = "true"
arcpy.AlterField_management(geocode_projects, "SummaryStats_Geocode_TrafficSection_1_TrafficSectionId", "TrafficSectionId", "TrafficSectionId", "", "25", "NON_NULLABLE", "false")
arcpy.env.transferDomains = tempEnvironment0
arcpy.env.qualifiedFieldNames = tempEnvironment1

# Process: Alter Field (2)
tempEnvironment0 = arcpy.env.transferDomains
arcpy.env.transferDomains = "false"
tempEnvironment1 = arcpy.env.qualifiedFieldNames
arcpy.env.qualifiedFieldNames = "true"
arcpy.AlterField_management(geocode_projects, "SummaryStats_Geocode_FuncClass_1_FunctionalClass", "FunctionalClass", "FunctionalClass", "", "2", "NON_NULLABLE", "false")
arcpy.env.transferDomains = tempEnvironment0
arcpy.env.qualifiedFieldNames = tempEnvironment1

arcpy.AddMessage("Functional classification added")

# ---------------------------------------------------------------------------
# Add functional classification text descriptions
# ---------------------------------------------------------------------------

# Process: Make Feature Layer
arcpy.MakeFeatureLayer_management(geocode_projects, FuncClass_Description, "", "", "OBJECTID OBJECTID VISIBLE NONE;Shape Shape VISIBLE NONE;OBJECTID_in OBJECTID_in VISIBLE NONE;Unique_ID Unique_ID VISIBLE NONE;F_Route_Name F_Route_Name VISIBLE NONE;F_Route__ F_Route__ VISIBLE NONE;Route_Concat Route_Concat VISIBLE NONE;Alt__Spur_Bus_ Alt__Spur_Bus_ VISIBLE NONE;Functional_Classification Functional_Classification VISIBLE NONE;Direction Direction VISIBLE NONE;F_From_Milepost F_From_Milepost VISIBLE NONE;FromMP_MP FromMP_MP VISIBLE NONE;FromMP_Offset FromMP_Offset VISIBLE NONE;F_To_Milepost F_To_Milepost VISIBLE NONE;ToMP_MP ToMP_MP VISIBLE NONE;ToMP_Offset ToMP_Offset VISIBLE NONE;Length Length VISIBLE NONE;County County VISIBLE NONE;COG_MPO COG_MPO VISIBLE NONE;District District VISIBLE NONE;F_Nomination_Source F_Nomination_Source VISIBLE NONE;F_Project_Name F_Project_Name VISIBLE NONE;Technical_Group Technical_Group VISIBLE NONE;Scope_of_Work Scope_of_Work VISIBLE NONE;field field VISIBLE NONE;F2021_Technical_Rank F2021_Technical_Rank VISIBLE NONE;F2021_Technical_Score F2021_Technical_Score VISIBLE NONE;Policy_Score Policy_Score VISIBLE NONE;Ave_Weighted_LOSS_Score__1_4_ Ave_Weighted_LOSS_Score__1_4_ VISIBLE NONE;Safety_Score Safety_Score VISIBLE NONE;District_Rank District_Rank VISIBLE NONE;District_Score District_Score VISIBLE NONE;Total_Score Total_Score VISIBLE NONE;Statewide_Rank Statewide_Rank VISIBLE NONE;Scoping_Cost_Estimate Scoping_Cost_Estimate VISIBLE NONE;Design_Cost_Estimate Design_Cost_Estimate VISIBLE NONE;Construction_Cost_Estimate Construction_Cost_Estimate VISIBLE NONE;F_Total_Estimated_Cost____ F_Total_Estimated_Cost____ VISIBLE NONE;Investment_Category Investment_Category VISIBLE NONE;Comments Comments VISIBLE NONE;Last_Updated__6_25_21 Last_Updated__6_25_21 VISIBLE NONE;UniqueIDCalced UniqueIDCalced VISIBLE NONE;Weighted_AADT Weighted_AADT VISIBLE NONE;Weighted_AADT_Single Weighted_AADT_Single VISIBLE NONE;Weighted_AADT_Combo Weighted_AADT_Combo VISIBLE NONE;geocode_onRoad_ATIS geocode_onRoad_ATIS VISIBLE NONE;geocode_onRoadCard geocode_onRoadCard VISIBLE NONE;geocode_onRoadName geocode_onRoadName VISIBLE NONE;geocode_onRoadRouteSubtype geocode_onRoadRouteSubtype VISIBLE NONE;geocode_fromId geocode_fromId VISIBLE NONE;geocode_fromOffset geocode_fromOffset VISIBLE NONE;geocode_fromType geocode_fromType VISIBLE NONE;geocode_fromRoutePoint_X geocode_fromRoutePoint_X VISIBLE NONE;geocode_fromRoutePoint_Y geocode_fromRoutePoint_Y VISIBLE NONE;geocode_fromRoutePoint_M geocode_fromRoutePoint_M VISIBLE NONE;geocode_fromSnappedRouteBearing geocode_fromSnappedRouteBearing VISIBLE NONE;geocode_fromRoutePart geocode_fromRoutePart VISIBLE NONE;geocode_toId geocode_toId VISIBLE NONE;geocode_toOffset geocode_toOffset VISIBLE NONE;geocode_toType geocode_toType VISIBLE NONE;geocode_toRoutePoint_X geocode_toRoutePoint_X VISIBLE NONE;geocode_toRoutePoint_Y geocode_toRoutePoint_Y VISIBLE NONE;geocode_toRoutePoint_M geocode_toRoutePoint_M VISIBLE NONE;geocode_toSnappedRouteBearing geocode_toSnappedRouteBearing VISIBLE NONE;geocode_toRoutePart geocode_toRoutePart VISIBLE NONE;geocode_fromSnappedLowestMarker geocode_fromSnappedLowestMarker VISIBLE NONE;geocode_fromSnappedHighestMarker geocode_fromSnappedHighestMarker VISIBLE NONE;geocode_toSnappedLowestMarker geocode_toSnappedLowestMarker VISIBLE NONE;geocode_toSnappedHighestMarker geocode_toSnappedHighestMarker VISIBLE NONE;geocode_problems geocode_problems VISIBLE NONE;Shape_Length Shape_Length VISIBLE NONE;TrafficSectionId TrafficSectionId VISIBLE NONE;FunctionalClass FunctionalClass VISIBLE NONE")

# Process: Add Field
arcpy.AddField_management(FuncClass_Description, "FunctionalClass_Description", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

# Process: Select Layer By Attribute
arcpy.SelectLayerByAttribute_management(FuncClass_Description, "NEW_SELECTION", "FunctionalClass = 1")

# Process: Calculate Field
arcpy.CalculateField_management(FuncClass_Description, "FunctionalClass_Description", "\"Rural Principal Arterial - Interstate\"", "VB", "")

# Process: Select Layer By Attribute (2)
arcpy.SelectLayerByAttribute_management(FuncClass_Description, "NEW_SELECTION", "FunctionalClass = 2")

# Process: Calculate Field (2)
arcpy.CalculateField_management(FuncClass_Description, "FunctionalClass_Description", "\"Rural Principal Arterial - Other\"", "VB", "")

# Process: Select Layer By Attribute (3)
arcpy.SelectLayerByAttribute_management(FuncClass_Description, "NEW_SELECTION", "FunctionalClass = 3")

# Process: Calculate Field (3)
arcpy.CalculateField_management(FuncClass_Description, "FunctionalClass_Description", "\"Rural Principal Arterial - Other Fwys & Expwys\"", "VB", "")

# Process: Select Layer By Attribute (4)
arcpy.SelectLayerByAttribute_management(FuncClass_Description, "NEW_SELECTION", "FunctionalClass = 6")

# Process: Calculate Field (4)
arcpy.CalculateField_management(FuncClass_Description, "FunctionalClass_Description", "\"Rural Minor Arterial\"", "VB", "")

# Process: Select Layer By Attribute (5)
arcpy.SelectLayerByAttribute_management(FuncClass_Description, "NEW_SELECTION", "FunctionalClass = 7")

# Process: Calculate Field (5)
arcpy.CalculateField_management(FuncClass_Description, "FunctionalClass_Description", "\"Rural Major Collector\"", "VB", "")

# Process: Select Layer By Attribute (6)
arcpy.SelectLayerByAttribute_management(FuncClass_Description, "NEW_SELECTION", "FunctionalClass = 8")

# Process: Calculate Field (6)
arcpy.CalculateField_management(FuncClass_Description, "FunctionalClass_Description", "\"Rural Minor Collector\"", "VB", "")

# Process: Select Layer By Attribute (7)
arcpy.SelectLayerByAttribute_management(FuncClass_Description, "NEW_SELECTION", "FunctionalClass = 9")

# Process: Calculate Field (7)
arcpy.CalculateField_management(FuncClass_Description, "FunctionalClass_Description", "\"Rural Local\"", "VB", "")

# Process: Select Layer By Attribute (8)
arcpy.SelectLayerByAttribute_management(FuncClass_Description, "NEW_SELECTION", "FunctionalClass = 11")

# Process: Calculate Field (8)
arcpy.CalculateField_management(FuncClass_Description, "FunctionalClass_Description", "\"Urban Principal Arterial - Interstate\"", "VB", "")

# Process: Select Layer By Attribute (9)
arcpy.SelectLayerByAttribute_management(FuncClass_Description, "NEW_SELECTION", "FunctionalClass = 12")

# Process: Calculate Field (9)
arcpy.CalculateField_management(FuncClass_Description, "FunctionalClass_Description", "\"Urban Principal Arterial - Other Fwys & Expwys\"", "VB", "")

# Process: Select Layer By Attribute (10)
arcpy.SelectLayerByAttribute_management(FuncClass_Description, "NEW_SELECTION", "FunctionalClass = 14")

# Process: Calculate Field (10)
arcpy.CalculateField_management(FuncClass_Description, "FunctionalClass_Description", "\"Urban Principal Arterial - Other\"", "VB", "")

# Process: Select Layer By Attribute (11)
arcpy.SelectLayerByAttribute_management(FuncClass_Description, "NEW_SELECTION", "FunctionalClass = 16")

# Process: Calculate Field (11)
arcpy.CalculateField_management(FuncClass_Description, "FunctionalClass_Description", "\"Urban Minor Arterial\"", "VB", "")

# Process: Select Layer By Attribute (12)
arcpy.SelectLayerByAttribute_management(FuncClass_Description, "NEW_SELECTION", "FunctionalClass = 17")

# Process: Calculate Field (12)
arcpy.CalculateField_management(FuncClass_Description, "FunctionalClass_Description", "\"Urban Major Collector\"", "VB", "")

# Process: Select Layer By Attribute (13)
arcpy.SelectLayerByAttribute_management(FuncClass_Description, "NEW_SELECTION", "FunctionalClass = 18")

# Process: Calculate Field (13)
arcpy.CalculateField_management(FuncClass_Description, "FunctionalClass_Description", "\"Urban Minor Collector\"", "VB", "")

# Process: Select Layer By Attribute (14)
arcpy.SelectLayerByAttribute_management(FuncClass_Description, "NEW_SELECTION", "FunctionalClass = 19")

# Process: Calculate Field (14)
arcpy.CalculateField_management(FuncClass_Description, "FunctionalClass_Description", "\"Urban Local\"", "VB", "")

# Process: Join Field
arcpy.JoinField_management(geocode_projects, "UniqueIDCalced", FuncClass_Description, "UniqueIDCalced", "FunctionalClass_Description")

# Process: Delete Field
arcpy.DeleteField_management(geocode_projects, "FunctionalClass_Description_1")

arcpy.AddMessage("Functional classification descriptions added")

# ---------------------------------------------------------------------------
# Add rounded average T-Factor
# ---------------------------------------------------------------------------

# Process: Summary Statistics
arcpy.Statistics_analysis(TFactor_AADT_Publication, SummaryStats_TFactor, "T_Factor__ MEAN", "TrafficSectionId")

# Process: Add Field
arcpy.AddField_management(SummaryStats_TFactor, "TFactor_Rounded_Avg", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

# Process: Calculate Field
arcpy.CalculateField_management(SummaryStats_TFactor, "TFactor_Rounded_Avg", "round( !MEAN_T_Factor__!,1)", "PYTHON_9.3", "")

# Process: Join Field
arcpy.JoinField_management(geocode_projects, "TrafficSectionId", SummaryStats_TFactor, "TrafficSectionId", "TFactor_Rounded_Avg")

arcpy.AddMessage("Rounded average T-Factor added")


# ---------------------------------------------------------------------------
# Optional: delete intermediate tables
# ---------------------------------------------------------------------------

ischecked = arcpy.GetParameterAsText(4)

tables = [Geocode_UpdatedProjects_TabletoTable, Overlay_Geocode_Intersect, SummaryStats_Geocode, SummaryStats_Geocode_FuncClass_1, SummaryStats_Geocode_FuncClass_2, SummaryStats_Geocode_TrafficSection_1, SummaryStats_Geocode_TrafficSection_2, SummaryStats_TFactor]

if str(ischecked) == 'true':
    arcpy.AddMessage("Deleting intermediate tables")
    for i in tables:
        arcpy.Delete_management(i, "Table")

else:
    arcpy.AddMessage("Retaining intermediate tables")

