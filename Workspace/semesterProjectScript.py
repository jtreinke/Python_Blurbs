#GIS 5578 - GIS PROGRAMMING - Python Project
#Shoumith Jeyakumar
#Jennifer Reinke
#5.16.2014

# Import system modules
import arcpy
import sys
import os
import csv
import shapefile as shp
from arcpy import env

# Setting current workspace
arcpy.env.workspace = r'C:\Temp\Workspace'
env.overwriteOutput = True

# Setting input and output folders
inputFolder = r"C:\Temp\Workspace\inputFiles"
outFolder = r"C:\Temp\Workspace\outputFiles"
tempFolder = r"C:\Temp\Workspace\projectedFiles"

#----------------------------------------------------------------------------

# Import CSV file and create point feature class (earthquake points)
out_file = inputFolder + r'\earthquake.shp'

print "Reading CSV file"

# Checks if shapefile Exists and deletes if it does exist
if arcpy.Exists(out_file):
    arcpy.AddMessage("Deleting Existing Shapefile")
    arcpy.Delete_management(out_file)

#Set up blank lists for data
id_no,date,x,y,m =[],[],[],[],[]

#read data from csv file and store in lists
with open('quakePoints.csv', 'rb') as csvfile:
    r = csv.reader(csvfile, delimiter=',')
    for i,row in enumerate(r):
        if i > 0: #skip header
            x.append(float(row[3]))
            y.append(float(row[2]))
            id_no.append(row[0])
            date.append(row[1])
            m.append(float(row[4]))

#Set up shapefile writer and create empty fields
w = shp.Writer(shp.POINT)
w.autoBalance = 1 #ensures geometry and attributes match
w.field('X','F',10,8)
w.field('Y','F',10,8)
w.field('Date','N')
w.field('Magnitude','F',4)
w.field('ID','N')

#loop through the data and write the shapefile
for j,k in enumerate(x):
    w.point(k,y[j]) #write the geometry
    w.record(k,y[j],date[j], m[j], id_no[j]) #write the attributes

#Save shapefile
w.save(out_file)

print "the earthquake points shapefile is created from the CSV file in the inputFiles folder within Workspace." 
#----------------------------------------------------------------------------

# Setting shapefiles to work with in ArcMap
earthquakeDataset = inputFolder + r'\earthquake.shp'
countiesDataset = inputFolder + r'\CA_Counties.shp'
faultsDataset = inputFolder + r'\CA_Faultlines.shp'
saFaultDataset = inputFolder + r'\SA_Fault.shp'
citiesDataset = inputFolder + r'\CA_Cities.shp'

#---------------------------------------------------------------------------------------------------
# Define projection for dataset

coordinateSystem = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"

arcpy.DefineProjection_management(earthquakeDataset, coordinateSystem)
arcpy.DefineProjection_management(countiesDataset, coordinateSystem)
arcpy.DefineProjection_management(faultsDataset, coordinateSystem)
arcpy.DefineProjection_management(saFaultDataset, coordinateSystem)
arcpy.DefineProjection_management(citiesDataset, coordinateSystem)

print "The shapefiles' projection has been defined to GCS WGS 1984."
#----------------------------------------------------------------------------------------------------------------------------------------

# Reproject all input feature classes into NAD 1983 UTM zone 11N.

# Set local variables

mypath = "C:\\Temp\\Workspace\\inputFiles"

# This is an empty list where the shapefile names will be stored. 
shapefiles = []

print "Shapefile list has been created."
# Input feature classes
# Here we will use the OS.PATH fucntions to get a list of all the shapefiles
# in the directory, by getting a list of all files and selects .SHP file extensions

for filename in os.listdir(mypath):
    if filename.endswith('.shp'):
        shapefiles.append(filename)

print "Reading the shapefile list"    
try:
    # Use ListFeatureClasses to generate a list of inputs 
    for infc in shapefiles:
           
        # Determine if the input has a defined coordinate system, can't project it if it does not
        dsc = arcpy.Describe(mypath+"\\"+infc)
            
        if dsc.spatialReference.Name == "Unknown":
            print ('skipped this fc due to undefined coordinate system: ' + infc)

        else:
            # Determine the new output feature class path and name
            outfc = os.path.join(tempFolder, infc)

            if arcpy.Exists(outfc):
                print "Deleting "+outfc
                arcpy.Delete_management(outfc)
            
            # Set output coordinate system
            outCS = arcpy.SpatialReference('NAD 1983 UTM Zone 11N')
            
            # run project tool
            arcpy.Project_management(mypath+"\\"+infc, outfc, outCS)

            print "shapefiles projected"
            
            # check messages
            print(arcpy.GetMessages())
            
except Exception as ex:
    print(ex.args[0])

print "The shapefiles have been reprojected to NAD 1983 UTM Zone 11N and saved in the projectedFiles folder within Workspace."
#----------------------------------------------------------------------------------------------------------------------------------------

# Creating a buffer of the San Andreas Fault line

print "Creating buffer for San Andreas Fault Line"

# Set local variables
try:
    faultDataset = tempFolder + r'\SA_Fault.shp'
    faultBuffer = outFolder + r'\saFaultBuffer.shp'
    distanceField = "50 Kilometers"
    sideType = "FULL"
    endType = "ROUND"

# Checks if shapefile Exists and deletes if it does exist
    if arcpy.Exists(faultBuffer):
        arcpy.AddMessage("Deleting Existing Shapefile")
        arcpy.Delete_management(faultBuffer)
    
# Execute Buffer
    arcpy.Buffer_analysis(faultDataset, faultBuffer, distanceField, sideType, endType)
    
except:
    arcpy.AddError(arcpy.GetMessages(2))

print "The buffer for 50 Kilometers has been created and saved in the outputFiles folder within Workspace."
#---------------------------------------------------------------------------------------------------------------------------
#Clip the earthquake points within the San Andreas Fault buffer

print "Using the buffer to clip out the earthquake points falling within 80 KM from the fault line."
# Set local variables
in_features = tempFolder + r'\earthquake.shp'
clip_features = outFolder + r'\saFaultBuffer.shp'
out_clip = outFolder + r'\earthquakeClip.shp'
xy_tolerance = ""

# Checks if shapefile Exists and deletes if it does exist
if arcpy.Exists(out_clip):
    arcpy.AddMessage("Deleting Existing Shapefile")
    arcpy.Delete_management(out_clip)

# Execute Clip
arcpy.Clip_analysis(in_features, clip_features, out_clip, xy_tolerance)

print "The clipped earthquake points shapefile has been created and saved in the ouputFiles folder within Workspace."
