import arcpy
import os
import zipfile
import re
import datetime
import concurrent.futures
import itertools
import shutil


# Set Variables

Year = arcpy.GetParameterAsText(0)
DeliveryNumber = arcpy.GetParameterAsText(1)
Date = arcpy.GetParameterAsText(2)
zipfile_path = arcpy.GetParameterAsText(3)
routing_fc = arcpy.GetParameterAsText(4)
prev_year_del = arcpy.GetParameterAsText(5)
database_connection = arcpy.GetParameterAsText(6)
tolerance=5 #in terms of % so 5 = 5% change
false_positive_table="I:\TaskAssignments\Master\HPMSBins_MasterTables.gdb\FalsePositive_Near_MasterBinsList"
arcpy.AddMessage( "Starting Geometry Review Script for - {0}".format(zipfile_path))

# generate workspace variables
basefolder_path = os.path.dirname(zipfile_path)
input_gdb= os.path.join(basefolder_path,basefolder_path,os.path.splitext(os.path.basename(zipfile_path))[0])
review_folder = os.path.join(basefolder_path, "AZ{0}_Delivery{1}_forReview".format(Year, DeliveryNumber))
output_mxd=os.path.join(review_folder,"AZ{0}_Delivery{1}_forReview.mxd".format(Year, DeliveryNumber))
output_gdb=os.path.join(basefolder_path,review_folder,"Delivery{1}_forReview.gdb".format(Year,DeliveryNumber))
input_fc= os.path.join(input_gdb, "GIS_Delivery_{0}".format(DeliveryNumber))
input_fc_copy=os.path.join(output_gdb, "GIS_Delivery_{0}".format(DeliveryNumber))
review_delivery_unprojected = os.path.join(output_gdb, "Delivery{0}_forReview_unprojected".format(DeliveryNumber))
review_delivery= os.path.join(output_gdb, "Delivery{0}_forReview".format(DeliveryNumber))
review_folder_forvendor=os.path.join(review_folder, "AZ{0}_Delivery{1}_ADOTFeedback_{2}".format(Year, DeliveryNumber,Date))
output_gdb_forvendor=os.path.join(review_folder_forvendor,"Delivery{0}_ADOTFeedback.gdb".format(DeliveryNumber))
output_fc_forvendor=os.path.join(output_gdb_forvendor,"Delivery{0}_ADOTFeedback".format(DeliveryNumber))
master_gdb=os.path.join(basefolder_path,"Master.gdb")
# Create review folder
if not arcpy.Exists(review_folder):
    os.makedirs(review_folder)
    arcpy.AddMessage( "Review Folder Created - {0}".format(review_folder))

# Create review gdb
if not arcpy.Exists(output_gdb):
    arcpy.management.CreateFileGDB(review_folder, "Delivery{1}_forReview".format(Year,DeliveryNumber))
    arcpy.AddMessage( "Review GDB Created - {0}".format(output_gdb))
    
# Unzip vendor delivery file
    with zipfile.ZipFile(zipfile_path, 'r') as zip_ref:
        zip_ref.extractall(basefolder_path)
        arcpy.AddMessage( "Delivery {0} unzipped to - {1}".format(DeliveryNumber,basefolder_path))
        
arcpy.env.workspace = output_gdb
# Copy the feature class to the destination GDB
if not arcpy.Exists(review_delivery_unprojected):
    arcpy.FeatureClassToGeodatabase_conversion(input_fc,output_gdb)
    arcpy.AddMessage( "Delivery {0} moved to - {1}".format(DeliveryNumber,output_gdb))
#Rename
    arcpy.Rename_management(input_fc_copy,"Delivery{0}_forReview_unprojected".format(DeliveryNumber))
#Move Zip file
if not os.path.exists(os.path.join(zipfile_path,review_folder)):
    shutil.move(zipfile_path,review_folder)
if arcpy.Exists(input_gdb):
    arcpy.Delete_management(input_gdb)
#Project
if not arcpy.Exists(review_delivery):
    arcpy.Project_management("Delivery{0}_forReview_unprojected".format(DeliveryNumber),"Delivery{0}_forReview".format(DeliveryNumber),routing_fc)
    arcpy.AddMessage( "Delivery {0} Projected to Arizona State Plane Central (this is the feature class used for analysis)".format(DeliveryNumber,output_gdb))

if not arcpy.Exists(output_mxd):
# Save MXD
    mxd2 = arcpy.mapping.MapDocument(r"I:\TaskAssignments\ICC_2023\GeometryReview\Toolbox\NODELETE_ForScript.mxd")

