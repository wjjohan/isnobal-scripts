# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name: createPrecipitationMassRaster
# Purpose: This script follows the detrended kriging methods outlined by
#          Susong, Marks, and Garen (1999) for estimating precipitation mass
#          grids.
# Input: 0- Elevation raster
#        1- Station location feature class
#        2- Stand-alone data table
# Output: precipitation mass raster
#
# Output used in:
#
#-------------------------------------------------------------------------------

'''======Define internal functions======'''
#Linear Regression Function- calculate linear precip-elevation relations from the observed data.
def linRegress(inTable):
    arcpy.AddMessage("Running linear regression on precipitation mass and elevation...")
    #Linear Regression on MEAN precipitation mass values
    elevation = list((row.getValue("RASTERVALU") for row in arcpy.SearchCursor(inTable,fields="RASTERVALU")))
    precip = list((row.getValue("MEAN_ppts") for row in arcpy.SearchCursor(inTable,fields="MEAN_ppts")))
    lr_results = stats.linregress(elevation,precip)
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

    #calculate residuals
    # EQUATION: predicted = slope*elevation + intercept
    temp = [slope*val for val in elevation]
    predicted = [val+intercept for val in temp]
    residual = [precip - predicted for precip, predicted in zip(precip, predicted)]


    #Append residual list to inTable's empty "residual" field
    cursor = arcpy.UpdateCursor(inTable)
    row =cursor.next()
    i = 0
    while row:
        row.setValue("residual", residual[i])
        cursor.updateRow(row)
        i = i + 1
        row = cursor.next()
    del cursor

    return inTable

#create the final output raster by adding back the elevation trends that were taken out before kriging
def createFinalRaster(residual_raster, elevation_raster, slope_intercept_table):
    #assign values from slope_intercept_table to individual scalar variables
    cursor = arcpy.SearchCursor(slope_intercept_table)
    for row in cursor:
        slope = row.getValue("slope")
        intercept = row.getValue("intercept")

    #Equation to follow for final raster:
        #Precip_final = Precip_resid_raster - slope*elevation_raster + intercept
    output_raster = Raster(residual_raster) + (Raster(elevation_raster) * slope + intercept)
    output_raster.save("precipitation_mass")

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

#calculate the mean precipitation mass for each station over the n-hour time period (select appropriate column: ppts for shielded; pptu for unshielded; ppta for dual gage wind corrected
arcpy.AddMessage("Calculating average precipitation mass")
arcpy.Statistics_analysis(data_table, scratchGDB + "\station_statistics", "ppts MEAN", "site_key")

#join elevations to the statistics table created above
arcpy.AddMessage("Joining elevations to data table")
arcpy.JoinField_management(scratchGDB + "\station_statistics", "site_key", scratchGDB + "\station_elevations", "Site_Key", "RASTERVALU")

#select rows in "station_statistics" that have a positive elevation
arcpy.AddMessage("Removing \"no-data\" rows from data table")
arcpy.TableSelect_analysis(scratchGDB + "\station_statistics", scratchGDB +  "\stats1", "RASTERVALU > 0 and RASTERVALU IS NOT NULL")

#add "residual" field to "stats1" for future use
arcpy.AddField_management(scratchGDB + "\stats1", "residual", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

#run the internal function "linRegress" with "stats1" as input
kriging_table = linRegress(scratchGDB + "\stats1")

#make a copy of the station_locations feature class to be used in kriging steps
arcpy.CopyFeatures_management(station_locations, scratchGDB + "\\fcKriging")

#join the residuals from the linRegress function to the kriging feature class created above
arcpy.JoinField_management(scratchGDB + "\\fcKriging", "Site_Key", kriging_table, "site_key", "residual")

#run empirical bayesian kriging
arcpy.AddMessage("Performing kriging on residuals")
arcpy.EmpiricalBayesianKriging_ga(scratchGDB + "\\fcKriging", "residual", "", scratchGDB + "\kriged_residual_raster", output_cell_size, "NONE", "100", "1", "100", "NBRTYPE=SmoothCircular RADIUS=2299.71700172693 SMOOTH_FACTOR=1", "PREDICTION", "0.5", "EXCEED", "")

#run the internal function "createFinalRaster" which adds back the elevation component to the residuals raster
arcpy.AddMessage("Creating final raster")
output_raster = createFinalRaster(scratchGDB + "\\kriged_residual_raster", elevation_raster, scratchGDB + "\slope_intercept_table")


# Set output parameter
arcpy.SetParameterAsText(3, output_raster)

#Clear scratch workspace
arcpy.AddMessage("Deleting scratch workspace")
arcpy.Delete_management(scratchGDB)
'''==== end script ======'''



'''=======References======='''
#Susong, D., Marks, D., & Garen, D. (1999). Methods for developing time-series
#   climate surfaces to drive topographically distributed energy- and
#   water-balance models. Hydrological Processes, 13, 2003–2021. Retrieved from
#   ftp://ftp.nwrc.ars.usda.gov/publications/1999/Marks-Methods for developing
#   time-series climate surfaces to drive topographically distributed energy-
#   and water-balance models.pdf