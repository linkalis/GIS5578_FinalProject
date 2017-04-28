import PyQt4.QtCore

# Select all layers
layers = iface.legendInterface().layers()

for layer in layers:
    print layer
    # Load a previously-generated .QML file to use for styling the raster
    layer.loadNamedStyle("<local_filepath>/QGIS_ClassifiedRasterStyle.qml")
    layer.triggerRepaint()