# Add Layers to MXD
    dataframe = arcpy.mapping.ListDataFrames(mxd2)[0]

    arcpy.MakeFeatureLayer_management(r"{0}\ATIS_Prod.DBO.LRSN_ATIS_Routes".format(database_connection), "ATIS Routes")
    ATIS = arcpy.mapping.Layer("ATIS Routes")
    arcpy.mapping.AddLayer(dataframe, ATIS, "AUTO_ARRANGE")

    arcpy.MakeFeatureLayer_management(r"{0}\ATIS_Prod.DBO.LRSE_HPMSBins".format(database_connection), "HPMS_Bins")
    Bins = arcpy.mapping.Layer("HPMS_Bins")
    arcpy.mapping.AddLayer(dataframe, Bins, "AUTO_ARRANGE")

# Remove the existing "Routing File" layer if it already exists
    existing_routing_layer = arcpy.mapping.ListLayers(mxd2, "Routing File", dataframe)
    if existing_routing_layer:
        arcpy.mapping.RemoveLayer(dataframe, existing_routing_layer[0])

    arcpy.MakeFeatureLayer_management(routing_fc, "Routing File")
    Routing = arcpy.mapping.Layer("Routing File")
    arcpy.mapping.AddLayer(dataframe, Routing, "AUTO_ARRANGE")

    arcpy.MakeFeatureLayer_management(review_delivery, "Delivery {0} for Review".format(DeliveryNumber))
    delivery_layer = arcpy.mapping.Layer("Delivery {0} for Review".format(DeliveryNumber))
    arcpy.mapping.AddLayer(dataframe, delivery_layer, "AUTO_ARRANGE")
    mxd2.saveACopy(output_mxd)
    arcpy.AddMessage( "Delivery {0} MXD saved to - {1}. Includes the Delivery for Review, ATIS Routes , HPMSBins, and The Current Routing File as layers.".format(DeliveryNumber,output_mxd))

    
field_names = [field.name for field in arcpy.ListFields(review_delivery)]
routing_fieldnames= [field.name for field in arcpy.ListFields(routing_fc)]

### TESTS  

master_start_time=datetime.datetime.now()
master_str_start_time=datetime.datetime.now().strftime("%H:%M:%S")
arcpy.AddMessage("Beginning Checks @ {0}".format(master_str_start_time))

###SCHEMA 

str_start_time = datetime.datetime.now().strftime("%H:%M:%S")
arcpy.AddMessage("START CHECK - Feature Class Expected Schema (against routing file) - {0}".format(str_start_time))

def compare_schema(feature_class1, feature_class2, exclude_fields=None):
    # Get the field information for feature class 1
    fields1 = arcpy.ListFields(feature_class1)

    # Get the field information for feature class 2
    fields2 = arcpy.ListFields(feature_class2)

    # Compare field names
    field_names1 = [field.name for field in fields1]
    field_names2 = [field.name for field in fields2]
    field_name_diff = set(field_names1) - set(field_names2)

    # Exclude fields if specified
    if exclude_fields:
        field_name_diff -= set(exclude_fields)

    # Compare field types
    field_types1 = [(field.name, field.type) for field in fields1]
    field_types2 = [(field.name, field.type) for field in fields2]
    field_type_diff = [(name, type1, type2) for name, type1 in field_types1 for name2, type2 in field_types2 if name == name2 and type1 != type2]

    return field_name_diff, field_type_diff


# List of fields to exclude from the schema check
excluded_fields = ["Comments_For_ADOT", "Comments_To_Vendor", "Percent_Coverage", "Distance_ToRoutedBin"]

# Compare the schema of the feature classes
field_name_diff, field_type_diff = compare_schema(review_delivery, routing_fc, exclude_fields=excluded_fields)

# Print the differences in field names
if field_name_diff:
    arcpy.AddMessage("Differences in field names:")
    for field_name in field_name_diff:
        arcpy.AddMessage(field_name)
else:
    arcpy.AddMessage("No differences in field names.")

# Print the differences in field types
if field_type_diff:
    arcpy.AddMessage("Differences in field types:")
    for name, type1, type2 in field_type_diff:
        arcpy.AddMessage("Field '{0}' has different types: {1} (Delivery) vs {2} (Routing)".format(name, type1, type2))
else:
    arcpy.AddMessage("No differences in field types.")

str_end_time = datetime.datetime.now().strftime("%H:%M:%S")
start_time = datetime.datetime.strptime(str_start_time, "%H:%M:%S")
end_time = datetime.datetime.strptime(str_end_time, "%H:%M:%S")
elapsed_time = end_time - start_time
arcpy.AddMessage("END CHECK - Feature Class Expected Schema - {0}. Run Time: {1}".format(str_end_time, elapsed_time))



### ADD REVIEW FIELDS    
field_names = [field.name for field in arcpy.ListFields(review_delivery)]
routing_fieldnames= [field.name for field in arcpy.ListFields(routing_fc)]
if not "Comments_For_ADOT" in field_names:
    arcpy.management.AddField(review_delivery, "Comments_For_ADOT","TEXT",field_alias="Comments_For_ADOT" )
    arcpy.management.AddField(review_delivery, "Comments_To_Vendor","TEXT",field_alias="Comments_To_Vendor" )
    arcpy.AddMessage( "Delivery {0} - fields added 'Comments_For_ADOT' &'Comments_To_Vendor' ".format(DeliveryNumber))
    arcpy.AddMessage( "Use 'Comments_For_ADOT' &'Comments_To_Vendor' to store final comments for specific group".format(DeliveryNumber))
    
