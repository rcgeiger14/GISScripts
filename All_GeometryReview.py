import arcpy
import os
import zipfile
import re

Year = '2023'
DeliveryNumber = '1'
Date = '20230518'
zipfile_path = r"I:\Data\ArcView_ft\X_Custom\Reid\GIS Delivery 1 - 20230428.GDB.zip"
routing_fc = r"I:\TaskAssignments\ICC_2023\2023_RteNetwork\Rte_20230407\RteNetwork_20230407_FINAL.gdb\HPMSBins_Routing_20230407_FINAL"
prev_year_del = r"Database Connections\Prod_Reid.sde\ATIS_Prod.DBO.LRSE_HPMSBin_Data_Cy2021"
database_connection = r"Database Connections\Prod_Reid.sde"


# Set up workspace variables
basefolder_path = os.path.dirname(zipfile_path)
input_gdb= os.path.join(basefolder_path,basefolder_path,os.path.splitext(os.path.basename(zipfile_path))[0])
review_folder = os.path.join(basefolder_path, "AZ{0}_Delivery{1}_forReview".format(Year, DeliveryNumber))
output_gdb=os.path.join(basefolder_path,review_folder,"Delivery{1}_forReview.gdb".format(Year,DeliveryNumber))
input_fc= os.path.join(input_gdb, "GIS_Delivery_{0}".format(DeliveryNumber))
input_fc_copy=os.path.join(output_gdb, "GIS_Delivery_{0}".format(DeliveryNumber))
review_delivery = os.path.join(output_gdb, "Delivery{0}_forReview".format(DeliveryNumber))

# Create review folder

if not os.path.exists(review_folder):
    os.makedirs(review_folder)
if not os.path.exists(output_gdb):
    arcpy.management.CreateFileGDB(review_folder, "Delivery{1}_forReview".format(Year,DeliveryNumber))

arcpy.env.workspace = output_gdb

# Unzip vendor delivery file
with zipfile.ZipFile(zipfile_path, 'r') as zip_ref:
    zip_ref.extractall(basefolder_path)


# Copy the feature class to the destination GDB
arcpy.FeatureClassToGeodatabase_conversion(input_fc,output_gdb)
arcpy.Rename_management(input_fc_copy,"Delivery{0}_forReview".format(DeliveryNumber))
# Add necessary fields for review

arcpy.management.AddField(review_delivery, "Comments_For_ADOT","TEXT",field_alias="Comments_For_ADOT", )
arcpy.management.AddField(review_delivery, "Comments_To_Vendor","TEXT",field_alias="Comments_To_Vendor", )


# Save MXD
mxd2 = arcpy.mapping.MapDocument(r"C:\Users\e5490\AppData\Roaming\ESRI\Desktop10.7\ArcMap\Templates\Untitled.mxd")

# Add Layers to MXD
dataframe = arcpy.mapping.ListDataFrames(mxd2)[0]
arcpy.MakeFeatureLayer_management(r"{0}\ATIS_Prod.DBO.LRSN_ATIS_Routes".format(database_connection), "ATIS Routes")
ATIS = arcpy.mapping.Layer("ATIS Routes")
arcpy.mapping.AddLayer(dataframe, ATIS, "AUTO_ARRANGE")

arcpy.MakeFeatureLayer_management(r"{0}\ATIS_Prod.DBO.LRSE_HPMSBins".format(database_connection), "HPMS_Bins")
Bins = arcpy.mapping.Layer("HPMS_Bins")
arcpy.mapping.AddLayer(dataframe, Bins, "AUTO_ARRANGE")

arcpy.MakeFeatureLayer_management(routing_fc, "Routing File")
Routing = arcpy.mapping.Layer("Routing File")
arcpy.mapping.AddLayer(dataframe, Routing, "AUTO_ARRANGE")

for fc in arcpy.ListFeatureClasses():
    arcpy.MakeFeatureLayer_management(os.path.join(output_gdb, fc), "{0} Delivery For Review".format(DeliveryNumber))

mxd2.saveACopy(r"{0}\AZ{1}_Delivery{2}_forReview\{3}_AZ{1}_Delivery{2}_forReview.mxd".format(review_folder, Year, DeliveryNumber, Date))



    ##### TEST  #####

