"""DamageScanner - a directe damage assessment toolkit

Plot results of DamageScanner
"""
import os
import numpy
import rasterio
import pandas
import geopandas
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Patch
import matplotlib.pyplot as plt
from rasterio.plot import show

def landuse_vector(landuse,color_dict={},save=False,**kwargs):
    """
    Arguments:
        *landuse_map* : Shapefile, Pandas DataFrame or Geopandas GeoDataFrame 
        with land-use information of the area.

    Optional Arguments:
        *color_dict* : Supply a dictionary with the land-use classes as keys 
        and color hex codes as values. If empty, it will use a default list (based on OSM attributes)
        
        *save* : Set to True if you would like to save the output. Requires 
        several **kwargs**
        
    kwargs:
        *output_path* : Specify where files should be saved.
        
        *scenario_name*: Give a unique name for the files that are going to be saved.
    """
    # load land-use map
    if isinstance(landuse,str):
        landuse = geopandas.read_file(landuse)
    elif isinstance(landuse, geopandas.GeoDataFrame):
        landuse = landuse.copy()
    elif isinstance(landuse, pandas.DataFrame):
        landuse = geopandas.GeoDataFrame(landuse,geometry='geometry')
    else:
        print('ERROR: landuse should either be a shapefile, a GeoDataFrame or a pandas Dataframe with a geometry column')
    
    if len(color_dict) == 0:
        color_dict = {  "grass":'#c3eead',
                        "forest":'#1c7426',
                        "orchard":'#fe6729',
                        "residential":'#f13013',
                        "industrial":'#0f045c',
                        "retail":'#b71456',
                        "farmland":'#fcfcb9',
                        "cemetery":'#c39797',
                        "construction":'#c0c0c0',
                        "meadow":'#c3eead',
                        "farmyard":'#fcfcb9',
                        "scrub":'#98574d',
                        "allotments":'#fbffe2',
                        "reservoir":'#8af4f2',
                        "static_caravan":'#ff3a55',
                        "commercial":'#27142c'}
                    
    map_dict = dict(zip(color_dict.keys(),[x for x in range(len(color_dict))]))

    landuse['int_landuse'] = landuse.landuse.apply(lambda x: map_dict[x])

    fig, ax = plt.subplots(1, 1,figsize=(12,10))
    color_scheme_map = list(color_dict.values())

    cmap = LinearSegmentedColormap.from_list(name='landuse',
                                         colors=color_scheme_map)  


    landuse.plot(column='int_landuse',ax=ax,linewidth=0,cmap=cmap)

    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_axis_off()
    legend_elements = []
    for iter_,item in enumerate(color_dict):
        legend_elements.append(Patch(facecolor=color_scheme_map[iter_],label=item))        

    ax.legend(handles=legend_elements,edgecolor='black',facecolor='#fefdfd',prop={'size':12},loc=(1.02,0.2)) 

    if save:
        if 'output_path' in kwargs:
            output_path = kwargs['output_path']
            if not os.path.exists(output_path):
                os.mkdir(output_path)
        if 'scenario_name' in kwargs:
            scenario_name = kwargs['scenario_name']
        fig.tight_layout()
        fig.savefig('Landuse_{}.png'.format(scenario_name),dpi=350, bbox_inches='tight')
 
    return ax

def landuse_raster(landuse,color_dict={},save=False,**kwargs):
    """
    Arguments:
        *landuse_map* : GeoTiff with land-use information per grid cell. 

    Optional Arguments:
        *color_dict* : Supply a dictionary with the land-use classes as keys 
        and color hex codes as values. If empty, it will use a default list (which will probably fail)
        
        *save* : Set to True if you would like to save the output. Requires 
        several **kwargs**
        
    kwargs:
        *output_path* : Specify where files should be saved.
        
        *scenario_name*: Give a unique name for the files that are going to be saved.
    """
      

    return ax