arcpy.AddField_management(review_delivery, "Percent_Coverage", "DOUBLE")
field_names.append("Percent_Coverage")
arcpy.AddField_management(review_delivery, "Distance_ToRoutedBin", "DOUBLE")
field_names.append("Distance_ToRoutedBin")
field_names.append("SHAPE@")
routing_fieldnames.append("SHAPE@")


### 32 CHARACTER PROBLEMS - ROUTEID 
str_start_time = datetime.datetime.now().strftime("%H:%M:%S")
arcpy.AddMessage("START CHECK - RouteId 32 Character Compliance - {0}".format(str_start_time))

updated_count = 0

# Create a dictionary to store the mapping between HPMS_BinID and RouteID
routeid_mapping = {}

# Iterate over the routing feature class and populate the dictionary
with arcpy.da.SearchCursor(routing_fc, ["HPMS_BinID", "RouteId"]) as routing_cursor:
    for row in routing_cursor:
        hpms_bin_id = row[0]
        route_id = row[1]
        routeid_mapping[hpms_bin_id] = route_id

# Perform the update operation on the review_delivery feature class
with arcpy.da.UpdateCursor(review_delivery, ["HPMS_BinID", "RouteId"]) as update_cursor:
    for row in update_cursor:
        hpms_bin_id = row[0]
        if hpms_bin_id in routeid_mapping:
            row[1] = routeid_mapping[hpms_bin_id]
            update_cursor.updateRow(row)
            updated_count += 1

# Print the number of records that were updated
if updated_count > 0:
    arcpy.AddMessage("{} records were updated.".format(updated_count))

str_end_time = datetime.datetime.now().strftime("%H:%M:%S")
start_time = datetime.datetime.strptime(str_start_time, "%H:%M:%S")
end_time = datetime.datetime.strptime(str_end_time, "%H:%M:%S")
elapsed_time = (end_time - start_time)
arcpy.AddMessage("END CHECK - RouteId 32 Character Compliance - {0}. Run Time: {1}".format(str_end_time, elapsed_time))

### All BINIDS EXIST IN ROUTING
str_start_time=None
str_end_time=None
elapsed_time=None
str_start_time = datetime.datetime.now().strftime("%H:%M:%S")
arcpy.AddMessage("START CHECK - Valid BinId - {0}".format(str_start_time))
def test_bin_delivery_in_routing(routing_fc, review_delivery, output_gdb):
    import arcpy
    import os
    
    # Get the set of HPMSBin_ID values from the routing feature class
    routing_ids = set()
    with arcpy.da.SearchCursor(routing_fc, "HPMS_BinID") as cursor:
        for row in cursor:
            routing_ids.add(row[0])

    # Get the set of HPMSBin_ID values from the delivery feature class
    delivery_ids = set()
    with arcpy.da.SearchCursor(review_delivery, "HPMS_BinID") as cursor:
        for row in cursor:
            delivery_ids.add(row[0])

    # Find the missing HPMSBin_IDs
    missing_ids = delivery_ids - routing_ids

    # Create a new feature class to store the missing IDs
    output_fc = "MissingBinIds_ToReview"
    if arcpy.Exists("MissingBinIds_ToReview"):
        arcpy.Delete_management("MissingBinIds_ToReview")
    arcpy.CreateFeatureclass_management(output_gdb, "MissingBinIds_ToReview", "POLYLINE", spatial_reference=routing_fc)

    # Add the HPMSBinID field to the new feature class
    arcpy.AddField_management(os.path.join(output_gdb, output_fc), "HPMSBinID", "TEXT")

    # Use an insert cursor to populate the new feature class with the missing IDs
    with arcpy.da.InsertCursor(os.path.join(output_gdb, output_fc), ["SHAPE@", "HPMSBinID"]) as cursor:
        for bin_id in missing_ids:
            cursor.insertRow([None, bin_id])

    # Print the count of missing HPMSBin_IDs
    count = len(missing_ids)
    if count > 0:
        arcpy.AddMessage("{} records were found".format(count))
    else:
        arcpy.Delete_management(os.path.join(output_gdb, output_fc))

test_bin_delivery_in_routing(routing_fc, review_delivery, output_gdb)
str_end_time = datetime.datetime.now().strftime("%H:%M:%S")
start_time = datetime.datetime.strptime(str_start_time, "%H:%M:%S")
end_time = datetime.datetime.strptime(str_end_time, "%H:%M:%S")
elapsed_time = (end_time - start_time)
arcpy.AddMessage("END CHECK - Valid BinId - {0}. Run Time: {1}".format(str_end_time,elapsed_time))


