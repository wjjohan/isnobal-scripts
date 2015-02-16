# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name: createSoilTemperatureConstantRaster
# Purpose: This script creates a constant soil temperature raster from a user
#          specified value (Default 0 degrees C)
# Input: 0- Elevation raster
#        1- Specified contstant soil temperature
# Output: constant soil temperature raster
#
# Output used in:
#
#-------------------------------------------------------------------------------

'''======Define internal functions======'''
#This script has no internal functions


'''==== start script ======'''
#Import necessary modules
import arcpy
from arcpy.sa import *

#Check-out necessary extensions
arcpy.CheckOutExtension('Spatial')

#Set input parameters
elevation_raster = arcpy.GetParameterAsText(0)
constant_value = arcpy.GetParameterAsText(1)
#If "constant_value" is empty, use default value of 0
if not constant_value:
    constant_value = "0"

#Setup workspace
#output cell size should be the same as elevation raster cell size
arcpy.env.cellSize = elevation_raster
output_cell_size = arcpy.env.cellSize
scratchGDB = arcpy.env.scratchGDB
arcpy.env.overwriteOutput = True
currentWS = arcpy.env.workspace
soilTemperatureRaster = currentWS + "\\soil_temperature"

#Get coordinate system information
desc = arcpy.Describe(elevation_raster)
coordSystem = desc.spatialReference

# Process: Create Constant Raster
arcpy.AddMessage("Creating constant soil temperature raster")
arcpy.gp.CreateConstantRaster_sa(soilTemperatureRaster, constant_value, "FLOAT", output_cell_size, elevation_raster)

# Process: Define Projection
arcpy.AddMessage("Defining coordinate system")
arcpy.DefineProjection_management(soilTemperatureRaster,coordSystem)

# Set output parameter
arcpy.SetParameterAsText(2, soilTemperatureRaster)
'''==== end script ======'''



'''=======References======='''
