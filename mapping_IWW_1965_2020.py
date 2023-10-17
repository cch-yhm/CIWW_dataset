#!/usr/bin/env python
# coding: utf-8


import pandas as pd
import numpy as np
import xarray as xr
from pyproj import Geod
from shapely.geometry import Point, LineString, Polygon


def mapping_data_IWW_interannual_month(d_pro,d_rate,dm_lt,r,range_lat,range_lon,transform):
    """calculate monthly industrial water withdrawal of China from 1965 to 2020:
    d_pro --- province_id2.nc,
    d_rate --- sum_water_withdrawal_rate_grid.nc ,
    dm_lt ---- industrial_water_withdrawal_mon1965_2020.csv
    range_lat ---- the row of latitude of range  r=0.25,range_lat=145;r=0.1,range_lat=361
    range_lon ---- the row of longitude of range  r=0.25,range_lon=245;r=0.1,range_lat=611
    transform ---- whether or not transform the metric m2 to mm"""
    res=r
    pro_id = d_pro['ProID'].values
    pro_list = np.unique(pro_id[~np.isnan(pro_id)])#get the province ID

    times=pd.date_range(start='1/1/1965', periods=672, freq='MS')#time series
    year_list =list(dm_lt.columns[5:])
    #provincial monthly industrial water withdrawal 1965-2020
    wb = xr.DataArray(np.zeros((672,range_lat,range_lon)),#025--145，245#010--361,611
                      coords=[times,d_pro.lat,d_pro.lon],
                      dims=["time","lat","lon"],
                      name='ww', 
                      attrs=dict(long_name='industrial water withdrawal bulletin',
                                 units='100 million cubic meters (100,000,000 m³)',
                                 description = 'ProfZhoufeng1965_2002&bulletin_data2003_2020'))

    for i in range(56):
        yr= year_list[i]
        for mon in range(12):
            for j in range(34):##the number of citys/provinces
                if j == 0:
                    c = np.where(pro_id == pro_list[j],
                                 dm_lt[dm_lt['ID'].isin([pro_list[j]])].iloc[mon].at[yr],pro_id)
                elif j<31:
                    c = np.where(c == pro_list[j],dm_lt[dm_lt['ID'].isin([pro_list[j]])].iloc[mon].at[yr],c)

                else:
                    c = np.where(c == pro_list[j],np.NaN,c)

            wb[i*12+mon,:,:]=c
    # # attributes settings
    # wb.lat.attrs = {'long_name' : 'Latitude', 'units' : 'degrees_north'}
    # wb.lon.attrs = {'long_name' : 'Longitude', 'units' : 'degrees_east'}
    # wb.time.attrs = {'long_name': 'Times'}  #NO SETTING units---or can't conserve

    # d_owb = wb.to_dataset()
    # d_owb.attrs ={'long name':'provincial monthly industrial water withdrawal from 1965 to 2020','Fillna':'nan'}
    # #save the dataset
    # d_owb.to_netcdf('data/process/CHINA_IWW_MON_PRO_010deg_1965_2020.nc')
    
    #Monthly industrial water withdrawal of China from 1965 to 2020
    water = xr.DataArray(np.zeros((672,range_lat,range_lon)),#025--145，245 #010--361,611
                         coords=[times,d_pro.lat,d_pro.lon],
                         dims=["time","lat","lon"],
                         name='iww1',
                         attrs=dict(long_name = 'industrial water withdrawal',
                                    units = 'm$^{3}$',
                                    FillValue = 'NaN' ))
                                    #description = 'grid_1965_2020'))
    for t in range(672):
        water_t = wb.isel(time = t)*100000000*d_rate #unit:10000 m³
        water[t,:,:] = water_t.rate#010:water_t.rate08，025:water_t.rate

    # attributes settings                           
    water.lat.attrs = {'long_name' : 'Latitude', 'units' : 'degrees_north'}
    water.lon.attrs = {'long_name' : 'Longitude', 'units' : 'degrees_east'}
    water.time.attrs = {'long_name': 'Times'}

    # global attributes settings
    d_water = water.to_dataset()
    d_water.attrs ={'Title': "China's total industrial water withdrawal 1965-2020 (adjusted)",
                    'Description': 'Adjusted industrial water withdrawal by the provincial statistics of total industrial water use from the water resources bulletin for 2003-2020 and Zhou (2020) for 1965 to 2002',
                    'Authors': 'Chengcheng Hou, Yan Li',
                    'Institution': 'Faculty of Geographical Science,Beijing Normal University',
                    'Contact': 'cch@mail.bnu.edu.cn, yanli@bnu.edu.cn',
                    'Reference': "Hou et al., 2023. High-resolution mapping of China industrial water withdrawal from 1965 to 2020 "}

    # conversion of units        
    if transform:            
        l= list()
        geod = Geod(ellps="WGS84")
        for g_lat in range(range_lat):
            a = d_water.iww1.lat[g_lat:g_lat+1]+res/2
            for g_lon in range(range_lon):
                b =d_water.iww1.lon[g_lon:g_lon+1]-res/2
                s = geod.geometry_area_perimeter(Polygon([(b, a), (b, a-res),(b+res, a-res), (b+res, a),]))  
                l.append(list(s[:1]))   
        area_pre = np.array(l,dtype=float).flatten()
        area_m2 = area_pre.reshape(range_lat,range_lon)

        d_water['cell_area']=(['lat','lon'], area_m2)
        d_water.cell_area.attrs = { 'units' : ' m$^{2}$'}

        # from m3 to mm: IWW（m3）/area(m2)*1000  ##from mm to m3: IWW（mm）/1000*area(m2); 
        d_water_mm = d_water.iww1/d_water.cell_area*1000
        d_water['iww']=d_water_mm
        d_water.iww.attrs = {'long_name' : 'industrial water withdrawal', 'units' : 'mm','FillValue': 'NaN' }
        
        d_water1 = d_water[['iww','cell_area']]
        # save the dataset, encoding for compress the data format
        d_water1.to_netcdf('../工业工厂位置数据/data/products/figshare/V2302/CHINA_IWW_MON_0'+str(int(res*100))+'deg_1965_2020.nc',
                          encoding={'lat':{'dtype': 'float32'},'lon':{'dtype': 'float32'},
                                    'cell_area': {'dtype': 'float32', 'scale_factor': res, '_FillValue': -9999},
                                    'iww': {'dtype': 'float32', 'scale_factor': res, '_FillValue': -9999}}
                         )
        
    else:
        # save the dataset,encoding for compress the data format
        d_water.to_netcdf('../工业工厂位置数据/data/products/figshare/V2302/CHINA_IWW_MON_0'+str(int(res*100))+'deg_NOmm_1965_2020.nc',
                          encoding={'lat':{'dtype': 'float32'},'lon':{'dtype': 'float32'},
                                    'iww': {'dtype': 'float32', 'scale_factor': res, '_FillValue': -9999}}
                         )
          
    return print('ok')


def run_IWW_interannual_month(r,range_lat,range_lon,transform): 
    res=r
    if res==0.1:
        dm_lt = pd.read_csv('data/industrial_water_withdrawal_mon1965_2020V2.csv')#010
        dp_re = xr.open_dataset('../工业工厂年际变化/province_id2.nc')#010
        d_rate = xr.open_dataset('data/process/water_withdrawal_rate_grid_010_230223.nc')#010
    else:
        dm_lt = pd.read_csv('data/industrial_water_withdrawal_mon1965_2020V2.csv')#025
        dp_re = xr.open_dataset('../工业工厂年际变化/province_id2_025u.nc')#025
        d_rate = xr.open_dataset('data/process/water_withdrawal_rate_grid_025_230223.nc')#025
    
    if transform:
        mapping_data_IWW_interannual_month(dp_re,d_rate,dm_lt,r,range_lat,range_lon,transform=True)
    else:
        mapping_data_IWW_interannual_month(dp_re,d_rate,dm_lt,r,range_lat,range_lon,transform=False)
    return print('okk')


if __name__=="__main__":
####     run_IWW_interannual_month(0.1,361,611,transform=True)
####    run_IWW_interannual_month(0.25,145,245,transform=True)

