#import
import arcpy, os
from arcpy import env

#workspace
map = arcpy.mapping.MapDocument("current")
df = arcpy.mapping.ListDataFrames(map) [0]
print arcpy.mapping.ListLayers(map, "", df)

#set output locations
gdbOutputs = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\Outputs.gdb'
gdbFC = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\FuncClass_Overlays.gdb'
gdbFC_ramps = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\FC_Ramps_Overlay.gdb'

#set data item variables
Carriageway = 'Carriageway'
Urban = 'UrbanCode'
NHS = 'NHS'
Access = 'AccessControl'
ThroughLanes = 'ThroughLane'
Median = 'Median'
Painted = 'PaintedMedian'
AADT = 'AADT'
JunctionLeg = 'JunctionLeg'
FunClass = 'FunctionalClass'
SurfaceType = 'TravelSurfaceType'
OwnerMaint = 'OwnerMaint'
Facility = 'FacilityType'

#create data item list
DataItems = [Carriageway, Urban, NHS, Access, ThroughLanes, Median, Painted, AADT, JunctionLeg]

#run overlay for each data item for fc, ownership, facility, and surface type breakout
for fc in DataItems:
	arcpy.env.overwriteOutput = True
	in_network = "ATIS_Routes"
	network_fields = ["RouteId", "RouteType", "RouteName"]
	event_layers = ["FunctionalClass", "TravelSurfaceType", "OwnerMaint", "FacilityType", fc]
	include_geometry = "INCLUDE_GEOMETRY"
	output_rows = ""
	output_features = gdbOutputs + os.sep + str(fc) + "_overlay_fc"
	print "Starting..." + fc
	arcpy.OverlayRouteEvents_locref(in_network, network_fields, event_layers,include_geometry, output_rows, output_features)

print "Done with data item overlays, creating overlay for funcclass, travel surface, facility, atis routes, and OwnerMaint"

#create overlay for four network data items and atis routes so results can later be queried for these data items
output_network_fcs = gdbOutputs + os.sep + "overlay_network_fcs"
in_network = "ATIS_Routes"
network_fields = ["RouteId", "RouteType", "RouteName"]
event_layers = ["FunctionalClass", "TravelSurfaceType", "OwnerMaint", "FacilityType"]
include_geometry = "INCLUDE_GEOMETRY"
output_rows = ""

arcpy.OverlayRouteEvents_locref(in_network, network_fields, event_layers,include_geometry, output_rows, output_network_fcs)

print "Done with overlay, running overlays for functional class network"

FC_DataItems = [Carriageway, Urban, NHS, Access, ThroughLanes, Median, Painted, AADT, JunctionLeg, Facility, OwnerMaint, SurfaceType]

#run overlay for each data item for functional class and ATIS to get output for just data item and fc non-local and local
for fc in FC_DataItems:
	arcpy.env.overwriteOutput = True
	in_network = "ATIS_Routes"
	network_fields = ["RouteId", "RouteType", "RouteName"]
	event_layers = ["FunctionalClass", fc]
	include_geometry = "INCLUDE_GEOMETRY"
	output_rows = ""
	output_features = gdbFC + os.sep + str(fc) +"_func_fc"
	print "Starting..." + fc
	arcpy.OverlayRouteEvents_locref(in_network, network_fields, event_layers,include_geometry, output_rows, output_features)

print "Done with overlays for FC network, making overlay for ramps"

#run overlay for ramp data items for functionally classified v. non functionally classified output
FC_ramps = [OwnerMaint, AADT]

for fc in FC_ramps:
	arcpy.env.overwriteOutput = True
	in_network = "ATIS_Routes"
	network_fields = ["RouteId", "RouteType", "RouteName"]
	event_layers = ["FunctionalClass", "FacilityType", fc]
	include_geometry = "INCLUDE_GEOMETRY"
	output_rows = ""
	output_features = gdbFC_ramps + os.sep + fc + "_ramps"
	print "Starting..." + fc
	arcpy.OverlayRouteEvents_locref(in_network, network_fields, event_layers,include_geometry, output_rows, output_features)

print "Done with ramp data items, overlay for functional class and ramps"

in_network = "ATIS_Routes"
arcpy.env.overwriteOutput = True
network_fields = ["RouteId", "RouteType", "RouteName"]
event_layer = ["FunctionalClass", "FacilityType"]
include_geometry = "INCLUDE_GEOMETRY"
output_rows = ""
output_feature = gdbFC_ramps + os.sep + "FunctionalClass_ramps"
print "Starting...FunctionalClass"
arcpy.OverlayRouteEvents_locref(in_network, network_fields, event_layer,include_geometry, output_rows, output_feature)

print "Done with ramps, doing last overlay"

in_network = "ATIS_Routes"
arcpy.env.overwriteOutput = True
network_fields = ["RouteId", "RouteType", "RouteName"]
event_layer = "FunctionalClass"
include_geometry = "INCLUDE_GEOMETRY"
output_rows = ""
output_feature = gdbFC + os.sep + "FunctionalClass"
print "Starting...FunctionalClass"
arcpy.OverlayRouteEvents_locref(in_network, network_fields, event_layer,include_geometry, output_rows, output_feature)

print "Done with overlays"

#query for networks and export out
from arcpy import env, os

arcpy.env.workspace = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\Outputs.gdb'

gdbNonLocal = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\NonLocal_Paved.gdb'

gdbLocal = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\Local_Paved.gdb'

gdbUnpaved = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\Unpaved.gdb'

layers = arcpy.ListFeatureClasses()

#look into surface type value of 28 - does this still exist?
for item in layers:
	arcpy.env.overwriteOutput = True
	SQL_NLP = """("FunctionalClass" <> 9 AND "FunctionalClass" <> 19 AND "FunctionalClass" IS NOT NULL) AND ("SurfaceType" <> 28 AND "SurfaceType" <> 10 AND "SurfaceType" <> 16)"""
	print "Making selection for" + " " + item
	arcpy.SelectLayerByAttribute_management(item, "NEW_SELECTION", SQL_NLP)
	output_nonlocal = gdbNonLocal + os.sep + item
	arcpy.CopyFeatures_management(item, output_nonlocal)

print "Done with non local paved, making local paved selections"

for item in layers:
	arcpy.env.overwriteOutput = True
	SQL_LP = """("FunctionalClass" = 9 OR "FunctionalClass" = 19 AND "FunctionalClass" IS NOT NULL) AND ("SurfaceType" <> 28 AND "SurfaceType" <> 10 AND "SurfaceType" <> 16)"""
	print "Making selection for" + " " + item
	arcpy.SelectLayerByAttribute_management(item, "NEW_SELECTION", SQL_LP)
	output_local = gdbLocal + os.sep + item
	arcpy.CopyFeatures_management(item, output_local)

print "Done with local paved, making unpaved selections"

for item in layers:
	arcpy.env.overwriteOutput = True
	SQL_UP = """("SurfaceType" = 28 OR "SurfaceType" = 10 OR "SurfaceType" = 16)"""
	print "Making selection for" + " " + item
	arcpy.SelectLayerByAttribute_management(item, "NEW_SELECTION", SQL_UP)
	output_unpaved = gdbUnpaved + os.sep + item
	arcpy.CopyFeatures_management(item, output_unpaved)

print "Done with MIRE network queries, query for local and non local fcs"

#query for fc networks and export
from arcpy import env, os

arcpy.env.workspace = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\FuncClass_Overlays.gdb'

gdbFCNonLoc = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\FC_NonLocal.gdb'

gdbAllLocal = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\All_Local.gdb'

layers = arcpy.ListFeatureClasses()

for layer in layers:
	arcpy.env.overwriteOutput = True
	SQL_FC = """"FunctionalClass" <> 9 AND "FunctionalClass" <> 19 AND "FunctionalClass" IS NOT NULL"""
	print "Starting" + " " + layer
	arcpy.SelectLayerByAttribute_management(layer, "NEW_SELECTION", SQL_FC)
	output_fc = gdbFCNonLoc + os.sep + layer
	arcpy.CopyFeatures_management(layer, output_fc)

print "Done with FC Non Local selections"

for layer in layers:
	arcpy.env.overwriteOutput = True
	SQL_All = """"FunctionalClass" = 9 OR "FunctionalClass" = 19 OR "FunctionalClass" IS NULL"""
	arcpy.SelectLayerByAttribute_management(layer, "NEW_SELECTION", SQL_All)
	print "Starting" + " " + layer
	output_all_fc = gdbAllLocal + os.sep + layer
	arcpy.CopyFeatures_management(layer, output_all_fc)

print "Done making network selections for MIRE and Functional Class, making ramp selections"

#reset environment and make ramp selections
from arcpy import env, os

arcpy.env.workspace = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\FC_Ramps_Overlay.gdb'

gdbFCNonLoc_ramps = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\FCNonLoc_ramps.gdb'

gdbFCAll_ramps = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\FCAll_ramps.gdb'

items = arcpy.ListFeatureClasses()

for item in items:
	arcpy.env.overwriteOutput = True
	SQL_FC_ramps = """("FunctionalClass" <> 9 AND "FunctionalClass" <> 19 AND "FunctionalClass" IS NOT NULL) AND "FacilityType" = 4"""
	print "Starting" + " " + item
	arcpy.SelectLayerByAttribute_management(item, "NEW_SELECTION", SQL_FC_ramps)
	output_fc = gdbFCNonLoc_ramps + os.sep + item
	arcpy.CopyFeatures_management(item, output_fc)

print "Done with non local ramp selection"

for item in items:
	arcpy.env.overwriteOutput = True
	SQL_FC_all_ramps = """("FunctionalClass" = 9 OR "FunctionalClass" = 19 OR "FunctionalClass" IS NULL) AND "FacilityType" = 4"""
	print "Starting" + " " + item
	arcpy.SelectLayerByAttribute_management(item, "NEW_SELECTION", SQL_FC_all_ramps)
	output_fc = gdbFCAll_ramps + os.sep + item
	arcpy.CopyFeatures_management(item, output_fc)

print "Done with network selections"

#make MIRE attribute selections for layers to get complete mileage and mileage of missing attributes
from arcpy import env, os

arcpy.env.workspace = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\NonLocal_Paved.gdb'

gdbNLP_export = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\NLP_exports.gdb'

Carriageway = 'Carriageway_overlay_fc'
UrbanCode = 'UrbanCode_overlay_fc'
AccessControl = 'AccessControl_overlay_fc'
ThroughLanes = 'ThroughLane_overlay_fc'
Median = 'Median_overlay_fc'
Painted = 'PaintedMedian_overlay_fc'
AADT = 'AADT_overlay_fc'
JunctionLeg = 'JunctionLeg_overlay_fc'
Overlay = 'overlay_network_fcs'
NHS = 'NHS_overlay_fc'

NLP = [Carriageway, UrbanCode, AccessControl, ThroughLanes, Median, Painted, AADT, JunctionLeg, Overlay, NHS]

#query for non local paved complete mileage based on ownership
print "Making coverage selections for non local paved"

arcpy.SelectLayerByAttribute_management(Carriageway, "NEW_SELECTION", """"Ownership" = 'DOT' AND "CarriagewayDir" IS  NOT NULL""")
arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" = 'DOT' AND "FunctionalClass" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(UrbanCode, "NEW_SELECTION", """"Ownership" = 'DOT' AND "UrbanCode" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AccessControl, "NEW_SELECTION", """"Ownership" = 'DOT' AND "AccessControl" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(Median, "NEW_SELECTION", """"Ownership" = 'DOT' AND "MedianType" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(Painted, "NEW_SELECTION", """"Ownership" = 'DOT' AND "TurnLaneTwoWayLeft" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" = 'DOT' AND "AADT" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(JunctionLeg, "NEW_SELECTION", """"Ownership" = 'DOT' AND "MasterLegID" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(ThroughLanes, "NEW_SELECTION", """"Ownership" = 'DOT' AND "NumberOfLanes" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(NHS, "NEW_SELECTION", """"Ownership" = 'DOT' AND  "NHS" IS NOT NULL""")

for item in NLP: 
	output_fe = gdbNLP_export + os.sep + str(item) + "_own_selection"
	arcpy.CopyFeatures_management(item, output_fe)

print "Done with initial selections, selecting for AADT, SurfaceType, and Facility"

#query for other layers
NLP_other = [AADT, Overlay]

arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" = 'DOT' AND "SurfaceType" IS NOT NULL AND "SurfaceType" <> 14""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" = 'DOT' AND "SubmittalYear" IS NOT NULL""")

for item in NLP_other:
	output_fe = gdbNLP_export + os.sep + str(item) + "surface_addt_submit" + "_own_selection"
	arcpy.CopyFeatures_management(item, output_fe)

#make last selection for facility type
arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" = 'DOT' AND "FacilityType" IS NOT NULL""")
output_facility = gdbNLP_export + os.sep + "facility" + "_own_selection"
arcpy.CopyFeatures_management(Overlay, output_facility)

print "Done with state owned selections for non local paved, query for non state owned"

#switch selection to non-state owned
arcpy.SelectLayerByAttribute_management(Carriageway, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "CarriagewayDir" IS  NOT NULL""")
arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "FunctionalClass" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(UrbanCode, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "UrbanCode" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AccessControl, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "AccessControl" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(Median, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "MedianType" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(Painted, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "TurnLaneTwoWayLeft" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "AADT" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(JunctionLeg, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "MasterLegID" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(ThroughLanes, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "NumberOfLanes" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(NHS, "NEW_SELECTION", """"Ownership" <> 'DOT' AND  "NHS" IS NOT NULL""")


for item in NLP: 
	output_fe = gdbNLP_export + os.sep + str(item) + "_nonown_selection"
	arcpy.CopyFeatures_management(item, output_fe)

print "Done with initial selections, selecting for AADT, SurfaceType, and Facility for non state owned"

#query for other layers
NLP_other = [AADT, Overlay]

arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "SurfaceType" IS NOT NULL AND "SurfaceType" <> 14""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "SubmittalYear" IS NOT NULL""")

for item in NLP_other:
	output_fe = gdbNLP_export + os.sep + str(item) + "surface_addt_submit" + "_nonown_selection"
	arcpy.CopyFeatures_management(item, output_fe)

#make last selection for facility type
arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "FacilityType" IS NOT NULL""")
output_facility = gdbNLP_export + os.sep + "facility" + "_nonown_selection"
arcpy.CopyFeatures_management(Overlay, output_facility)

print "Done with non state owned selections, making ramp selections"

#query for ramp data items
ramp_items = [Overlay, AADT]

arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" = 'DOT' AND "FacilityType" = 4 AND "FunctionalClass" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" = 'DOT' AND "FacilityType" = 4 AND "AADT" IS NOT NULL""")

for item in ramp_items:
	output_fe = gdbNLP_export + os.sep + str(item) + "_own_ramps_selection"
	arcpy.CopyFeatures_management(item, output_fe)

print "Done with funcclass and aadt selection, query for aadt year state owned"

arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" = 'DOT' AND "FacilityType" = 4 AND "SubmittalYear" IS NOT NULL""")
output_aadt = gdbNLP_export + os.sep + "aadt_year" + "_own_ramps_selection"
arcpy.CopyFeatures_management(AADT, output_aadt)

print "Done with state owned ramps selection, query for non state"

#switch query to non state owned
ramp_items = [Overlay, AADT]

arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "FacilityType" = 4 AND "FunctionalClass" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "FacilityType" = 4 AND "AADT" IS NOT NULL""")

for item in ramp_items:
	output_fe = gdbNLP_export + os.sep + str(item) + "_nonown_ramps_selection"
	arcpy.CopyFeatures_management(item, output_fe)

print "Done with funcclass and aadt selection, query for aadt year state owned"

arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "FacilityType" = 4 AND "SubmittalYear" IS NOT NULL""")
output_aadt = gdbNLP_export + os.sep + "aadt_year" + "_nonown_ramps_selection"
arcpy.CopyFeatures_management(AADT, output_aadt)

print "Done with non local paved state and non state owned selections"

#summarize selections for non local paved
from arcpy import env, os

arcpy.env.workspace = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\NLP_exports.gdb'

gdbNLP_export = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\NLP_exports.gdb'

NLP_stats = arcpy.ListFeatureClasses('*_own_selection')

for item in NLP_stats:
	print "Calculating Summary Statistics for" + " " + item
	stats = [["SHAPE_Length", "SUM"]]
	output_nlp_state = gdbNLP_export + os.sep + str(item) + "_state_own_stats"
	arcpy.Statistics_analysis(item, output_nlp_state, stats)

print "Done with summary statistics for full extent non local paved state owned"

NLP_nonfe_stats = arcpy.ListFeatureClasses("*_nonown_selection")

for item in NLP_nonfe_stats:
	print "Calculating Summary Statistics for" + " " + item
	stats = [["SHAPE_Length", "SUM"]]
	output_nlp_nonstate = gdbNLP_export + os.sep + str(item) + "_non_stateown_stats"
	arcpy.Statistics_analysis(item, output_nlp_nonstate, stats)

print "Done with summary statistics for full extent non local paved non-state owned"

NLP_fe_ramps_stats = arcpy.ListFeatureClasses("*_own_ramps_selection")

for item in NLP_fe_ramps_stats:
	print "Calculating Summary Statistics for" + " " + item
	stats = [["SHAPE_Length", "SUM"]]
	output_nlp_state_ramps = gdbNLP_export + os.sep + str(item) + "_own_ramps_stats"
	arcpy.Statistics_analysis(item, output_nlp_state_ramps, stats)

NLP_nonfe_ramps_stats = arcpy.ListFeatureClasses("*_nonown_ramps_selection")

for item in NLP_nonfe_ramps_stats:
	print "Calculating Summary Statistics for" + " " + item
	stats = [["SHAPE_Length", "SUM"]]
	output_nlp_nonstate_ramps = gdbNLP_export + os.sep + str(item) + "_non_own_ramps_stats"
	arcpy.Statistics_analysis(item, output_nlp_nonstate_ramps, stats)

print "Done with summary stats for non full extent ramps"

#make tables for summary stats and write values to
print "Creating tables and adding data..."
arcpy.CreateTable_management(gdbNLP_export, "StateOwned")
arcpy.AddField_management("StateOwned", "data_items", "TEXT")
arcpy.AddField_management("StateOwned", "feet_len",  "DOUBLE", "32", "16")
arcpy.AddField_management("StateOwned", "mile_len",  "DOUBLE", "32", "16")

