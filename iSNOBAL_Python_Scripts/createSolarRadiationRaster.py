# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name: createSolarRadiationRaster
# Purpose: This script uses a built in ArcGIS tool to estimate a clear-sky solar
#          radiation grid, and then corrects the grid using observed data
# Input: 0- Elevation raster
#        1- Station locations feature class
#        2- Stand-alone data table
#        3- Date and time of simulation
# Output: constant soil temperature raster
#
# Output used in:
#
#
#-------------------------------------------------------------------------------

'''======Define internal functions======'''




'''==== start script ======'''
#Import necessary modules
import arcpy
import os
import multiprocessing
import sys
import subprocess
import glob
from arcpy.sa import *
import numpy
from scipy import stats
import arcpy.mapping
import datetime

#Check-out necessary extensions
arcpy.CheckOutExtension('Spatial')

#Set input parameters
elevation_raster = arcpy.GetParameterAsText(0)
station_locations = arcpy.GetParameterAsText(1)
data_table = arcpy.GetParameterAsText(2)
date_time = arcpy.GetParameterAsText(3)



#Setup workspace
#output cell size should be the same as elevation raster cell size
arcpy.env.cellSize = elevation_raster
output_cell_size = arcpy.env.cellSize
scratchGDB = arcpy.env.scratchGDB
arcpy.env.overwriteOutput = True

#Start Script

#RUN SIMULATED CLEAR-SKY CALCULATIONS
#make a copy of the station location feature class in the scratchspace
arcpy.CopyFeatures_management(station_locations, scratchGDB + "\\station_locations_sr")

#set up area solar radiation tool parameters and run the tool
arcpy.AddMessage("Running area solar radiation tool")
global_radiation_raster = scratchGDB + "\\global_radiation_raster"
skySize = 200
arcpy.gp.AreaSolarRadiation_sa(elevation_raster, global_radiation_raster, "",skySize, date_time,"","1","NOINTERVAL","1","FROM_DEM","32","8","8","UNIFORM_SKY","0.3","0.5","#","#","#")

#CORRECT SIMULATED VALUES TO OBSERVED DATA
arcpy.AddMessage("Correcting simulated radiation values")

#Extract simulated global radiation values to station location feature class
arcpy.AddMessage("Extracting simulated values")
arcpy.gp.ExtractMultiValuesToPoints_sa(scratchGDB + "\\station_locations_sr",scratchGDB + "\\global_radiation_raster","NONE")

#Join the data table to "station_locations_sr"
arcpy.JoinField_management(scratchGDB + "\\station_locations_sr", "Site_Key", data_table, "site_key", "in_solar_radiation")

#select non-null rows
arcpy.AddMessage("Removing \"no-data\" rows")
arcpy.TableSelect_analysis(scratchGDB + "\\station_locations_sr", scratchGDB + "\\station_locations_sr_noNULL", "in_solar_radiation IS NOT NULL and global_radiation_raster > 0")
#arcpy.TableSelect_analysis(scratchGDB + "\\station_locations_sr_noNULL", scratchGDB + "\\station_locations_sr_noNULL2", "global_radiation_raster > 0")

#add "ratio" field to station locations
arcpy.AddField_management(scratchGDB + "\\station_locations_sr_noNULL","ratio","FLOAT","#","#","#","#","NULLABLE","NON_REQUIRED","#")

#calculate "ratio" field (observed radiation / simulated radiation)
arcpy.AddMessage("Calculating observed/simulated ratios")
arcpy.CalculateField_management(scratchGDB + "\\station_locations_sr_noNULL","ratio","!in_solar_radiation!/ !global_radiation_raster!","PYTHON","#")

#convert "ratio" field to numpy array
na = arcpy.da.TableToNumPyArray(scratchGDB + "\\station_locations_sr_noNULL", "ratio")

#calculate average ratio
arcpy.AddMessage("Calculating average ratio")
dMeanRatio = numpy.mean(na["ratio"])
dMeanRatio2 = numpy.asscalar(dMeanRatio)

#multiply simulated raster by average ratio
arcpy.AddMessage("Multiplying simulated values by average ratio")
output_raster = Raster(scratchGDB +"\\global_radiation_raster") * dMeanRatio2
arcpy.AddMessage("Creating final raster")
output_raster.save("solar_radiation")

# Set output parameter
arcpy.SetParameterAsText(4, output_raster)

#Clear scratch workspace
arcpy.AddMessage("Deleting scratch workspace")
arcpy.Delete_management(scratchGDB)
'''==== end script ======'''



'''=======References======='''