### NULL SHAPES
str_start_time=None
str_end_time=None
elapsed_time=None
str_start_time = datetime.datetime.now().strftime("%H:%M:%S")
arcpy.AddMessage("START CHECK - NULL Shape - {0}".format(str_start_time))
if arcpy.Exists("NoShape_ForReview"):
        arcpy.Delete_management("NoShape_ForReview")
arcpy.CreateFeatureclass_management(output_gdb, "NoShape_ForReview", "POLYLINE", review_delivery,
                                    spatial_reference=arcpy.Describe(review_delivery).spatialReference)

with arcpy.da.InsertCursor("NoShape_ForReview", field_names) as cursor:
    with arcpy.da.SearchCursor(review_delivery, field_names) as search_cursor:
        for row in search_cursor:
            shape = row[field_names.index("Shape_Length")]  # Access the SHAPE field value
            if shape is None:
                cursor.insertRow(row)

if int(arcpy.GetCount_management("NoShape_ForReview").getOutput(0)) > 0:
    arcpy.AddMessage( " {0} records found.".format(str(arcpy.GetCount_management("NoShape_ForReview").getOutput(0))))
else:
    arcpy.Delete_management("NoShape_ForReview")
str_end_time = datetime.datetime.now().strftime("%H:%M:%S")
start_time = datetime.datetime.strptime(str_start_time, "%H:%M:%S")
end_time = datetime.datetime.strptime(str_end_time, "%H:%M:%S")
elapsed_time = (end_time - start_time)
arcpy.AddMessage("END CHECK - NULL Shape - {0}. Run Time: {1}".format(str_end_time,elapsed_time))


### DUPLICATES
str_start_time=None
str_end_time=None
elapsed_time=None
str_start_time = datetime.datetime.now().strftime("%H:%M:%S")                
arcpy.AddMessage("START CHECK - Duplicate BinIds - {0}".format(str_start_time))
arcpy.CreateFeatureclass_management(output_gdb, "Duplicates_ForReview", "POLYLINE", review_delivery,
                                    spatial_reference=arcpy.Describe(review_delivery).spatialReference)

duplicate_dict = {}
with arcpy.da.SearchCursor(review_delivery, field_names) as search_cursor:
    for row in search_cursor:
        shape = row[field_names.index("Shape_Length")]
        value = row[field_names.index("HPMS_BinID")]
        if value in duplicate_dict:
            duplicate_dict[value].append(row)
        else:
            duplicate_dict[value] = [row]

duplicate_pairs = []
for bin_id, rows in duplicate_dict.items():
    if len(rows) > 1:
        duplicate_pairs.extend(rows)

if len(duplicate_pairs) > 0:
    with arcpy.da.InsertCursor("Duplicates_ForReview", field_names) as cursor:
        for row in duplicate_pairs:
            cursor.insertRow(row)
    arcpy.AddMessage("{} records found.".format(len(duplicate_pairs)))
else:
    arcpy.Delete_management("Duplicates_ForReview")
str_end_time = datetime.datetime.now().strftime("%H:%M:%S")
start_time = datetime.datetime.strptime(str_start_time, "%H:%M:%S")
end_time = datetime.datetime.strptime(str_end_time, "%H:%M:%S")
elapsed_time = (end_time - start_time)
arcpy.AddMessage("END CHECK - Duplicate BinIds - {0}. Run Time: {1}".format(str_end_time,elapsed_time))


### LENGTH COMPARISION
str_start_time = datetime.datetime.now().strftime("%H:%M:%S")
arcpy.AddMessage("START CHECK - Length Comparision (against routing file) - {0}".format(str_start_time))

non_compliant_records = []

# Create a dictionary to store the original bin lengths based on HPMS_BinID in the routing feature class
org_lengths = {}
with arcpy.da.SearchCursor(routing_fc, routing_fieldnames) as cursor:
    for org in cursor:
        org_hpms_bin_id = org[routing_fieldnames.index("HPMS_BinID")]
        org_shape_length = org[routing_fieldnames.index("Shape_Length")]
        org_lengths[org_hpms_bin_id] = org_shape_length

# Use update cursor to calculate the percent coverage in the review feature class
with arcpy.da.UpdateCursor(review_delivery, field_names + ["Percent_Coverage"]) as update_cursor:
    for row in update_cursor:
        shape_length = row[field_names.index("Shape_Length")]
        hpms_bin_id = row[field_names.index("HPMS_BinID")]
        if hpms_bin_id in org_lengths:
            original_length = org_lengths[hpms_bin_id]
            coverage = (shape_length / original_length) * 100
            row[len(field_names)] = coverage  # Update the last field (Percent_Coverage)
            update_cursor.updateRow(row)
            if coverage < 50:
                non_compliant_records.append(list(row))  # Append the field values as a list