print 'copy information from stat tables into output table'
fields = ['data_items','feet_len', 'mile_len']
output_table = os.path.join(gdbNLP_export, "StateOwned")
output_cursor = arcpy.da.InsertCursor(output_table, fields)

stats_tables = arcpy.ListTables()

for table in stats_tables:
        if not table.endswith('_state_own_stats'):
                continue
        stat_fields = ['SUM_SHAPE_Length']
        with arcpy.da.SearchCursor(table, stat_fields) as cursor:
                for row in cursor:
                        output_row =[table, row[0], row[0]/5280]
                        output_cursor.insertRow(output_row)
row_count = 0
with arcpy.da.SearchCursor(output_table, fields) as cursor:
    for row in cursor:
        row_count += 1

print "{0} generated with {1} rows".format(output_table, row_count)

#create table for non state owned
print "Creating tables and adding data..."
arcpy.CreateTable_management(gdbNLP_export, "NonStateOwned")
arcpy.AddField_management("NonStateOwned", "data_items", "TEXT")
arcpy.AddField_management("NonStateOwned", "feet_len",  "DOUBLE", "32", "16")
arcpy.AddField_management("NonStateOwned", "mile_len",  "DOUBLE", "32", "16")

print 'copy information from stat tables into output table'
fields = ['data_items','feet_len', 'mile_len']
output_table = os.path.join(gdbNLP_export, "NonStateOwned")
output_cursor = arcpy.da.InsertCursor(output_table, fields)

stats_tables = arcpy.ListTables()

for table in stats_tables:
        if not table.endswith('_non_stateown_stats'):
                continue
        stat_fields = ['SUM_SHAPE_Length']
        with arcpy.da.SearchCursor(table, stat_fields) as cursor:
                for row in cursor:
                        output_row =[table, row[0], row[0]/5280]
                        output_cursor.insertRow(output_row)
row_count = 0
with arcpy.da.SearchCursor(output_table, fields) as cursor:
    for row in cursor:
        row_count += 1

print "{0} generated with {1} rows".format(output_table, row_count)

print "Done with non full extent table, making tables for ramps"

print "Creating tables and adding data..."
arcpy.CreateTable_management(gdbNLP_export, "OwnRamps")
arcpy.AddField_management("OwnRamps", "data_items", "TEXT")
arcpy.AddField_management("OwnRamps", "feet_len",  "DOUBLE", "32", "16")
arcpy.AddField_management("OwnRamps", "mile_len",  "DOUBLE", "32", "16")

print 'copy information from stat tables into output table'
fields = ['data_items','feet_len', 'mile_len']
output_table = os.path.join(gdbNLP_export, "OwnRamps")
output_cursor = arcpy.da.InsertCursor(output_table, fields)

stats_tables = arcpy.ListTables()

for table in stats_tables:
        if not table.endswith('_own_ramps_stats'):
                continue
        stat_fields = ['SUM_SHAPE_Length']
        with arcpy.da.SearchCursor(table, stat_fields) as cursor:
                for row in cursor:
                        output_row =[table, row[0], row[0]/5280]
                        output_cursor.insertRow(output_row)
row_count = 0
with arcpy.da.SearchCursor(output_table, fields) as cursor:
    for row in cursor:
        row_count += 1

print "{0} generated with {1} rows".format(output_table, row_count)

print "Done with fe ramps, making nonfe ramp table"

print "Creating tables and adding data..."
arcpy.CreateTable_management(gdbNLP_export, "NonOwnRamps")
arcpy.AddField_management("NonOwnRamps", "data_items", "TEXT")
arcpy.AddField_management("NonOwnRamps", "feet_len",  "DOUBLE", "32", "16")
arcpy.AddField_management("NonOwnRamps", "mile_len",  "DOUBLE", "32", "16")

print 'copy information from stat tables into output table'
fields = ['data_items','feet_len', 'mile_len']
output_table = os.path.join(gdbNLP_export, "NonOwnRamps")
output_cursor = arcpy.da.InsertCursor(output_table, fields)

stats_tables = arcpy.ListTables()

for table in stats_tables:
        if not table.endswith('_non_own_ramps_stats'):
                continue
        stat_fields = ['SUM_SHAPE_Length']
        with arcpy.da.SearchCursor(table, stat_fields) as cursor:
                for row in cursor:
                        output_row =[table, row[0], row[0]/5280]
                        output_cursor.insertRow(output_row)
row_count = 0
with arcpy.da.SearchCursor(output_table, fields) as cursor:
    for row in cursor:
        row_count += 1

print "{0} generated with {1} rows".format(output_table, row_count)

print "Done with full extent coverage, querying by attribute"

#query for null attributes in required fields
from arcpy import env, os

arcpy.env.workspace = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\NonLocal_Paved.gdb'

gdbNLP_export = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\NLP_exports.gdb'

Carriageway = 'Carriageway_overlay_fc'
UrbanCode = 'UrbanCode_overlay_fc'
AccessControl = 'AccessControl_overlay_fc'
ThroughLanes = 'ThroughLane_overlay_fc'
Median = 'Median_overlay_fc'
Painted = 'PaintedMedian_overlay_fc'
AADT = 'AADT_overlay_fc'
JunctionLeg = 'JunctionLeg_overlay_fc'
Overlay = 'overlay_network_fcs'
NHS = 'NHS_overlay_fc'

NLP = [Carriageway, UrbanCode, AccessControl, ThroughLanes, Median, Painted, AADT, JunctionLeg, Overlay]

#query for non local paved complete mileage based on ownership
print "Making attribute selections for non local paved"

arcpy.SelectLayerByAttribute_management(Carriageway, "NEW_SELECTION", """"Ownership" = 'DOT' AND "CarriagewayDir" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" = 'DOT' AND "FunctionalClass" IS NULL AND "FromDate_1" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(UrbanCode, "NEW_SELECTION", """"Ownership" = 'DOT' AND "UrbanCode" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AccessControl, "NEW_SELECTION", """"Ownership" = 'DOT' AND "AccessControl" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(Median, "NEW_SELECTION", """"Ownership" = 'DOT' AND "MedianType" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(Painted, "NEW_SELECTION", """"Ownership" = 'DOT' AND "TurnLaneTwoWayLeft" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" = 'DOT' AND "AADT" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(JunctionLeg, "NEW_SELECTION", """"Ownership" = 'DOT' AND "MasterLegID" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(ThroughLanes, "NEW_SELECTION", """"Ownership" = 'DOT' AND "NumberOfLanes" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(NHS, "NEW_SELECTION", """"Ownership" = 'DOT' AND "NHS" IS NULL AND "FromDate_5" IS NOT NULL""")

for item in NLP: 
	output_fe = gdbNLP_export + os.sep + str(item) + "_own_attr_selection"
	arcpy.CopyFeatures_management(item, output_fe)

print "Done with initial selections, selecting for AADT, SurfaceType, and Facility"

#query for other layers
NLP_other = [AADT, Overlay]

arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" = 'DOT' AND "SurfaceType" IS NULL AND "FromDate_2" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" = 'DOT' AND "SubmittalYear" IS NULL AND "FromDate_5" IS NOT NULL""")

for item in NLP_other:
	output_fe = gdbNLP_export + os.sep + str(item) + "F_submit" + "_own_attr_selection"
	arcpy.CopyFeatures_management(item, output_fe)

#select where surface type is unknown
arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" = 'DOT' AND "SurfaceType" = 14 AND "FromDate_2" IS NOT NULL""")
output_surface = gdbNLP_export + os.sep + "surface_unknown" + "_own_attr_selection"
arcpy.CopyFeatures_management(Overlay, output_surface)

#make last selection for facility type
arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" = 'DOT' AND "FacilityType" IS NULL AND "FromDate_4" IS NOT NULL""")
output_facility = gdbNLP_export + os.sep + "facility" + "_own_attr_selection"
arcpy.CopyFeatures_management(Overlay, output_facility)

print "Done with state owned selections for non local paved, query for non state owned"

#switch selection to non-state owned
arcpy.SelectLayerByAttribute_management(Carriageway, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "CarriagewayDir" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "FunctionalClass" IS NULL AND "FromDate_1" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(UrbanCode, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "UrbanCode" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AccessControl, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "AccessControl" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(Median, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "MedianType" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(Painted, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "TurnLaneTwoWayLeft" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "AADT" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(JunctionLeg, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "MasterLegID" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(ThroughLanes, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "NumberOfLanes" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(NHS, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "NHS" IS NULL AND "FromDate_5" IS NOT NULL""")

for item in NLP: 
	output_fe = gdbNLP_export + os.sep + str(item) + "_nonown_attr_selection"
	arcpy.CopyFeatures_management(item, output_fe)

print "Done with initial selections, selecting for AADT, SurfaceType, and Facility for non state owned"

#query for other layers
NLP_other = [AADT, Overlay]

arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "SurfaceType" IS NULL AND "FromDate_2" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "SubmittalYear" IS NULL AND "FromDate_5" IS NOT NULL""")

for item in NLP_other:
	output_fe = gdbNLP_export + os.sep + str(item) + "surface_addt_submit" + "_nonown_attr_selection"
	arcpy.CopyFeatures_management(item, output_fe)

#select where surface type is unknown
arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "SurfaceType" = 14 AND "FromDate_2" IS NOT NULL""")
output_surface = gdbNLP_export + os.sep + "surface_unknown" + "_nonown_attr_selection"
arcpy.CopyFeatures_management(Overlay, output_surface)

#make last selection for facility type
arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "FacilityType" IS NULL AND "FromDate_4" IS NOT NULL""")
output_facility = gdbNLP_export + os.sep + "facility" + "_nonown_attr_selection"
arcpy.CopyFeatures_management(Overlay, output_facility)

print "Done with non state owned selections, making ramp selections"

#query for ramp data items
ramp_items = [Overlay, AADT]

arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" = 'DOT' AND "FacilityType" = 4 AND "FunctionalClass" IS NULL AND "FromDate_1" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" = 'DOT' AND "FacilityType" = 4 AND "AADT" IS NULL AND "FromDate_5" IS NOT NULL""")

for item in ramp_items:
	output_fe = gdbNLP_export + os.sep + str(item) + "_own_ramps_attr_selection"
	arcpy.CopyFeatures_management(item, output_fe)

print "Done with funcclass and aadt selection, query for aadt year state owned"

arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" = 'DOT' AND "FacilityType" = 4 AND "SubmittalYear" IS NULL AND "FromDate_5" IS NOT NULL""")
output_aadt = gdbNLP_export + os.sep + "aadt_year" + "_own_ramps_attr_selection"
arcpy.CopyFeatures_management(AADT, output_aadt)

print "Done with state owned ramps attr selection, query for non state"

#switch query to non state owned
ramp_items = [Overlay, AADT]

arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "FacilityType" = 4 AND "FunctionalClass" IS NULL AND "FromDate_1" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "FacilityType" = 4 AND "AADT" IS NULL AND "FromDate_5" IS NOT NULL""")

for item in ramp_items:
	output_fe = gdbNLP_export + os.sep + str(item) + "_nonown_ramps_attr_selection"
	arcpy.CopyFeatures_management(item, output_fe)

print "Done with funcclass and aadt selection, query for aadt year state owned"

arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "FacilityType" = 4 AND "SubmittalYear" IS NULL AND "FromDate_5" IS NOT NULL""")
output_aadt = gdbNLP_export + os.sep + "aadt_year" + "_nonown_ramps_attr_selection"
arcpy.CopyFeatures_management(AADT, output_aadt)

print "Done with selections"

#summarize attribute selections for non local paved
from arcpy import env, os

arcpy.env.workspace = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\NLP_exports.gdb'

gdbNLP_export = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\NLP_exports.gdb'

NLP_stats = arcpy.ListFeatureClasses('*_own_attr_selection')

for item in NLP_stats:
	print "Calculating Summary Statistics for" + " " + item
	stats = [["SHAPE_Length", "SUM"]]
	output_nlp_state = gdbNLP_export + os.sep + str(item) + "_state_own_attr_stats"
	arcpy.Statistics_analysis(item, output_nlp_state, stats)

print "Done with summary statistics for full extent non local paved state owned"

NLP_nonfe_stats = arcpy.ListFeatureClasses("*_nonown_attr_selection")

for item in NLP_nonfe_stats:
	print "Calculating Summary Statistics for" + " " + item
	stats = [["SHAPE_Length", "SUM"]]
	output_nlp_nonstate = gdbNLP_export + os.sep + str(item) + "_non_stateown_attr_stats"
	arcpy.Statistics_analysis(item, output_nlp_nonstate, stats)

print "Done with summary statistics for full extent non local paved non-state owned"

NLP_fe_ramps_stats = arcpy.ListFeatureClasses("*_own_ramps_attr_selection")

for item in NLP_fe_ramps_stats:
	print "Calculating Summary Statistics for" + " " + item
	stats = [["SHAPE_Length", "SUM"]]
	output_nlp_state_ramps = gdbNLP_export + os.sep + str(item) + "_own_ramps_attr_stats"
	arcpy.Statistics_analysis(item, output_nlp_state_ramps, stats)

NLP_nonfe_ramps_stats = arcpy.ListFeatureClasses("*_nonown_ramps_attr_selection")

print "Done with summary stats for state owned ramps"

for item in NLP_nonfe_ramps_stats:
	print "Calculating Summary Statistics for" + " " + item
	stats = [["SHAPE_Length", "SUM"]]
	output_nlp_nonstate_ramps = gdbNLP_export + os.sep + str(item) + "_non_own_ramps_attr_stats"
	arcpy.Statistics_analysis(item, output_nlp_nonstate_ramps, stats)

print "Done with summary stats for non state owned ramps"

#make tables for summary stats and write values to
print "Creating tables and adding data..."
arcpy.CreateTable_management(gdbNLP_export, "StateOwnedAttr")
arcpy.AddField_management("StateOwnedAttr", "data_items", "TEXT")
arcpy.AddField_management("StateOwnedAttr", "feet_len",  "DOUBLE", "32", "16")
arcpy.AddField_management("StateOwnedAttr", "mile_len",  "DOUBLE", "32", "16")

print 'copy information from stat tables into output table'
fields = ['data_items','feet_len', 'mile_len']
output_table = os.path.join(gdbNLP_export, "StateOwnedAttr")
output_cursor = arcpy.da.InsertCursor(output_table, fields)

stats_tables = arcpy.ListTables()

for table in stats_tables:
        if not table.endswith('_state_own_attr_stats'):
                continue
        stat_fields = ['SUM_SHAPE_Length']
        with arcpy.da.SearchCursor(table, stat_fields) as cursor:
                for row in cursor:
                        output_row =[table, row[0], row[0]/5280]
                        output_cursor.insertRow(output_row)
row_count = 0
with arcpy.da.SearchCursor(output_table, fields) as cursor:
    for row in cursor:
        row_count += 1

print "{0} generated with {1} rows".format(output_table, row_count)

#create table for non state owned
print "Creating tables and adding data..."
arcpy.CreateTable_management(gdbNLP_export, "NonStateOwnedAttr")
arcpy.AddField_management("NonStateOwnedAttr", "data_items", "TEXT")
arcpy.AddField_management("NonStateOwnedAttr", "feet_len",  "DOUBLE", "32", "16")
arcpy.AddField_management("NonStateOwnedAttr", "mile_len",  "DOUBLE", "32", "16")

print 'copy information from stat tables into output table'
fields = ['data_items','feet_len', 'mile_len']
output_table = os.path.join(gdbNLP_export, "NonStateOwnedAttr")
output_cursor = arcpy.da.InsertCursor(output_table, fields)

stats_tables = arcpy.ListTables()

for table in stats_tables:
        if not table.endswith('_non_stateown_attr_stats'):
                continue
        stat_fields = ['SUM_SHAPE_Length']
        with arcpy.da.SearchCursor(table, stat_fields) as cursor:
                for row in cursor:
                        output_row =[table, row[0], row[0]/5280]
                        output_cursor.insertRow(output_row)
row_count = 0
with arcpy.da.SearchCursor(output_table, fields) as cursor:
    for row in cursor:
        row_count += 1

print "{0} generated with {1} rows".format(output_table, row_count)

print "Done with ownership tables, making tables for ramps"

print "Creating tables and adding data..."
arcpy.CreateTable_management(gdbNLP_export, "OwnAttrRamps")
arcpy.AddField_management("OwnAttrRamps", "data_items", "TEXT")
arcpy.AddField_management("OwnAttrRamps", "feet_len",  "DOUBLE", "32", "16")
arcpy.AddField_management("OwnAttrRamps", "mile_len",  "DOUBLE", "32", "16")

print 'copy information from stat tables into output table'
fields = ['data_items','feet_len', 'mile_len']
output_table = os.path.join(gdbNLP_export, "OwnAttrRamps")
output_cursor = arcpy.da.InsertCursor(output_table, fields)

stats_tables = arcpy.ListTables()

for table in stats_tables:
        if not table.endswith('_own_ramps_attr_stats'):
                continue
        stat_fields = ['SUM_SHAPE_Length']
        with arcpy.da.SearchCursor(table, stat_fields) as cursor:
                for row in cursor:
                        output_row =[table, row[0], row[0]/5280]
                        output_cursor.insertRow(output_row)
row_count = 0
with arcpy.da.SearchCursor(output_table, fields) as cursor:
    for row in cursor:
        row_count += 1

print "{0} generated with {1} rows".format(output_table, row_count)

print "Done with state owned attr ramps, making non state owned attr ramp table"

print "Creating tables and adding data..."
arcpy.CreateTable_management(gdbNLP_export, "NonOwnAttrRamps")
arcpy.AddField_management("NonOwnAttrRamps", "data_items", "TEXT")
arcpy.AddField_management("NonOwnAttrRamps", "feet_len",  "DOUBLE", "32", "16")
arcpy.AddField_management("NonOwnAttrRamps", "mile_len",  "DOUBLE", "32", "16")

print 'copy information from stat tables into output table'
fields = ['data_items','feet_len', 'mile_len']
output_table = os.path.join(gdbNLP_export, "NonOwnAttrRamps")
output_cursor = arcpy.da.InsertCursor(output_table, fields)

stats_tables = arcpy.ListTables()

for table in stats_tables:
        if not table.endswith('_non_own_ramps_attr_stats'):
                continue
        stat_fields = ['SUM_SHAPE_Length']
        with arcpy.da.SearchCursor(table, stat_fields) as cursor:
                for row in cursor:
                        output_row =[table, row[0], row[0]/5280]
                        output_cursor.insertRow(output_row)
row_count = 0
with arcpy.da.SearchCursor(output_table, fields) as cursor:
    for row in cursor:
        row_count += 1

print "{0} generated with {1} rows".format(output_table, row_count)

print "Done with non local paved"

#make selections for local paved roads
from arcpy import env, os

arcpy.env.workspace = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\Local_Paved.gdb'

gdbLP_export = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\LP_exports.gdb'

Carriageway = 'Carriageway_overlay_fc'
UrbanCode = 'UrbanCode_overlay_fc'
NHS = 'NHS_overlay_fc'
AccessControl = 'AccessControl_overlay_fc'
ThroughLanes = 'ThroughLane_overlay_fc'
Median = 'Median_overlay_fc'
Painted = 'PaintedMedian_overlay_fc'
AADT = 'AADT_overlay_fc'
JunctionLeg = 'JunctionLeg_overlay_fc'
Overlay = 'overlay_network_fcs'

LP = [Carriageway, UrbanCode, NHS, AccessControl, ThroughLanes, Median, Painted, AADT, JunctionLeg, Overlay]

#query for local paved complete mileage based on ownership
print "Making coverage selections for local paved"

arcpy.SelectLayerByAttribute_management(Carriageway, "NEW_SELECTION", """"Ownership" = 'DOT' AND "CarriagewayDir" IS  NOT NULL""")
arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" = 'DOT' AND "FunctionalClass" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(UrbanCode, "NEW_SELECTION", """"Ownership" = 'DOT' AND "UrbanCode" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AccessControl, "NEW_SELECTION", """"Ownership" = 'DOT' AND "AccessControl" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(Median, "NEW_SELECTION", """"Ownership" = 'DOT' AND "MedianType" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(Painted, "NEW_SELECTION", """"Ownership" = 'DOT' AND "TurnLaneTwoWayLeft" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" = 'DOT' AND "AADT" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(JunctionLeg, "NEW_SELECTION", """"Ownership" = 'DOT' AND "MasterLegID" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(ThroughLanes, "NEW_SELECTION", """"Ownership" = 'DOT' AND "NumberOfLanes" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(NHS, "NEW_SELECTION", """"Ownership" = 'DOT' AND  "NHS" IS NOT NULL""")


for item in LP: 
	output_fe = gdbLP_export + os.sep + str(item) + "_own_selection"
	arcpy.CopyFeatures_management(item, output_fe)

print "Done with initial selections, selecting for AADT, SurfaceType, and Facility"

#query for other layers
LP_other = [AADT, Overlay]

arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" = 'DOT' AND "SurfaceType" IS NOT NULL AND "SurfaceType" <> 14""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" = 'DOT' AND "SubmittalYear" IS NOT NULL""")

for item in LP_other:
	output_fe = gdbLP_export + os.sep + str(item) + "surface_addt_submit" + "_own_selection"
	arcpy.CopyFeatures_management(item, output_fe)

#make last selection for facility type
arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" = 'DOT' AND "FacilityType" IS NOT NULL""")
output_facility = gdbLP_export + os.sep + "facility" + "_own_selection"
arcpy.CopyFeatures_management(Overlay, output_facility)

print "Done with state owned selections for local paved, query for non state owned"

#switch selection to non-state owned
arcpy.SelectLayerByAttribute_management(Carriageway, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "CarriagewayDir" IS  NOT NULL""")
arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "FunctionalClass" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(UrbanCode, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "UrbanCode" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AccessControl, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "AccessControl" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(Median, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "MedianType" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(Painted, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "TurnLaneTwoWayLeft" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "AADT" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(JunctionLeg, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "MasterLegID" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(ThroughLanes, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "NumberOfLanes" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(NHS, "NEW_SELECTION", """"Ownership" <> 'DOT' AND  "NHS" IS NOT NULL""")

for item in LP: 
	output_fe = gdbLP_export + os.sep + str(item) + "_nonown_selection"
	arcpy.CopyFeatures_management(item, output_fe)

print "Done with initial selections, selecting for AADT, SurfaceType, and Facility"

#query for other layers
LP_other = [AADT, Overlay]

arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "SurfaceType" IS NOT NULL AND "SurfaceType" <> 14""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "SubmittalYear" IS NOT NULL""")

for item in LP_other:
	output_fe = gdbLP_export + os.sep + str(item) + "surface_addt_submit" + "_nonown_selection"
	arcpy.CopyFeatures_management(item, output_fe)

#make last selection for facility type
arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "FacilityType" IS NOT NULL""")
output_facility = gdbLP_export + os.sep + "facility" + "_nonown_selection"
arcpy.CopyFeatures_management(Overlay, output_facility)

print "Done with non state owned selections, making ramp selections"

#query for ramp data items
ramp_items = [Overlay, AADT]

arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" = 'DOT' AND "FacilityType" = 4 AND "FunctionalClass" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" = 'DOT' AND "FacilityType" = 4 AND "AADT" IS NOT NULL""")

for item in ramp_items:
	output_fe = gdbLP_export + os.sep + str(item) + "_own_ramps_selection"
	arcpy.CopyFeatures_management(item, output_fe)

print "Done with funcclass and aadt selection, query for aadt year state owned"

arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" = 'DOT' AND "FacilityType" = 4 AND "SubmittalYear" IS NOT NULL""")
output_aadt = gdbLP_export + os.sep + "aadt_year" + "_own_ramps_selection"
arcpy.CopyFeatures_management(AADT, output_aadt)

print "Done with state owned ramps selection, query for non state"

#switch query to non state owned
ramp_items = [Overlay, AADT]

arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "FacilityType" = 4 AND "FunctionalClass" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "FacilityType" = 4 AND "AADT" IS NOT NULL""")

for item in ramp_items:
	output_fe = gdbLP_export + os.sep + str(item) + "_nonown_ramps_selection"
	arcpy.CopyFeatures_management(item, output_fe)

print "Done with funcclass and aadt selection, query for aadt year state owned"

arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "FacilityType" = 4 AND "SubmittalYear" IS NOT NULL""")
output_aadt = gdbLP_export + os.sep + "aadt_year" + "_nonown_ramps_selection"
arcpy.CopyFeatures_management(AADT, output_aadt)

