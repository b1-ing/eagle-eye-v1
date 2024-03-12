# Code borrowed from https://subscription.packtpub.com/book/application_development/9781783984985/1/ch01lvl1sec18/creating-a-standalone-application
# and upgraded for QGIS 3.0
import os
import sys
import shutil
import tempfile
import urllib.request
from zipfile import ZipFile
from glob import glob
import threading

from qgis.core import (QgsPoint, QgsRectangle, QgsApplication, QgsCoordinateReferenceSystem, QgsFeature, QgsCoordinateTransform,
                       QgsGeometry, QgsProject, QgsRasterLayer, QgsVectorLayer,QgsLayerTreeLayer, QgsLayerTreeModel)
from qgis.gui import QgsLayerTreeMapCanvasBridge, QgsMapCanvas, QgsDockWidget, QgsLayerTreeView
from qgis.PyQt.QtCore import Qt
# Unused so commented
# from qgis.PyQt.QtGui import *
app = QgsApplication([], True)
# On Linux, didn't need to set it so commented
# app.setPrefixPath("C:/Program Files/QGIS Brighton/apps/qgis", True)
app.initQgis()
canvas = QgsMapCanvas()
canvas.setWindowTitle("PyQGIS Standalone Application Example")
canvas.setCanvasColor(Qt.white)
crs = QgsCoordinateReferenceSystem(3857)
project = QgsProject.instance()
canvas.setDestinationCrs(crs)


def map_viewer(input_folder, epsg):
    for root, dirs, files in os.walk(input_folder):
        files.sort()
        for file in files:
            fname = root + '/' + file
            bname = os.path.basename(file)
            print(fname)
            layer = QgsRasterLayer(fname, bname)
            if layer.isValid():
                project.addMapLayer(layer)
            else:
                print('invalid layer')


    urlWithParams = 'type=xyz&url=https://a.tile.openstreetmap.org/%7Bz%7D/%7Bx%7D/%7By%7D.png&zmax=19&zmin=0&crs=EPSG3857'
    rlayer2 = QgsRasterLayer(urlWithParams, 'OpenStreetMap', 'wms')

    if rlayer2.isValid():
        project.addMapLayer(rlayer2)
    else:
        print('invalid layer')
    # Download shp ne_10m_admin_0_countries.shp and associated files in the same directory

    root = QgsProject.instance().layerTreeRoot()
    bridge = QgsLayerTreeMapCanvasBridge(root, canvas)

    vl = QgsProject.instance().mapLayersByName("OpenStreetMap")[0]
    myvl = root.findLayer(vl.id())
    print(myvl)
    myvlclone = myvl.clone()
    print(myvlclone)
    parent = myvl.parent()
    print(parent)
    parent.insertChildNode(-1, myvlclone)
    # remove the original myvl
    root.removeChildNode(myvl)
    checked_layers = root.checkedLayers()
    print(checked_layers)
    first_file = os.listdir("Output")[0]
    print(first_file)
    layer = QgsProject.instance().mapLayersByName(first_file)[0]
    extent = layer.extent()
    crsSrc = QgsCoordinateReferenceSystem(epsg)    # WGS 84
    crsDest = QgsCoordinateReferenceSystem(3857)  # WGS 84 / UTM zone 33N
    xform = QgsCoordinateTransform(crsSrc, crsDest, QgsProject.instance())
    pt1 = xform.transformBoundingBox(extent)
    QgsMapCanvas.zoomToFeatureExtent(canvas, pt1)

    canvas.freeze(True)
    canvas.show()
    canvas.refresh()
    canvas.freeze(False)
    canvas.repaint()
    #bridge = QgsLayerTreeMapCanvasBridge(
    #    project.layerTreeRoot(),
    #    canvas
    #)


    def run_when_project_saved():
        print('Saved')

    project.projectSaved.connect(run_when_project_saved)

    project.write('my_new_qgis_project.qgz')

    def run_when_application_state_changed(state):
        print('State changed', state)

    app.applicationStateChanged.connect(run_when_application_state_changed)

    exitcode = app.exec()
    QgsApplication.exitQgis()
    sys.exit(exitcode)



