# ---
# jupyter:
#   jupytext:
#     formats: ipynb,pct.py:percent,lgt.py:light,spx.py:sphinx,md,Rmd
#     text_representation:
#       extension: .pct.py
#       format_name: percent
#       format_version: '1.1'
#       jupytext_version: 0.8.0
#   kernelspec:
#     display_name: Python 2
#     language: python
#     name: python2
#   language_info:
#     codemirror_mode:
#       name: ipython
#       version: 3
#     file_extension: .py
#     mimetype: text/x-python
#     name: python
#     nbconvert_exporter: python
#     pygments_lexer: ipython3
#     version: 3.6.6
# ---

# %% [markdown]
# # MapScript Quick Start
# 
# Welcome to the Python MapScript quick start guide. 
# MapScript provides a programming interface to MapServer, and this notebook
# provides an overview of its key functionality. 
#
# ## Mapfiles
# The simplest way to use MapScript is to work with an existing [Mapfile](https://mapserver.org/mapfile/). 
# A new ```mapObj``` can be created by passing the path to a Mapfile. We will 
# be working with the Itasca demo map that is also used in the 
# [MapServer Demo](http://localhost/mapserver_demos/itasca/) on OSGeoLive. 

# %%
import sys
sys.path.append("/rofs/usr/lib/python2.7/dist-packages") # temporary hack for OSGeoLive

import os
import mapscript
from IPython.display import Image

demo_fld = os.getenv("MAPSERVER_DEMO")
mapfile = os.path.join(demo_fld, "itasca.map")

map = mapscript.mapObj(mapfile)

# %% [markdown]
# Anything found in the Mapfile can be accessed and manipulated using MapScript. 
# For example we can get the count of all the layers in the Mapfile, and loop
# through them printing out each layers name. 
# 
# MapScript objects are typically accessed using an index. 

# %%
for idx in range(0, map.numlayers):
    lyr = map.getLayer(idx)
    print(lyr.name)

# %% [markdown]
# ## Drawing Maps
# MapScript can be used to create an image file. The draw method
# returns an imageObj which can be saved to a filename on disk. 

# %%
import tempfile
# before creating images let's set the working directory to the temp folder
os.chdir(tempfile.gettempdir()) 

output_file = "map.png"
image = map.draw()
image.save(output_file)
Image(filename=output_file)

# %% [markdown]
# The map image above doesn't contain all the layers in the Mapfile. 
# This can be because they are set to hidden by default using ```LAYER STATUS OFF```.
# 
# To turn on these layers and create a more interesting map, we 
# can loop through the layers again and set their ```STATUS``` to ```ON```. 
# We can then use the ```isVisible``` method to check if the layer will
# be drawn onto the map. 

# %%
for idx in range(0, map.numlayers):
    lyr = map.getLayer(idx)
    lyr.status = mapscript.MS_ON
    print(lyr.name, lyr.isVisible())

# %% [markdown]
# You may notice that the *ctybdpy2* layer is still not visible even though
# we set its ```STATUS``` to ```ON```. This is due to the ```REQUIRES``` keyword in its layer 
# definition that hides the layer if the *drgs* layer is displayed. 
# The *ctyrdln3* and *ctyrdln3_anno* layers are both hidden because of the ```MAXSCALE 300000```
# layer setting. 

# Now we can now draw the map again with the newly visible layers. 

# %%
output_file = "map_full.png"
image = map.draw()
image.save(output_file)
Image(filename=output_file)

# %% [markdown]
# Other types of images can also be created from the ```mapObj```. These
# use the same process of creating an ```imageObj``` and saving it to disk. 
#
# For example to create a legend image:

# %%
output_file = "map_legend.png"
legend_img = map.drawLegend()
legend_img.save(output_file)
Image(filename=output_file)

# %% [markdown]
# ## Querying Maps
# As well as drawing maps using MapScript we can also query the data
# referenced by the layers. In this example we will be finding the
# layer to query using its name, and then querying the ```NAME``` field to find
# the name of an airport. 

# %%
qry_layer = map.getLayerByName('airports')
qry_layer.queryByAttributes(qry_layer.map, "NAME", "Bowstring Municipal Airport", 
                            mapscript.MS_SINGLE)

results = qry_layer.getResults()
assert results.numresults == 1 # as we did a single query (using MS_SINGLE) there should be only one result
result = results.getResult(0)
Image(filename=output_file)