### 32 CHARACTER PROBLEMS - ROUTEID 
### Add part to fix the bad ones
import arcpy
field_names = [field.name for field in arcpy.ListFields(review_delivery)]
print("START - 32 character Test on ROUTEIDs ")

updated_count = 0

with arcpy.da.UpdateCursor(review_delivery, field_names) as cursor:
    for row in cursor:
        shape = row[field_names.index("Shape_Length")]
        value = row[field_names.index("RouteID")]
        if len(value) != 32:
            row[-1] = "CharacterCompliance_RouteId_ToReview"  # Update the last element in the row
            cursor.updateRow(row)
            updated_count += 1
print("COMPLETE - 32 character Test on ROUTEIDs ")
# Print the number of records that were updated
if updated_count > 0:
    print("{} records were found to not have 32 character RouteId Compliance.".format(updated_count))
else:
    print("No records found that required updating the RouteId.")



###32 CHARACTER PROBLEMS - HPMS_BinID
print("START - 32 character Test on BinIDs ")
# Count the number of non-compliant records
non_compliant_count = 0
with arcpy.da.UpdateCursor(review_delivery, field_names) as cursor:
    for row in cursor:
        try:
            shape = row[field_names.index("Shape_Length")]
            value = row[field_names.index("HPMS_BinID")]
            if len(value) < 32:
                row[-1] = "{} | CharacterCompliance_BinID_ToReview".format(row[-1])
                cursor.updateRow(row)
                non_compliant_count += 1
        except Exception as e:
            arcpy.AddWarning("Skipped a row due to an error: {}".format(str(e)))


# Check if any non-compliant records were found
if non_compliant_count > 0:
    print("{} records were found to not have over 32 character BinID Compliance.".format(non_compliant_count))
else:
    print("No records found without 32 Character Compliance in the BinId Field.")
print("COMPLETE - 32 character Test on BinIDs ")

### DUPLICATE Test
print("START - Duplicate BinID Test ")
arcpy.CreateFeatureclass_management(output_gdb, "Duplicates_ToReview", "POLYLINE", review_delivery,
                                    spatial_reference=arcpy.Describe(review_delivery).spatialReference)

unique_values = set()
with arcpy.da.InsertCursor("Duplicates_ToReview", field_names) as cursor:
    with arcpy.da.SearchCursor(review_delivery, field_names) as search_cursor:
        for row in search_cursor:
            shape = row[field_names.index("Shape_Length")]
            value = row[field_names.index("HPMS_BinID")]
            if value in unique_values:
                cursor.insertRow(row)
            else:
                unique_values.add(value)

if int(arcpy.GetCount_management("Duplicates_ToReview").getOutput(0)) > 0:
    print(str(arcpy.GetCount_management("Duplicates_ToReview").getOutput(0)), "records found. Output feature class:",
          "Duplicates_ToReview")
else:
    arcpy.Delete_management("Duplicates_ToReview")
    print("No duplicate HPMS_BinID records found")
print("COMPLETE - Duplicate BinID Test ")

### NULL SHAPES 
print("START - NULL or Small Shape Test ")
arcpy.CreateFeatureclass_management(output_gdb, "NoShape_ToReview", "POLYLINE", review_delivery,
                                    spatial_reference=arcpy.Describe(review_delivery).spatialReference)

with arcpy.da.InsertCursor("NoShape_ToReview", field_names) as cursor:
    with arcpy.da.SearchCursor(review_delivery, field_names) as search_cursor:
        for row in search_cursor:
            shape = row[field_names.index("Shape_Length")]  # Access the SHAPE field value
            if shape is None or shape<10:
                cursor.insertRow(row)

if int(arcpy.GetCount_management("NoShape_ToReview").getOutput(0)) > 0:
    print(str(arcpy.GetCount_management("NoShape_ToReview").getOutput(0)), "records found. Output feature class:",
          "NoShape_ToReview")
else:
    arcpy.Delete_management("NoShape_ToReview")
    print("No records found with NULL Shape Length or ShapeLength under 10ft found.")

print("END- Duplicate BinID Test ")

### LENGTH CHECK Compared to Routed Bins
print("START - Length Comparision Test (against routing file)")
import arcpy
exclude_query="CONST = 0 AND LANEDEV = 0"
# Create a dictionary to store the original bin lengths based on HPMSBin_ID
original_lengths = {}
with arcpy.da.SearchCursor(routing_fc, ["HPMS_BinID", "Shape_Length",]) as cursor:
    for row in cursor:
        hpms_bin_id = row[0]
        shape_length = row[1]
        original_lengths[hpms_bin_id] = shape_length

