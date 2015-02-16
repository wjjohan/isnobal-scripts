# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name: createInitialSnowPropertiesRasters
# Purpose: This script uses the elevation raster to perform linear interpolation
#          on set values to produce rasters for average snowcover density,
#          active (upper) snow layer temperature, and average snowcover
#          temperature
# Input: 0- Elevation raster
# Output: snow density raster, active layer snow temperature raster, average
#         snowcover temperature raster
# Output used in:
#
#-------------------------------------------------------------------------------

'''======Define internal functions======'''




'''==== start script ======'''
#Import necessary modules
import arcpy
from arcpy.sa import *

#Check-out necessary extensions
arcpy.CheckOutExtension('Spatial')

#Set input parameters
elevation_raster = arcpy.GetParameterAsText(0)

#Setup workspace
#output cell size should be the same as elevation raster cell size
arcpy.env.cellSize = elevation_raster
output_cell_size = arcpy.env.cellSize
scratchGDB = arcpy.env.scratchGDB
arcpy.env.overwriteOutput = True

#Start Process

#Density Equation: y = -0.0395(elevation) + 405.26
arcpy.AddMessage("Creating snow density raster from linear interpolation")
snow_density_raster = -0.0395 * Raster(elevation_raster) + 405.26
snow_density_raster.save("snow_density")

#Upper Layer Temperature Equation: y = -0.0008(elevation) + 0.1053
arcpy.AddMessage("Creating upper snow layer temperature raster from linear interpolation")
upper_layer_temperature = -0.0008 * Raster(elevation_raster) + 0.1053
upper_layer_temperature.save("upper_layer_snow_temperature")

#lower layer temperature equation: y = -0.0008(elevation) + 1.3056
arcpy.AddMessage("Creating lower snow layer temperature raster from linear interpolation")
lower_layer_temperature = -0.0008 * Raster(elevation_raster) + 1.3056

#average snowcover temperature is the average of the upper and lower layer temperatures
arcpy.AddMessage("Creating average snowcover temperature raster")
average_snowcover_temperature = arcpy.sa.CellStatistics([upper_layer_temperature, lower_layer_temperature],"MEAN","NODATA")
average_snowcover_temperature.save("average_snowcover_temperature")

# Set output parameters
arcpy.SetParameterAsText(1, snow_density_raster)
arcpy.SetParameterAsText(2, upper_layer_temperature)
arcpy.SetParameterAsText(3, average_snowcover_temperature)


'''==== end script ======'''



'''=======References======='''
