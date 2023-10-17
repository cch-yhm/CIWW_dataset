#!/usr/bin/env python
# coding: utf-8


import pandas as pd
import numpy as np
from affine import Affine
import xarray as xr


def mapping_spatial_IWW2008(d,dp, r, subsector, save_netcdf):
    """transfer water withdrawal(table) to netcdf.
       r -- the resolution of netcdf [0.01,0.05,0.1,0.25,0.5];
       dp -- province_id2.nc---mask [0.1,0.25]
       subsector -- weather or not get the subsector water withdrawal [True or False]
       save_netcdf -- weather or not save the format [True or False]
       """
    # read the file d -- the industry water withdrawal(table);
    # d=pd.read_csv('data/China_industry_water_withdrawal.csv')
    # dp =xr.open_dataset('../工业工厂年际变化/province_id2.nc')
    df = d
    print('Combined data loaded')
    # Affine transformation, global scale
    res = r # degree
    a = Affine(res,0,-180,0,-res,90)
    
    # get col and row number at the global scale
    df['col_g'], df['row_g'] = ~a * (df['longitude'], df['latitude'])
    
    # China range: lon 74: 135; lat 18: 54 # detemined based on max() min()
    lat_max=np.ceil(df.latitude.max())  #np.ceil   1.3→2，4.1→5，-1.2→-1
    lat_min=np.floor(df.latitude.min())  #np.floor  1.3→1，4.1→4，-1.2→-2
    lon_min=np.floor(df.longitude.min())
    lon_max=np.ceil(df.longitude.max())   
    ll = ~a * (np.floor(df.longitude.min()), np.floor(df.latitude.min())) # lower left pixel
    rr = ~a * (np.ceil(df.longitude.max()), np.ceil(df.latitude.max())) # upper right pixel
    print('China range defined as lat: %d to %d, and lon: %d to %d'%(lat_min, lat_max,lon_min, lon_max))
    
    # Get China range in cols and rows
    col_n = rr[0]-ll[0]+1
    row_n = ll[1]-rr[1]+1
    
    # Get regonal col/row within the China range
    df['row_r']=df['row_g']-rr[1]
    df['col_r']=df['col_g']-ll[0]

    # convert to int type 
    df['col_r'] = df['col_r'].apply(np.floor).astype(int)
    df['row_r'] = df['row_r'].apply(np.floor).astype(int)
    
    if subsector: 
        # The first sector classification should be enough
        subsector_list = np.sort(df['行业大类代码'].unique())     # '行业门类代码'just 'C/D/E'，‘行业大类代码'-sector :36
        # create a var to save mapping results in China for industiral value of different sectors
        map_value=np.zeros([subsector_list.shape[0],int(row_n),int(col_n)])  
        map_count=np.zeros([subsector_list.shape[0],int(row_n),int(col_n)])
        map_water=np.zeros([subsector_list.shape[0],int(row_n),int(col_n)]) 
        # aggregate values to pixel
        row_col_value = df.groupby(['row_r','col_r','行业大类代码']).sum().reset_index()
        row_col_count = df.groupby(['row_r','col_r','行业大类代码']).count().reset_index()
        
        # Do mapping
        for i, s in enumerate(subsector_list):
            temp_v= np.zeros([int(row_n),int(col_n)]) # temporary 2d value  
            temp_c= np.zeros([int(row_n),int(col_n)]) 
            temp_w= np.zeros([int(row_n),int(col_n)])
            temp_v[row_col_value.loc[row_col_value['行业大类代码']==s,'row_r'],
                   row_col_value.loc[row_col_value['行业大类代码']==s,'col_r']]=row_col_value.loc[row_col_value['行业大类代码']==s,
                                                                                            '工业总产值_当年价格(千元)']
            
            temp_c[row_col_count.loc[row_col_count['行业大类代码']==s,'row_r'],
                        row_col_count.loc[row_col_count['行业大类代码']==s,'col_r']]=row_col_count.loc[row_col_count['行业大类代码']==s,
                                                                                                 '工业总产值_当年价格(千元)'] 
 
            temp_w[row_col_value.loc[row_col_value['行业大类代码']==s,'row_r'],
                         row_col_value.loc[row_col_value['行业大类代码']==s,'col_r']] = row_col_value.loc[row_col_value['行业大类代码']==s, 
                                                                                                  '工厂年取水量_效率（立方米）']
           
            map_value[i,:,:]=temp_v
            map_count[i,:,:]=temp_c
            map_water[i,:,:]=temp_w
    else:
        # create a var to save mapping results in China for totol industiral value
        map_value=np.zeros([int(row_n),int(col_n)])
        map_count=np.zeros([int(row_n),int(col_n)])
        map_water=np.zeros([int(row_n),int(col_n)])

        # aggregate values to pixel
        row_col_value = df.groupby(['row_r','col_r']).sum().reset_index()
        row_col_count = df.groupby(['row_r','col_r']).count().reset_index()
        
        map_value[row_col_value['row_r'],row_col_value['col_r']]=row_col_value['工业总产值_当年价格(千元)']
        map_count[row_col_count['row_r'],row_col_count['col_r']]=row_col_count['工业总产值_当年价格(千元)']
        map_water[row_col_value['row_r'],row_col_value['col_r']]=row_col_value['工厂年取水量_效率（立方米）']


    if save_netcdf:
        # Add half res for center lat/lon of the grid cell
        lat_values = np.arange(lat_max, lat_min -res/2,-res)-res/2#np.round(lon,2)
        lon_values = np.arange(lon_min, lon_max+res/2, res)+res/2
        lon2 = np.round(lon_values,3)
        lat2 = np.round(lat_values,3)

        if subsector: 
            map_count_net = xr.DataArray(map_count,
                                         dims=["subsector","lat","lon"],
                                         coords=[subsector_list,lat2,lon2],
                                         name='in')
            map_value_net = xr.DataArray(map_value,
                                         dims=["subsector","lat","lon"],
                                         coords=[subsector_list,lat2,lon2],
                                         name='iov')
            map_water_net = xr.DataArray(map_water,
                                         dims=["subsector","lat","lon"],
                                         coords=[subsector_list,lat2,lon2],
                                         name='iww')
            fn='data/products/figshare/V2302/CHINA_IWW_MAPPING_SUBSECTER_0'+str(int(res*100))+'deg_2008.nc'
            
        else:
            map_count_net = xr.DataArray(map_count,coords=[lat2, lon2], dims=["lat","lon"], 
                                         name='in')
            map_value_net = xr.DataArray(map_value,coords=[lat2, lon2], dims=["lat","lon"], 
                                         name='iov')
            map_water_net = xr.DataArray(map_water,dims=["lat","lon"], coords=[lat2, lon2],
                                         name='iww')
            fn='data/products/figshare/V2302/CHINA_IWW_MAPPING_0'+str(int(res*100))+'deg_2008.nc'
            
        d_out =xr.merge([map_count_net,map_value_net,map_water_net]) 

        pro_id = dp['ProID'].values
        c = np.where(pro_id>70 ,np.nan,pro_id)
        c = np.where(c>1,1,c)
        
        d_out1 = d_out*c
        
        if subsector:
            d_out1.subsector.attrs = {'Sector1':'Mining: 6,7,8,10,11',
                                      'Sector2':'Manufacture: 13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,34,35,36,37,39,40,41,42,43',
                                      'Sector3':'Electricity_and_gas_generation: 44,45'}
            
        d_out1['iww'].attrs = {'long_name':'industrial water withdrawal','units':' m$^{3}$/year'}
        d_out1['in'].attrs = {'long_name':'the number of industrial enterprises'}
        d_out1['iov'].attrs = {'long_name':'industrial output value','units':'10$^{3}$ yuan/year'}
      
        d_out1.lat.attrs = { 'long_name' : 'Latitude', 'units' : 'degrees_north'}
        d_out1.lon.attrs = { 'long_name' : 'Longitude', 'units' : 'degrees_east'}
        d_out1.attrs ={'Title': "China's subsector industrial water withdrawal in 2008 (raw)",
                       'Description': 'Raw data for mapping industrial water withdrawal.The industrial water withdrawal is produced by combining the georeferenced point data of Database of Chinese Industrial Enterprises with provincial water use efficiency data for 2008',
                       'Authors': 'Chengcheng Hou, Yan Li',
                       'Institution': 'Faculty of Geographical Science,Beijing Normal University',
                       'Contact': 'cch@mail.bnu.edu.cn, yanli@bnu.edu.cn',
                       'Reference': "Hou et al., 2023. High-resolution mapping of China industrial water withdrawal from 1965 to 2020"}
                    
        
        d_out1.to_netcdf(fn)
        print('netcdf file saved')
    return 


if __name__=="__main__":
####     d = pd.read_csv('../工业工厂位置数据/data/China_industry_water_withdrawal_v4.csv')
####     dp010 = xr.open_dataset('../工业工厂年际变化/province_id2.nc')
####     dp025 = xr.open_dataset('../工业工厂年际变化/province_id2_025u.nc')
####     mapping_water_withdrawal_just(d,dp010,0.1,subsector=True, save_netcdf=True)
####     mapping_water_withdrawal_just(d,dp025,0.25,subsector=True, save_netcdf=True)
####     mapping_water_withdrawal_just(d,dp010,0.1,subsector=False, save_netcdf=True)
####     mapping_water_withdrawal_just(d,dp025,0.25,subsector=False, save_netcdf=True)

