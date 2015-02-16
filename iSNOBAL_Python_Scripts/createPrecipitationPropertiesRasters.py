# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name: createPrecipitationPropertiesRasters
# Purpose: This script creates precipitation properties rasters (percentage of
#          precipitation mass that was snow, density of snow portion of the
#          precipitation)
# Input: 0- Dew-point temperature raster
# Output: percent snow raster, density of snow portion raster
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
dp_temperature_raster = arcpy.GetParameterAsText(0)

#Setup workspace
#output cell size should be the same as dp temp raster cell size
arcpy.env.cellSize = dp_temperature_raster
output_cell_size = arcpy.env.cellSize
scratchGDB = arcpy.env.scratchGDB
arcpy.env.overwriteOutput = True

#Start Script

#Percent snow conditional:
arcpy.AddMessage("Creating raster for percentage of precipitation that was snow")
inRas = Raster(dp_temperature_raster)
outPercentSnowRaster = arcpy.sa.Con(inRas < -5.0, 1.0, Con((inRas >= -5.0) & (inRas < -3.0), 1.0,
                                                           Con((inRas >= -3) & (inRas < -1.5), 1.0,
                                                               Con((inRas >= -1.5) & (inRas < -0.5), 1.0,
                                                                   Con((inRas >= -0.5) & (inRas < 0), 0.75,
                                                                       Con((inRas >= 0) & (inRas < 0.5), 0.25,
                                                                           Con(inRas >= 0.5,0)))))))
outPercentSnowRaster.save("percent_snow")

#Snow density conditional:
arcpy.AddMessage("Creating raster for density of snow portion of precipitation")
outSnowDensityRaster = arcpy.sa.Con(inRas < -5.0, 75.0, Con((inRas >= -5.0) & (inRas < -3.0), 100.0,
                                                           Con((inRas >= -3) & (inRas < -1.5), 150.0,
                                                               Con((inRas >= -1.5) & (inRas < -0.5), 175.0,
                                                                   Con((inRas >= -0.5) & (inRas < 0), 200.0,
                                                                       Con((inRas >= 0) & (inRas < 0.5), 250.0,
                                                                           Con(inRas >= 0.5,0)))))))
outSnowDensityRaster.save("snow_density_of_precipitation")


# Set output parameters
arcpy.SetParameterAsText(1, outPercentSnowRaster)
arcpy.SetParameterAsText(2, outSnowDensityRaster)
'''==== end script ======'''



'''=======References======='''