# Use update cursor to calculate the "Review Comment" field in the delivery feature class
with arcpy.da.UpdateCursor(review_delivery, ["HPMS_BinID", "Shape_Length", "Comments_To_Vendor"],exclude_query) as cursor:
    for row in cursor:
        hpms_bin_id = row[0]
        shape_length = row[1]
        review_comments = row[2]
        
        # Check if the review_comments field is None or empty
        if review_comments is None or review_comments.strip() == "":
            review_comments = ""

        if hpms_bin_id in original_lengths:
            original_length = original_lengths[hpms_bin_id]
            if shape_length < 0.5 * original_length:
                if review_comments:
                    review_comments += " | "
                review_comments += "ICC Review | Less Than 50% of Bin Delivered"

        # Update the Review_Comments field
        row[2] = review_comments
        cursor.updateRow(row)

# Count the number of non-compliant records
non_compliant_count = 0
with arcpy.da.SearchCursor(review_delivery, ["Comments_To_Vendor"]) as cursor:
    for row in cursor:
        review_comments = row[0]
        if review_comments is not None and "ICC Review | Less Than 50% of Bin Delivered" in review_comments:
            non_compliant_count += 1

# Print the count of non-compliant records
print("{} records were not in compliance for 50% of Collection compared to Delivered Bin Length.".format(non_compliant_count))
print("END - Length Comparision Test (against routing file)")


### SECTION ID Gaps Test


print("START - SESSION ID Gap Test")
# Dissolve the delivery by Session and RouteID
dissolved_delivery = arcpy.management.Dissolve(
    review_delivery, r"in_memory\dissolved_delivery", ["Session", "RouteID"]
)

# Sort the dissolved features by Session, RouteID, and start measure
sorted_delivery = arcpy.management.Sort(
    dissolved_delivery, r"in_memory\sorted_delivery", [["Session", "ASCENDING"], ["RouteID", "ASCENDING"]]
)

# Get the spatial reference from the sorted deliveryarcpy.featureclasstofeatureclass
spatial_reference = arcpy.Describe(sorted_delivery).spatialReference

# Create a new feature class for the gaps
gap_feature_class = arcpy.management.CreateFeatureclass(
    arcpy.env.workspace, "SectionId_Gaps_ToReview", "POLYLINE", None, None, None, spatial_reference
)

# Add fields to store gap information
arcpy.management.AddField(gap_feature_class, "Session", "TEXT")
arcpy.management.AddField(gap_feature_class, "RouteID", "TEXT")
arcpy.management.AddField(gap_feature_class, "Gap_Length", "DOUBLE")

# Find and create gaps
with arcpy.da.SearchCursor(sorted_delivery, ["Session", "RouteID", "Shape@"]) as search_cursor:
    with arcpy.da.InsertCursor(gap_feature_class, ["Session", "RouteID", "Shape@", "Gap_Length"]) as insert_cursor:
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
    print("No gaps found in each Session.")
else:
	print(gap_count,"Section Id Gaps found in each Session.")
print("END - SESSION ID Gap Test")


### Intersection Test

print("START - Intersection Test")
import arcpy
# Create a new feature class for the intersections
intersection_feature_class=arcpy.Intersect_analysis(review_delivery,"Intersection_ToReview")

# Print the count of features
feature_count = int(arcpy.GetCount_management(intersection_feature_class).getOutput(0))
if feature_count > 0:
    print("Total number of features that Intersect other Bins:", feature_count)
else:
    arcpy.management.Delete(intersection_feature_class)
    print("No features found. The feature class has been deleted.")

### ELEVATION TEST

# Sort the delivery features by RouteID, FromMeasure, and ToMeasure
sorted_delivery = arcpy.management.Sort(
    review_delivery, r"in_memory\sorted_delivery",
    [["RouteID", "ASCENDING"], ["FromMeasure", "ASCENDING"], ["ToMeasure", "ASCENDING"]]
)

# Create a new feature class to store the features with elevation changes
elevation_change_feature_class = arcpy.management.CreateFeatureclass(
    arcpy.env.workspace, "ElevationChange_ToReview", "POLYLINE", None, None, None, sorted_delivery
)

