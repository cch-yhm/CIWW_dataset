#!/usr/bin/env python
# coding: utf-8

import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.colors as mcolors
import matplotlib.ticker as mtick
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
#### get_ipython().run_line_magic('matplotlib','inline') 

from pyproj import Geod
from shapely.geometry import Point, LineString, Polygon

shp_path1 = '../shp_china/区划/省.shp'
shp_path2=r'../shp_china/九段线/九段线.shp'
shp_path4=r'../zhoufeng/HK_MC_TW.shp'
shp1=shpreader.Reader(shp_path1)
shp2=shpreader.Reader(shp_path2)
shp4=shpreader.Reader(shp_path4)

#### unit conversion
def transform_mm_and_m3(df,res,range_lat,range_lon):
    """ unit conversion
        res ---- resolution
        range_lat ---- the number of latitude coordinates
        range_lon ---- the number of longitude coordinates
    """
    l= list()
    geod = Geod(ellps="WGS84")
    for i in range(range_lat):
        a = df.iww.lat[i:i+1]+res/2
        for j in range(range_lon):
            b=df.iww.lon[j:j+1]-res/2
            c = geod.geometry_area_perimeter(Polygon([(b, a), (b, a-res),(b+res, a-res), (b+res, a),]))  
            l.append(list(c[:1]))   
    area_pre = np.array(l,dtype=float).flatten()
    area_m2 = area_pre.reshape(range_lat,range_lon)
    
    df['area']=(['lat','lon'], area_m2)
    df.area.attrs = {'long_name' : 'grid_area', 'units' : ' m$^{2}$'}
    
    # from m3 to mm: 用水量（m3）/面积*1000  ##from mm to m3: 用水量（mm）/1000*面积; 
    df_mm = df.iww/df.area*1000
    df['iww_mm']=df_mm
    df.iww_mm.attrs = {'long_name' : 'industrial water withdrawal', 'units' : 'mm'+'/month'}
    return df