print "Done with non local paved state and non state owned selections"

#summarize selections for local paved
from arcpy import env, os

arcpy.env.workspace = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\LP_exports.gdb'

gdbLP_export = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\LP_exports.gdb'

LP_stats = arcpy.ListFeatureClasses('*_own_selection')

for item in LP_stats:
	print "Calculating Summary Statistics for" + " " + item
	stats = [["SHAPE_Length", "SUM"]]
	output_lp_state = gdbLP_export + os.sep + str(item) + "_state_own_stats"
	arcpy.Statistics_analysis(item, output_lp_state, stats)

print "Done with summary statistics for full extent local paved state owned"

LP_nonfe_stats = arcpy.ListFeatureClasses("*_nonown_selection")

for item in LP_nonfe_stats:
	print "Calculating Summary Statistics for" + " " + item
	stats = [["SHAPE_Length", "SUM"]]
	output_lp_nonstate = gdbLP_export + os.sep + str(item) + "_non_stateown_stats"
	arcpy.Statistics_analysis(item, output_lp_nonstate, stats)

print "Done with summary statistics for full extent local paved non-state owned"

LP_fe_ramps_stats = arcpy.ListFeatureClasses("*_own_ramps_selection")

for item in LP_fe_ramps_stats:
	print "Calculating Summary Statistics for" + " " + item
	stats = [["SHAPE_Length", "SUM"]]
	output_lp_state_ramps = gdbLP_export + os.sep + str(item) + "_own_ramps_stats"
	arcpy.Statistics_analysis(item, output_lp_state_ramps, stats)

LP_nonfe_ramps_stats = arcpy.ListFeatureClasses("*_nonown_ramps_selection")

for item in LP_nonfe_ramps_stats:
	print "Calculating Summary Statistics for" + " " + item
	stats = [["SHAPE_Length", "SUM"]]
	output_lp_nonstate_ramps = gdbLP_export + os.sep + str(item) + "_non_own_ramps_stats"
	arcpy.Statistics_analysis(item, output_lp_nonstate_ramps, stats)

print "Done with summary stats for ramps"

#make tables for summary stats and write values to
print "Creating tables and adding data..."
arcpy.CreateTable_management(gdbLP_export, "StateOwned")
arcpy.AddField_management("StateOwned", "data_items", "TEXT")
arcpy.AddField_management("StateOwned", "feet_len",  "DOUBLE", "32", "16")
arcpy.AddField_management("StateOwned", "mile_len",  "DOUBLE", "32", "16")

print 'copy information from stat tables into output table'
fields = ['data_items','feet_len', 'mile_len']
output_table = os.path.join(gdbLP_export, "StateOwned")
output_cursor = arcpy.da.InsertCursor(output_table, fields)

stats_tables = arcpy.ListTables()

for table in stats_tables:
        if not table.endswith('_state_own_stats'):
                continue
        stat_fields = ['SUM_SHAPE_Length']
        with arcpy.da.SearchCursor(table, stat_fields) as cursor:
                for row in cursor:
                        output_row =[table, row[0], row[0]/5280]
                        output_cursor.insertRow(output_row)
row_count = 0
with arcpy.da.SearchCursor(output_table, fields) as cursor:
    for row in cursor:
        row_count += 1

print "{0} generated with {1} rows".format(output_table, row_count)

#create table for nonstateowned
print "Creating tables and adding data..."
arcpy.CreateTable_management(gdbLP_export, "NonStateOwned")
arcpy.AddField_management("NonStateOwned", "data_items", "TEXT")
arcpy.AddField_management("NonStateOwned", "feet_len",  "DOUBLE", "32", "16")
arcpy.AddField_management("NonStateOwned", "mile_len",  "DOUBLE", "32", "16")

print 'copy information from stat tables into output table'
fields = ['data_items','feet_len', 'mile_len']
output_table = os.path.join(gdbLP_export, "NonStateOwned")
output_cursor = arcpy.da.InsertCursor(output_table, fields)

stats_tables = arcpy.ListTables()

for table in stats_tables:
        if not table.endswith('_non_stateown_stats'):
                continue
        stat_fields = ['SUM_SHAPE_Length']
        with arcpy.da.SearchCursor(table, stat_fields) as cursor:
                for row in cursor:
                        output_row =[table, row[0], row[0]/5280]
                        output_cursor.insertRow(output_row)
row_count = 0
with arcpy.da.SearchCursor(output_table, fields) as cursor:
    for row in cursor:
        row_count += 1

print "{0} generated with {1} rows".format(output_table, row_count)

print "Done with non full extent table, making tables for ramps"

print "Creating tables and adding data..."
arcpy.CreateTable_management(gdbLP_export, "OwnRamps")
arcpy.AddField_management("OwnRamps", "data_items", "TEXT")
arcpy.AddField_management("OwnRamps", "feet_len",  "DOUBLE", "32", "16")
arcpy.AddField_management("OwnRamps", "mile_len",  "DOUBLE", "32", "16")

print 'copy information from stat tables into output table'
fields = ['data_items','feet_len', 'mile_len']
output_table = os.path.join(gdbLP_export, "OwnRamps")
output_cursor = arcpy.da.InsertCursor(output_table, fields)

stats_tables = arcpy.ListTables()

for table in stats_tables:
        if not table.endswith('_own_ramps_stats'):
                continue
        stat_fields = ['SUM_SHAPE_Length']
        with arcpy.da.SearchCursor(table, stat_fields) as cursor:
                for row in cursor:
                        output_row =[table, row[0], row[0]/5280]
                        output_cursor.insertRow(output_row)
row_count = 0
with arcpy.da.SearchCursor(output_table, fields) as cursor:
    for row in cursor:
        row_count += 1

print "{0} generated with {1} rows".format(output_table, row_count)

print "Done with state owned ramps, making non state owned ramp table"

print "Creating tables and adding data..."
arcpy.CreateTable_management(gdbLP_export, "NonOwnRamps")
arcpy.AddField_management("NonOwnRamps", "data_items", "TEXT")
arcpy.AddField_management("NonOwnRamps", "feet_len",  "DOUBLE", "32", "16")
arcpy.AddField_management("NonOwnRamps", "mile_len",  "DOUBLE", "32", "16")

print 'copy information from stat tables into output table'
fields = ['data_items','feet_len', 'mile_len']
output_table = os.path.join(gdbLP_export, "NonOwnRamps")
output_cursor = arcpy.da.InsertCursor(output_table, fields)

stats_tables = arcpy.ListTables()

for table in stats_tables:
        if not table.endswith('_non_own_ramps_stats'):
                continue
        stat_fields = ['SUM_SHAPE_Length']
        with arcpy.da.SearchCursor(table, stat_fields) as cursor:
                for row in cursor:
                        output_row =[table, row[0], row[0]/5280]
                        output_cursor.insertRow(output_row)
row_count = 0
with arcpy.da.SearchCursor(output_table, fields) as cursor:
    for row in cursor:
        row_count += 1

print "{0} generated with {1} rows".format(output_table, row_count)

print "Done with full extent coverage, querying by attribute"

#query for null attributes in required fields
from arcpy import env, os

arcpy.env.workspace = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\Local_Paved.gdb'

gdbLP_export = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\LP_exports.gdb'

Carriageway = 'Carriageway_overlay_fc'
UrbanCode = 'UrbanCode_overlay_fc'
AccessControl = 'AccessControl_overlay_fc'
ThroughLanes = 'ThroughLane_overlay_fc'
Median = 'Median_overlay_fc'
Painted = 'PaintedMedian_overlay_fc'
AADT = 'AADT_overlay_fc'
JunctionLeg = 'JunctionLeg_overlay_fc'
NHS = 'NHS_overlay_fc'
Overlay = 'overlay_network_fcs'

LP = [Carriageway, UrbanCode, AccessControl, ThroughLanes, Median, Painted, AADT, JunctionLeg, Overlay]

#query for local paved complete mileage based on ownership
print "Making attribute selections for local paved"

arcpy.SelectLayerByAttribute_management(Carriageway, "NEW_SELECTION", """"Ownership" = 'DOT' AND "CarriagewayDir" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" = 'DOT' AND "FunctionalClass" IS NULL AND "FromDate_1" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(UrbanCode, "NEW_SELECTION", """"Ownership" = 'DOT' AND "UrbanCode" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AccessControl, "NEW_SELECTION", """"Ownership" = 'DOT' AND "AccessControl" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(Median, "NEW_SELECTION", """"Ownership" = 'DOT' AND "MedianType" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(Painted, "NEW_SELECTION", """"Ownership" = 'DOT' AND "TurnLaneTwoWayLeft" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" = 'DOT' AND "AADT" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(JunctionLeg, "NEW_SELECTION", """"Ownership" = 'DOT' AND "MasterLegID" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(ThroughLanes, "NEW_SELECTION", """"Ownership" = 'DOT' AND "NumberOfLanes" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(NHS, "NEW_SELECTION", """"Ownership" = 'DOT' AND  "NHS" IS NOT NULL AND "FromDate_5" IS NOT NULL""")

for item in LP: 
	output_fe = gdbLP_export + os.sep + str(item) + "_own_attr_selection"
	arcpy.CopyFeatures_management(item, output_fe)

print "Done with initial selections, selecting for AADT, SurfaceType, and Facility"

#query for other layers
LP_other = [AADT, Overlay]

arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" = 'DOT' AND "SurfaceType" IS NULL AND "FromDate_2" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" = 'DOT' AND "SubmittalYear" IS NULL AND "FromDate_5" IS NOT NULL""")

for item in LP_other:
	output_fe = gdbLP_export + os.sep + str(item) + "surface_addt_submit" + "_own_attr_selection"
	arcpy.CopyFeatures_management(item, output_fe)

#select where surface type is unknown
arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" = 'DOT' AND "SurfaceType" = 14 AND "FromDate_2" IS NOT NULL""")
output_surface = gdbLP_export + os.sep + "surface_unknown" + "_own_attr_selection"
arcpy.CopyFeatures_management(Overlay, output_surface)

#make last selection for facility type
arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" = 'DOT' AND "FacilityType" IS NULL AND "FromDate_4" IS NOT NULL""")
output_facility = gdbLP_export + os.sep + "facility" + "_own_attr_selection"
arcpy.CopyFeatures_management(Overlay, output_facility)

print "Done with state owned selections for local paved, query for non state owned"

