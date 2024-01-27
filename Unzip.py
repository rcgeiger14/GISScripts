import arcpy
import zipfile
import os

path_to_zip_file=arcpy.GetParameterAsText(0)
filename=(path_to_zip_file.split('\\')[-1]).replace('.zip','')
if not os.path.isdir(filename):
   os.makedirs(filename)
with zipfile.ZipFile(path_to_zip_file) as zip_ref:
    zip_ref.extractall(filename)