# Print the count of non-compliant records
if len(non_compliant_records) > 0:
    arcpy.AddMessage("{} records found.".format(len(non_compliant_records)))
    length_comparison_table = "LengthComparison_ToReview"
    arcpy.CreateFeatureclass_management(output_gdb, length_comparison_table, "POLYLINE", review_delivery, spatial_reference=review_delivery)
    with arcpy.da.InsertCursor(length_comparison_table, field_names + ["Percent_Coverage"]) as insert_cursor:
        for record in non_compliant_records:
            insert_cursor.insertRow(record)
else:
    arcpy.Delete_management("LengthComparision_ToReview")
str_end_time = datetime.datetime.now().strftime("%H:%M:%S")
start_time = datetime.datetime.strptime(str_start_time, "%H:%M:%S")
end_time = datetime.datetime.strptime(str_end_time, "%H:%M:%S")
elapsed_time = end_time - start_time

arcpy.AddMessage("END CHECK - Length Comparison (against routing file) - {0}. Run Time: {1}".format(str_end_time, elapsed_time))

###SECTION ID GAPS 
str_start_time=None
str_end_time=None
elapsed_time=None
str_start_time = datetime.datetime.now().strftime("%H:%M:%S")
arcpy.AddMessage("START CHECK - SESSION Gaps - {0}".format(str_start_time))
# Dissolve the delivery by Session and RouteID
dissolved_delivery = arcpy.management.Dissolve(review_delivery, r"in_memory\dissolved_delivery", ["Session", "RouteId"])

# Sort the dissolved features by Session, RouteID, and start measure
sorted_delivery = arcpy.management.Sort(dissolved_delivery, r"in_memory\sorted_delivery", [["Session", "ASCENDING"], ["RouteId", "ASCENDING"]])

# Get the spatial reference from the sorted delivery
spatial_reference = arcpy.Describe(review_delivery).spatialReference

# Create a new feature class for the gaps
gap_feature_class = arcpy.management.CreateFeatureclass(
    arcpy.env.workspace, "SectionId_Gaps_ToReview", "POLYLINE", None, None, None, spatial_reference
)

# Add fields to store gap information
arcpy.management.AddField(gap_feature_class, "Session", "TEXT")
arcpy.management.AddField(gap_feature_class, "RouteId", "TEXT")
arcpy.management.AddField(gap_feature_class, "Gap_Length", "DOUBLE")

# Find and create gaps
with arcpy.da.SearchCursor(sorted_delivery, ["Session", "RouteId", "Shape@"]) as search_cursor:
    with arcpy.da.InsertCursor(gap_feature_class, ["Session", "RouteId", "Shape@", "Gap_Length"]) as insert_cursor:
        previous_section = None
        previous_route_id = None
        previous_end_measure = None

        for row in search_cursor:
            section = row[0]
            route_id = row[1]
            shape = row[2]
            start_measure = shape.firstPoint.M
            end_measure = shape.lastPoint.M

            if (
                previous_section is not None
                and previous_route_id is not None
                and section == previous_section
                and route_id == previous_route_id
            ):
                gap_length = start_measure - previous_end_measure

                if gap_length > 0:
                    gap_geometry = arcpy.Geometry("polyline", spatial_reference)
                    gap_geometry.addPart(shape.getPart(0))
                    gap_geometry.addPart(arcpy.Array([shape.lastPoint]))

                    insert_cursor.insertRow((section, route_id, gap_geometry, gap_length))

            previous_section = section
            previous_route_id = route_id
            previous_end_measure = end_measure

# Print the count of gap features
gap_count = int(arcpy.GetCount_management(gap_feature_class).getOutput(0))

# Delete the feature class if there are no gaps
if gap_count == 0:
    arcpy.management.Delete(gap_feature_class)
else:
    arcpy.AddMessage("{0} records found.".format(gap_count))
str_end_time = datetime.datetime.now().strftime("%H:%M:%S")
start_time = datetime.datetime.strptime(str_start_time, "%H:%M:%S")
end_time = datetime.datetime.strptime(str_end_time, "%H:%M:%S")
elapsed_time = (end_time - start_time)
arcpy.AddMessage("END CHECK - SESSION Gaps- {0}. Run Time: {1}".format(str_end_time,elapsed_time))


### INTERSECTIONS
str_start_time=None
str_end_time=None
elapsed_time=None
str_start_time = datetime.datetime.now().strftime("%H:%M:%S")
arcpy.AddMessage("START CHECK - Intersections - {0}".format(str_start_time))
# Create a new feature class for the intersections
intersection_feature_class = os.path.join(output_gdb, "Intersection_ToReview")
arcpy.Intersect_analysis([review_delivery], intersection_feature_class)

# Print the count of features
feature_count = int(arcpy.GetCount_management(intersection_feature_class).getOutput(0))
if feature_count > 0:
    arcpy.AddMessage("{0} records found.".format(feature_count))
else:
    arcpy.management.Delete(intersection_feature_class)
