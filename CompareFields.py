def CompareFields(fc_list="CURRENT"):
    aprx=arcpy.mp.ArcGISProject("CURRENT")
    map=aprx.listMaps()[0]
    layer_field_dict=dict()
    for layer in map.listLayers():
        layername=layer.name
        layerfields=layer.listFields()
        layer_field_dict[layername]=layerfields
        
        
