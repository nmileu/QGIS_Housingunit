from qgis.core import *
from qgis.core import QgsRasterLayer
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry
from PyQt4.QtCore import QFileInfo, QVariant
import sys
import math
import csv
import processing
import os, gdal

def CalcHUM(vector1,vector2,diretorioOut,resolucao,campoPopulation,campoHousing):
	#Set GRASS extent
	fileInfo1 = QFileInfo(vector1)
	path1 = fileInfo1.filePath()
	baseName1 = fileInfo1.baseName()
	layer1 = QgsVectorLayer(vector1,"bgri","ogr")
	if layer1.isValid() is True:
		print "Layer1 was loaded successfully!"
	else:
		print "Unable to read basename and file path - Your string is probably invalid"
	ext = layer1.extent()
	(xmin, xmax, ymin, ymax) = (ext.xMinimum(), ext.xMaximum(), ext.yMinimum(), ext.yMaximum())
	grassExtent = str(xmin) + "," + str(xmax) + "," + str(ymin) + "," + str(ymax)
	print grassExtent
	
	fileInfo2 = QFileInfo(vector2)
	path2 = fileInfo2.filePath()
	baseName2 = fileInfo2.baseName()
	layer2 = QgsVectorLayer(vector2,"addresses","ogr")
	if layer2.isValid() is True:
		print "Layer2 was loaded successfully!"
	else:
		print "Unable to read basename and file path - Your string is probably invalid"
	
	# Adicionar campos para calculo (Campo1, Campo 2)
	#shp_uri = vector1
	#shp =  QgsVectorLayer(shp_uri, 'bgri', 'ogr')
	#print shp
	caps = layer1.dataProvider().capabilities()
	if caps & QgsVectorDataProvider.AddAttributes:
		res = layer1.dataProvider().addAttributes([QgsField("INDIVALOJ", QVariant.Double)])
	layer1.updateFields()
	layer1.commitChanges()
	layer1.dataProvider().forceReload()
	
	# Update do campo INDALOJ no shapefile
	expressionA = QgsExpression("N_INDIVIDU/N_ALOJAMEN")
	indexA = layer1.fieldNameIndex("INDIVALOJ")	
	expressionA.prepare(layer1.pendingFields())
	layer1.startEditing()
	for feature in layer1.getFeatures():
		valueA = expressionA.evaluate(feature)
		layer1.changeAttributeValue(feature.id(), indexA, valueA)
	layer1.commitChanges()
	layer1.dataProvider().forceReload()
	print 'Updated!'
	
	QgsMapLayerRegistry.instance().reloadAllLayers()
	#Processing HUM to vector grid
	resultado1 = diretorioOut + r"\addresses_join_stats.shp"
	processing.runalg("qgis:joinattributesbylocation",vector2,vector1,['intersects'],0,0,"sum",0,resultado1)
	resultado2 = diretorioOut + r"\grelha.shp"
	processing.runalg("qgis:vectorgrid",grassExtent,resolucao,resolucao,0,resultado2)
	resultado3 = diretorioOut + r"\resultado.shp"
	processing.runalg("qgis:joinattributesbylocation",resultado2,resultado1,['intersects'],0,1,"sum",1,resultado3)
	print 'Processed!'
	
def ExportHUMgrid2raster(diretorioOut,resolucao):
	resultado3 = diretorioOut + r"\resultado.shp"
	layer = QgsVectorLayer(resultado3,'resultado', 'ogr')
	ext = layer.extent()
	(xmin, xmax, ymin, ymax) = (ext.xMinimum(), ext.xMaximum(), ext.yMinimum(), ext.yMaximum())
	grassExtent = str(xmin) + "," + str(xmax) + "," + str(ymin) + "," + str(ymax)
	QgsMapLayerRegistry.instance().addMapLayer(layer)
	query = '"sumINDIVAL"  is null'
	selection = layer.getFeatures(QgsFeatureRequest().setFilterExpression(query))
	layer.setSelectedFeatures([k.id() for k in selection])
	selection = layer.getFeatures(QgsFeatureRequest().setFilterExpression(query))
	layer.setSelectedFeatures([k.id() for k in selection])
	# Update do campo sumINDIVAL no shapefile
	expressionB = QgsExpression("0")
	indexB = layer.fieldNameIndex("sumINDIVAL")	
	expressionB.prepare(layer.pendingFields())
	layer.startEditing()
	for feature in layer.getFeatures(QgsFeatureRequest().setFilterExpression(query)):
		valueB = expressionB.evaluate(feature)
		layer.changeAttributeValue(feature.id(), indexB, valueB)
	layer.commitChanges()
	layer.updateExtents()
	layer.dataProvider().forceReload()
	layer.removeSelection()
	print 'Updated!'
	
	resultado4 = diretorioOut + r"\centroides.shp"
	processing.runalg("qgis:polygoncentroids",resultado3,resultado4)
	
	layer1 = QgsVectorLayer(resultado4,'centroides', 'ogr')
	QgsMapLayerRegistry.instance().addMapLayer(layer1)
	
	resultado5 = diretorioOut + r"\resultado.tif"
	#processing.runalg("saga:shapestogrid",resultado4,"sumINDIVAL",2,4,0,0,3,grassExtent,resolucao,0,resultado5)
	processing.runalg("grass7:v.to.rast.attribute",resultado4,0,"sumINDIVAL",grassExtent,resolucao,-1,0.0001,resultado5)
	fileInfo2 = QFileInfo(resultado5)
	path2 = fileInfo2.filePath()
	baseName2 = fileInfo2.baseName()
	layer2 = QgsRasterLayer(path2, baseName2)
	if layer2.isValid() is True:
		QgsMapLayerRegistry.instance().addMapLayer(layer2)
		print "Layer2 was loaded successfully!"
	else:
		print "Unable to read basename2 and file path2 - Your string is probably invalid"
	