str_end_time=datetime.datetime.now().strftime("%H:%M:%S")
start_time = datetime.datetime.strptime(str_start_time, "%H:%M:%S")
end_time = datetime.datetime.strptime(str_end_time, "%H:%M:%S")
elapsed_time = (end_time - start_time)
arcpy.AddMessage("END CHECK - Intersections - {0}. Run Time: {1}".format(str_end_time,elapsed_time))

### ELEVATION 
str_start_time=None
str_end_time=None
elapsed_time=None
str_start_time = datetime.datetime.now().strftime("%H:%M:%S")
## This needs to use cardinality and direction of collection

arcpy.AddMessage("START CHECK - Elevation Continuity - {0}".format(str_start_time))
# Sort the delivery features by RouteID, FromMeasure, and ToMeasure
sorted_delivery = arcpy.management.Sort(review_delivery, r"in_memory\sorted_delivery",[["RouteId", "ASCENDING"], ["FromMeasure", "ASCENDING"], ["ToMeasure", "ASCENDING"]])
reverse_sorted_delivery = arcpy.management.Sort(review_delivery, r"in_memory\rev_sorted_delivery",[["RouteId", "ASCENDING"], ["FromMeasure", "DESCENDING"], ["ToMeasure", "DESCENDING"]])

# Create a new feature class to store the features with elevation changes
if arcpy.Exists("ElevationChange_ToReview"):
     arcpy.Delete_management("ElevationChange_ToReview")
elevation_change_feature_class = arcpy.management.CreateFeatureclass(
    arcpy.env.workspace, "ElevationChange_ToReview", "POLYLINE", spatial_reference=review_delivery)

# Add fields to store elevation change information
arcpy.management.AddField(elevation_change_feature_class, "RouteId", "TEXT")
arcpy.management.AddField(elevation_change_feature_class, "ELEVATION_BEGIN", "DOUBLE")
arcpy.management.AddField(elevation_change_feature_class, "ELEVATION_END", "DOUBLE")
arcpy.management.AddField(elevation_change_feature_class, "ElevationChange", "DOUBLE")
arcpy.management.AddField(elevation_change_feature_class, "HPMSBinID1", "TEXT")
arcpy.management.AddField(elevation_change_feature_class, "HPMSBinID2", "TEXT")
arcpy.management.AddField(elevation_change_feature_class, "Cardinality_REF", "TEXT")
#CardinalSide
# Search for elevation changes
with arcpy.da.SearchCursor(sorted_delivery, ["RouteId", "FromMeasure", "ToMeasure", "ELEVATION_BEGIN", "ELEVATION_END", "Shape@", "HPMS_BinID","Cardinality_REF"],"Cardinality_REF='C'") as search_cursor:
    with arcpy.da.InsertCursor(elevation_change_feature_class, ["RouteId", "ELEVATION_BEGIN", "ELEVATION_END", "ElevationChange", "Shape@", "HPMSBinID1", "HPMSBinID2","Cardinality_REF"]) as insert_cursor:
        previous_route_id = None
        previous_end_elevation = None
        previous_bin_id = None

        for row in search_cursor:
            route_id = row[0]
            from_measure = row[1]
            to_measure = row[2]
            begin_elevation = row[3]
            end_elevation = row[4]
            shape = row[5]
            bin_id = row[6]
            card=row[7]
            # Extract the numerical part from the HPMSBinID
            bin_number = re.findall(r'\d+', bin_id)[-1]

            # Check for consecutive bins on the same route and exclude HPMSBin IDs with an absolute difference greater than 1
            if (
                previous_route_id is not None
                and previous_route_id == route_id
                and abs(int(bin_number) - int(previous_bin_number)) <= 1
                and abs((begin_elevation - previous_end_elevation)/previous_end_elevation)*100 > tolerance  # Adjust the threshold as needed
            ):
                elevation_change = abs(begin_elevation - previous_end_elevation)
                insert_cursor.insertRow((route_id, previous_end_elevation, begin_elevation, elevation_change, shape, previous_bin_id, bin_id,card))

            previous_route_id = route_id
            previous_end_elevation = end_elevation
            previous_bin_id = bin_id
            previous_bin_number = bin_number
