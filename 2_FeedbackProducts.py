
import arcpy
import os
import zipfile
import re
import datetime
import concurrent.futures


# Set Variables

Year = arcpy.GetParameterAsText(0)
DeliveryNumber = arcpy.GetParameterAsText(1)
Date = arcpy.GetParameterAsText(2)
zipfile_path = arcpy.GetParameterAsText(3)
routing_fc = arcpy.GetParameterAsText(4)
prev_year_del = arcpy.GetParameterAsText(5)
database_connection = arcpy.GetParameterAsText(6)
tolerance=5 #in terms of % so 5 = 5% change


arcpy.AddMessage( "Starting Geometry Feedback Script for - {0}".format(zipfile_path))

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
field_names = [field.name for field in arcpy.ListFields(review_delivery)]
routing_fieldnames= [field.name for field in arcpy.ListFields(routing_fc)]

if DeliveryNumber == '1':
    if not arcpy.Exists(master_gdb):
        arcpy.management.CreateFileGDB(basefolder_path, "Master.gdb")
    arcpy.env.workspace = master_gdb
    if not arcpy.Exists(os.path.join(master_gdb, "Compiled_Bins")):
        arcpy.FeatureClassToFeatureClass_conversion(review_delivery, master_gdb, "Compiled_Bins")
    if not arcpy.Exists(os.path.join(master_gdb, "AllRouted_BinID_sum")):
        arcpy.Statistics_analysis(routing_fc, os.path.join(master_gdb, "AllRouted_BinID_sum"), [["HPMS_BinID", "COUNT"]], "HPMS_BinID")
    if not arcpy.Exists(os.path.join(master_gdb, "AllRouted_Route_sum")):
        arcpy.Statistics_analysis(routing_fc, os.path.join(master_gdb, "AllRouted_Route_sum"), [["RouteId", "COUNT"]], "RouteId")
        arcpy.AlterField_management(os.path.join(master_gdb, "AllRouted_Route_sum"), "COUNT_RouteId", "Routing_Total","Routing_Total")
    arcpy.AddField_management(os.path.join(master_gdb, "Compiled_Bins"), "DeliveryNumber", "TEXT")
    field_names.append("DeliveryNumber")
    with arcpy.da.UpdateCursor(os.path.join(master_gdb, "Compiled_Bins"), field_names) as update_cursor:
        for row in update_cursor:
            delivery_num = row[field_names.index("DeliveryNumber")]
            if delivery_num is None:
                row[field_names.index("DeliveryNumber")] = DeliveryNumber
                update_cursor.updateRow(row)
if  not DeliveryNumber == '1':
#Append Into Master FC
    arcpy.env.workspace = master_gdb
    arcpy.AddField_management(os.path.join(master_gdb, "Compiled_Bins"), "DeliveryNumber", "TEXT")
    arcpy.AddField_management(review_delivery, "DeliveryNumber", "TEXT")
    field_names.append("DeliveryNumber")
    arcpy.DeleteField_management(review_delivery, "DeliveryNumber")
    
    #Calculate Delivery Number in Compiled Feature Class
    with arcpy.da.UpdateCursor(os.path.join(master_gdb, "Compiled_Bins"), field_names) as update_cursor:
         for row in update_cursor:
            delivery_num = row[field_names.index("DeliveryNumber")]
            if delivery_num is None:
                row[field_names.index("DeliveryNumber")] = DeliveryNumber
                update_cursor.updateRow(row)
# Create Output Folder for Vendor
if not arcpy.Exists(review_folder_forvendor):
    os.makedirs(review_folder_forvendor)
    arcpy.AddMessage("Feedback Folder Created - {0}. ".format(review_folder_forvendor))

# Create review output gdb for vendor
if not arcpy.Exists(output_gdb_forvendor):
    arcpy.management.CreateFileGDB(review_folder_forvendor, "Delivery{0}_ADOTFeedback.gdb".format(DeliveryNumber))
    arcpy.AddMessage("Feedback GDB Created - {0}. This gdb should be used to store final deliveries for the Vendor. ".format(output_gdb_forvendor))
arcpy.env.workspace = output_gdb_forvendor
arcpy.env.overwriteOutput = True
arcpy.FeatureClassToFeatureClass_conversion(review_delivery, output_gdb_forvendor, "Delivery_{0}_ADOTFeedback".format(DeliveryNumber))
# Generate Output Tables
arcpy.AddMessage("Begin Generation of Feedback Outputs ")