# %% [markdown]
# Query results are stored as ```resultCacheObj```. These contain a reference to the
# result feature - a ```shapeObj```. The ```shapeObj``` can access both the geometry and 
# attributes of a feature. 
# 
# Let's get the ```shapeObj``` from the ```resultCacheObj``` and 
# loop through the shapes attributes to store them in a list. 

# %%
result_shp = qry_layer.getShape(result)

values = []
for idx in range(0, result_shp.numvalues):
    values.append(result_shp.getValue(idx))

print(values)

# %% [markdown]
# It would be nice to have also the property names alongside the values. Field names
# are stored in the layer in which the ```shapeObj``` belongs, and not in the ```shapeObj```
# itself. We can get a list of fields from the layer, and then use the Python ```zip``` function
# to join them with the shape values: 

# %%
fields = []
for idx in range(0, qry_layer.numitems):
    fields.append(qry_layer.getItem(idx))

print(fields)
props = zip(fields, values)  # join fields to values
print(props)

# %% [markdown]
# We can also create a map showing the query results: 
# *Note the imageObj is broken for Python MapScript 7.0, but is fixed in 7.2*

# %%
# create a new 400 by 400 empty image
query_image = mapscript.imageObj(400, 400)
# draw the query into the image and save it to file
qry_layer.drawQuery(qry_layer.map, query_image)
output_file = r"layer_query.png"
query_image.save(output_file)
Image(filename=output_file)

# %% [markdown]
# If we want to zoom in on the results we can set the map extent to a buffered area
# around the results: 

# %%
bbox = result_shp.bounds
print(bbox.minx, bbox.miny, bbox.maxx, bbox.maxy)
buffer = 2000

map.getLayerByName('drgs').status = mapscript.MS_OFF # hide the raster layer for this map
map.setExtent(bbox.minx - buffer, bbox.miny - buffer, bbox.maxx + buffer, bbox.maxy + buffer)

output_file = r"map_query.png"
image = map.draw()
image.save(output_file)
Image(filename=output_file)

# %% [markdown]
# ## OGC Web Services
#
# MapScript can also be used to send requests to MapServer OWS capabilities, to 
# query WMS and WFS services. First we will get the WMS GetCapabilities XML for the map: 

# %%
ows_req = mapscript.OWSRequest()
ows_req.type = mapscript.MS_GET_REQUEST
ows_req.setParameter("SERVICE", "WMS");
ows_req.setParameter("VERSION", "1.3.0");
ows_req.setParameter("REQUEST", "GetCapabilities");

# %% [markdown]
# We use the msIO methods to capture the response the request
# that is sent to ```stdout```. 
# The response is typically an HTTP response with HTTP content headers. 
# We can strip these out using MapScript

# %%
mapscript.msIO_installStdoutToBuffer()
map.OWSDispatch(ows_req)
content_type = mapscript.msIO_stripStdoutBufferContentType()
# remove the content type header from the XML
mapscript.msIO_stripStdoutBufferContentHeaders() # Strip all Content-* headers
result = mapscript.msIO_getStdoutBufferBytes()
print(result)

# %% [markdown]
# We can also retrieve images from a WMS service. 
# Rather than setting lots of individual parameters we can simply load them from
# a string in the same format was would be sent via a web client. 

# %%
# First let's get the extent of the map to use in the request
extent = map.extent
print(extent)

bbox = "BBOX={},{},{},{}".format(extent.minx, extent.miny, extent.maxx, extent.maxy)
querystring = "SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0&LAYERS=lakespy2&CRS=EPSG:26915&FORMAT=image/png&WIDTH=400&HEIGHT=400&{}".format(bbox)

ows_req = mapscript.OWSRequest()
ows_req.loadParamsFromURL(querystring)
success = map.OWSDispatch(ows_req)
assert success == mapscript.MS_SUCCESS

# clear the HTTP headers or we will have an invalid image
headers = mapscript.msIO_getAndStripStdoutBufferMimeHeaders()
result = mapscript.msIO_getStdoutBufferBytes()

output_file = "wms.png"
with open(output_file, "wb") as f:
    f.write(result)

Image(filename=output_file)

# %% [markdown]
# Finally let's get the SLD for one of the layers in the map: 

# %%
lakes_layer = map.getLayerByName('lakespy2')
result = lakes_layer.generateSLD()
print(result)


# %% [markdown]
# Thanks for working through this notebook! For more information on MapScript
# please see the [MapScript documentation](https://mapserver.org/mapscript/introduction.html). 
# Additional Python examples can be found in the [MapServer GitHub repository](https://github.com/mapserver/mapserver/tree/master/mapscript/python/examples)