#switch selection to non-state owned
arcpy.SelectLayerByAttribute_management(Carriageway, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "CarriagewayDir" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "FunctionalClass" IS NULL AND "FromDate_1" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(UrbanCode, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "UrbanCode" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AccessControl, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "AccessControl" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(Median, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "MedianType" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(Painted, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "TurnLaneTwoWayLeft" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "AADT" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(JunctionLeg, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "MasterLegID" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(ThroughLanes, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "NumberOfLanes" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(NHS, "NEW_SELECTION", """"Ownership" <> 'DOT' AND  "NHS" IS NOT NULL AND "FromDate_5" IS NOT NULL""")

for item in LP: 
	output_fe = gdbLP_export + os.sep + str(item) + "_nonown_attr_selection"
	arcpy.CopyFeatures_management(item, output_fe)

print "Done with initial selections, selecting for AADT, SurfaceType, and Facility"

#query for other layers
LP_other = [AADT, Overlay]

arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "SurfaceType" IS NULL AND "FromDate_2" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "SubmittalYear" IS NULL AND "FromDate_5" IS NOT NULL""")

for item in LP_other:
	output_fe = gdbLP_export + os.sep + str(item) + "surface_addt_submit" + "_nonown_attr_selection"
	arcpy.CopyFeatures_management(item, output_fe)

#select where surface type is unknown
arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "SurfaceType" = 14 AND "FromDate_2" IS NOT NULL""")
output_surface = gdbLP_export + os.sep + "surface_unknown" + "_nonown_attr_selection"
arcpy.CopyFeatures_management(Overlay, output_surface)

#make last selection for facility type
arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "FacilityType" IS NULL AND "FromDate_4" IS NOT NULL""")
output_facility = gdbLP_export + os.sep + "facility" + "_nonown_attr_selection"
arcpy.CopyFeatures_management(Overlay, output_facility)

print "Done with non state owned selections, making ramp selections"

#query for ramp data items
ramp_items = [Overlay, AADT]

arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" = 'DOT' AND "FacilityType" = 4 AND "FunctionalClass" IS NULL AND "FromDate_1" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" = 'DOT' AND "FacilityType" = 4 AND "AADT" IS NULL AND "FromDate_5" IS NOT NULL""")

for item in ramp_items:
	output_fe = gdbLP_export + os.sep + str(item) + "_own_ramps_attr_selection"
	arcpy.CopyFeatures_management(item, output_fe)

print "Done with funcclass and aadt selection, query for aadt year state owned"

arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" = 'DOT' AND "FacilityType" = 4 AND "SubmittalYear" IS NULL AND "FromDate_5" IS NOT NULL""")
output_aadt = gdbLP_export + os.sep + "aadt_year" + "_own_ramps_attr_selection"
arcpy.CopyFeatures_management(AADT, output_aadt)

print "Done with state owned ramps attr selection, query for non state"

#switch query to non state owned
ramp_items = [Overlay, AADT]

arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "FacilityType" = 4 AND "FunctionalClass" IS NULL AND "FromDate_1" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "FacilityType" = 4 AND "AADT" IS NULL AND "FromDate_5" IS NOT NULL""")

for item in ramp_items:
	output_fe = gdbLP_export + os.sep + str(item) + "_nonown_ramps_attr_selection"
	arcpy.CopyFeatures_management(item, output_fe)

print "Done with funcclass and aadt selection, query for aadt year state owned"

arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "FacilityType" = 4 AND "SubmittalYear" IS NULL AND "FromDate_5" IS NOT NULL""")
output_aadt = gdbLP_export + os.sep + "aadt_year" + "_nonown_ramps_attr_selection"
arcpy.CopyFeatures_management(AADT, output_aadt)

print "Done with selections"

#summarize attribute selections for local paved
from arcpy import env, os

arcpy.env.workspace = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\LP_exports.gdb'

gdbLP_export = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\LP_exports.gdb'

LP_stats = arcpy.ListFeatureClasses('*_own_attr_selection')

for item in LP_stats:
	print "Calculating Summary Statistics for" + " " + item
	stats = [["SHAPE_Length", "SUM"]]
	output_lp_state = gdbLP_export + os.sep + str(item) + "_state_own_attr_stats"
	arcpy.Statistics_analysis(item, output_lp_state, stats)

print "Done with summary statistics for full extent local paved state owned"

LP_nonfe_stats = arcpy.ListFeatureClasses("*_nonown_attr_selection")

for item in LP_nonfe_stats:
	print "Calculating Summary Statistics for" + " " + item
	stats = [["SHAPE_Length", "SUM"]]
	output_lp_nonstate = gdbLP_export + os.sep + str(item) + "_non_stateown_attr_stats"
	arcpy.Statistics_analysis(item, output_lp_nonstate, stats)

print "Done with summary statistics for full extent local paved non-state owned"

LP_fe_ramps_stats = arcpy.ListFeatureClasses("*_own_ramps_attr_selection")

for item in LP_fe_ramps_stats:
	print "Calculating Summary Statistics for" + " " + item
	stats = [["SHAPE_Length", "SUM"]]
	output_lp_state_ramps = gdbLP_export + os.sep + str(item) + "_own_ramps_attr_stats"
	arcpy.Statistics_analysis(item, output_lp_state_ramps, stats)

LP_nonfe_ramps_stats = arcpy.ListFeatureClasses("*_nonown_ramps_attr_selection")

print "Done with summary stats for state owned ramps"

for item in LP_nonfe_ramps_stats:
	print "Calculating Summary Statistics for" + " " + item
	stats = [["SHAPE_Length", "SUM"]]
	output_lp_nonstate_ramps = gdbLP_export + os.sep + str(item) + "_non_own_ramps_attr_stats"
	arcpy.Statistics_analysis(item, output_lp_nonstate_ramps, stats)

print "Done with summary stats for non state owned ramps"

#make tables for summary stats and write values to
print "Creating tables and adding data..."
arcpy.CreateTable_management(gdbLP_export, "StateOwnedAttr")
arcpy.AddField_management("StateOwnedAttr", "data_items", "TEXT")
arcpy.AddField_management("StateOwnedAttr", "feet_len",  "DOUBLE", "32", "16")
arcpy.AddField_management("StateOwnedAttr", "mile_len",  "DOUBLE", "32", "16")

print 'copy information from stat tables into output table'
fields = ['data_items','feet_len', 'mile_len']
output_table = os.path.join(gdbLP_export, "StateOwnedAttr")
output_cursor = arcpy.da.InsertCursor(output_table, fields)

stats_tables = arcpy.ListTables()

for table in stats_tables:
        if not table.endswith('_state_own_attr_stats'):
                continue
        stat_fields = ['SUM_SHAPE_Length']
        with arcpy.da.SearchCursor(table, stat_fields) as cursor:
                for row in cursor:
                        output_row =[table, row[0], row[0]/5280]
                        output_cursor.insertRow(output_row)
row_count = 0
with arcpy.da.SearchCursor(output_table, fields) as cursor:
    for row in cursor:
        row_count += 1

print "{0} generated with {1} rows".format(output_table, row_count)

#create table for nonstateowned
print "Creating tables and adding data..."
arcpy.CreateTable_management(gdbLP_export, "NonStateOwnedAttr")
arcpy.AddField_management("NonStateOwnedAttr", "data_items", "TEXT")
arcpy.AddField_management("NonStateOwnedAttr", "feet_len",  "DOUBLE", "32", "16")
arcpy.AddField_management("NonStateOwnedAttr", "mile_len",  "DOUBLE", "32", "16")

print 'copy information from stat tables into output table'
fields = ['data_items','feet_len', 'mile_len']
output_table = os.path.join(gdbLP_export, "NonStateOwnedAttr")
output_cursor = arcpy.da.InsertCursor(output_table, fields)

stats_tables = arcpy.ListTables()

for table in stats_tables:
        if not table.endswith('_non_stateown_attr_stats'):
                continue
        stat_fields = ['SUM_SHAPE_Length']
        with arcpy.da.SearchCursor(table, stat_fields) as cursor:
                for row in cursor:
                        output_row =[table, row[0], row[0]/5280]
                        output_cursor.insertRow(output_row)
row_count = 0
with arcpy.da.SearchCursor(output_table, fields) as cursor:
    for row in cursor:
        row_count += 1

print "{0} generated with {1} rows".format(output_table, row_count)

print "Done with ownership tables, making tables for ramps"

print "Creating tables and adding data..."
arcpy.CreateTable_management(gdbLP_export, "OwnAttrRamps")
arcpy.AddField_management("OwnAttrRamps", "data_items", "TEXT")
arcpy.AddField_management("OwnAttrRamps", "feet_len",  "DOUBLE", "32", "16")
arcpy.AddField_management("OwnAttrRamps", "mile_len",  "DOUBLE", "32", "16")

print 'copy information from stat tables into output table'
fields = ['data_items','feet_len', 'mile_len']
output_table = os.path.join(gdbLP_export, "OwnAttrRamps")
output_cursor = arcpy.da.InsertCursor(output_table, fields)

stats_tables = arcpy.ListTables()

for table in stats_tables:
        if not table.endswith('_own_ramps_attr_stats'):
                continue
        stat_fields = ['SUM_SHAPE_Length']
        with arcpy.da.SearchCursor(table, stat_fields) as cursor:
                for row in cursor:
                        output_row =[table, row[0], row[0]/5280]
                        output_cursor.insertRow(output_row)
row_count = 0
with arcpy.da.SearchCursor(output_table, fields) as cursor:
    for row in cursor:
        row_count += 1

print "{0} generated with {1} rows".format(output_table, row_count)

print "Done with state owned attr ramps, making non state owned attr ramp table"

print "Creating tables and adding data..."
arcpy.CreateTable_management(gdbLP_export, "NonOwnAttrRamps")
arcpy.AddField_management("NonOwnAttrRamps", "data_items", "TEXT")
arcpy.AddField_management("NonOwnAttrRamps", "feet_len",  "DOUBLE", "32", "16")
arcpy.AddField_management("NonOwnAttrRamps", "mile_len",  "DOUBLE", "32", "16")

print 'copy information from stat tables into output table'
fields = ['data_items','feet_len', 'mile_len']
output_table = os.path.join(gdbLP_export, "NonOwnAttrRamps")
output_cursor = arcpy.da.InsertCursor(output_table, fields)

stats_tables = arcpy.ListTables()

for table in stats_tables:
        if not table.endswith('_non_own_ramps_attr_stats'):
                continue
        stat_fields = ['SUM_SHAPE_Length']
        with arcpy.da.SearchCursor(table, stat_fields) as cursor:
                for row in cursor:
                        output_row =[table, row[0], row[0]/5280]
                        output_cursor.insertRow(output_row)
row_count = 0
with arcpy.da.SearchCursor(output_table, fields) as cursor:
    for row in cursor:
        row_count += 1

print "{0} generated with {1} rows".format(output_table, row_count)

print "Done with local paved"

#make selection for unpaved roads for state and non state owned
from arcpy import env, os

arcpy.env.workspace = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\Unpaved.gdb'

gdbUnpaved = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\Unpaved.gdb'

gdbUP_export = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\UP_exports.gdb'

Carriageway = 'Carriageway_overlay_fc'
UrbanCode = 'UrbanCode_overlay_fc'
AccessControl = 'AccessControl_overlay_fc'
ThroughLanes = 'ThroughLane_overlay_fc'
Median = 'Median_overlay_fc'
Painted = 'PaintedMedian_overlay_fc'
AADT = 'AADT_overlay_fc'
JunctionLeg = 'JunctionLeg_overlay_fc'
NHS = 'NHS_overlay_fc'
Overlay = 'overlay_network_fcs'

UP = [Carriageway, UrbanCode, AccessControl, ThroughLanes, Median, Painted, AADT, JunctionLeg, Overlay]

#query for unpaved complete mileage based on ownership
print "Making coverage selections for unpaved"

arcpy.SelectLayerByAttribute_management(Carriageway, "NEW_SELECTION", """"Ownership" = 'DOT' AND "CarriagewayDir" IS  NOT NULL""")
arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" = 'DOT' AND "FunctionalClass" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(UrbanCode, "NEW_SELECTION", """"Ownership" = 'DOT' AND "UrbanCode" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AccessControl, "NEW_SELECTION", """"Ownership" = 'DOT' AND "AccessControl" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(Median, "NEW_SELECTION", """"Ownership" = 'DOT' AND "MedianType" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(Painted, "NEW_SELECTION", """"Ownership" = 'DOT' AND "TurnLaneTwoWayLeft" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" = 'DOT' AND "AADT" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(JunctionLeg, "NEW_SELECTION", """"Ownership" = 'DOT' AND "MasterLegID" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(ThroughLanes, "NEW_SELECTION", """"Ownership" = 'DOT' AND "NumberOfLanes" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(NHS, "NEW_SELECTION", """"Ownership" = 'DOT' AND  "NHS" IS NOT NULL""")

for item in UP: 
	output_fe = gdbUP_export + os.sep + str(item) + "_own_selection"
	arcpy.CopyFeatures_management(item, output_fe)

print "Done with initial selections, selecting for AADT, SurfaceType, and Facility"

#query for other layers
UP_other = [AADT, Overlay]

arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" = 'DOT' AND "SurfaceType" IS NOT NULL AND "SurfaceType" <> 14""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" = 'DOT' AND "SubmittalYear" IS NOT NULL""")

for item in UP_other:
	output_fe = gdbUP_export + os.sep + str(item) + "surface_addt_submit" + "_own_selection"
	arcpy.CopyFeatures_management(item, output_fe)

#make last selection for facility type
arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" = 'DOT' AND "FacilityType" IS NOT NULL""")
output_facility = gdbUP_export + os.sep + "facility" + "_own_selection"
arcpy.CopyFeatures_management(Overlay, output_facility)

print "Done with state owned selections for unpaved, query for non state owned"

#switch selection to non-state owned
arcpy.SelectLayerByAttribute_management(Carriageway, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "CarriagewayDir" IS  NOT NULL""")
arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "FunctionalClass" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(UrbanCode, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "UrbanCode" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AccessControl, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "AccessControl" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(Median, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "MedianType" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(Painted, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "TurnLaneTwoWayLeft" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "AADT" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(JunctionLeg, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "MasterLegID" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(ThroughLanes, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "NumberOfLanes" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(NHS, "NEW_SELECTION", """"Ownership" <> 'DOT' AND  "NHS" IS NOT NULL""")

for item in UP: 
	output_fe = gdbUP_export + os.sep + str(item) + "_nonown_selection"
	arcpy.CopyFeatures_management(item, output_fe)

print "Done with initial selections, selecting for AADT, SurfaceType, and Facility for non state owned"

#query for other layers
UP_other = [AADT, Overlay]

arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "SurfaceType" IS NOT NULL AND "SurfaceType" <> 14""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "SubmittalYear" IS NOT NULL""")

for item in UP_other:
	output_fe = gdbUP_export + os.sep + str(item) + "surface_addt_submit" + "_nonown_selection"
	arcpy.CopyFeatures_management(item, output_fe)

#make last selection for facility type
arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "FacilityType" IS NOT NULL""")
output_facility = gdbUP_export + os.sep + "facility" + "_nonown_selection"
arcpy.CopyFeatures_management(Overlay, output_facility)

print "Done with non state owned selections, making ramp selections"

#query for ramp data items
ramp_items = [Overlay, AADT]

arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" = 'DOT' AND "FacilityType" = 4 AND "FunctionalClass" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" = 'DOT' AND "FacilityType" = 4 AND "AADT" IS NOT NULL""")

for item in ramp_items:
	output_fe = gdbUP_export + os.sep + str(item) + "_own_ramps_selection"
	arcpy.CopyFeatures_management(item, output_fe)

print "Done with funcclass and aadt selection, query for aadt year state owned"

arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" = 'DOT' AND "FacilityType" = 4 AND "SubmittalYear" IS NOT NULL""")
output_aadt = gdbUP_export + os.sep + "aadt_year" + "_own_ramps_selection"
arcpy.CopyFeatures_management(AADT, output_aadt)

print "Done with state owned ramps selection, query for non state"

#switch query to non state owned
ramp_items = [Overlay, AADT]

arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "FacilityType" = 4 AND "FunctionalClass" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "FacilityType" = 4 AND "AADT" IS NOT NULL""")

for item in ramp_items:
	output_fe = gdbUP_export + os.sep + str(item) + "_nonown_ramps_selection"
	arcpy.CopyFeatures_management(item, output_fe)

print "Done with funcclass and aadt selection, query for aadt year state owned"

arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "FacilityType" = 4 AND "SubmittalYear" IS NOT NULL""")
output_aadt = gdbUP_export + os.sep + "aadt_year" + "_nonown_ramps_selection"
arcpy.CopyFeatures_management(AADT, output_aadt)

print "Done with non unpaved state and non state owned selections"

#summarize selections for unpaved
from arcpy import env, os

arcpy.env.workspace = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\UP_exports.gdb'

gdbUP_export = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\UP_exports.gdb'

UP_stats = arcpy.ListFeatureClasses('*_own_selection')

for item in UP_stats:
	print "Calculating Summary Statistics for" + " " + item
	stats = [["SHAPE_Length", "SUM"]]
	output_lp_state = gdbUP_export + os.sep + str(item) + "_state_own_stats"
	arcpy.Statistics_analysis(item, output_lp_state, stats)

print "Done with summary statistics for full extent unpaved state owned"

UP_nonfe_stats = arcpy.ListFeatureClasses("*_nonown_selection")

for item in UP_nonfe_stats:
	print "Calculating Summary Statistics for" + " " + item
	stats = [["SHAPE_Length", "SUM"]]
	output_lp_nonstate = gdbUP_export + os.sep + str(item) + "_non_stateown_stats"
	arcpy.Statistics_analysis(item, output_lp_nonstate, stats)

print "Done with summary statistics for full extent unpaved non-state owned"

UP_fe_ramps_stats = arcpy.ListFeatureClasses("*_own_ramps_selection")

for item in UP_fe_ramps_stats:
	print "Calculating Summary Statistics for" + " " + item
	stats = [["SHAPE_Length", "SUM"]]
	output_lp_state_ramps = gdbUP_export + os.sep + str(item) + "_own_ramps_stats"
	arcpy.Statistics_analysis(item, output_lp_state_ramps, stats)

UP_nonfe_ramps_stats = arcpy.ListFeatureClasses("*_nonown_ramps_selection")

for item in UP_nonfe_ramps_stats:
	print "Calculating Summary Statistics for" + " " + item
	stats = [["SHAPE_Length", "SUM"]]
	output_lp_nonstate_ramps = gdbUP_export + os.sep + str(item) + "_non_own_ramps_stats"
	arcpy.Statistics_analysis(item, output_lp_nonstate_ramps, stats)

print "Done with summary stats for ramps"

#make tables for summary stats and write values to
print "Creating tables and adding data..."
arcpy.CreateTable_management(gdbUP_export, "StateOwned")
arcpy.AddField_management("StateOwned", "data_items", "TEXT")
arcpy.AddField_management("StateOwned", "feet_len",  "DOUBLE", "32", "16")
arcpy.AddField_management("StateOwned", "mile_len",  "DOUBLE", "32", "16")

print 'copy information from stat tables into output table'
fields = ['data_items','feet_len', 'mile_len']
output_table = os.path.join(gdbUP_export, "StateOwned")
output_cursor = arcpy.da.InsertCursor(output_table, fields)

stats_tables = arcpy.ListTables()

for table in stats_tables:
        if not table.endswith('_state_own_stats'):
                continue
        stat_fields = ['SUM_SHAPE_Length']
        with arcpy.da.SearchCursor(table, stat_fields) as cursor:
                for row in cursor:
                        output_row =[table, row[0], row[0]/5280]
                        output_cursor.insertRow(output_row)
row_count = 0
with arcpy.da.SearchCursor(output_table, fields) as cursor:
    for row in cursor:
        row_count += 1

print "{0} generated with {1} rows".format(output_table, row_count)

#create table for nonstateowned
print "Creating tables and adding data..."
arcpy.CreateTable_management(gdbUP_export, "NonStateOwned")
arcpy.AddField_management("NonStateOwned", "data_items", "TEXT")
arcpy.AddField_management("NonStateOwned", "feet_len",  "DOUBLE", "32", "16")
arcpy.AddField_management("NonStateOwned", "mile_len",  "DOUBLE", "32", "16")

