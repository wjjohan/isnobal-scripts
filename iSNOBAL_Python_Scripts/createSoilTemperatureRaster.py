# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name: createSoilTemperatureRaster
# Purpose: This script takes soil temperature data and creates an interpolated
#          raster using linear interpolation methods
# Input: 0- Elevation raster
#        1- Station location feature class
#        2- Stand-alone data table
# Output: Soil temperature raster
#-------------------------------------------------------------------------------

'''======Define internal functions======'''
#Linear Regression Function- calculate linear temperature-elevation relations from the observed data.
def linRegress(inTable):
    arcpy.AddMessage("Running linear regression on soil temperature and elevation...")
    #Linear Regression on soil temperature values
    elevation = list((row.getValue("RASTERVALU") for row in arcpy.SearchCursor(inTable,fields="RASTERVALU")))
    temperature = list((row.getValue("st005") for row in arcpy.SearchCursor(inTable,fields="st005")))
    lr_results = stats.linregress(elevation,temperature)
    slope = lr_results[0]
    intercept = lr_results[1]
    r_value = lr_results[2]
    arcpy.AddMessage("r-squared: " + str(r_value**2))

    #build a table for future use that contains the slope and intercept values
    arcpy.CreateTable_management(scratchGDB,"slope_intercept_table")
    arcpy.AddField_management(scratchGDB + "\slope_intercept_table","slope","DOUBLE")
    arcpy.AddField_management(scratchGDB + "\slope_intercept_table","intercept","DOUBLE")
    rows = arcpy.InsertCursor(scratchGDB + "\slope_intercept_table")
    row = rows.newRow()
    row.slope = slope
    row.intercept = intercept
    rows.insertRow(row)
    del row, rows

#create the final output raster
def createFinalRaster(elevation_raster, slope_intercept_table):
    #assign values from slope_intercept_table to individual scalar variables
    cursor = arcpy.SearchCursor(slope_intercept_table)
    for row in cursor:
        slope = row.getValue("slope")
        intercept = row.getValue("intercept")

    #Equation to follow for final raster:
        #T_est = slope * elevation + intercept
    output_raster = (Raster(elevation_raster) * slope + intercept)
    output_raster.save("soil_temperature_lr")

    return output_raster

'''==== start script ======'''
#Import necessary modules
import arcpy
from arcpy.sa import *
import numpy
from scipy import stats

#Check-out necessary extensions
arcpy.CheckOutExtension('Spatial')

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

#Start process

#extract elevations to stations
arcpy.AddMessage("Extracting elevations")
arcpy.gp.ExtractValuesToPoints_sa(station_locations, elevation_raster, scratchGDB + "\station_elevations", "NONE", "VALUE_ONLY")

#join elevations to the soil data table
arcpy.AddMessage("Joining elevations to data table")
arcpy.JoinField_management(scratchGDB + "\station_elevations", "Site_Key", data_table, "site_key", "st005")

#select rows where elevation and soil data are not null
arcpy.AddMessage("Removing \"no-data\" rows from data table")
arcpy.TableSelect_analysis(scratchGDB + "\station_elevations", scratchGDB + "\station_elevations_noNULL", "RASTERVALU IS NOT NULL and RASTERVALU > 0 and st005 IS NOT NULL")

#run the internal function "linRegress" with "station_elevations_noNULL" as input
linRegress(scratchGDB + "\station_elevations_noNULL")

#run the internal function "createFinalRaster"
arcpy.AddMessage("Creating final raster")
output_raster = createFinalRaster(elevation_raster, scratchGDB + "\slope_intercept_table")

# Set output parameter
arcpy.SetParameterAsText(3, output_raster)

#Clear scratch workspace
arcpy.AddMessage("Deleting scratch workspace")
arcpy.Delete_management(scratchGDB)
'''==== end script ======'''



'''=======References======='''
