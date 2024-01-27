import arcpy

# Input Parameters
input_features = arcpy.GetParameterAsText(0) # Feature classes or feature services
output_folder = arcpy.GetParameterAsText(1) # Output folder path for APRX file
aprx_name = arcpy.GetParameterAsText(2) # Name of APRX file to be created
agol_username = arcpy.GetParameterAsText(3) # AGOL Username
agol_password = arcpy.GetParameterAsText(4) # AGOL Password
service_name = arcpy.GetParameterAsText(5) # Name of the feature service to be created

# Create new empty APRX file
aprx = arcpy.mp.ArcGISProject("CREATE")

# Loop through input features and add to map
m = aprx.listMaps()[0]
for input_feature in input_features.split(';'):
    if input_feature.startswith('http') or input_feature.startswith('https'):
        m.addDataFromPath(input_feature)
    else:
        m.addDataFromPath(input_feature)

# Save APRX file
aprx.saveACopy(output_folder + '\\' + aprx_name + '.aprx')

# Sign in to AGOL
arcpy.SignInToPortal(agol_username, agol_password)

# Get the AGOL connection information
gis = arcpy.env.active_gis

# Find the project item on AGOL and publish
search_result = gis.content.search(query='title:"{}" AND type:"Project"'.format(aprx_name), item_type='Project')
if len(search_result) > 0:
    project_item = search_result[0]
    project_item.updateConnectionProperties({'url': gis.properties.url + '/sharing/rest',
                                              'user': agol_username,
                                              'password': agol_password})
    sharing_draft = project_item.getWebLayerSharingDraft("HOSTING_SERVER", "FEATURE", service_name)
    sharing_draft.shareItem("My Hosted Layers")
    arcpy.AddMessage("Feature service has been created and published to AGOL.")
else:
    arcpy.AddMessage("Project not found on AGOL.")
    # Create a new feature service
    sharing_draft = arcpy.sharing.CreateSharingDraft("LOCAL", "FEATURE", service_name)
    sharing_draft.addData(aprx.filePath)
    sharing_draft.shareItem("My Hosted Layers")
    arcpy.AddMessage("Feature service has been created and published to AGOL.")

# Sign out of AGOL
arcpy.SignOutFromPortal()