# Add fields to store elevation change information
arcpy.management.AddField(elevation_change_feature_class, "RouteID", "TEXT")
arcpy.management.AddField(elevation_change_feature_class, "ELEVATION_BEGIN", "DOUBLE")
arcpy.management.AddField(elevation_change_feature_class, "ELEVATION_END", "DOUBLE")
arcpy.management.AddField(elevation_change_feature_class, "ElevationChange", "DOUBLE")
arcpy.management.AddField(elevation_change_feature_class, "HPMSBinID1", "TEXT")
arcpy.management.AddField(elevation_change_feature_class, "HPMSBinID2", "TEXT")

# Search for elevation changes
with arcpy.da.SearchCursor(sorted_delivery, ;
                           ["RouteID";
                            ,"FromMeasure";
                            ,"ToMeasure", ;
                            ,"ELEVATION_BEGIN",;
                            ,"ELEVATION_END",;
                           ,"Shape@",;
                          ,"HPMS_BinID"]) as search_cursor:
    with arcpy.da.InsertCursor(elevation_change_feature_class, ["RouteID", ;
                                                                "ELEVATION_BEGIN",;
                                                               "ELEVATION_END";, "ElevationChange", "Shape@", "HPMSBinID1", "HPMSBinID2"]) as insert_cursor:
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

            # Extract the numerical part from the HPMSBinID
            bin_number = re.findall(r'\d+', bin_id)[-1]

            # Check for consecutive bins on the same route and exclude HPMSBin IDs with an absolute difference greater than 1
            if (
                previous_route_id is not None
                and previous_route_id == route_id
                and abs(int(bin_number) - int(previous_bin_number)) <= 1
                and abs(begin_elevation - previous_end_elevation) > 20  # Adjust the threshold as needed
            ):
                elevation_change = abs(begin_elevation - previous_end_elevation)
                insert_cursor.insertRow((route_id, previous_end_elevation, begin_elevation, elevation_change, shape, previous_bin_id, bin_id))

            previous_route_id = route_id
            previous_end_elevation = end_elevation
            previous_bin_id = bin_id
            previous_bin_number = bin_number
### XY Test
("START - XY Test (against previous year's delivery)")

# Sort the delivery features by RouteID, FromMeasure, and ToMeasure
sorted_delivery = arcpy.management.Sort(
    review_delivery, r"in_memory\sorted_delivery",
    [["RouteID", "ASCENDING"], ["FromMeasure", "ASCENDING"], ["ToMeasure", "ASCENDING"]]
)
sorted_prev_delivery = arcpy.management.Sort(
    prev_year_del, r"in_memory\sorted_prev_delivery",
    [["RouteID", "ASCENDING"], ["FromMeasure", "ASCENDING"], ["ToMeasure", "ASCENDING"]]
)

# Create a new feature class to store the features with XY changes
xy_change_feature_class = arcpy.management.CreateFeatureclass(
    arcpy.env.workspace, "XY_ToReview", "POLYLINE", None, None, None)

# Add fields to store XY change information
arcpy.management.AddField(xy_change_feature_class, "RouteID", "TEXT")
arcpy.management.AddField(xy_change_feature_class, "HPMS_BinID", "TEXT")
field_names_add = ["LATITUDE_BEGIN", "LATITUDE_END", "LONGITUDE_BEGIN",
               "LONGITUDE_END", "LATITUDE_BEGIN_Prev", "LATITUDE_END_Prev", "LONGITUDE_BEGIN_Prev",
               "LONGITUDE_END_Prev", "BEGIN_LATITUDE_Difference","END_LATITUDE_Difference", "BEGIN_LONGITUDE_Difference", "END_LONGITUDE_Difference"]

for field_name in field_names_add:
    arcpy.management.AddField(xy_change_feature_class, field_name, "DOUBLE")


field_names=[field.name for field in arcpy.ListFields(sorted_delivery)]
xy_field_names = [field.name for field in arcpy.ListFields(xy_change_feature_class)]
prev_field_names = [field.name for field in arcpy.ListFields(sorted_prev_delivery)]

