#!/usr/bin/env python
# coding: utf-8

import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.ticker as mtick
import matplotlib as mlp
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
#### get_ipython().run_line_magic('matplotlib', 'inline')

shp_path1 = '../shp_china/区划/省.shp'
shp_path2=r'../shp_china/九段线/九段线.shp'
shp_path4=r'../zhoufeng/HK_MC_TW.shp'
shp1=shpreader.Reader(shp_path1)
shp2=shpreader.Reader(shp_path2)
shp4=shpreader.Reader(shp_path4)


def plot_figure_AppendixB2():
    # read the file 
    data825 = xr.open_dataset('data/products/figshare/V2302/CHINA_IWW_MAPPING_025deg_2008.nc')
    # convert 0 values to nan
    data825['in'].values[data825['in'].values==0]=np.nan

    data_proj = ccrs.PlateCarree()
    proj = ccrs.LambertConformal(central_longitude=105, central_latitude=35)
    cbar_kwargs1 = {'anchor':(0.57,0.0),'orientation': 'horizontal','pad': 0.0005, 'shrink': 0.8,
                    'label': 'Amount','format':'%.0f' }

    fig = plt.figure(figsize=(9,7))#,projection=proj)
    ax = fig.subplots(1, 1, subplot_kw={'projection': proj})

    p = data825['in'].plot.pcolormesh(ax=ax,robust=True,cmap='rocket_r' ,levels=np.array([0,100,200,300,400,500,600]),
                                      transform=data_proj,add_labels=False,cbar_kwargs=cbar_kwargs1)

    ax.add_geometries(shp1.geometries(),crs=data_proj,facecolor='none',edgecolor='black',lw=0.5,alpha=0.9)
    ax.add_geometries(shp2.geometries(),crs=data_proj,facecolor='none',edgecolor='black',lw=0.5,alpha=0.8)
    ax.add_geometries(shp4.geometries(),crs=data_proj,facecolor='none',hatch='\\\\\\',edgecolor='black',lw=0.5,alpha=0.8) ## Taiwan
    ax.set_extent([77, 135, 13, 54])

    #girdlines
    gl = ax.gridlines(crs=data_proj, linewidth=0.5, color='grey', alpha=0.5, linestyle='--',
                      draw_labels=True,x_inline=False,y_inline=False,xpadding=15)
    gl.top_labels = False
    gl.right_labels = False
    gl.xlocator = mtick.FixedLocator(np.arange(80,125,20))
    gl.ylocator = mtick.FixedLocator(np.arange(20,50,10))
    gl.xformatter = LongitudeFormatter()
    gl.yformatter = LatitudeFormatter()
    gl.xlabel_style ={'rotation':0,'size':13}
    gl.ylabel_style ={'rotation':0,'size':13}
    
    ax.text(64,47,'Number of all enterprises: 406 945.',fontdict = {'size':13},transform=data_proj)

    # subgraph
    left, bottom, width, height = 0.75, 0.24, 0.12, 0.165
    ax2 = fig.add_axes([left, bottom, width, height], projection=proj)
    data825['in'].plot.pcolormesh(ax=ax2,robust=True,cmap='rocket_r' ,levels=np.array([0,100,200,300,400,500,600]),
                                  transform=data_proj,add_labels=False,add_colorbar=False)
    ax2.add_geometries(shp1.geometries(),crs=data_proj,facecolor='none',edgecolor='black',lw=0.5,alpha=0.9)
    ax2.add_geometries(shp2.geometries(),crs=data_proj,facecolor='none',edgecolor='black',lw=0.5,alpha=0.8)
    ax2.add_geometries(shp4.geometries(),crs=data_proj,facecolor='none',hatch='\\\\\\',edgecolor='black',lw=0.5,alpha=0.8)# Taiwan

    ax2.set_extent([105, 125, 2, 25])
    gl2 = ax2.gridlines(crs=data_proj, linewidth=0.5, color='grey', alpha=0.5, linestyle='--',draw_labels=True,x_inline=False)
    gl2.bottom_labels = False
    gl2.right_labels = False
    gl2.xlocator = mtick.FixedLocator(np.arange(105,125,10))
    gl2.ylocator = mtick.FixedLocator(np.arange(0,25,10))
    gl2.xformatter = LongitudeFormatter()
    gl2.yformatter = LatitudeFormatter()
    gl2.xlabel_style ={'rotation':0,'size':6}
    gl2.ylabel_style ={'size':6}
    plt.savefig('08pre/Figure_test/Sfig2_number.jpg',dpi=300, bbox_inches='tight')
    return

if __name__=="__main__":
    plot_figure_AppendixB2() 




