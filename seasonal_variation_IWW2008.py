#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import xarray as xr
from pyproj import Geod
from shapely.geometry import Point, LineString, Polygon


# In[3]:


def mapping_water_withdrawal_seasonal(res, range_lat, range_lon, dm_rate, d08):
    """allocate annual industrial water withdrawal in 2008 to month.
       res -- the resolution of netcdf [0.1,0.25];
       range_lat ---- the row of latitude of range  r=0.25,range_lat=145;r=0.1,range_lat=361
       range_lon ---- the row of longitude of range  r=0.25,range_lon=245;r=0.1,range_lat=611
       dm_rate -- the monthly fraction of subsector industrial water withdrawal
                  (monthly fraction for all subsectors_sector filled with)
       d08 -- the spatial industrial water withdrawal in 2008 (two versions for two resolution)
       """
    times = np.array([1,2,3,4,5,6,7,8,9,10,11,12])#time series
    subsector = d08.subsector.values
    dw2008 = xr.DataArray(np.zeros((12,36,range_lat,range_lon)),
                          coords=[times,subsector,d08.lat,d08.lon],
                          dims=["time","subsector","lat","lon"],
                          name='iww', 
                          attrs=dict(FillValue='NaN',
                                     Long_name='industrial water withdrawal',
                                     Units=' m$^{3}$'))


    ## "other mining" and "waste recycling" -----using sectoral monthly IWW fraction
    fn = 'data/products/figshare/V2302/CHINA_IWW_MAPPING_MON_0'+str(int(res*100))+'deg_2008.nc'
    month_rate1 = dm_rate
    for i in range(36):
            w_y = d08.iww[i,:,:].values
            for t in range(12):
                a1 = month_rate1[month_rate1['行业大类代码'].isin([subsector[i]])][str(t)].values
                w_m1 = a1*w_y
                dw2008[t,i,:,:]=w_m1
        
    
    # create dataset 
    d2008_d =  xr.Dataset({'iww':(['month','subsector','lat','lon'],  dw2008.values),
                           'iov':(['subsector','lat','lon'],d08.iov.values),
                           'amount':(['subsector','lat','lon'],d08['in'].values)},
                           coords={'month':times,'subsector':subsector,'lat':d08.lat.data,'lon':d08.lon.data})
    d2008_d.lat.attrs = {'long_name' : 'Latitude', 'units' : 'degrees_north'}
    d2008_d.lon.attrs = {'long_name' : 'Longitude', 'units' : 'degrees_east'}
    d2008_d.month.attrs = {'long_name': 'Month'}
    d2008_d.subsector.attrs = {'Subsector1':'Mining: 6,7,8,10,11',
                               'Subsector2':'Manufacture: 13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,34,35,36,37,39,40,41,42,43',
                               'Subsector3':'Electricity_and_gas_generation: 44,45'}

    d2008_d['iww'].attrs = {'long_name':'industrial water withdrawal','units':'m$^{3}$','FillValue': 'NaN' }
    d2008_d['amount'].attrs = {'long_name':'the number of industrial enterprises','FillValue': 'NaN' }
    d2008_d['iov'].attrs = {'long_name':'industrial output value','units':'10$^{3}$ yuan','FillValue': 'NaN' }

    d2008_d.attrs ={'Title': "China's subsector industrial water withdrawal in 2008 (raw)",
                    'Description': 'Raw data for mapping industrial water withdrawal.The industrial water withdrawal is produced by combining the georeferenced point data of Database of Chinese Industrial Enterprises with provincial water use efficiency data for 2008',
                    'Authors': 'Chengcheng Hou, Yan Li',
                    'Institution': 'Faculty of Geographical Science,Beijing Normal University',
                    'Contact': 'cch@mail.bnu.edu.cn, yanli@bnu.edu.cn',
                    'Reference': "Hou et al., 2023. High-resolution mapping of China industrial water withdrawal from 1965 to 2020 "}
    
    # conversion of units        
    l= list()
    geod = Geod(ellps="WGS84")
    for g_lat in range(range_lat):
        c = d2008_d.iww.lat[g_lat:g_lat+1]+res/2
        for g_lon in range(range_lon):
            b =d2008_d.iww.lon[g_lon:g_lon+1]-res/2
            s = geod.geometry_area_perimeter(Polygon([(b, c), (b, c-res),(b+res, c-res), (b+res, c),]))  
            l.append(list(s[:1]))   
    area_pre = np.array(l,dtype=float).flatten()
    area_m2 = area_pre.reshape(range_lat,range_lon)
    
    
    d2008_d['cell_area']=(['lat','lon'], area_m2)
    d2008_d['cell_area'].attrs = { 'units' : ' m$^{2}$'}

#     # from m3 to mm: 用水量（m3）/面积*1000  ##from mm to m3: 用水量（mm）/1000*面积; 
#     d2008_d_mm = d2008_d.iww/d2008_d.area*1000
#     d2008_d['iww_mm']=d2008_d_mm
#     d2008_d.iww_mm.attrs = {'long_name' : 'industrial water withdrawal', 'units' : 'mm'}

    # save the dataset, encoding for compress the data format
    d2008_d.to_netcdf(fn,
                      encoding={'month':{'dtype':'int8'},'lat':{'dtype': 'float32'},'lon':{'dtype': 'float32'},
                                'subsector':{'dtype': 'int8'},
                                'iww': {'dtype': 'float32', 'scale_factor': res, '_FillValue': -9999},
                                'iov': {'dtype': 'float32', 'scale_factor': res, '_FillValue': -9999},
                                'amount': {'dtype': 'float32', 'scale_factor': res, '_FillValue': -9999},
                                'cell_area': {'dtype': 'float32', 'scale_factor': res, '_FillValue': -9999}} )
    
    return print('ok')


# In[4]:


def run_mapping_water_withdrawal_seasonal(r,range_lat,range_lon,all_mon): 
    res=r
    if res==0.1:
        d08 = xr.open_dataset('data/products/figshare/V2302/CHINA_IWW_MAPPING_SUBSECTER_010deg_2008.nc')
    else:
        d08 =  xr.open_dataset('data/products/figshare/V2302/CHINA_IWW_MAPPING_SUBSECTER_025deg_2008.nc')
        
    month_rate = pd.read_csv('data/process/month_subsector_rate_2006_2010_all_for_seasonal.csv')
    mapping_water_withdrawal_seasonal(res,range_lat,range_lon,month_rate,d08)

    return print('okk')


# In[ ]:


if __name__=="__main__":
####     run_mapping_water_withdrawal_seasonal(0.25,145,245)
####     run_mapping_water_withdrawal_seasonal(0.1,361,611)