# Search for XY changes
with arcpy.da.SearchCursor(sorted_prev_delivery, prev_field_names + ["SHAPE@"]) as previous_search_cursor:
    with arcpy.da.SearchCursor(sorted_delivery, field_names + ["SHAPE@"]) as current_search_cursor:
        with arcpy.da.InsertCursor(xy_change_feature_class, xy_field_names + ["SHAPE@"]) as insert_cursor:

            prev_bins = set()  # Set to store unique previous HPMS_BinIDs

            for prev_row in previous_search_cursor:
                prev_bin_id = prev_row[prev_field_names.index("HPMS_BinID")]
                prev_bins.add(prev_bin_id)  # Add the previous HPMS_BinID to the set

            for curr_row in current_search_cursor:
                route_id = curr_row[field_names.index("RouteID")]
                bin_id = curr_row[field_names.index("HPMS_BinID")]

                if bin_id in prev_bins:  # Check if the current HPMS_BinID exists in the previous set
                    lat_beg = curr_row[field_names.index("LATITUDE_BEGIN")]
                    lat_end = curr_row[field_names.index("LATITUDE_END")]
                    lon_beg = curr_row[field_names.index("LONGITUDE_BEGIN")]
                    lon_end = curr_row[field_names.index("LONGITUDE_END")]
                    shape = curr_row[-1]

                    # Retrieve the corresponding previous record based on the HPMS_BinID
                    prev_row = [row for row in previous_search_cursor if row[prev_field_names.index("HPMS_BinID")] == bin_id]

                    if prev_row:
                        prev_row = prev_row[0]  # Get the first matching record
                        prev_lat_beg = prev_row[prev_field_names.index("LATITUDE_BEGIN")]
                        prev_lat_end = prev_row[prev_field_names.index("LATITUDE_END")]
                        prev_lon_beg = prev_row[prev_field_names.index("LONGITUDE_BEGIN")]
                        prev_lon_end = prev_row[prev_field_names.index("LONGITUDE_END")]

                        # Check for xy changes and insert the row
                        if (
                            abs(lat_beg - prev_lat_beg) / prev_lat_beg * 100 > 5
                            or abs(lat_end - prev_lat_end) / prev_lat_end * 100 > 5
                            or abs(lon_beg - prev_lon_beg) / prev_lon_beg * 100 > 5
                            or abs(lon_end - prev_lon_end) / prev_lon_end * 100 > 5
                        ):
                            b_l_change = abs(lat_beg - prev_lat_beg) / prev_lat_beg * 100
                            e_l_change = abs(lat_end - prev_lat_end) / prev_lat_end * 100
                            b_lo_change = abs(lon_beg - prev_lon_beg) / prev_lon_beg * 100
                            e_lo_change = abs(lon_end - prev_lon_end) / prev_lon_end * 100

                            insert_cursor.insertRow(
                                (
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
                                    e_lo_change,
                                    shape
                                )
                            )

# Print the count of features
feature_count = int(arcpy.GetCount_management(xy_change_feature_class).getOutput(0))
if feature_count > 0:
    print("Total number of features with Large XY Difference compared To Previous Year:", feature_count)
else:
    arcpy.management.Delete(xy_change_feature_class)
    print("No features found with Large XY Difference Between Years. The feature class has been deleted.")
("COMPLETE - XY Test (against previous year's delivery)")

### Near Test


# Create a new field to store the distance information
distance_field_name = "Distance"
arcpy.AddField_management(review_delivery, distance_field_name, "DOUBLE")

# Create a dictionary to store the bin pair distances
bin_pair_distances = {}

# Iterate through the delivery feature class
with arcpy.da.UpdateCursor(review_delivery, ["HPMS_BinID", "RouteID", "SHAPE@", distance_field_name]) as cursor:
    for row in cursor:
        bin_id = row[0]
        route_id = row[1]
        shape = row[2]

        # Create a query to find the corresponding pair in the routing feature class
        query = "HPMS_BinID = '{}' AND RouteID = '{}'".format(bin_id, route_id)

        # Find the corresponding pair in the routing feature class using a search cursor and the query
        with arcpy.da.SearchCursor(routing_fc, ["HPMS_BinID", "RouteID", "SHAPE@"], query) as routing_cursor:
            for routing_row in routing_cursor:
                routing_shape = routing_row[2]

                # Calculate the distance between the shapes
                distance = shape.distanceTo(routing_shape)
                row[3] = distance  # Update the distance field in the delivery feature class
                bin_pair_distances[(bin_id, route_id)] = distance  # Store the distance in the dictionary
                cursor.updateRow(row)
                break

("COMPLETE - Near Test (against current routing file)")