# NonCardinalSide
with arcpy.da.SearchCursor(reverse_sorted_delivery, ["RouteId", "FromMeasure", "ToMeasure", "ELEVATION_BEGIN", "ELEVATION_END", "Shape@", "HPMS_BinID", "Cardinality_REF"], "Cardinality_REF='N'") as nc_search_cursor:
    with arcpy.da.InsertCursor(elevation_change_feature_class, ["RouteId", "ELEVATION_BEGIN", "ELEVATION_END", "ElevationChange", "Shape@", "HPMSBinID1", "HPMSBinID2", "Cardinality_REF"]) as nc_insert_cursor:
        nc_previous_route_id = None
        nc_previous_end_elevation = None
        nc_previous_bin_id = None

        for row in nc_search_cursor:
            nc_route_id = row[0]
            nc_from_measure = row[1]
            nc_to_measure = row[2]
            nc_begin_elevation = row[3]
            nc_end_elevation = row[4]
            nc_shape = row[5]
            nc_bin_id = row[6]
            nc_card = row[7]
            # Extract the numerical part from the HPMSBinID
            nc_bin_number = re.findall(r'\d+', nc_bin_id)[-1]

            # Check for consecutive bins on the same route and exclude HPMSBin IDs with an absolute difference greater than 1
            if (
                nc_previous_route_id is not None
                and nc_previous_route_id == nc_route_id
                and abs(int(nc_bin_number) - int(nc_previous_bin_number)) <= 1
                and abs((nc_begin_elevation - nc_previous_end_elevation) / nc_previous_end_elevation) * 100 > tolerance  # Adjust the threshold as needed
            ):
                elevation_change = abs(nc_begin_elevation - nc_previous_end_elevation)
                nc_insert_cursor.insertRow((nc_route_id, nc_previous_end_elevation, nc_begin_elevation, elevation_change, nc_shape, nc_previous_bin_id, nc_bin_id, nc_card))

            nc_previous_route_id = nc_route_id
            nc_previous_end_elevation = nc_end_elevation
            nc_previous_bin_id = nc_bin_id
            nc_previous_bin_number = nc_bin_number
feature_count = int(arcpy.GetCount_management(elevation_change_feature_class).getOutput(0))
if feature_count > 0:
    arcpy.AddMessage("{0} records found.".format(feature_count))
else:
    arcpy.management.Delete(elevation_change_feature_class)
str_end_time = datetime.datetime.now().strftime("%H:%M:%S")
start_time = datetime.datetime.strptime(str_start_time, "%H:%M:%S")
end_time = datetime.datetime.strptime(str_end_time, "%H:%M:%S")
elapsed_time = (end_time - start_time)
arcpy.AddMessage("END CHECK - Elevation Continuity - {0}. Run Time: {1}".format(str_end_time,elapsed_time))

###XY 

start_time = datetime.datetime.now()
str_start_time = start_time.strftime("%H:%M:%S")
arcpy.AddMessage("START CHECK - Expected XY (against previous year's delivery) - {0}".format(str_start_time))

# Create a new feature class to store the features with XY changes
if arcpy.Exists("XY_ToReview"):
    arcpy.Delete_management("XY_ToReview")
xy_change_feature_class = arcpy.management.CreateFeatureclass(
    arcpy.env.workspace, "XY_ToReview", "POLYLINE", spatial_reference=routing_fc)

# Add fields to store XY change information
arcpy.management.AddField(xy_change_feature_class, "RouteId", "TEXT")
arcpy.management.AddField(xy_change_feature_class, "HPMS_BinID", "TEXT")
field_names_add = ["LATITUDE_BEGIN", "LATITUDE_END", "LONGITUDE_BEGIN",
                   "LONGITUDE_END", "LATITUDE_BEGIN_Prev", "LATITUDE_END_Prev", "LONGITUDE_BEGIN_Prev",
                   "LONGITUDE_END_Prev", "BEGIN_LATITUDE_Difference", "END_LATITUDE_Difference",
                   "BEGIN_LONGITUDE_Difference", "END_LONGITUDE_Difference"]

for field_name in field_names_add:
    arcpy.management.AddField(xy_change_feature_class, field_name, "DOUBLE")

field_names = [field.name for field in arcpy.ListFields(review_delivery)]
xy_field_names = [field.name for field in arcpy.ListFields(xy_change_feature_class)]
prev_field_names = [field.name for field in arcpy.ListFields(prev_year_del)]

# Create a dictionary of previous records using HPMS_BinID as the key
prev_records_dict = {}
with arcpy.da.SearchCursor(prev_year_del, prev_field_names + ["SHAPE@"]) as previous_search_cursor:
    for prev_row in previous_search_cursor:
        prev_bin_id = prev_row[prev_field_names.index("HPMS_BinID")]
        prev_records_dict[prev_bin_id] = prev_row

