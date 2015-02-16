# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name: createInitialUpperLayerSnowTemperatureRaster
# Purpose: This script creates an intitial upper layer snow temperature raster
#          from set interpolation points and an elevation surface.
# Input: 1- Elevation raster
# Output: initial upper layer snow temperature raster
# Shares input with:
#
# Output used in:
#
#-------------------------------------------------------------------------------

'''======Define internal functions======'''




'''==== start script ======'''
#Import necessary modules
import arcpy
import datetime
import os
import multiprocessing
import sys
import subprocess
import glob
from arcpy.sa import *
import numpy
from scipy import stats
import arcpy.mapping

#Check-out necessary extensions
arcpy.CheckOutExtension('Spatial')

arcpy.AddMessage("Creating initial upper layer snow temperature raster...")

#Set input parameters
elevation_raster = arcpy.GetParameterAsText(0)

#Setup workspace
#output cell size should be the same as elevation raster cell size
arcpy.env.cellSize = elevation_raster
output_cell_size = arcpy.env.cellSize
scratchGDB = arcpy.env.scratchGDB
arcpy.env.overwriteOutput = True

#Start Process
#Upper Layer Temperature Equation: y = -0.0008(elevation) + 0.1053
upper_layer_temperature = -0.0008 * Raster(elevation_raster) + 0.1053
upper_layer_temperature.save("upper_layer_snow_temperature")

# Set output parameter
arcpy.SetParameterAsText(1, upper_layer_temperature)

'''==== end script ======'''



'''=======References======='''