#### plot
def plot_figure3():
    ## read the dataset
    data825sec = xr.open_dataset('data/products/figshare/V2302/CHINA_IWW_MAPPING_SUBSECTER_025deg_2008.nc')

    ## transform unit from m3 to mm
    transform_mm_and_m3(data825sec,0.25,145,245)

    ## sum subsectors to sectors
    d_min=data825sec.isel(subsector=[0,1,2,3,4]).sum('subsector')
    d_man=data825sec.isel(subsector=[5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33]).sum('subsector')
    d_ele=data825sec.isel(subsector=[34,35]).sum('subsector')
    d_iww = data825sec.sum('subsector')

    ## convert 0 value to nan
    d_min['iww_mm'].values[d_min['iww_mm'].values==0]=np.nan
    d_man['iww_mm'].values[d_man['iww_mm'].values==0]=np.nan
    d_ele['iww_mm'].values[d_ele['iww_mm'].values==0]=np.nan
    d_iww['iww_mm'].values[d_iww['iww_mm'].values==0]=np.nan

    ## values of sectors 
    mining_ind =d_min['iww_mm'].values
    mining_ind =mining_ind.flatten()
    a = mining_ind[mining_ind> 0]

    manu_ind =d_man['iww_mm'].values
    manu_ind =manu_ind.flatten()
    b = manu_ind[manu_ind> 0]

    ele_ind =d_ele['iww_mm'].values
    ele_ind =ele_ind.flatten()
    c = ele_ind[ele_ind> 0]

    all_ind =d_iww['iww_mm'].values
    all_ind =all_ind.flatten()
    s = all_ind[all_ind> 0]
    array=[s,c,b,a]
    
    ## plot 
    proj = ccrs.LambertConformal(central_longitude=105, central_latitude=35)
    data_proj = ccrs.PlateCarree()
    # set colorbar
    colordict0 = ['mediumblue','royalblue','lightskyblue','#f7c8c5','salmon','r']#'mistyrose',
    cmap2=mcolors.ListedColormap(colordict0)
    cmap2.set_over('#822327')
    array_a =[[0, 0.2, 1, 5, 25, 50, 100],[0, 0.2, 1, 5, 25, 50, 100],
              [0,0.05,0.25, 1, 5, 10, 25],[0,0.05,0.25,1, 5, 10, 25]] 
    
    data =[d_iww['iww_mm'],d_ele['iww_mm'],d_man['iww_mm'],d_min['iww_mm']]
    title=['All sectors','Electricity and gas production and supply','Manufacturing','Mining']
    number_r =['57.85%','37.11%','5.03%']  # three sectors' ratio of national
    label=['a','b','c','d']

    fig = plt.figure(figsize=(28,16))  
    plt.subplots_adjust(wspace=-0.1)

    for i in range(4):
        colorlevel0= array_a[i]
        norm2=mcolors.BoundaryNorm(colorlevel0,cmap2.N)

        ax = fig.add_subplot(2,2,1+i, projection=proj)
        ax.set_extent([75, 136, 14, 53.5])
        p = data[i].plot.pcolormesh(ax=ax,robust=True,cmap=cmap2 ,norm = norm2,transform=data_proj, add_labels=False,add_colorbar=False)

        if i==1 or i==3:
            cb1 = plt.colorbar(p,orientation='vertical',pad=0.025,shrink=0.9,format='%.3g' )
            cb1.ax.tick_params(labelsize=18) 
            cb1.set_label(label='Water withdrawal (mm)',fontsize=22)

        ax.add_geometries(shp1.geometries(),crs=data_proj,facecolor='none',edgecolor='black',lw=0.5,alpha=0.8)
        ax.add_geometries(shp2.geometries(),crs=data_proj,facecolor='none',edgecolor='black',lw=0.5,alpha=0.8)
        ax.add_geometries(shp4.geometries(),crs=data_proj,facecolor='none',hatch='\\\\\\',edgecolor='black',lw=0.5,alpha=0.8)
        ax.text(50,46,'('+label[i]+')',fontsize=30,transform=data_proj)

        if i>0:
            ax.text(64,47,number_r[i-1],fontdict={'size':26,'weight':'medium'},transform=data_proj)
        
        # gridlines
        gl = ax.gridlines(crs=data_proj, linewidth=0.5, color='grey', alpha=0.5, linestyle='--',
                          draw_labels=True,x_inline=False,y_inline=False,xpadding=15)
        gl.top_labels = False
        gl.right_labels = False
        gl.xlocator = mtick.FixedLocator(np.arange(80,125,20))
        gl.ylocator = mtick.FixedLocator(np.arange(20,50,10))
        gl.xformatter = LongitudeFormatter()
        gl.yformatter = LatitudeFormatter()
        gl.xlabel_style ={'rotation':0,'size':18}
        gl.ylabel_style ={'rotation':0,'size':18}

        ax.set_title(title[i],fontdict={'size':30,'weight':'roman'},pad=10)
        
        # inset_axes
        ax1 = ax.inset_axes([0.06,0.06,0.12,0.3],transform=ax.transAxes)
        ax1.boxplot(array[i],meanline=True,showmeans=True,showfliers=False,
                    patch_artist=True,capprops={'linewidth':'1.5'},whiskerprops={'linewidth':'1.5'},
                    medianprops={'color':'tomato','linewidth':'2.5'},
                    meanprops={'color':'#FFAA33','linewidth':'2.5'},##FFAA33
                    boxprops={'color':'royalblue','linewidth':'2','facecolor':'skyblue','alpha':0.6})
        ax1.set_xticklabels('')
        ax1.tick_params(labelsize=15) 
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.spines['bottom'].set_visible(False)
    
    # subgraph
    for j in range(4):
        left=[0.430,0.775,0.430,0.775]
        bottom =[0.54,0.54,0.12,0.12]
        width, height = 0.05, 0.1
        ax11 = fig.add_axes([left[j], bottom[j], width, height], projection=proj)
        ax11.set_extent([105, 125, 0, 25])
        data[j].plot.pcolormesh(ax=ax11,robust=True,cmap=cmap2 ,norm = norm2,transform=data_proj,add_labels=False,add_colorbar=False)# 
        ax11.add_geometries(shp1.geometries(), linewidth=0.6, crs=data_proj,facecolor='none',edgecolor='black',lw=0.5,alpha=0.8)
        ax11.add_geometries(shp2.geometries(),crs=data_proj,facecolor='k',edgecolor='black',lw=0.5,alpha=0.8)
        gl2 = ax11.gridlines(crs=data_proj, linewidth=0.5, color='grey', alpha=0.5, linestyle='--',
                             draw_labels=True,x_inline=False,xpadding=10)
        gl2.bottom_labels = False
        gl2.right_labels = False
        gl2.xlocator = mtick.FixedLocator(np.arange(105,125,10))
        gl2.ylocator = mtick.FixedLocator(np.arange(0,25,10))
        gl2.xformatter = LongitudeFormatter()
        gl2.yformatter = LatitudeFormatter()
        gl2.xlabel_style ={'rotation':0,'size':12}
        gl2.ylabel_style ={'size':12}
    plt.savefig('08pre/Figure_test/industry4_4.jpg',dpi=300, bbox_inches='tight')
    return

if __name__=="__main__":
    plot_figure3() 