# Search for XY changes
with arcpy.da.SearchCursor(review_delivery, field_names + ["SHAPE@","SHAPE@Length"]) as current_search_cursor:
    with arcpy.da.InsertCursor(xy_change_feature_class, xy_field_names) as insert_cursor:
        for curr_row in current_search_cursor:
            route_id = curr_row[field_names.index("RouteId")]
            bin_id = curr_row[field_names.index("HPMS_BinID")]
            shape_len=curr_row[-1]
            shape=curr_row[-2]
            oid=curr_row[field_names.index("OBJECTID")]
            if bin_id in prev_records_dict:
                lat_beg = curr_row[field_names.index("LATITUDE_BEGIN")]
                lat_end = curr_row[field_names.index("LATITUDE_END")]
                lon_beg = curr_row[field_names.index("LONGITUDE_BEGIN")]
                lon_end = curr_row[field_names.index("LONGITUDE_END")]
                
                # Retrieve the corresponding previous record based on the HPMS_BinID
                prev_row = prev_records_dict[bin_id]
                prev_lat_beg = prev_row[prev_field_names.index("LATITUDE_BEGIN")]
                prev_lat_end = prev_row[prev_field_names.index("LATITUDE_END")]
                prev_lon_beg = prev_row[prev_field_names.index("LONGITUDE_BEGIN")]
                prev_lon_end = prev_row[prev_field_names.index("LONGITUDE_END")]

                # Calculate changes
                b_l_change = abs((lat_beg - prev_lat_beg) / prev_lat_beg) * 100 if prev_lat_beg != 0 else 0
                e_l_change = abs((lat_end - prev_lat_end) / prev_lat_end) * 100 if prev_lat_end != 0 else 0
                b_lo_change = abs((lon_beg - prev_lon_beg) / prev_lon_beg) * 100 if prev_lon_beg != 0 else 0
                e_lo_change = abs((lon_end - prev_lon_end) / prev_lon_end) * 100 if prev_lon_end != 0 else 0

                # Insert the row if changes exceed the tolerance
                if (
                    b_l_change > tolerance
                    or e_l_change > tolerance
                    or b_lo_change > tolerance
                    or e_lo_change > tolerance
                ):
                    insert_cursor.insertRow(
                        (   oid,
                            shape,
                            shape_len,
                            route_id,
                            bin_id,
                            lat_beg,
                            lat_end,
                            lon_beg,
                            lon_end,
                            prev_lat_beg,
                            prev_lat_end,
                            prev_lon_beg,
                            prev_lon_end,
                            b_l_change,
                            e_l_change,
                            b_lo_change,
                            e_lo_change
                        )
                    )

# Print the count of features
feature_count = int(arcpy.GetCount_management(xy_change_feature_class).getOutput(0))
if feature_count > 0:
    arcpy.AddMessage("{0} records found.".format(feature_count))
else:
    arcpy.management.Delete(xy_change_feature_class)

end_time = datetime.datetime.now()
str_end_time = end_time.strftime("%H:%M:%S")
elapsed_time = end_time - start_time
arcpy.AddMessage(
    "END CHECK - Expected XY (against previous year's delivery) - {0}. Run Time: {1}".format(
        str_end_time, elapsed_time
    )
)

# DISTANCE FROM ROUTED BIN
arcpy.env.workspace = output_gdb

def calculate_distance(row):
    bin_id = row[0]
    route_id = row[1]
    shape = row[2]

    # Create a query to find the corresponding pair in the routing feature class
    query = "HPMS_BinID = '{}' AND RouteID = '{}'".format(bin_id, route_id)

    # Find the corresponding pair in the routing feature class using a search cursor and the query
    with arcpy.da.SearchCursor(routing_fc, ["HPMS_BinID", "RouteId", "SHAPE@"], query) as routing_cursor:
        for routing_row in routing_cursor:
            routing_shape = routing_row[2]

            # Calculate the distance between the shapes
            distance = shape.distanceTo(routing_shape)

            # Update the distance field in the delivery feature class
            row[3] = distance
            cursor.updateRow(row)

            # Store the row if the distance exceeds the threshold
            if distance > 20:
                return row

# Start the timer
start_time = datetime.datetime.now()
str_start_time = start_time.strftime("%H:%M:%S")
arcpy.AddMessage("START CHECK - Distance from Routed Bin - {0}".format(str_start_time))

# Create a list to store the rows that meet the distance criteria
distance_exceeded_rows = []

# Iterate through the delivery feature class
with arcpy.da.UpdateCursor(review_delivery, ["HPMS_BinID", "RouteId", "SHAPE@", "Distance_ToRoutedBin"], "Distance_ToRoutedBin is NULL") as cursor:
    for row in cursor:
        processed_row = calculate_distance(row)
        if processed_row:
            distance_exceeded_rows.append(processed_row)

# Delete the intermediate feature class if it exists
if arcpy.Exists("NearAnalysis_ForReview"):
    arcpy.Delete_management("NearAnalysis_ForReview")

# Perform the analysis on the updated feature class
arcpy.FeatureClassToFeatureClass_conversion(review_delivery, output_gdb, "NearAnalysis_ForReview", where_clause="Distance_ToRoutedBin > 20")
feature_count = int(arcpy.GetCount_management("NearAnalysis_ForReview").getOutput(0))

# Print the count of features
if feature_count > 0:
    arcpy.AddMessage("{0} records found.".format(feature_count))

# End the timer
end_time = datetime.datetime.now()
str_end_time = end_time.strftime("%H:%M:%S")
elapsed_time = end_time - start_time

arcpy.AddMessage("END CHECK - Distance from Routed Bin - {0}. Run Time: {1}".format(str_end_time, elapsed_time))
arcpy.AddMessage("NEXT STEPS: Review all '_ToReview' feature classes in the review gdb stored at {0}".format(output_gdb))



                 
                 







