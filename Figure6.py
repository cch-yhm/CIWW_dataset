#!/usr/bin/env python
# coding: utf-8

import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from pyproj import Geod
from shapely.geometry import Point, LineString, Polygon
#### get_ipython().run_line_magic('matplotlib', 'inline')

shp_path1 = '../shp_china/区划/省.shp'
shp_path4=r'../zhoufeng/HK_MC_TW.shp'
shp_path5=r'../shp_china/区划/市.shp'
shp_path6=r'../shp_china/区划/县.shp'
shp1=shpreader.Reader(shp_path1)
shp4=shpreader.Reader(shp_path4)
shp5=shpreader.Reader(shp_path5)
shp6=shpreader.Reader(shp_path6)

def plot_figure6():
    df6 = xr.open_dataset('工业企业数据2008/industrial_water_withdrawal_sector_res0.01.nc')
    # calculate each grid area 
    l_at= list()
    geod = Geod(ellps="WGS84")
    for i in range(3601):
        a = df6.lat[i:i+1]+0.005
        for j in range(1):
            b=df6.lon[j:j+1]-0.005
            c = geod.geometry_area_perimeter(Polygon([(b, a), (b, a-0.01),(b+0.01, a-0.01), (b+0.01, a),]))  
            l_at.append(list(c[:1]))       

    area_pre_1 = np.array(l_at,dtype=float).flatten()
    # print(area_pre_1,np.shape(area_pre_1))
    area_pre_2 = area_pre_1.reshape(3601,1)
    area_pre =np.tile(area_pre_2, (1,6101 ))
    df6['area']=(['lat','lon'], area_pre) 

    # sum subsector to sector
    df6_manu = df6.isel(sector=slice(5, 34)).sum('sector')  
    df6_ele = df6.isel(sector=slice(34, None)).sum('sector') 

    # transfrom m3 to mm
    df6_manu_mm = df6_manu['water withdrawal']/df6_manu.area*1000 ## m^3/m^2*1000 = mm
    df6_ele_mm = df6_ele['water withdrawal']/df6_ele.area*1000
    # convert 0 values to nan
    df6_ele_mm.values[df6_ele_mm.values==0]=np.nan
    df6_manu_mm.values[df6_manu_mm.values==0]=np.nan

    ## select the range of regions
    ## Pearl River Delta
    d_g01_manu_mm =df6_manu_mm.sel(lat=slice(24,21.8),lon=slice(112.4,114.8))
    d_g01_ele_mm =df6_ele_mm.sel(lat=slice(24,21.8),lon=slice(112.4,114.8))
    ## Beijing-Tianjin-Hebei Region
    d_b01_manu_mm =df6_manu_mm.sel(lat=slice(41.1,38.9),lon=slice(115.7,118.1)) 
    d_b01_ele_mm =df6_ele_mm.sel(lat=slice(41.1,38.9),lon=slice(115.7,118.1)) 
    ## Yangtze River Delta
    d_h01_maun_mm =df6_manu_mm.sel(lat=slice(32.1,29.9),lon=slice(119.7,122.1))  
    d_h01_ele_mm =df6_ele_mm.sel(lat=slice(32.1,29.9),lon=slice(119.7,122.1))

    ## plot 
    proj = ccrs.LambertConformal(central_longitude=105, central_latitude=35)
    data_proj = ccrs.PlateCarree()
    data_c = [d_b01_manu_mm,d_h01_maun_mm,d_g01_manu_mm,d_b01_ele_mm,d_h01_ele_mm,d_g01_ele_mm]
    level_h = [150,150,150,200,200,200]
    xlabel = [116,118.1,120,122.1,113,115]
    ylabel = [39,41.1,30,32.1,22,24.1]
    rate = ['58%','34%','76%','36%','66%','24%']
    label = ['(a)','(b)','(c)','(d)','(e)','(f)']

    lat_formatter = LatitudeFormatter()
    lon_formatter = LongitudeFormatter(zero_direction_label=True)

    proj = ccrs.PlateCarree() 
    fig = plt.figure(figsize=(15,9.5))  #创建页面
    plt.tight_layout()

    rate_xl = [115.85,121.75,114.37]
    rate_yl = [40.95,31.95,23.85]

    ## Panel abc ###
    for i in range(3):
        ax =fig.add_subplot(2,3,i+1,projection=proj)
        p = data_c[i].plot.pcolormesh(ax=ax,robust=True,transform=proj,cmap='rainbow',
                                      levels=np.linspace(0,level_h[i],7),add_labels=False,add_colorbar=False)
        ax.add_geometries(shp1.geometries(),crs=proj,facecolor='none',edgecolor='black',lw=0.5)
        ax.add_geometries(shp6.geometries(),crs=proj,facecolor='none',edgecolor='black',lw=0.3,alpha=0.75)
        ax.add_geometries(shp5.geometries(),crs=proj,facecolor='none',edgecolor='black',lw=0.2,alpha=0.75)
        ax.set_xticks(np.arange(xlabel[i*2],xlabel[i*2+1],1),crs=ccrs.PlateCarree())
        ax.set_yticks(np.arange(ylabel[i*2],ylabel[i*2+1],1),crs=ccrs.PlateCarree())
        ax.tick_params(labelsize=12.5)
        ax.yaxis.set_major_formatter(lat_formatter)
        ax.xaxis.set_major_formatter(lon_formatter)
        ax.text(rate_xl[i],rate_yl[i],rate[i],fontsize=14.5,weight='roman',color = 'crimson')
        if i==0:
            ax.set_title('Beijing-Tianjin-Hebei Region',fontsize=16,pad=35)
            ax.text(115.25,41.25,'Manufacturing',fontsize=14.5)
            ax.text(rate_xl[i]-0.58,rate_yl[i]+0.18,label[i],fontsize=15)      
        elif i==1:
            ax.set_title('Yangtze River Delta',fontsize=16,pad=35)
            ax.text(rate_xl[i]-2.5,rate_yl[i]+0.20,label[i],fontsize=15)
        elif i==2:
            ax.set_title('Pearl River Delta',fontsize=16,pad=35)
            ax.text(rate_xl[i]-2.4,rate_yl[i]+0.22,label[i],fontsize=15)
            ax.add_geometries(shp4.geometries(),crs=data_proj,facecolor='none',hatch='\\\\\\',edgecolor='grey',lw=0.5)

    ## Panel def ###
    for j in range(3):
        ax =fig.add_subplot(2,3,j+4,projection=proj)
        f = data_c[j+3].plot.pcolormesh(ax=ax,robust=True,transform=proj,cmap='rainbow',
                                        levels=np.linspace(0,level_h[j+3],7),add_labels=False,add_colorbar=False)
        ax.add_geometries(shp1.geometries(),crs=proj,facecolor='none',edgecolor='k',lw=0.5,alpha=0.85)
        ax.add_geometries(shp6.geometries(),crs=proj,facecolor='none',edgecolor='black',lw=0.3,alpha=0.75)
        ax.add_geometries(shp5.geometries(),crs=proj,facecolor='none',edgecolor='black',lw=0.2,alpha=0.75)
        ax.set_xticks(np.arange(xlabel[j*2],xlabel[j*2+1],1),crs=ccrs.PlateCarree())
        ax.set_yticks(np.arange(ylabel[j*2],ylabel[j*2+1],1),crs=ccrs.PlateCarree())
        ax.tick_params(labelsize=12.5)
        ax.yaxis.set_major_formatter(lat_formatter)
        ax.xaxis.set_major_formatter(lon_formatter)
        ax.text(rate_xl[j],rate_yl[j],rate[j+3],fontsize=13,weight='roman',color = 'crimson')
        if j==0:
            ax.text(115.25,41.33,'Electricity and gas production and supply',fontsize=14.5)
            ax.text(rate_xl[j]-0.6,rate_yl[j]+0.20,label[j+3],fontsize=15)
        elif j==1:
            ax.text(rate_xl[j]-2.5,rate_yl[j]+0.20,label[j+3],fontsize=15)
        else:
            ax.text(rate_xl[j]-2.4,rate_yl[j]+0.23,label[j+3],fontsize=15)
            ax.add_geometries(shp4.geometries(),crs=data_proj,facecolor='none',hatch='\\\\\\',edgecolor='grey',lw=0.5)

    cbar_ax3 = fig.add_axes([0.92,0.55, 0.014, 0.3])
    cb3= fig.colorbar(p,cax=cbar_ax3, orientation='vertical',extend='max',format='%.0f')
    cb3.ax.tick_params(labelsize=14) 
    cb3.set_label(label='Water withdrawal(mm)',fontsize=14)

    cbar_ax6 = fig.add_axes([0.92,0.13, 0.014, 0.3])
    cb6= fig.colorbar(f,cax=cbar_ax6, orientation='vertical',extend='max',format='%.f')
    cb6.ax.tick_params(labelsize=14) 
    cb6.set_label(label='Water withdrawal(mm)',fontsize=14)
    plt.savefig('08pre/Figure_test/high_analysis5.jpg',dpi=500, bbox_inches='tight')    
    return

if __name__=="__main__":
    plot_figure6() 