arcpy.Statistics_analysis("Delivery_{0}_ADOTFeedback".format(DeliveryNumber), os.path.join(output_gdb_forvendor, "Delivery{0}_UniqueBinsByRouteId".format(DeliveryNumber)), [["RouteId", "COUNT"]], "RouteId")
arcpy.DeleteField_management(os.path.join(output_gdb_forvendor, "Delivery{0}_UniqueBinsByRouteId".format(DeliveryNumber)),"COUNT_RouteId")

arcpy.Statistics_analysis(os.path.join(master_gdb,"Compiled_Bins"), os.path.join(output_gdb_forvendor, "PostDel{0}_UniqueBins".format(DeliveryNumber)), [["HPMS_BinID", "COUNT"]], "HPMS_BinID")
arcpy.DeleteField_management("PostDel{0}_UniqueBins".format(DeliveryNumber),"COUNT_HPMS_BinID")

arcpy.Statistics_analysis(os.path.join(master_gdb,"Compiled_Bins"), os.path.join(output_gdb_forvendor, "PostDel{0}_ByRouteAndDel".format(DeliveryNumber)), [["RouteId", "COUNT"], ["DeliveryNumber", "COUNT"]], ["RouteId", "DeliveryNumber"])
arcpy.DeleteField_management(os.path.join(output_gdb_forvendor, "PostDel{0}_ByRouteAndDel".format(DeliveryNumber)),"COUNT_RouteID")
arcpy.DeleteField_management(os.path.join(output_gdb_forvendor, "PostDel{0}_ByRouteAndDel".format(DeliveryNumber)),"COUNT_DeliveryNumber")

arcpy.Statistics_analysis(os.path.join(master_gdb, "Compiled_Bins"), os.path.join(output_gdb_forvendor, "PostDel{0}_ByRoute".format(DeliveryNumber)), [["RouteId", "COUNT"]], "RouteId")
arcpy.DeleteField_management(os.path.join(output_gdb_forvendor, "PostDel{0}_ByRoute".format(DeliveryNumber)),"COUNT_RouteID")


arcpy.TableToTable_conversion(os.path.join(output_gdb_forvendor, "PostDel{0}_ByRoute".format(DeliveryNumber)), output_gdb_forvendor, "PostDel{0}_ComparedToRouting_ByRoute".format(DeliveryNumber))
arcpy.JoinField_management(os.path.join(output_gdb_forvendor, "PostDel{0}_ComparedToRouting_ByRoute".format(DeliveryNumber)), "RouteId", os.path.join(master_gdb, "AllRouted_Route_sum"), "RouteId", ["Routing_Total"])
arcpy.AddField_management(os.path.join(output_gdb_forvendor, "PostDel{0}_ComparedToRouting_ByRoute".format(DeliveryNumber)), "ToBeDelivered", "LONG")
arcpy.AlterField_management(os.path.join(output_gdb_forvendor, "PostDel{0}_ComparedToRouting_ByRoute".format(DeliveryNumber)), "FREQUENCY", "Delivered_Total","Delivered_Total")
arcpy.CalculateField_management(os.path.join(output_gdb_forvendor, "PostDel{0}_ComparedToRouting_ByRoute".format(DeliveryNumber)), "ToBeDelivered", "[Routing_Total]-[Delivered_Total]")
arcpy.DeleteField_management(os.path.join(output_gdb_forvendor, "PostDel{0}_ComparedToRouting_ByRoute".format(DeliveryNumber)),"COUNT_RouteID")

arcpy.FeatureClassToFeatureClass_conversion("Delivery_{0}_ADOTFeedback".format(DeliveryNumber), output_gdb_forvendor, "Delivery{0}_CommentsToVendor".format(DeliveryNumber), where_clause="Comments_To_Vendor IS NOT NULL")

arcpy.Statistics_analysis(os.path.join(output_gdb_forvendor, "Delivery{0}_CommentsToVendor".format(DeliveryNumber)), os.path.join(output_gdb_forvendor, "Delivery{0}_CommentsToVendor_sum".format(DeliveryNumber)), [["Comments_To_Vendor", "COUNT"]], "Comments_To_Vendor")
arcpy.DeleteField_management(os.path.join(output_gdb_forvendor, "Delivery{0}_CommentsToVendor_sum".format(DeliveryNumber)),"COUNT_Comments_To_Vendor")


output_tables = arcpy.ListTables("Post*")
for table in output_tables:
    table_name = arcpy.Describe(table).name
    output_table_path = os.path.join(output_gdb_forvendor, table_name)
    master_table_path = os.path.join(master_gdb, table_name)
    arcpy.Copy_management(output_table_path, master_table_path)

arcpy.AddMessage("Output tables have been moved to the master geodatabase.")



arcpy.AddMessage("End Generation of Feedback Outputs. Please Zip up the Feedback GDB and upload to Sharefile.")
