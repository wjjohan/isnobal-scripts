# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name: createInitialSnowDensityRaster
# Purpose: This script creates an intitial snow density raster from
#          set interpolation points and an elevation surface.
# Input: 1- Elevation raster
# Output: initial snow density raster
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

arcpy.AddMessage("Creating initial snow density raster...")

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
snow_density_raster = -0.0395 * Raster(elevation_raster) + 405.26
snow_density_raster.save("initial_snow_density")

# Set output parameter
arcpy.SetParameterAsText(1, snow_density_raster)

'''==== end script ======'''



'''=======References======='''