print 'copy information from stat tables into output table'
fields = ['data_items','feet_len', 'mile_len']
output_table = os.path.join(gdbUP_export, "NonStateOwned")
output_cursor = arcpy.da.InsertCursor(output_table, fields)

stats_tables = arcpy.ListTables()

for table in stats_tables:
        if not table.endswith('_non_stateown_stats'):
                continue
        stat_fields = ['SUM_SHAPE_Length']
        with arcpy.da.SearchCursor(table, stat_fields) as cursor:
                for row in cursor:
                        output_row =[table, row[0], row[0]/5280]
                        output_cursor.insertRow(output_row)
row_count = 0
with arcpy.da.SearchCursor(output_table, fields) as cursor:
    for row in cursor:
        row_count += 1

print "{0} generated with {1} rows".format(output_table, row_count)

print "Done with non full extent table, making tables for ramps"

print "Creating tables and adding data..."
arcpy.CreateTable_management(gdbUP_export, "OwnRamps")
arcpy.AddField_management("OwnRamps", "data_items", "TEXT")
arcpy.AddField_management("OwnRamps", "feet_len",  "DOUBLE", "32", "16")
arcpy.AddField_management("OwnRamps", "mile_len",  "DOUBLE", "32", "16")

print 'copy information from stat tables into output table'
fields = ['data_items','feet_len', 'mile_len']
output_table = os.path.join(gdbUP_export, "OwnRamps")
output_cursor = arcpy.da.InsertCursor(output_table, fields)

stats_tables = arcpy.ListTables()

for table in stats_tables:
        if not table.endswith('_own_ramps_stats'):
                continue
        stat_fields = ['SUM_SHAPE_Length']
        with arcpy.da.SearchCursor(table, stat_fields) as cursor:
                for row in cursor:
                        output_row =[table, row[0], row[0]/5280]
                        output_cursor.insertRow(output_row)
row_count = 0
with arcpy.da.SearchCursor(output_table, fields) as cursor:
    for row in cursor:
        row_count += 1

print "{0} generated with {1} rows".format(output_table, row_count)

print "Done with state owned ramps, making non state owned ramp table"

print "Creating tables and adding data..."
arcpy.CreateTable_management(gdbUP_export, "NonOwnRamps")
arcpy.AddField_management("NonOwnRamps", "data_items", "TEXT")
arcpy.AddField_management("NonOwnRamps", "feet_len",  "DOUBLE", "32", "16")
arcpy.AddField_management("NonOwnRamps", "mile_len",  "DOUBLE", "32", "16")

print 'copy information from stat tables into output table'
fields = ['data_items','feet_len', 'mile_len']
output_table = os.path.join(gdbUP_export, "NonOwnRamps")
output_cursor = arcpy.da.InsertCursor(output_table, fields)

stats_tables = arcpy.ListTables()

for table in stats_tables:
        if not table.endswith('_non_own_ramps_stats'):
                continue
        stat_fields = ['SUM_SHAPE_Length']
        with arcpy.da.SearchCursor(table, stat_fields) as cursor:
                for row in cursor:
                        output_row =[table, row[0], row[0]/5280]
                        output_cursor.insertRow(output_row)
row_count = 0
with arcpy.da.SearchCursor(output_table, fields) as cursor:
    for row in cursor:
        row_count += 1

print "{0} generated with {1} rows".format(output_table, row_count)

print "Done with full extent coverage, querying by attribute"

#query for null attributes in required fields
from arcpy import env, os

arcpy.env.workspace = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\Unpaved.gdb'

gdbUP_export = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\UP_exports.gdb'

Carriageway = 'Carriageway_overlay_fc'
UrbanCode = 'UrbanCode_overlay_fc'
AccessControl = 'AccessControl_overlay_fc'
ThroughLanes = 'ThroughLane_overlay_fc'
Median = 'Median_overlay_fc'
Painted = 'PaintedMedian_overlay_fc'
AADT = 'AADT_overlay_fc'
JunctionLeg = 'JunctionLeg_overlay_fc'
NHS = 'NHS_overlay_fc'
Overlay = 'overlay_network_fcs'

UP = [Carriageway, UrbanCode, AccessControl, ThroughLanes, Median, Painted, AADT, JunctionLeg, Overlay]

#query for unpaved complete mileage based on ownership
print "Making attribute selections for unpaved"

arcpy.SelectLayerByAttribute_management(Carriageway, "NEW_SELECTION", """"Ownership" = 'DOT' AND "CarriagewayDir" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" = 'DOT' AND "FunctionalClass" IS NULL AND "FromDate_1" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(UrbanCode, "NEW_SELECTION", """"Ownership" = 'DOT' AND "UrbanCode" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AccessControl, "NEW_SELECTION", """"Ownership" = 'DOT' AND "AccessControl" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(Median, "NEW_SELECTION", """"Ownership" = 'DOT' AND "MedianType" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(Painted, "NEW_SELECTION", """"Ownership" = 'DOT' AND "TurnLaneTwoWayLeft" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" = 'DOT' AND "AADT" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(JunctionLeg, "NEW_SELECTION", """"Ownership" = 'DOT' AND "MasterLegID" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(ThroughLanes, "NEW_SELECTION", """"Ownership" = 'DOT' AND "NumberOfLanes" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(NHS, "NEW_SELECTION", """"Ownership" = 'DOT' AND  "NHS" IS NOT NULL AND "FromDate_5" IS NOT NULL""")

for item in UP: 
	output_fe = gdbUP_export + os.sep + str(item) + "_own_attr_selection"
	arcpy.CopyFeatures_management(item, output_fe)

print "Done with initial selections, selecting for AADT, SurfaceType, and Facility"

#query for other layers
UP_other = [AADT, Overlay]

arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" = 'DOT' AND "SurfaceType" IS NULL AND "FromDate_2" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" = 'DOT' AND "SubmittalYear" IS NULL AND "FromDate_5" IS NOT NULL""")

for item in UP_other:
	output_fe = gdbUP_export + os.sep + str(item) + "surface_addt_submit" + "_own_attr_selection"
	arcpy.CopyFeatures_management(item, output_fe)

#select where surface type is unknown
arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" = 'DOT' AND "SurfaceType" = 14 AND "FromDate_2" IS NOT NULL""")
output_surface = gdbUP_export + os.sep + "surface_unknown" + "_own_attr_selection"
arcpy.CopyFeatures_management(Overlay, output_surface)

#make last selection for facility type
arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" = 'DOT' AND "FacilityType" IS NULL AND "FromDate_4" IS NOT NULL""")
output_facility = gdbUP_export + os.sep + "facility" + "_own_attr_selection"
arcpy.CopyFeatures_management(Overlay, output_facility)

print "Done with state owned selections for unpaved, query for non state owned"