def inundation_map(inun_map,lu_raster=False,lu_vector=False,save=False,**kwargs):
    """
    Arguments:
        *inun_map* : GeoTiff with inundation depth per grid cell.

    Optional Arguments:
        *lu_raster* : Set to **True** if you would like to use the landuse raster 
        as background.
            
        *lu_vector* : Set to **True** if you would like to use the landuse raster 
        as background.
        
        *save* : Set to **True** if you would like to save the output. Requires 
        several **kwargs**
        
    kwargs:
        *landuse_map* : Path to land-use map.
        
        *output_path* : Specify where files should be saved.
        
        *scenario_name*: Give a unique name for the files that are going to be saved.
        
    """    
    if (lu_raster == False) & (lu_vector == False):
        fig, ax = plt.subplots(1, 1,figsize=(12,10))

        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_axis_off()
        
    elif (lu_raster == False) & (lu_vector == True):
        landuse = kwargs['landuse_map']
        ax = landuse_vector(landuse)

    elif (lu_raster == True) & (lu_vector == False):
        landuse = kwargs['landuse_map']
        ax = landuse_raster(landuse)
        
    with rasterio.open(inun_map) as src:
        inundation = numpy.array(src.read()[0,:,:],dtype=float)
        inundation[inundation == 0] = numpy.nan

        max_value = 6
        show(inundation,ax=ax,cmap='Blues',transform=src.transform,zorder=2,vmax=max_value)

    if save:
        if 'output_path' in kwargs:
            output_path = kwargs['output_path']
            if not os.path.exists(output_path):
                os.mkdir(output_path)
        if 'scenario_name' in kwargs:
            scenario_name = kwargs['scenario_name']

        fig.tight_layout()
        fig.savefig('inundation_{}.png'.format(scenario_name),dpi=350, bbox_inches='tight')

     
def damagemap_vector(losses,bins=[],save=False,**kwargs):
    """
    Arguments:
        *losses* : Shapefile, Pandas DataFrame or Geopandas GeoDataFrame 
        with land-use information of the area.

    Optional Arguments:
        *bins* : Supply list of bin values for the colorscheme. If empty, it will use a default list.
        
        *save* : Set to True if you would like to save the output. Requires 
        several **kwargs**.
        
    kwargs:
        *output_path* : Specify where files should be saved.
        
        *scenario_name*: Give a unique name for the files that are going to be saved.
    """

    fig, ax = plt.subplots(1, 1,figsize=(12,10))
    color_scheme_map =  ['white','#fee5d9','#fcae91','#fb6a4a','#de2d26','#a50f15']

    cmap = LinearSegmentedColormap.from_list(name='damages',
                                         colors=color_scheme_map)  
    labels = [0,1,2,3,4]
    if len(bins) == 0:
        bins = [0,10000,100000,500000,1e6,losses.tot_dam.max()]

    losses['binned'] = pandas.cut(losses['tot_dam'], bins=bins, labels=labels)
    losses['binned'] = losses['binned'].fillna(0)

    losses.plot(column='binned',ax=ax,linewidth=0.1,cmap=cmap,edgecolor='black')

    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_axis_off()
    legend_elements = []
    for iter_,item in enumerate(bins):
        if iter_ < len(bins)-1:
            legend_elements.append(Patch(facecolor=color_scheme_map[iter_],label='{}-{} Euro'.format(int(bins[iter_]),int(bins[iter_+1]))))        
        else:
            legend_elements.append(Patch(facecolor=color_scheme_map[iter_],label='> {} Euro'.format(int(bins[iter_]))))        

    ax.legend(handles=legend_elements,edgecolor='black',facecolor='#fefdfd',prop={'size':12},loc=(1,0.4)) 

    if save:
        if 'output_path' in kwargs:
            output_path = kwargs['output_path']
            if not os.path.exists(output_path):
                os.mkdir(output_path)
        if 'scenario_name' in kwargs:
            scenario_name = kwargs['scenario_name']

        fig.tight_layout()
        fig.savefig('Damagemap_{}.png'.format(scenario_name),dpi=350, bbox_inches='tight')