# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name: createVaporPressureRasterFromDewpoint
# Purpose: This script uses the equation found in ____ to calculate vapor
#          pressure values from dew-point temperature surfaces.
# Input: 1- Elevation raster
#        2- Station location feature class
#        3- Stand-alone data table
# Output: vapor pressure raster
# Shares input with:
#
# Output used in:
#
#-------------------------------------------------------------------------------

'''======Define internal functions======'''
#This script has no internal functions

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

arcpy.AddMessage("Creating vapor pressure raster from dew-point temperatures...")

#Set input parameters
dewPoint_raster = arcpy.GetParameterAsText(0)

#Setup workspace
#output cell size should be the same as elevation raster cell size
scratchGDB = arcpy.env.scratchGDB
arcpy.env.overwriteOutput = True

#Start process

inRaster = Raster(dewPoint_raster)

output_raster = arcpy.sa.Float(6.11 * 10 ** ((7.5 * arcpy.sa.Float(inRaster))/(237.3 + arcpy.sa.Float(inRaster))))*100
output_raster.save("vapor_pressure_from_dewpoint")

# Set output parameter
arcpy.SetParameterAsText(1, output_raster)

'''==== end script ======'''



'''=======References======='''