#switch selection to non-state owned
arcpy.SelectLayerByAttribute_management(Carriageway, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "CarriagewayDir" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "FunctionalClass" IS NULL AND "FromDate_1" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(UrbanCode, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "UrbanCode" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AccessControl, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "AccessControl" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(Median, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "MedianType" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(Painted, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "TurnLaneTwoWayLeft" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "AADT" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(JunctionLeg, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "MasterLegID" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(ThroughLanes, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "NumberOfLanes" IS NULL AND "FromDate_5" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(NHS, "NEW_SELECTION", """"Ownership" <> 'DOT' AND  "NHS" IS NOT NULL AND "FromDate_5" IS NOT NULL""")

for item in UP: 
	output_fe = gdbUP_export + os.sep + str(item) + "_nonown_attr_selection"
	arcpy.CopyFeatures_management(item, output_fe)

print "Done with initial selections, selecting for AADT, SurfaceType, and Facility"

#query for other layers
UP_other = [AADT, Overlay]

arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "SurfaceType" IS NULL AND "FromDate_2" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "SubmittalYear" IS NULL AND "FromDate_5" IS NOT NULL""")

for item in UP_other:
	output_fe = gdbUP_export + os.sep + str(item) + "surface_addt_submit" + "_nonown_attr_selection"
	arcpy.CopyFeatures_management(item, output_fe)

#select where surface type is unknown
arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "SurfaceType" = 14 AND "FromDate_2" IS NOT NULL""")
output_surface = gdbUP_export + os.sep + "surface_unknown" + "_nonown_attr_selection"
arcpy.CopyFeatures_management(Overlay, output_surface)

#make last selection for facility type
arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "FacilityType" IS NULL AND "FromDate_4" IS NOT NULL""")
output_facility = gdbUP_export + os.sep + "facility" + "_nonown_attr_selection"
arcpy.CopyFeatures_management(Overlay, output_facility)

print "Done with non state owned selections, making ramp selections"

#query for ramp data items
ramp_items = [Overlay, AADT]

arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" = 'DOT' AND "FacilityType" = 4 AND "FunctionalClass" IS NULL AND "FromDate_1" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" = 'DOT' AND "FacilityType" = 4 AND "AADT" IS NULL AND "FromDate_5" IS NOT NULL""")

for item in ramp_items:
	output_fe = gdbUP_export + os.sep + str(item) + "_own_ramps_attr_selection"
	arcpy.CopyFeatures_management(item, output_fe)

print "Done with funcclass and aadt selection, query for aadt yeat state owned"

arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" = 'DOT' AND "FacilityType" = 4 AND "SubmittalYear" IS NULL AND "FromDate_5" IS NOT NULL""")
output_aadt = gdbUP_export + os.sep + "aadt_year" + "_own_ramps_attr_selection"
arcpy.CopyFeatures_management(AADT, output_aadt)

print "Done with state owned ramps attr selection, query for non state"

#switch query to non state owned
ramp_items = [Overlay, AADT]

arcpy.SelectLayerByAttribute_management(Overlay, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "FacilityType" = 4 AND "FunctionalClass" IS NULL AND "FromDate_1" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "FacilityType" = 4 AND "AADT" IS NULL AND "FromDate_5" IS NOT NULL""")

for item in ramp_items:
	output_fe = gdbUP_export + os.sep + str(item) + "_nonown_ramps_attr_selection"
	arcpy.CopyFeatures_management(item, output_fe)

print "Done with funcclass and aadt selection, query for aadt yeat state owned"

arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"Ownership" <> 'DOT' AND "FacilityType" = 4 AND "SubmittalYear" IS NULL AND "FromDate_5" IS NOT NULL""")
output_aadt = gdbUP_export + os.sep + "aadt_year" + "_nonown_ramps_attr_selection"
arcpy.CopyFeatures_management(AADT, output_aadt)

print "Done with selections"

#summarize attribute selections for unpaved
from arcpy import env, os

arcpy.env.workspace = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\UP_exports.gdb'

gdbUP_export = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\UP_exports.gdb'

UP_stats = arcpy.ListFeatureClasses('*_own_attr_selection')

for item in UP_stats:
	print "Calculating Summary Statistics for" + " " + item
	stats = [["SHAPE_Length", "SUM"]]
	output_lp_state = gdbUP_export + os.sep + str(item) + "_state_own_attr_stats"
	arcpy.Statistics_analysis(item, output_lp_state, stats)

print "Done with summary statistics for full extent unpaved state owned"

UP_nonfe_stats = arcpy.ListFeatureClasses("*_nonown_attr_selection")

for item in UP_nonfe_stats:
	print "Calculating Summary Statistics for" + " " + item
	stats = [["SHAPE_Length", "SUM"]]
	output_lp_nonstate = gdbUP_export + os.sep + str(item) + "_non_stateown_attr_stats"
	arcpy.Statistics_analysis(item, output_lp_nonstate, stats)

print "Done with summary statistics for full extent unpaved non-state owned"

UP_fe_ramps_stats = arcpy.ListFeatureClasses("*_own_ramps_attr_selection")

for item in UP_fe_ramps_stats:
	print "Calculating Summary Statistics for" + " " + item
	stats = [["SHAPE_Length", "SUM"]]
	output_lp_state_ramps = gdbUP_export + os.sep + str(item) + "_own_ramps_attr_stats"
	arcpy.Statistics_analysis(item, output_lp_state_ramps, stats)

UP_nonfe_ramps_stats = arcpy.ListFeatureClasses("*_nonown_ramps_attr_selection")

print "Done with summary stats for state owned ramps"

for item in UP_nonfe_ramps_stats:
	print "Calculating Summary Statistics for" + " " + item
	stats = [["SHAPE_Length", "SUM"]]
	output_lp_nonstate_ramps = gdbUP_export + os.sep + str(item) + "_non_own_ramps_attr_stats"
	arcpy.Statistics_analysis(item, output_lp_nonstate_ramps, stats)

print "Done with summary stats for non state owned ramps"

#make tables for summary stats and write values to
print "Creating tables and adding data..."
arcpy.CreateTable_management(gdbUP_export, "StateOwnedAttr")
arcpy.AddField_management("StateOwnedAttr", "data_items", "TEXT")
arcpy.AddField_management("StateOwnedAttr", "feet_len",  "DOUBLE", "32", "16")
arcpy.AddField_management("StateOwnedAttr", "mile_len",  "DOUBLE", "32", "16")

print 'copy information from stat tables into output table'
fields = ['data_items','feet_len', 'mile_len']
output_table = os.path.join(gdbUP_export, "StateOwnedAttr")
output_cursor = arcpy.da.InsertCursor(output_table, fields)

stats_tables = arcpy.ListTables()

for table in stats_tables:
        if not table.endswith('_state_own_attr_stats'):
                continue
        stat_fields = ['SUM_SHAPE_Length']
        with arcpy.da.SearchCursor(table, stat_fields) as cursor:
                for row in cursor:
                        output_row =[table, row[0], row[0]/5280]
                        output_cursor.insertRow(output_row)
row_count = 0
with arcpy.da.SearchCursor(output_table, fields) as cursor:
    for row in cursor:
        row_count += 1

print "{0} generated with {1} rows".format(output_table, row_count)

#create table for nonstateowned
print "Creating tables and adding data..."
arcpy.CreateTable_management(gdbUP_export, "NonStateOwnedAttr")
arcpy.AddField_management("NonStateOwnedAttr", "data_items", "TEXT")
arcpy.AddField_management("NonStateOwnedAttr", "feet_len",  "DOUBLE", "32", "16")
arcpy.AddField_management("NonStateOwnedAttr", "mile_len",  "DOUBLE", "32", "16")

print 'copy information from stat tables into output table'
fields = ['data_items','feet_len', 'mile_len']
output_table = os.path.join(gdbUP_export, "NonStateOwnedAttr")
output_cursor = arcpy.da.InsertCursor(output_table, fields)

stats_tables = arcpy.ListTables()

for table in stats_tables:
        if not table.endswith('_non_stateown_attr_stats'):
                continue
        stat_fields = ['SUM_SHAPE_Length']
        with arcpy.da.SearchCursor(table, stat_fields) as cursor:
                for row in cursor:
                        output_row =[table, row[0], row[0]/5280]
                        output_cursor.insertRow(output_row)
row_count = 0
with arcpy.da.SearchCursor(output_table, fields) as cursor:
    for row in cursor:
        row_count += 1

print "{0} generated with {1} rows".format(output_table, row_count)

print "Done with ownership tables, making tables for ramps"

print "Creating tables and adding data..."
arcpy.CreateTable_management(gdbUP_export, "OwnAttrRamps")
arcpy.AddField_management("OwnAttrRamps", "data_items", "TEXT")
arcpy.AddField_management("OwnAttrRamps", "feet_len",  "DOUBLE", "32", "16")
arcpy.AddField_management("OwnAttrRamps", "mile_len",  "DOUBLE", "32", "16")

print 'copy information from stat tables into output table'
fields = ['data_items','feet_len', 'mile_len']
output_table = os.path.join(gdbUP_export, "OwnAttrRamps")
output_cursor = arcpy.da.InsertCursor(output_table, fields)

stats_tables = arcpy.ListTables()

for table in stats_tables:
        if not table.endswith('_own_ramps_attr_stats'):
                continue
        stat_fields = ['SUM_SHAPE_Length']
        with arcpy.da.SearchCursor(table, stat_fields) as cursor:
                for row in cursor:
                        output_row =[table, row[0], row[0]/5280]
                        output_cursor.insertRow(output_row)
row_count = 0
with arcpy.da.SearchCursor(output_table, fields) as cursor:
    for row in cursor:
        row_count += 1

print "{0} generated with {1} rows".format(output_table, row_count)

print "Done with state owned attr ramps, making non state owned attr ramp table"

print "Creating tables and adding data..."
arcpy.CreateTable_management(gdbUP_export, "NonOwnAttrRamps")
arcpy.AddField_management("NonOwnAttrRamps", "data_items", "TEXT")
arcpy.AddField_management("NonOwnAttrRamps", "feet_len",  "DOUBLE", "32", "16")
arcpy.AddField_management("NonOwnAttrRamps", "mile_len",  "DOUBLE", "32", "16")

print 'copy information from stat tables into output table'
fields = ['data_items','feet_len', 'mile_len']
output_table = os.path.join(gdbUP_export, "NonOwnAttrRamps")
output_cursor = arcpy.da.InsertCursor(output_table, fields)

stats_tables = arcpy.ListTables()

for table in stats_tables:
        if not table.endswith('_non_own_ramps_attr_stats'):
                continue
        stat_fields = ['SUM_SHAPE_Length']
        with arcpy.da.SearchCursor(table, stat_fields) as cursor:
                for row in cursor:
                        output_row =[table, row[0], row[0]/5280]
                        output_cursor.insertRow(output_row)
row_count = 0
with arcpy.da.SearchCursor(output_table, fields) as cursor:
    for row in cursor:
        row_count += 1

print "{0} generated with {1} rows".format(output_table, row_count)

print "Done with unpaved"

#query for coverage along FC and ATIS_Route network
from arcpy import env, os

arcpy.env.workspace = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\FC_NonLocal.gdb'

gdbFC_NonLocal_export = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\FC_NonLocal_exports.gdb'

Carriageway = 'Carriageway_func_fc'
UrbanCode = 'UrbanCode_func_fc'
AccessControl = 'AccessControl_func_fc'
ThroughLanes = 'ThroughLane_func_fc'
Median = 'Median_func_fc'
Painted = 'PaintedMedian_func_fc'
AADT = 'AADT_func_fc'
JunctionLeg = 'JunctionLeg_func_fc'
OwnerMaint = 'OwnerMaint_func_fc'
Facility = 'FacilityType_func_fc'
FunClass = 'FunctionalClass'
SurfaceType = 'TravelSurfaceType_func_fc'

FC_items= [Carriageway, UrbanCode, AccessControl, ThroughLanes, Median, Painted, AADT, JunctionLeg, OwnerMaint, Facility, FunClass, SurfaceType]

arcpy.SelectLayerByAttribute_management(Carriageway, "NEW_SELECTION", """"CarriagewayDir" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(FunClass, "NEW_SELECTION", """"FunctionalClass" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(UrbanCode, "NEW_SELECTION", """"UrbanCode" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AccessControl, "NEW_SELECTION", """"AccessControl" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(Median, "NEW_SELECTION", """"MedianType" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(Painted, "NEW_SELECTION", """"TurnLaneTwoWayLeft" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"AADT" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(JunctionLeg, "NEW_SELECTION", """"MasterLegID" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(ThroughLanes, "NEW_SELECTION", """"NumberOfLanes" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(SurfaceType, "NEW_SELECTION", """"SurfaceType" IS NOT NULL AND "SurfaceType" <> 14""")
arcpy.SelectLayerByAttribute_management(Facility, "NEW_SELECTION", """"FacilityType" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(OwnerMaint, "NEW_SELECTION", """"Ownership" IS NOT NULL""")

for item in FC_items: 
	output_fe = gdbFC_NonLocal_export + os.sep + str(item) + "_coverage_selection"
	arcpy.CopyFeatures_management(item, output_fe)

print "Done with initial selections, selecting for other AADT"

arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"SubmittalYear" IS NOT NULL""")
output_aadt = gdbFC_NonLocal_export + os.sep + str(item) + "submit" + "_coverage_selection"
arcpy.CopyFeatures_management(AADT, output_aadt)

print "Done with coverage selections"

#make selection for missing coverage

FC_missing = [Carriageway, UrbanCode, AccessControl, ThroughLanes, Median, Painted, AADT, JunctionLeg, OwnerMaint, Facility, FunClass, SurfaceType]

arcpy.SelectLayerByAttribute_management(Carriageway, "NEW_SELECTION", """"CarriagewayDir" IS NULL""")
arcpy.SelectLayerByAttribute_management(FunClass, "NEW_SELECTION", """"FunctionalClass" IS NULL""")
arcpy.SelectLayerByAttribute_management(UrbanCode, "NEW_SELECTION", """"UrbanCode" IS NULL""")
arcpy.SelectLayerByAttribute_management(AccessControl, "NEW_SELECTION", """"AccessControl" IS NULL""")
arcpy.SelectLayerByAttribute_management(Median, "NEW_SELECTION", """"MedianType" IS NULL""")
arcpy.SelectLayerByAttribute_management(Painted, "NEW_SELECTION", """"TurnLaneTwoWayLeft" IS NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"AADT" IS NULL""")
arcpy.SelectLayerByAttribute_management(JunctionLeg, "NEW_SELECTION", """"MasterLegID" IS NULL""")
arcpy.SelectLayerByAttribute_management(ThroughLanes, "NEW_SELECTION", """"NumberOfLanes" IS NULL""")
arcpy.SelectLayerByAttribute_management(SurfaceType, "NEW_SELECTION", """"SurfaceType" IS NULL""")
arcpy.SelectLayerByAttribute_management(Facility, "NEW_SELECTION", """"FacilityType" IS NULL""")
arcpy.SelectLayerByAttribute_management(OwnerMaint, "NEW_SELECTION", """"Ownership" IS NULL""")

for item in FC_missing:
	output_fe = gdbFC_NonLocal_export + os.sep + str(item) + "_missing_fc_selection"
	arcpy.CopyFeatures_management(item, output_fe)

print "Done with missing fc selections, querying for other AADT"

arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"SubmittalYear" IS NULL""")
output_aadt_missing = gdbFC_NonLocal_export + os.sep + "aadt_submit" + "_missing_fc_selection"
arcpy.CopyFeatures_management(AADT, output_aadt_missing)

print "Done with data item selections"

#summarize selections
from arcpy import env, os

arcpy.env.workspace = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\FC_NonLocal_exports.gdb'

gdbFC_NonLocal_export = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\FC_NonLocal_exports.gdb'

FC_NonLocal_stats = arcpy.ListFeatureClasses('*_coverage_selection')

for item in FC_NonLocal_stats:
	print "Calculating Summary Statistics for" + " " + item
	stats = [["SHAPE_Length", "SUM"]]
	output_coverage = gdbFC_NonLocal_export + os.sep + str(item) + "_coverage_stats"
	arcpy.Statistics_analysis(item, output_coverage, stats)

print "Done with summary statistics for full extent non local paved state owned"

FC_NonLocal_missing = arcpy.ListFeatureClasses("*_missing_fc_selection")

for item in FC_NonLocal_missing:
	print "Calculating Summary Statistics for" + " " + item
	stats = [["SHAPE_Length", "SUM"]]
	output_missing = gdbFC_NonLocal_export + os.sep + str(item) + "_missing_stats"
	arcpy.Statistics_analysis(item, output_missing, stats)

print "Done with summary statistics for non local roads"

#make tables for summary stats and write values to
print "Creating tables and adding data..."
arcpy.CreateTable_management(gdbFC_NonLocal_export, "FC_Coverage")
arcpy.AddField_management("FC_Coverage", "data_items", "TEXT")
arcpy.AddField_management("FC_Coverage", "feet_len",  "DOUBLE", "32", "16")
arcpy.AddField_management("FC_Coverage", "mile_len",  "DOUBLE", "32", "16")

print 'copy information from stat tables into output table'
fields = ['data_items','feet_len', 'mile_len']
output_table = os.path.join(gdbFC_NonLocal_export, "FC_Coverage")
output_cursor = arcpy.da.InsertCursor(output_table, fields)

stats_tables = arcpy.ListTables()

for table in stats_tables:
        if not table.endswith('_coverage_stats'):
                continue
        stat_fields = ['SUM_SHAPE_Length']
        with arcpy.da.SearchCursor(table, stat_fields) as cursor:
                for row in cursor:
                        output_row =[table, row[0], row[0]/5280]
                        output_cursor.insertRow(output_row)
row_count = 0
with arcpy.da.SearchCursor(output_table, fields) as cursor:
    for row in cursor:
        row_count += 1

print "{0} generated with {1} rows".format(output_table, row_count)

#create table for non state owned
print "Creating tables and adding data..."
arcpy.CreateTable_management(gdbFC_NonLocal_export, "FC_Missing")
arcpy.AddField_management("FC_Missing", "data_items", "TEXT")
arcpy.AddField_management("FC_Missing", "feet_len",  "DOUBLE", "32", "16")
arcpy.AddField_management("FC_Missing", "mile_len",  "DOUBLE", "32", "16")

print 'copy information from stat tables into output table'
fields = ['data_items','feet_len', 'mile_len']
output_table = os.path.join(gdbFC_NonLocal_export, "FC_Missing")
output_cursor = arcpy.da.InsertCursor(output_table, fields)

stats_tables = arcpy.ListTables()

for table in stats_tables:
        if not table.endswith('_missing_stats'):
                continue
        stat_fields = ['SUM_SHAPE_Length']
        with arcpy.da.SearchCursor(table, stat_fields) as cursor:
                for row in cursor:
                        output_row =[table, row[0], row[0]/5280]
                        output_cursor.insertRow(output_row)
row_count = 0
with arcpy.da.SearchCursor(output_table, fields) as cursor:
    for row in cursor:
        row_count += 1

print "{0} generated with {1} rows".format(output_table, row_count)

print "Done with full extent coverage, querying by attribute"

#query for null attributes in required fields
from arcpy import env, os

arcpy.env.workspace = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\FC_NonLocal.gdb'

gdbFC_NonLocal_export = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\FC_NonLocal_exports.gdb'

Carriageway = 'Carriageway_func_fc'
UrbanCode = 'UrbanCode_func_fc'
AccessControl = 'AccessControl_func_fc'
ThroughLanes = 'ThroughLane_func_fc'
Median = 'Median_func_fc'
Painted = 'PaintedMedian_func_fc'
AADT = 'AADT_func_fc'
JunctionLeg = 'JunctionLeg_func_fc'
OwnerMaint = 'OwnerMaint_func_fc'
Facility = 'FacilityType_func_fc'
FunClass = 'FunctionalClass'
SurfaceType = 'TravelSurfaceType_func_fc'

FC = [Carriageway, UrbanCode, AccessControl, ThroughLanes, Median, Painted, AADT, JunctionLeg, OwnerMaint, Facility, FunClass, SurfaceType]

#query for non local paved complete mileage based on ownership
print "Making attribute selections for non local paved"

arcpy.SelectLayerByAttribute_management(Carriageway, "NEW_SELECTION", """"CarriagewayDir" IS NULL AND "FromDate_2" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(FunClass, "NEW_SELECTION", """"FunctionalClass" IS NULL AND "FromDate_1" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(UrbanCode, "NEW_SELECTION", """"UrbanCode" IS NULL AND "FromDate_2" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AccessControl, "NEW_SELECTION", """"AccessControl" IS NULL AND "FromDate_2" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(Median, "NEW_SELECTION", """"MedianType" IS NULL AND "FromDate_2" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(Painted, "NEW_SELECTION", """"TurnLaneTwoWayLeft" IS NULL AND "FromDate_2" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"AADT" IS NULL AND "FromDate_2" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(JunctionLeg, "NEW_SELECTION", """"MasterLegID" IS NULL AND "FromDate_2" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(ThroughLanes, "NEW_SELECTION", """"NumberOfLanes" IS NULL AND "FromDate_2" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(SurfaceType, "NEW_SELECTION", """"SurfaceType" IS NULL AND "FromDate_2" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(Facility, "NEW_SELECTION", """"FacilityType" IS NULL AND "FromDate_2" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(OwnerMaint, "NEW_SELECTION", """"Ownership" IS NULL AND "FromDate_2" IS NOT NULL""")

for item in FC: 
	output_fe = gdbFC_NonLocal_export + os.sep + str(item) + "_coverage_attr_selection"
	arcpy.CopyFeatures_management(item, output_fe)

print "Done with initial attribute selections"

#query for other layers
FC_other = [AADT, SurfaceType]

arcpy.SelectLayerByAttribute_management(SurfaceType, "NEW_SELECTION", """"SurfaceType" = 14 AND "FromDate_2" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"SubmittalYear" IS NULL AND "FromDate_2" IS NOT NULL""")

for item in FC_other:
	output_fe = gdbFC_NonLocal_export + os.sep + str(item) + "surface_unknown_addt" + "_coverage_attr_selection"
	arcpy.CopyFeatures_management(item, output_fe)

print "Done with missing attribute selections"

#summarize attribute selections for non local paved
from arcpy import env, os

arcpy.env.workspace = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\FC_NonLocal_exports.gdb'

gdbFC_NonLocal_export = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\FC_NonLocal_exports.gdb'

FC_stats = arcpy.ListFeatureClasses('*_coverage_attr_selection')

for item in FC_stats:
	print "Calculating Summary Statistics for" + " " + item
	stats = [["SHAPE_Length", "SUM"]]
	output_fc_attr = gdbFC_NonLocal_export + os.sep + str(item) + "_coverage_attr_stats"
	arcpy.Statistics_analysis(item, output_fc_attr, stats)

print "Done with summary statistics"

#make tables for summary stats and write values to
print "Creating tables and adding data..."
arcpy.CreateTable_management(gdbFC_NonLocal_export, "FC_Attr")
arcpy.AddField_management("FC_Attr", "data_items", "TEXT")
arcpy.AddField_management("FC_Attr", "feet_len",  "DOUBLE", "32", "16")
arcpy.AddField_management("FC_Attr", "mile_len",  "DOUBLE", "32", "16")

print 'copy information from stat tables into output table'
fields = ['data_items','feet_len', 'mile_len']
output_table = os.path.join(gdbFC_NonLocal_export, "FC_Attr")
output_cursor = arcpy.da.InsertCursor(output_table, fields)

stats_tables = arcpy.ListTables()

for table in stats_tables:
        if not table.endswith('_coverage_attr_stats'):
                continue
        stat_fields = ['SUM_SHAPE_Length']
        with arcpy.da.SearchCursor(table, stat_fields) as cursor:
                for row in cursor:
                        output_row =[table, row[0], row[0]/5280]
                        output_cursor.insertRow(output_row)
row_count = 0
with arcpy.da.SearchCursor(output_table, fields) as cursor:
    for row in cursor:
        row_count += 1

print "{0} generated with {1} rows".format(output_table, row_count)

print "Done with functionally classified non local roads"

#query for all local roads
from arcpy import env, os

arcpy.env.workspace = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\All_Local.gdb'

gdbAll_Local_export = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\All_Local_exports.gdb'

Carriageway = 'Carriageway_func_fc'
UrbanCode = 'UrbanCode_func_fc'
AccessControl = 'AccessControl_func_fc'
ThroughLanes = 'ThroughLane_func_fc'
Median = 'Median_func_fc'
Painted = 'PaintedMedian_func_fc'
AADT = 'AADT_func_fc'
JunctionLeg = 'JunctionLeg_func_fc'
OwnerMaint = 'OwnerMaint_func_fc'
Facility = 'FacilityType_func_fc'
FunClass = 'FunctionalClass'
SurfaceType = 'TravelSurfaceType_func_fc'

FC_All_items= [Carriageway, UrbanCode, AccessControl, ThroughLanes, Median, Painted, AADT, JunctionLeg, OwnerMaint, Facility, FunClass, SurfaceType]

arcpy.SelectLayerByAttribute_management(Carriageway, "NEW_SELECTION", """"CarriagewayDir" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(FunClass, "NEW_SELECTION", """"FunctionalClass" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(UrbanCode, "NEW_SELECTION", """"UrbanCode" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AccessControl, "NEW_SELECTION", """"AccessControl" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(Median, "NEW_SELECTION", """"MedianType" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(Painted, "NEW_SELECTION", """"TurnLaneTwoWayLeft" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"AADT" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(JunctionLeg, "NEW_SELECTION", """"MasterLegID" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(ThroughLanes, "NEW_SELECTION", """"NumberOfLanes" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(SurfaceType, "NEW_SELECTION", """"SurfaceType" IS NOT NULL AND "SurfaceType" <> 14""")
arcpy.SelectLayerByAttribute_management(Facility, "NEW_SELECTION", """"FacilityType" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(OwnerMaint, "NEW_SELECTION", """"Ownership" IS NOT NULL""")

for item in FC_All_items: 
	output_fe = gdbAll_Local_export + os.sep + str(item) + "_coverage_selection"
	arcpy.CopyFeatures_management(item, output_fe)

print "Done with initial selections, selecting for other AADT"

arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"SubmittalYear" IS NOT NULL""")
output_aadt = gdbAll_Local_export + os.sep + "aadt_submit" + "_coverage_selection"
arcpy.CopyFeatures_management(AADT, output_aadt)

print "Done with coverage selections"

#make selection for missing coverage
FC_All_missing = [Carriageway, UrbanCode, AccessControl, ThroughLanes, Median, Painted, AADT, JunctionLeg, OwnerMaint, Facility, FunClass, SurfaceType]

arcpy.SelectLayerByAttribute_management(Carriageway, "NEW_SELECTION", """"CarriagewayDir" IS NULL""")
arcpy.SelectLayerByAttribute_management(FunClass, "NEW_SELECTION", """"FunctionalClass" IS NULL""")
arcpy.SelectLayerByAttribute_management(UrbanCode, "NEW_SELECTION", """"UrbanCode" IS NULL""")
arcpy.SelectLayerByAttribute_management(AccessControl, "NEW_SELECTION", """"AccessControl" IS NULL""")
arcpy.SelectLayerByAttribute_management(Median, "NEW_SELECTION", """"MedianType" IS NULL""")
arcpy.SelectLayerByAttribute_management(Painted, "NEW_SELECTION", """"TurnLaneTwoWayLeft" IS NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"AADT" IS NULL""")
arcpy.SelectLayerByAttribute_management(JunctionLeg, "NEW_SELECTION", """"MasterLegID" IS NULL""")
arcpy.SelectLayerByAttribute_management(ThroughLanes, "NEW_SELECTION", """"NumberOfLanes" IS NULL""")
arcpy.SelectLayerByAttribute_management(SurfaceType, "NEW_SELECTION", """"SurfaceType" IS NULL""")
arcpy.SelectLayerByAttribute_management(Facility, "NEW_SELECTION", """"FacilityType" IS NULL""")
arcpy.SelectLayerByAttribute_management(OwnerMaint, "NEW_SELECTION", """"Ownership" IS NULL""")

for item in FC_All_missing:
	output_fe = gdbAll_Local_export + os.sep + str(item) + "_missing_fc_selection"
	arcpy.CopyFeatures_management(item, output_fe)

print "Done with missing fc selections, querying for other AADT"

arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"SubmittalYear" IS NULL""")
output_aadt_missing = gdbAll_Local_export + os.sep + "aadt_submit" + "_missing_fc_selection"
arcpy.CopyFeatures_management(AADT, output_aadt_missing)

print "Done with data item selections"

#summarize selections
from arcpy import env, os

arcpy.env.workspace = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\All_Local_exports.gdb'

gdbAll_Local_export = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\All_Local_exports.gdb'

All_Local_stats = arcpy.ListFeatureClasses('*_coverage_selection')

for item in All_Local_stats:
	print "Calculating Summary Statistics for" + " " + item
	stats = [["SHAPE_Length", "SUM"]]
	output_coverage = gdbAll_Local_export + os.sep + str(item) + "_coverage_stats"
	arcpy.Statistics_analysis(item, output_coverage, stats)

print "Done with summary statistics for full extent non local paved state owned"

All_Local_missing = arcpy.ListFeatureClasses("*_missing_fc_selection")

for item in All_Local_missing:
	print "Calculating Summary Statistics for" + " " + item
	stats = [["SHAPE_Length", "SUM"]]
	output_missing = gdbAll_Local_export + os.sep + str(item) + "_missing_stats"
	arcpy.Statistics_analysis(item, output_missing, stats)

print "Done with summary statistics for non local roads"

#make tables for summary stats and write values to
print "Creating tables and adding data..."
arcpy.CreateTable_management(gdbAll_Local_export, "FC_All_Coverage")
arcpy.AddField_management("FC_All_Coverage", "data_items", "TEXT")
arcpy.AddField_management("FC_All_Coverage", "feet_len",  "DOUBLE", "32", "16")
arcpy.AddField_management("FC_All_Coverage", "mile_len",  "DOUBLE", "32", "16")

print 'copy information from stat tables into output table'
fields = ['data_items','feet_len', 'mile_len']
output_table = os.path.join(gdbAll_Local_export, "FC_All_Coverage")
output_cursor = arcpy.da.InsertCursor(output_table, fields)

stats_tables = arcpy.ListTables()

for table in stats_tables:
        if not table.endswith('_coverage_stats'):
                continue
        stat_fields = ['SUM_SHAPE_Length']
        with arcpy.da.SearchCursor(table, stat_fields) as cursor:
                for row in cursor:
                        output_row =[table, row[0], row[0]/5280]
                        output_cursor.insertRow(output_row)
row_count = 0
with arcpy.da.SearchCursor(output_table, fields) as cursor:
    for row in cursor:
        row_count += 1

print "{0} generated with {1} rows".format(output_table, row_count)

#create table for missing coverage on all local roads
print "Creating tables and adding data..."
arcpy.CreateTable_management(gdbAll_Local_export, "FC_All_Missing")
arcpy.AddField_management("FC_All_Missing", "data_items", "TEXT")
arcpy.AddField_management("FC_All_Missing", "feet_len",  "DOUBLE", "32", "16")
arcpy.AddField_management("FC_All_Missing", "mile_len",  "DOUBLE", "32", "16")

print 'copy information from stat tables into output table'
fields = ['data_items','feet_len', 'mile_len']
output_table = os.path.join(gdbAll_Local_export, "FC_All_Missing")
output_cursor = arcpy.da.InsertCursor(output_table, fields)

stats_tables = arcpy.ListTables()

for table in stats_tables:
        if not table.endswith('_missing_stats'):
                continue
        stat_fields = ['SUM_SHAPE_Length']
        with arcpy.da.SearchCursor(table, stat_fields) as cursor:
                for row in cursor:
                        output_row =[table, row[0], row[0]/5280]
                        output_cursor.insertRow(output_row)
row_count = 0
with arcpy.da.SearchCursor(output_table, fields) as cursor:
    for row in cursor:
        row_count += 1

print "{0} generated with {1} rows".format(output_table, row_count)

print "Done with full extent coverage, querying by attribute"

#query for null attributes in required fields
from arcpy import env, os

arcpy.env.workspace = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\All_Local.gdb'

gdbAll_Local_export = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\All_Local_exports.gdb'

Carriageway = 'Carriageway_func_fc'
UrbanCode = 'UrbanCode_func_fc'
AccessControl = 'AccessControl_func_fc'
ThroughLanes = 'ThroughLane_func_fc'
Median = 'Median_func_fc'
Painted = 'PaintedMedian_func_fc'
AADT = 'AADT_func_fc'
JunctionLeg = 'JunctionLeg_func_fc'
OwnerMaint = 'OwnerMaint_func_fc'
Facility = 'FacilityType_func_fc'
FunClass = 'FunctionalClass'
SurfaceType = 'TravelSurfaceType_func_fc'

FC = [Carriageway, UrbanCode, AccessControl, ThroughLanes, Median, Painted, AADT, JunctionLeg, OwnerMaint, Facility, FunClass, SurfaceType]

#query for missing attribution
print "Making attribute selections for non local paved"

arcpy.SelectLayerByAttribute_management(Carriageway, "NEW_SELECTION", """"CarriagewayDir" IS NULL AND "FromDate_2" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(FunClass, "NEW_SELECTION", """"FunctionalClass" IS NULL AND "FromDate_1" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(UrbanCode, "NEW_SELECTION", """"UrbanCode" IS NULL AND "FromDate_2" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AccessControl, "NEW_SELECTION", """"AccessControl" IS NULL AND "FromDate_2" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(Median, "NEW_SELECTION", """"MedianType" IS NULL AND "FromDate_2" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(Painted, "NEW_SELECTION", """"TurnLaneTwoWayLeft" IS NULL AND "FromDate_2" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"AADT" IS NULL AND "FromDate_2" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(JunctionLeg, "NEW_SELECTION", """"MasterLegID" IS NULL AND "FromDate_2" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(ThroughLanes, "NEW_SELECTION", """"NumberOfLanes" IS NULL AND "FromDate_2" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(SurfaceType, "NEW_SELECTION", """"SurfaceType" IS NULL AND "FromDate_2" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(Facility, "NEW_SELECTION", """"FacilityType" IS NULL AND "FromDate_2" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(OwnerMaint, "NEW_SELECTION", """"Ownership" IS NULL AND "FromDate_2" IS NOT NULL""")

for item in FC: 
	output_fe = gdbAll_Local_export + os.sep + str(item) + "_coverage_attr_selection"
	arcpy.CopyFeatures_management(item, output_fe)

print "Done with initial attribute selections"

#query for other layers
FC_other = [AADT, SurfaceType]

arcpy.SelectLayerByAttribute_management(SurfaceType, "NEW_SELECTION", """"SurfaceType" = 14 AND "FromDate_2" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"SubmittalYear" IS NULL AND "FromDate_2" IS NOT NULL""")

for item in FC_other:
	output_fe = gdbAll_Local_export + os.sep + str(item) + "surface_unknown_addt" + "_coverage_attr_selection"
	arcpy.CopyFeatures_management(item, output_fe)

print "Done with missing attribute selections"

#summarize attribute selections for all local roads
from arcpy import env, os

arcpy.env.workspace = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\All_Local_exports.gdb'

gdbAll_Local_export = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\All_Local_exports.gdb'

FC_stats = arcpy.ListFeatureClasses('*_coverage_attr_selection')

for item in FC_stats:
	print "Calculating Summary Statistics for" + " " + item
	stats = [["SHAPE_Length", "SUM"]]
	output_fc_attr = gdbAll_Local_export + os.sep + str(item) + "_attr_stats"
	arcpy.Statistics_analysis(item, output_fc_attr, stats)

print "Done with summary statistics"

#make tables for summary stats and write values to
print "Creating tables and adding data..."
arcpy.CreateTable_management(gdbAll_Local_export, "FC_All_Attr")
arcpy.AddField_management("FC_All_Attr", "data_items", "TEXT")
arcpy.AddField_management("FC_All_Attr", "feet_len",  "DOUBLE", "32", "16")
arcpy.AddField_management("FC_All_Attr", "mile_len",  "DOUBLE", "32", "16")

print 'copy information from stat tables into output table'
fields = ['data_items','feet_len', 'mile_len']
output_table = os.path.join(gdbAll_Local_export, "FC_All_Attr")
output_cursor = arcpy.da.InsertCursor(output_table, fields)

stats_tables = arcpy.ListTables()

for table in stats_tables:
        if not table.endswith('_attr_stats'):
                continue
        stat_fields = ['SUM_SHAPE_Length']
        with arcpy.da.SearchCursor(table, stat_fields) as cursor:
                for row in cursor:
                        output_row =[table, row[0], row[0]/5280]
                        output_cursor.insertRow(output_row)
row_count = 0
with arcpy.da.SearchCursor(output_table, fields) as cursor:
    for row in cursor:
        row_count += 1

print "{0} generated with {1} rows".format(output_table, row_count)

print "Done with all local roads coverage, doing ramps"

#reset env and query for ramp data items
from arcpy import env, os

arcpy.env.workspace = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\FCNonLoc_ramps.gdb'

gdbFCNonLoc_ramps_exports = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\FCNonLoc_ramps_exports.gdb'

AADT = 'AADT_ramps'
OwnerMaint = 'OwnerMaint_ramps'
FunClass = 'FunctionalClass_ramps'

ramp_items= [AADT, OwnerMaint, FunClass]

arcpy.SelectLayerByAttribute_management(FunClass, "NEW_SELECTION", """"FunctionalClass" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"AADT" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(OwnerMaint, "NEW_SELECTION", """"Ownership" IS NOT NULL""")

for item in ramp_items:
	output_fe = gdbFCNonLoc_ramps_exports + os.sep + str(item) + "_fc_ramp_coverage_selection"
	arcpy.CopyFeatures_management(item, output_fe)

print "Done with coverage selection, selecting for aadt year"

arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"SubmittalYear" IS NOT NULL""")
output_aadt_year = gdbFCNonLoc_ramps_exports + os.sep + "aadt_submit" + "_fc_ramp_coverage_selection"
arcpy.CopyFeatures_management(AADT, output_aadt_year)

print "Done with coverage selection, selecing for missing mileage"

FC_ramp_items= [AADT, OwnerMaint, FunClass]

arcpy.SelectLayerByAttribute_management(FunClass, "NEW_SELECTION", """"FunctionalClass" IS NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"AADT" IS NULL""")
arcpy.SelectLayerByAttribute_management(OwnerMaint, "NEW_SELECTION", """"Ownership" IS NULL""")

for item in FC_ramp_items:
	output_fe = gdbFCNonLoc_ramps_exports + os.sep + str(item) + "_fc_ramp_missing_selection"
	arcpy.CopyFeatures_management(item, output_fe)

print "Done with coverage selection, selecting for aadt year"

arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"SubmittalYear" IS NULL""")
output_aadt_missing = gdbFCNonLoc_ramps_exports + os.sep + "aadt_submit" + "_fc_ramp_missing_selection"
arcpy.CopyFeatures_management(AADT, output_aadt_missing)

print "Done with missing mileage selection, selecting for missing attributes"

FC_ramp_items= [AADT, OwnerMaint, FunClass]

arcpy.SelectLayerByAttribute_management(FunClass, "NEW_SELECTION", """"FunctionalClass" IS NULL AND "FromDate_1" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"AADT" IS NULL AND "FromDate_3" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(OwnerMaint, "NEW_SELECTION", """"Ownership" IS NULL AND "FromDate_3" IS NOT NULL""")

for item in FC_ramp_items: 
	output_fe = gdbFCNonLoc_ramps_exports + os.sep + str(item) + "_fc_ramp_attr_selection"
	arcpy.CopyFeatures_management(item, output_fe)

print "Done with initial attribute selections for ramps, querying for aadt year"

arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"SubmittalYear" IS NULL AND "FromDate_3" IS NOT NULL""")
output_aadt_attr = gdbFCNonLoc_ramps_exports + os.sep + "aadt_submit" + "_fc_ramp_attr_selection"
arcpy.CopyFeatures_management(AADT, output_aadt_attr)

print "Done with fc non local selections"

#run summary stats for fc non local ramps
from arcpy import env, os

arcpy.env.workspace = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\FCNonLoc_ramps_exports.gdb'

gdbFCNonLoc_ramps_exports = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\FCNonLoc_ramps_exports.gdb'

FCNonLocal_coverage = arcpy.ListFeatureClasses('*_fc_ramp_coverage_selection')

for item in FCNonLocal_coverage:
	print "Calculating Summary Statistics for" + " " + item
	stats = [["SHAPE_Length", "SUM"]]
	output_coverage = gdbFCNonLoc_ramps_exports + os.sep + str(item) + "_coverage_stats"
	arcpy.Statistics_analysis(item, output_coverage, stats)

print "Done with coverage stats, summing missing mileage"

FCNonLocal_missing = arcpy.ListFeatureClasses('*_fc_ramp_missing_selection')

for item in FCNonLocal_missing:
	print "Calculating Summary Statistics for" + " " + item
	stats = [["SHAPE_Length", "SUM"]]
	output_coverage = gdbFCNonLoc_ramps_exports + os.sep + str(item) + "_missing_stats"
	arcpy.Statistics_analysis(item, output_coverage, stats)

print "Done with missing mileage, summing missing attributes"

FCNonLocal_attr = arcpy.ListFeatureClasses('*_fc_ramp_attr_selection')

for item in FCNonLocal_attr:
	print "Calculating Summary Statistics for" + " " + item
	stats = [["SHAPE_Length", "SUM"]]
	output_coverage = gdbFCNonLoc_ramps_exports + os.sep + str(item) + "_attr_stats"
	arcpy.Statistics_analysis(item, output_coverage, stats)

print "Done with summary stats for fc non local ramps"

#make tables for summary stats and write values to
print "Creating tables and adding data..."
arcpy.CreateTable_management(gdbFCNonLoc_ramps_exports, "FC_NonLocal_Ramps_Coverage")
arcpy.AddField_management("FC_NonLocal_Ramps_Coverage", "data_items", "TEXT")
arcpy.AddField_management("FC_NonLocal_Ramps_Coverage", "feet_len",  "DOUBLE", "32", "16")
arcpy.AddField_management("FC_NonLocal_Ramps_Coverage", "mile_len",  "DOUBLE", "32", "16")

print 'copy information from stat tables into output table'
fields = ['data_items','feet_len', 'mile_len']
output_table = os.path.join(gdbFCNonLoc_ramps_exports, "FC_NonLocal_Ramps_Coverage")
output_cursor = arcpy.da.InsertCursor(output_table, fields)

stats_tables = arcpy.ListTables()

for table in stats_tables:
        if not table.endswith('_coverage_stats'):
                continue
        stat_fields = ['SUM_SHAPE_Length']
        with arcpy.da.SearchCursor(table, stat_fields) as cursor:
                for row in cursor:
                        output_row =[table, row[0], row[0]/5280]
                        output_cursor.insertRow(output_row)
row_count = 0
with arcpy.da.SearchCursor(output_table, fields) as cursor:
    for row in cursor:
        row_count += 1

print "{0} generated with {1} rows".format(output_table, row_count)
print "Done with ramp coverage table, making for missing mileage"

print "Creating tables and adding data..."
arcpy.CreateTable_management(gdbFCNonLoc_ramps_exports, "FC_NonLocal_Ramps_Missing")
arcpy.AddField_management("FC_NonLocal_Ramps_Missing", "data_items", "TEXT")
arcpy.AddField_management("FC_NonLocal_Ramps_Missing", "feet_len",  "DOUBLE", "32", "16")
arcpy.AddField_management("FC_NonLocal_Ramps_Missing", "mile_len",  "DOUBLE", "32", "16")

print 'copy information from stat tables into output table'
fields = ['data_items','feet_len', 'mile_len']
output_table = os.path.join(gdbFCNonLoc_ramps_exports, "FC_NonLocal_Ramps_Missing")
output_cursor = arcpy.da.InsertCursor(output_table, fields)

stats_tables = arcpy.ListTables()

for table in stats_tables:
        if not table.endswith('_missing_stats'):
                continue
        stat_fields = ['SUM_SHAPE_Length']
        with arcpy.da.SearchCursor(table, stat_fields) as cursor:
                for row in cursor:
                        output_row =[table, row[0], row[0]/5280]
                        output_cursor.insertRow(output_row)
row_count = 0
with arcpy.da.SearchCursor(output_table, fields) as cursor:
    for row in cursor:
        row_count += 1

print "{0} generated with {1} rows".format(output_table, row_count)
print "Done with missing mileage table, making for attribute selections"

print "Creating tables and adding data..."
arcpy.CreateTable_management(gdbFCNonLoc_ramps_exports, "FC_NonLocal_Ramps_Attr")
arcpy.AddField_management("FC_NonLocal_Ramps_Attr", "data_items", "TEXT")
arcpy.AddField_management("FC_NonLocal_Ramps_Attr", "feet_len",  "DOUBLE", "32", "16")
arcpy.AddField_management("FC_NonLocal_Ramps_Attr", "mile_len",  "DOUBLE", "32", "16")

print 'copy information from stat tables into output table'
fields = ['data_items','feet_len', 'mile_len']
output_table = os.path.join(gdbFCNonLoc_ramps_exports, "FC_NonLocal_Ramps_Attr")
output_cursor = arcpy.da.InsertCursor(output_table, fields)

stats_tables = arcpy.ListTables()

for table in stats_tables:
        if not table.endswith('_attr_stats'):
                continue
        stat_fields = ['SUM_SHAPE_Length']
        with arcpy.da.SearchCursor(table, stat_fields) as cursor:
                for row in cursor:
                        output_row =[table, row[0], row[0]/5280]
                        output_cursor.insertRow(output_row)
row_count = 0
with arcpy.da.SearchCursor(output_table, fields) as cursor:
    for row in cursor:
        row_count += 1

print "{0} generated with {1} rows".format(output_table, row_count)
print "Done with tables for fc non local ramps, selecting for all local roads"

#reset env and query for ramp data items for all local roads
from arcpy import env, os

arcpy.env.workspace = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\FCAll_ramps.gdb'

gdbFCAll_ramps_exports = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\FCAll_ramps_exports.gdb'

AADT = 'AADT_ramps'
OwnerMaint = 'OwnerMaint_ramps'
FunClass = 'FunctionalClass_ramps'

ramp_items= [AADT, OwnerMaint, FunClass]

arcpy.SelectLayerByAttribute_management(FunClass, "NEW_SELECTION", """"FunctionalClass" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"AADT" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(OwnerMaint, "NEW_SELECTION", """"Ownership" IS NOT NULL""")

for item in ramp_items:
	output_fe = gdbFCAll_ramps_exports + os.sep + str(item) + "_all_ramp_coverage_selection"
	arcpy.CopyFeatures_management(item, output_fe)

print "Done with coverage selection, selecting for aadt year"

arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"SubmittalYear" IS NOT NULL""")
output_aadt_year = gdbFCAll_ramps_exports + os.sep + "aadt_submit" + "_all_ramp_coverage_selection"
arcpy.CopyFeatures_management(AADT, output_aadt_year)

print "Done with coverage selection, selecing for missing mileage"

FC_ramp_items= [AADT, OwnerMaint, FunClass]

arcpy.SelectLayerByAttribute_management(FunClass, "NEW_SELECTION", """"FunctionalClass" IS NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"AADT" IS NULL""")
arcpy.SelectLayerByAttribute_management(OwnerMaint, "NEW_SELECTION", """"Ownership" IS NULL""")

for item in FC_ramp_items:
	output_fe = gdbFCAll_ramps_exports + os.sep + str(item) + "_all_ramp_missing_selection"
	arcpy.CopyFeatures_management(item, output_fe)

print "Done with coverage selection, selecting for aadt year"

arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"SubmittalYear" IS NULL""")
output_aadt_missing = gdbFCAll_ramps_exports + os.sep + "aadt_submit" + "_all_ramp_missing_selection"
arcpy.CopyFeatures_management(AADT, output_aadt_missing)

print "Done with missing mileage selection, selecting for missing attributes"

FC_ramp_items= [AADT, OwnerMaint, FunClass]

arcpy.SelectLayerByAttribute_management(FunClass, "NEW_SELECTION", """"FunctionalClass" IS NULL AND "FromDate_1" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"AADT" IS NULL AND "FromDate_3" IS NOT NULL""")
arcpy.SelectLayerByAttribute_management(OwnerMaint, "NEW_SELECTION", """"Ownership" IS NULL AND "FromDate_3" IS NOT NULL""")

for item in FC_ramp_items: 
	output_fe = gdbFCAll_ramps_exports + os.sep + str(item) + "_all_ramp_attr_selection"
	arcpy.CopyFeatures_management(item, output_fe)

print "Done with initial attribute selections for ramps, querying for aadt year"

arcpy.SelectLayerByAttribute_management(AADT, "NEW_SELECTION", """"SubmittalYear" IS NULL AND "FromDate_3" IS NOT NULL""")
output_aadt_attr = gdbFCAll_ramps_exports + os.sep + "aadt_submit" + "_all_ramp_attr_selection"
arcpy.CopyFeatures_management(AADT, output_aadt_attr)

print "Done with all local roads selections"

#run summary stats for fc non local ramps
from arcpy import env, os

arcpy.env.workspace = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\FCAll_ramps_exports.gdb'

gdbFCAll_ramps_exports = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\FCAll_ramps_exports.gdb'

FCNonLocal_coverage = arcpy.ListFeatureClasses('*_all_ramp_coverage_selection')

for item in FCNonLocal_coverage:
	print "Calculating Summary Statistics for" + " " + item
	stats = [["SHAPE_Length", "SUM"]]
	output_coverage = gdbFCAll_ramps_exports + os.sep + str(item) + "_coverage_stats"
	arcpy.Statistics_analysis(item, output_coverage, stats)

print "Done with coverage stats, summing missing mileage"

FCNonLocal_missing = arcpy.ListFeatureClasses('*_all_ramp_missing_selection')

for item in FCNonLocal_missing:
	print "Calculating Summary Statistics for" + " " + item
	stats = [["SHAPE_Length", "SUM"]]
	output_coverage = gdbFCAll_ramps_exports + os.sep + str(item) + "_missing_stats"
	arcpy.Statistics_analysis(item, output_coverage, stats)

print "Done with missing mileage, summing missing attributes"

FCNonLocal_attr = arcpy.ListFeatureClasses('*_all_ramp_attr_selection')

for item in FCNonLocal_attr:
	print "Calculating Summary Statistics for" + " " + item
	stats = [["SHAPE_Length", "SUM"]]
	output_coverage = gdbFCAll_ramps_exports + os.sep + str(item) + "_attr_stats"
	arcpy.Statistics_analysis(item, output_coverage, stats)

print "Done with summary stats for fc non local ramps"

#make tables for summary stats and write values to
print "Creating tables and adding data..."
arcpy.CreateTable_management(gdbFCAll_ramps_exports, "AllLocal_Ramps_Coverage")
arcpy.AddField_management("AllLocal_Ramps_Coverage", "data_items", "TEXT")
arcpy.AddField_management("AllLocal_Ramps_Coverage", "feet_len",  "DOUBLE", "32", "16")
arcpy.AddField_management("AllLocal_Ramps_Coverage", "mile_len",  "DOUBLE", "32", "16")

print 'copy information from stat tables into output table'
fields = ['data_items','feet_len', 'mile_len']
output_table = os.path.join(gdbFCAll_ramps_exports, "AllLocal_Ramps_Coverage")
output_cursor = arcpy.da.InsertCursor(output_table, fields)

stats_tables = arcpy.ListTables()

for table in stats_tables:
        if not table.endswith('_coverage_stats'):
                continue
        stat_fields = ['SUM_SHAPE_Length']
        with arcpy.da.SearchCursor(table, stat_fields) as cursor:
                for row in cursor:
                        output_row =[table, row[0], row[0]/5280]
                        output_cursor.insertRow(output_row)
row_count = 0
with arcpy.da.SearchCursor(output_table, fields) as cursor:
    for row in cursor:
        row_count += 1

print "{0} generated with {1} rows".format(output_table, row_count)
print "Done with ramp coverage table, making for missing mileage"

print "Creating tables and adding data..."
arcpy.CreateTable_management(gdbFCAll_ramps_exports, "AllLocal_Ramps_Missing")
arcpy.AddField_management("AllLocal_Ramps_Missing", "data_items", "TEXT")
arcpy.AddField_management("AllLocal_Ramps_Missing", "feet_len",  "DOUBLE", "32", "16")
arcpy.AddField_management("AllLocal_Ramps_Missing", "mile_len",  "DOUBLE", "32", "16")

print 'copy information from stat tables into output table'
fields = ['data_items','feet_len', 'mile_len']
output_table = os.path.join(gdbFCAll_ramps_exports, "AllLocal_Ramps_Missing")
output_cursor = arcpy.da.InsertCursor(output_table, fields)

stats_tables = arcpy.ListTables()

for table in stats_tables:
        if not table.endswith('_missing_stats'):
                continue
        stat_fields = ['SUM_SHAPE_Length']
        with arcpy.da.SearchCursor(table, stat_fields) as cursor:
                for row in cursor:
                        output_row =[table, row[0], row[0]/5280]
                        output_cursor.insertRow(output_row)
row_count = 0
with arcpy.da.SearchCursor(output_table, fields) as cursor:
    for row in cursor:
        row_count += 1

print "{0} generated with {1} rows".format(output_table, row_count)
print "Done with missing mileage table, making for attribute selections"

print "Creating tables and adding data..."
arcpy.CreateTable_management(gdbFCAll_ramps_exports, "AllLocal_Ramps_Attr")
arcpy.AddField_management("AllLocal_Ramps_Attr", "data_items", "TEXT")
arcpy.AddField_management("AllLocal_Ramps_Attr", "feet_len",  "DOUBLE", "32", "16")
arcpy.AddField_management("AllLocal_Ramps_Attr", "mile_len",  "DOUBLE", "32", "16")

print 'copy information from stat tables into output table'
fields = ['data_items','feet_len', 'mile_len']
output_table = os.path.join(gdbFCAll_ramps_exports, "AllLocal_Ramps_Attr")
output_cursor = arcpy.da.InsertCursor(output_table, fields)

stats_tables = arcpy.ListTables()

for table in stats_tables:
        if not table.endswith('_attr_stats'):
                continue
        stat_fields = ['SUM_SHAPE_Length']
        with arcpy.da.SearchCursor(table, stat_fields) as cursor:
                for row in cursor:
                        output_row =[table, row[0], row[0]/5280]
                        output_cursor.insertRow(output_row)
row_count = 0
with arcpy.da.SearchCursor(output_table, fields) as cursor:
    for row in cursor:
        row_count += 1

print "{0} generated with {1} rows".format(output_table, row_count)
print "Done with tables for all local roads, switching to junctions"

#make selections for junctions, summarize, and write to tables
from arcpy import env, os

map = arcpy.mapping.MapDocument("current")
df = arcpy.mapping.ListDataFrames(map) [0]

#set variables
Junctions = 'Junction'
NLP_network = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\NonLocal_Paved.gdb\overlay_network_fcs'
LP_network = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\Local_Paved.gdb\overlay_network_fcs'
UP_network = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\Unpaved.gdb\overlay_network_fcs'
FC_NonLocal_network = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\FC_NonLocal.gdb\FunctionalClass'
FC_All_network = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\All_Local.gdb\FunctionalClass'

#set output location
gdbJunction_Count = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\Junctions_count.gdb'

#export networks to rename
output_nlp = gdbJunction_Count + os.sep + "NLP_network"
arcpy.CopyFeatures_management(NLP_network, output_nlp)

output_lp = gdbJunction_Count + os.sep + "LP_network"
arcpy.CopyFeatures_management(LP_network, output_lp)

output_up = gdbJunction_Count + os.sep + "UP_network"
arcpy.CopyFeatures_management(UP_network, output_up)

#create definition queries for ownership
layer = arcpy.mapping.ListLayers(map, "NLP_network" , df)[0]
layer.definitionQuery = ' "Ownership" = \'DOT\''

layer = arcpy.mapping.ListLayers(map, "LP_network" , df)[0]
layer.definitionQuery = ' "Ownership" = \'DOT\''

layer = arcpy.mapping.ListLayers(map, "UP_network" , df)[0]
layer.definitionQuery = ' "Ownership" = \'DOT\''

print "Queries made"

#select junctions that intersect all networks and write to new feature classes
NLP = 'NLP_network'
LP = 'LP_network'
UP = 'UP_network'

arcpy.SelectLayerByLocation_management(Junctions, 'intersect', NLP)
output_junctions = gdbJunction_Count + os.sep + "Junctions_NLP_StateOwned"
arcpy.CopyFeatures_management(Junctions, output_junctions)

arcpy.SelectLayerByLocation_management(Junctions, 'intersect', LP)
output_junctions = gdbJunction_Count + os.sep + "Junctions_LP_StateOwned"
arcpy.CopyFeatures_management(Junctions, output_junctions)

arcpy.SelectLayerByLocation_management(Junctions, 'intersect', UP)
output_junctions = gdbJunction_Count + os.sep + "Junctions_UP_StateOwned"
arcpy.CopyFeatures_management(Junctions, output_junctions)

#reset definition query to query for non-state maint
layer = arcpy.mapping.ListLayers(map, "NLP_network" , df)[0]
layer.definitionQuery = ' "Ownership" <> \'DOT\''

layer = arcpy.mapping.ListLayers(map, "LP_network" , df)[0]
layer.definitionQuery = ' "Ownership" <> \'DOT\''

layer = arcpy.mapping.ListLayers(map, "UP_network" , df)[0]
layer.definitionQuery = ' "Ownership" <> \'DOT\''

#select junctions that intersect all networks and write to new feature classes
arcpy.SelectLayerByLocation_management(Junctions, 'intersect', NLP)
output_junctions = gdbJunction_Count + os.sep + "Junctions_NLP_NonStateOwned"
arcpy.CopyFeatures_management(Junctions, output_junctions)

arcpy.SelectLayerByLocation_management(Junctions, 'intersect', LP)
output_junctions = gdbJunction_Count + os.sep + "Junctions_LP_NonStateOwned"
arcpy.CopyFeatures_management(Junctions, output_junctions)

arcpy.SelectLayerByLocation_management(Junctions, 'intersect', UP)
output_junctions = gdbJunction_Count + os.sep + "Junctions_UP_NonStateOwned"
arcpy.CopyFeatures_management(Junctions, output_junctions)

arcpy.SelectLayerByLocation_management(Junctions, 'intersect', FC_NonLocal_network)
output_junctions = gdbJunction_Count + os.sep + "Junctions_FC_NonLocal"
arcpy.CopyFeatures_management(Junctions, output_junctions)

arcpy.SelectLayerByLocation_management(Junctions, 'intersect', FC_All_network)
output_junctions = gdbJunction_Count + os.sep + "Junctions_FC_All"
arcpy.CopyFeatures_management(Junctions, output_junctions)

print "Done making selecting for junctions on all networks"

#reset env and make selections
from arcpy import env ,os 

arcpy.env.workspace = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\Junctions_count.gdb'

gdbJunction_Count = 'C:\Users\E1774\Desktop\MIRE_Gap_Analysis\Junctions_count.gdb'

layers = [item for item in arcpy.ListFeatureClasses() if not item.endswith('network')]

for layer in layers:
	arcpy.SelectLayerByAttribute_management(layer, "NEW_SELECTION", """"MasterJunctionID" IS NOT NULL""")
	output_junctionID = gdbJunction_Count + os.sep + layer + "_uniqueID"
	arcpy.CopyFeatures_management(layer, output_junctionID)

for layer in layers:
	arcpy.SelectLayerByAttribute_management(layer, "NEW_SELECTION", """"JunctionGeometry" IS NOT NULL""")
	output_junctiongeom = gdbJunction_Count + os.sep + layer + "_junctiongeom"
	arcpy.CopyFeatures_management(layer, output_junctiongeom)

for layer in layers:
	arcpy.SelectLayerByAttribute_management(layer, "NEW_SELECTION", """"TrafficControl" IS NOT NULL""")
	output_junctioncontrol = gdbJunction_Count + os.sep + layer + "_trafficcontrol"
	arcpy.CopyFeatures_management(layer, output_junctioncontrol)

for layer in layers:
	arcpy.SelectLayerByAttribute_management(layer, "NEW_SELECTION", """"MasterJunctionID" IS NULL""")
	output_null_junctionID = gdbJunction_Count + os.sep + layer + "_null_uniqueID"
	arcpy.CopyFeatures_management(layer, output_null_junctionID)

for layer in layers:
	arcpy.SelectLayerByAttribute_management(layer, "NEW_SELECTION", """"JunctionGeometry" IS NULL""")
	output_null_junctiongeom = gdbJunction_Count + os.sep + layer + "_null_junctiongeom"
	arcpy.CopyFeatures_management(layer, output_null_junctiongeom)

for layer in layers:
	arcpy.SelectLayerByAttribute_management(layer, "NEW_SELECTION", """"TrafficControl" IS NULL""")
	output_null_junctioncontrol = gdbJunction_Count + os.sep + layer + "_null_trafficcontrol"
	arcpy.CopyFeatures_management(layer, output_null_junctioncontrol)

print "Done making attribute selections for junctions"

#clear selections and calculate summary stats
import arcpy, os
from arcpy import env
map = arcpy.mapping.MapDocument("current")
df = arcpy.mapping.ListDataFrames(map) [0]
for lyr in arcpy.mapping.ListLayers(map, "", df):
	arcpy.SelectLayerByAttribute_management(lyr,"CLEAR_SELECTION")

print "Selections cleared"

StateOwn_stats = arcpy.ListFeatureClasses("*_StateOwned*")

for item in StateOwn_stats:
	print "Calculating Summary Statistics for" + " " + item
	stats = [["OBJECTID", "COUNT"]]
	output_stateown = gdbJunction_Count + os.sep + str(item) + "_stateowned_statistics"
	arcpy.Statistics_analysis(item, output_stateown, stats)

NonStateOwn_stats = arcpy.ListFeatureClasses("*_NonStateOwned*")

for item in NonStateOwn_stats:
	print "Calculating Summary Statistics for" + " " + item
	stats = [["OBJECTID", "COUNT"]]
	output_nonstateown = gdbJunction_Count + os.sep + str(item) + "_nonstateowned_statistics"
	arcpy.Statistics_analysis(item, output_nonstateown, stats)

FC_stats = list(set(arcpy.ListFeatureClasses("*_FC_NonLocal*")) | set(arcpy.ListFeatureClasses("*_FC_All*")))

for item in FC_stats:
	print "Calculating Summary Statistics for" + " " + item
	stats = [["OBJECTID", "COUNT"]]
	output_fc = gdbJunction_Count + os.sep + str(item) + "_fc_statistics"
	arcpy.Statistics_analysis(item, output_fc, stats)

#write data to tables
print "Creating tables and adding data..."
arcpy.CreateTable_management(gdbJunction_Count, "StateOwned")
arcpy.AddField_management("StateOwned", "data_items", "TEXT")
arcpy.AddField_management("StateOwned", "count",  "LONG", 9)

print 'copy information from stat tables into output table'
fields = ['data_items','count']
output_table = os.path.join(gdbJunction_Count, "StateOwned")
output_cursor = arcpy.da.InsertCursor(output_table, fields)

stats_tables = arcpy.ListTables()

for table in stats_tables:
        if not table.endswith('_stateowned_statistics'):
                continue
        stat_fields = ['COUNT_OBJECTID']
        with arcpy.da.SearchCursor(table, stat_fields) as cursor:
                for row in cursor:
                        output_row =[table, row[0]]
                        output_cursor.insertRow(output_row)
row_count = 0
with arcpy.da.SearchCursor(output_table, fields) as cursor:
    for row in cursor:
        row_count += 1

print "{0} generated with {1} rows".format(output_table, row_count)

print "Creating tables and adding data..."
arcpy.CreateTable_management(gdbJunction_Count, "NonStateOwned")
arcpy.AddField_management("NonStateOwned", "data_items", "TEXT")
arcpy.AddField_management("NonStateOwned", "count",  "LONG", 9)

print 'copy information from stat tables into output table'
fields = ['data_items','count']
output_table = os.path.join(gdbJunction_Count, "NonStateOwned")
output_cursor = arcpy.da.InsertCursor(output_table, fields)

stats_tables = arcpy.ListTables()

for table in stats_tables:
        if not table.endswith('_nonstateowned_statistics'):
                continue
        stat_fields = ['COUNT_OBJECTID']
        with arcpy.da.SearchCursor(table, stat_fields) as cursor:
                for row in cursor:
                        output_row =[table, row[0]]
                        output_cursor.insertRow(output_row)
row_count = 0
with arcpy.da.SearchCursor(output_table, fields) as cursor:
    for row in cursor:
        row_count += 1

print "{0} generated with {1} rows".format(output_table, row_count)

print "Creating tables and adding data..."
arcpy.CreateTable_management(gdbJunction_Count, "FC_NonLocal_and_FC_All")
arcpy.AddField_management("FC_NonLocal_and_FC_All", "data_items", "TEXT")
arcpy.AddField_management("FC_NonLocal_and_FC_All", "count",  "LONG", 9)

print 'copy information from stat tables into output table'
fields = ['data_items','count']
output_table = os.path.join(gdbJunction_Count, "FC_NonLocal_and_FC_All")
output_cursor = arcpy.da.InsertCursor(output_table, fields)

stats_tables = arcpy.ListTables()

for table in stats_tables:
        if not table.endswith('_fc_statistics'):
                continue
        stat_fields = ['COUNT_OBJECTID']
        with arcpy.da.SearchCursor(table, stat_fields) as cursor:
                for row in cursor:
                        output_row =[table, row[0]]
                        output_cursor.insertRow(output_row)
row_count = 0
with arcpy.da.SearchCursor(output_table, fields) as cursor:
    for row in cursor:
        row_count += 1

print "{0} generated with {1} rows".format(output_table, row_count)

print "Done with junctions - You Win!!!!"