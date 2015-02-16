# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name: createSoilTemperatureRaster
# Purpose: This script takes soil temperature data and creates an interpolated
#          raster using linear interpolation methods
# Input: 0- Elevation raster
#        1- Soil data table
# Output: Soil temperature raster
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

arcpy.AddMessage("Creating constant soil temperature raster...")

#Set input parameters
elevation_raster = arcpy.GetParameterAsText(0)
station_locations = arcpy.GetParameterAsText(1)
data_table = arcpy.GetParameterAsText(2)

#Setup workspace
#output cell size should be the same as elevation raster cell size
arcpy.env.cellSize = elevation_raster
output_cell_size = arcpy.env.cellSize
scratchGDB = arcpy.env.scratchGDB
arcpy.env.overwriteOutput = True

# Set output parameter
arcpy.SetParameterAsText(3, soilTemperatureRaster)

'''==== end script ======'''



'''=======References======='''
