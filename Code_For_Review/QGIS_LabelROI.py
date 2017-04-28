from PyQt4.QtCore import QVariant
from PyQt4.QtGui import QColor

import os
import sys
import shutil # for copying files
import random

# SETTINGS VARIABLES

# Define directories where rasters are stored and where training data should be
# saved once the user is done labeling the vector layer
RASTER_DIR = "/path/to/NAIP/rasters/" # make sure to include a trailing "/" here!
TRAINING_SAVE_DIR = "/path/for/saving/training/shapefiles/" # make sure to include a trailing "/" here!


# 1) LOAD A RANDOM RASTER LAYER

# Pick a random NAIP image from the raster directory
files_list = os.listdir(RASTER_DIR)
file_to_train = random.choice(files_list)

# Load the image as a raster layer into the QGIS project
roi_raster_layer = iface.addRasterLayer(RASTER_DIR + file_to_train, "TrainingImage")

# Get the extent of the raster layer so we can use this same extent for the
# corresponding vector layer
layer_extent = roi_raster_layer.extent()


# 2) PRE-POPULATE A VECTOR LAYER TEMPLATE AND ADD NEW VECTOR LAYER TO QGIS
# Create a vector layer with all of the fields and classes pre-populated and
# color-coded, so all the user has to do is trace regions of interest (ROI)

# Create a new vector layer using the "memory" data provider; this means that
# changes are saved in memory until the user executes the saveROILayer()
# function (below) to save to a shapefile on disk
roi_vector_layer = QgsVectorLayer("Polygon", "ROITrainingLayer", "memory")
data_provider = roi_vector_layer.dataProvider()

# Set the new layer's extent to be equal to that of the raster layer
roi_vector_layer.extent = layer_extent

# Add field for class attribute
data_provider.addAttributes([QgsField("Class", QVariant.Int)])
roi_vector_layer.updateFields() # tell the vector layer to fetch changes from the provider

# Set symbology in the renderer to use as convenient pre-filled classification
# options for the user. Start by defining a dictionary of the classifications
# and colors we want to use.
landuse = {
    "0": ("#cccccc", "other-0"),
    "1": ("#cc0000", "asphalt-1"),
    "2": ("#ff9933", "buildings-2"),
    "3": ("#3399ff", "water-3"),
    "4": ("#66ff33", "grass-4"),
    "5": ("#009900", "trees-5"),
    "6": ("#ffcc33", "agriculture-6"),
    "7": ("#996600", "dirt-7"),
    "8": ("#66ff99", "algae-8")
    }

categories = []

# Cycle through the landuse dictionary defined above and turn each entry into
# a category that we can use in the categorical renderer in QGIS.
for terrain, (color, label) in landuse.items():
    symbol = QgsSymbolV2.defaultSymbol(roi_vector_layer.geometryType())
    symbol.setColor(QColor(color))
    category = QgsRendererCategoryV2(terrain, symbol, label)
    categories.append(category)

renderer = QgsCategorizedSymbolRendererV2("class", categories)
roi_vector_layer.setRendererV2(renderer)

# Toggle the layer to editing mode
roi_vector_layer.startEditing()

# Add layer to map layer registry to display in GUI
QgsMapLayerRegistry.instance().addMapLayer(roi_vector_layer)


# 3) GIVE THE USER FEEDBACK AS THEY'RE ADDING ROI/FEATURES TO THE LAYER

# Count the number of classes from the landuse dictionary defined above
nbr_of_classes = len(landuse)

def roiLayerStats(featureAdded):
    '''
    Print off stats about the total number of features that have been labeled and
    the number of features in each class in the ROI vector layer. This function
    is called by the featureAdded.connect() listener every time the user adds
    a new feature.
    '''
    total_features = roi_vector_layer.featureCount()
    print "There are " + str(total_features) + " total features."
    features = roi_vector_layer.getFeatures()

    # Query the features in the layer and tally the number of features with each class label
    idx = roi_vector_layer.fieldNameIndex("class")

    # Populate a dictionary to hold a tally of the number of features of each class
    # the user has labeled
    feature_count_dict = {str(key): 0 for (key, value) in enumerate(range(0, nbr_of_classes))}

    for feature in features:
        assigned_class = str(feature.attributes()[idx])
        feature_count_dict[assigned_class] = feature_count_dict[assigned_class] + 1

    # Print out the tally to the console, so the user can estimate which classes
    # need more feature labels
    for key, val in feature_count_dict.iteritems():
        print "Class " + key + ": " + str(val) + " features labeled"

# Add a listener to the map layer to announce when the user adds a feature and
# run a function to get the latest stats on the layer
# https://gis.stackexchange.com/questions/53269/handle-add-new-feature-event-and-or-access-feature-before-commit
roi_vector_layer.featureAdded.connect(roiLayerStats)


# 4) GAMIFY!!!

def Waldo():
    '''
    A function the user can call in the QGIS Python console if they want to be
    prompted with a random class to look for when marking their next ROI/feature.
    Helps make the task of marking ROIs less tedious and more like a game!
    '''
    random_key = random.choice(list(landuse))
    random_class = landuse[random_key][1]
    print "Can you find a feature with class " + random_class + "?"


# 5) SAVE THE RESULTS

def saveROILayer():
    '''
    A function the user can call in the QGIS Python console when they are done
    labeling classes and are ready to save the vector layer as a shapefile
    '''
    try:
        # Define a filename the incorporates the original raster image's filename
        # so the vector layer can be linked back to its associated raster during training
        filepath_to_save = TRAINING_SAVE_DIR + file_to_train[:-4]+ "_ROI_classified.shp"
        print "Saving your layer to filepath: " + filepath_to_save

        # Save the vector layer as a shapefile to TRAINING_SAVE_DIR
        QgsVectorFileWriter.writeAsVectorFormat(roi_vector_layer, filepath_to_save, "utf-8", None, "ESRI Shapefile")

        # Copy associated raster file into TRAINING_SAVE_DIR, so we have it set aside for training
        shutil.copy2(RASTER_DIR + file_to_train, TRAINING_SAVE_DIR)

    except(e):
        print "Couldn't save file: " + e
