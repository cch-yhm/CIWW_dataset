#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from rasterstats import zonal_stats
from affine import Affine
from pyproj import Geod
from shapely.geometry import Point, LineString, Polygon
from functools import reduce
import math
import sklearn.metrics
import scipy.stats as stats
import matplotlib.patches as patches
##### get_ipython().run_line_magic('matplotlib', 'inline')

#### convert unit from mm to m3
def transform_mm_and_m3(df,res,range_lat,range_lon):
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
    
    # from m3 to mm: m3/area(m2)*1000  ##from mm to m3: mm/1000*area(m2); 
    df_mm = df.iww/df.area*1000
    df['iww_mm']=df_mm
    df.iww_mm.attrs = {'long_name' : 'industrial water withdrawal', 'units' : 'mm'+'/month'}
    return df


# prepare for zonal statistic
def make_affine(res,lat_north,lon_west):
    a = res        # change in x with x         # a = width of a pixel
    b = 0           # change in y with x        # b = row rotation (typically zero)
    c = lon_west    # x offset                  # c = x-coordinate of the upper-left corner of the upper-left pixel
    d = 0           # change in y with x        # d = column rotation (typically zero)
    e = -res        # change in y with y        # e = height of a pixel (typically negative)
    f = lat_north   # y offset                  # f = y-coordinate of the of the upper-left corner of the upper-left pixel
    af = Affine(a, b, c, d, e, f)
    return af


def prefecture_IWW_hcc(data,year_range,year_start,res,name):
    """ average gridded data over each prefecture and then multiply by the prefecture area to obtain IWW for each prefecture (unit: km3)
    year_range ---- time span of the data
    year_start ---- the first year of the data
    res ---- resolution
    name ----'huang','hcc',and 'model'
    """
    
    shi_id = pd.read_csv('data/dijishi_ID.csv',encoding='gbk')
    shape_fn_shi =r'../zhoufeng/GIS_Shapefile/perfectures.shp'
    re_shi = pd.DataFrame(shi_id[['Perfecture','Province_n','city']])
    idsz = pd.read_csv('../zhoufeng/per_id.csv')
    # get the mean IWW of the prefecture
    if name == 'huang':
        af_h = make_affine(data.lon.data[1]-data.lon.data[0],data.lat.data[71],data.lon.data[0])
    else:
        af_h = make_affine(data.lon.data[1]-data.lon.data[0],data.lat.data[0],data.lon.data[0])
        
    df2_h = pd.DataFrame()
    for i in range(year_range):
        if name == 'huang':
            zs1_h = zonal_stats(shape_fn_shi, np.flipud(data.with_ind[i].values), stats=['mean'], affine=af_h)
        else:
            zs1_h = zonal_stats(shape_fn_shi, data.iww_mm[i].values, stats=['mean'], affine=af_h)
        df_h = pd.DataFrame(zs1_h)['mean'].rename(i+year_start)
        df2_h = pd.concat([df2_h,df_h],axis=1)   #unit:mm
    s_h = pd.concat([re_shi,df2_h],axis=1)
    # combine the area of prefecture and obtain the prefecture IWW
    s_h= s_h.merge(idsz[['Perfecture','area']],on='Perfecture',how='left')
    s_h1 = pd.concat([s_h.iloc[:,:3],s_h.iloc[:,3:-1].mul(s_h[s_h.columns[year_range+3]].values,axis=0)/1000000],axis=1)
    # extract prefecture number
    city_id=s_h1.pop('Perfecture').str[1:]
    s_h1.insert(year_range+2,'City_id',city_id)
    # clean the file 
    s_h2 = pd.DataFrame(s_h1.set_index('City_id').iloc[:,2:].stack()).reset_index()
    s_h2.rename(columns={'level_1':'年份',0:str(name)+'_zonal_mm_zfshp_'+str(res)},inplace=True)
    s_h2.City_id = s_h2.City_id.astype(float)
    return s_h2


def File_read_clean():
    ## Huang Data
    dhmin = xr.open_dataset('参考数据/HuangPaperData/transfer_withd_min.nc')
    dhmfg = xr.open_dataset('参考数据/HuangPaperData/transfer_withd_mfg.nc')
    dhele = xr.open_dataset('参考数据/HuangPaperData/transfer_withd_elec.nc')
    ## select China 
    dhmin_ch = dhmin.sel(lon =slice(74.25,134.75),lat= slice(18.25,53.75))
    dhmfg_ch = dhmfg.sel(lon =slice(74.25,135.25),lat= slice(18.25,53.75))
    dhele_ch = dhele.sel(lon =slice(74.25,135.25),lat= slice(18.25,53.75))
    ## sum sector to industry
    dhch = dhele_ch.withd_elec+dhmfg_ch.withd_mfg+dhmin_ch.withd_min
    dhch1 = dhch.rename('with_ind').to_dataset()
    ## clean the dataset
    dhch2 =dhch1.transpose('month2', 'lat', 'lon')
    dhchy1 =dhch2.groupby('month2.year').sum()
    
    ## CIWW
    hcc025 = xr.open_dataset('data/products/figshare/CHINA_IWW_MON_025deg_1965_2020.nc')
    hcc025y = hcc025.groupby('time.year').sum()
    hcc050y =hcc025y.iww_mm.coarsen(lat=2,lon=2,boundary='pad',side='left').mean().to_dataset()
    hcc010 = xr.open_dataset('data/products/figshare/CHINA_IWW_MON_010deg_1965_2020.nc')
    hcc010y = hcc010.groupby('time.year').sum()
    
    ## model data
    md = xr.open_dataset('参考数据/indww_histsoc_annual_1901-2005.nc',decode_times=False)
    # 模型中1965-2005年的工业取水数据
    mdind = md.sel(lon =slice(74.25,134.75),lat= slice(53.75,18.25)).indww[64:,:,:]
    mdind= mdind.to_dataset()
    mdind = mdind.rename({'indww':'iww'})
    mdind2 = transform_mm_and_m3(mdind,0.5,72,122)
    
    ## Zhou2020 data
    zfdt = pd.read_excel('../zhoufeng/industry_water_use_shilevel1965_2013.xlsx')
    idsz = pd.read_csv('../zhoufeng/per_id.csv')
    idsz.rename(columns={'Perfecture':'City_ID'},inplace=True)
    zfdt1 = zfdt.merge(idsz[['ID','City_ID']],on='City_ID',how='left')[:16709]## 去掉中国
    zfdt1['ID'] =zfdt1['ID'].map(lambda x:int(x))
    zfdt1.rename(columns={'City_ID':'Perfecture','ID':'City_id','Year':'年份'},inplace=True)
    
    ## calculate prefectures' IWW
    huang_050 = prefecture_IWW_hcc(dhchy1 ,40,1971,50,'huang')
    hcc_050 = prefecture_IWW_hcc(hcc050y,56,1965,50,'hcc')
    hcc_025 = prefecture_IWW_hcc(hcc025y,56,1965,25,'hcc')
    hcc_010 = prefecture_IWW_hcc(hcc010y,56,1965,10,'hcc')
    model_050 = prefecture_IWW_hcc(mdind2,41,1965,50,'model')
    
    ## union all compared data
    union1=[zfdt1,huang_050,hcc_050,hcc_025,hcc_010,model_050]
    cp_union = reduce(lambda x, y: pd.merge(x, y, on=['年份','City_id'], how='outer'), union1)
    cp_union1 = cp_union[~cp_union.isnull().T.any()]
    cp_uniony = cp_union1.groupby('City_id').mean().reset_index()
    return cp_uniony


#Regression analysis fitting function
def plot_fitting(df, x_txt, y_txt, ax, order=1,lw=1.5,ls='--', color='r',fontsize=10):#,legend=True
    y_max = np.max(df[y_txt])
    parameter=np.polyfit(df[x_txt],df[y_txt],order)
    p = np.poly1d(parameter)
    y= parameter[0] * df[x_txt]  + parameter[1] 
    xp = np.linspace(df[x_txt].min(), df[x_txt].max(), 50)
    correlation = df[x_txt].corr(df[y_txt])  
    correlation=("%.2f" %correlation)
    c=str(correlation)
    
    mse = sklearn.metrics.mean_squared_error(df[y_txt],y)
    rmse = math.sqrt(mse)
    m = str('%.2f'%rmse)
    
    p_=stats.pearsonr(df[x_txt], df[y_txt])
    p_value=p_[1]
    s=""
    if p_value <0.05 and (p_value > 0.01 or p_value == 0.01):
        s="*"
    elif p_value < 0.01 and (p_value > 0.001 or p_value == 0.001):
        s="**"
    elif p_value <0.001:
        s="***"
    ax.plot(xp, p(xp),ls=ls,color=color,lw=lw)
    return (c,s)


## plot
def plot_figure2():
    # read the file
    cp_uniony = File_read_clean()
    Hd = pd.read_csv('参考数据/HuangPaperData/HuangBeijing0610_MonRate.csv')
    Estd = pd.read_csv('data/省级别工业取水月尺度比例_全国统一二级产业比例.csv')
    Ld = pd.read_csv('../Longdi/北京工业数据0616mon_rate.csv')
    
    # calculate RMSE
    mse1 = sklearn.metrics.mean_squared_error(cp_uniony['IND'],cp_uniony['hcc_zonal_mm_zfshp_50'])
    rmse1 = math.sqrt(mse1)
    mse2 = sklearn.metrics.mean_squared_error(cp_uniony['IND'],cp_uniony['huang_zonal_mm_zfshp_50'])
    rmse2 = math.sqrt(mse2)
    mse3 = sklearn.metrics.mean_squared_error(cp_uniony['IND'],cp_uniony['model_zonal_mm_zfshp_50'])
    rmse3 = math.sqrt(mse3)
    mse4 = sklearn.metrics.mean_squared_error(cp_uniony['IND'],cp_uniony['hcc_zonal_mm_zfshp_25'])
    rmse4 = math.sqrt(mse4)
    mse5 = sklearn.metrics.mean_squared_error(cp_uniony['IND'],cp_uniony['hcc_zonal_mm_zfshp_10'])
    rmse5 = math.sqrt(mse5)
    
    # plot
    label=[2006, 2007, 2008, 2009, 2010,2011, 2012, 2013, 2014, 2015,2016]
    x = [1,2,3,4,5,6,7,8,9,10,11,12]
    xticks1 =['J','F','M','A','M','J','J','A','S','O','N','D']
    x0= np.arange(0, 6, 0.5)
    y0=x0

    fig = plt.figure(figsize=(13,6))  #创建页面fig=plt.figure(figsize=(8,6),dpi=100)

    ### Panel a ###
    ax1 = fig.add_subplot(1,2,1)
    ax1.scatter(cp_uniony['IND'],cp_uniony['hcc_zonal_mm_zfshp_50'],label='CIWW (0.5$^\circ$)',color='blue',alpha=0.75)
    ax1.scatter(cp_uniony['IND'],cp_uniony['huang_zonal_mm_zfshp_50'],label='Huang (0.5$^\circ$)',color='orange',alpha=0.75 )
    ax1.scatter(cp_uniony['IND'],cp_uniony['model_zonal_mm_zfshp_50'],label='Model (0.5$^\circ$)',color='green',alpha=0.75 )
    # ax1.scatter(cp_uniony['IND'],cp_uniony['hcc_zonal_mm_zfshp_25'],label='CIWW_mm_25',color='green',marker='^',alpha=0.5)
    # ax1.scatter(cp_uniony['IND'],cp_uniony['hcc_zonal_mm_zfshp_10'],label='CIWW_mm_10',color='red',marker='*',alpha=0.5)

    r1,s1 = plot_fitting(cp_uniony,'IND','hcc_zonal_mm_zfshp_50',ax1,color='blue')
    r2,s2 = plot_fitting(cp_uniony,'IND','huang_zonal_mm_zfshp_50',ax1,color='orange')
    r3,s3 = plot_fitting(cp_uniony,'IND','model_zonal_mm_zfshp_50',ax1,color='green')
    r4,s4 = plot_fitting(cp_uniony,'IND','hcc_zonal_mm_zfshp_25',ax1,color='white')
    r5,s5 = plot_fitting(cp_uniony,'IND','hcc_zonal_mm_zfshp_10',ax1,color='white')  

    ax1.plot(x0,y0,':',lw=1.25,color='k')
    ax1.set_ylabel('Estimated water withdrawal (km$^{3}$)',fontsize=13)
    ax1.set_xlabel('Statistical water withdrawal (km$^{3}$)',fontsize=13)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.legend(fontsize=12)

    ax1.text(2.1,5.4,'R$^{2}$:'+r1+' RMSE:'+str(round(rmse1,2)),color='blue',fontsize=12 )
    ax1.text(2.1,5.1,'R$^{2}$:'+r2+' RMSE:'+str(round(rmse2,2)),color='orange',fontsize=12 )
    ax1.text(2.1,4.8,'R$^{2}$:'+r3+' RMSE:'+str(round(rmse3,2)),color='green',fontsize=12 )
    ax1.text(2.,0.2,'CIWW (0.25$^\circ$): R$^{2}$:'+r4+' RMSE:'+str(round(rmse4,2)),color='blue',fontsize=12 )
    ax1.text(2.1,-0.1,'CIWW (0.1$^\circ$): R$^{2}$:'+r5+' RMSE:'+str(round(rmse5,2)),color='blue',fontsize=12 )

    ax1.set_title('Spatial comparison',fontsize=15,pad=8,weight='roman')
    ax1.text(-1.,5.8,'(a)',fontsize=15)
    ax1.text(4.,4.,'x=y',color='grey',fontsize=13)
    ax1.legend(loc=2)

    #add Rectangle
    currentAxis=plt.gca()
    rect=patches.Rectangle((-0.1,-0.1),1.88,1.7,linewidth=1,edgecolor='r',ls='--',facecolor='none')
    currentAxis.add_patch(rect)
    #add 
    ax1.arrow(0.8, 1.6, -0.4, 1.6, head_width=0.125, head_length=0.2, ls='-.',shape="full",fc='red',ec='red',alpha=0.75, overhang=0.5)
    ax1.arrow(0.8, 1.6, 0.85, 1.63, head_width=0.125, head_length=0.2, ls='-.',shape="full",fc='red',ec='red',alpha=0.75, overhang=0.5)
    ax1.arrow(0.8, 1.6, 1.9, 1.7, head_width=0.125, head_length=0.2, ls='-.',shape="full",fc='red',ec='red',alpha=0.75, overhang=0.5)

    ax11 = ax1.inset_axes([0.05, 0.615, 0.18, 0.2],transform=ax1.transAxes)
    ax11.scatter(cp_uniony['IND'],cp_uniony['hcc_zonal_mm_zfshp_50'],color='blue',alpha=0.2)
    ax11.plot(x0,y0,':',color='k')
    plot_fitting(cp_uniony,'IND','hcc_zonal_mm_zfshp_50',ax11,color='blue')
    ax11.set_xlim(-0.2,1.7)
    ax11.set_ylim(-0.2,1.68)

    ax12 = ax1.inset_axes([0.26, 0.615, 0.18, 0.2],transform=ax1.transAxes)
    ax12.scatter(cp_uniony['IND'],cp_uniony['huang_zonal_mm_zfshp_50'],color='orange',alpha=0.2)
    plot_fitting(cp_uniony,'IND','huang_zonal_mm_zfshp_50',ax12,color='orange')
    ax12.plot(x0,y0,':',color='k')
    ax12.set_xlim(-0.2,1.7)
    ax12.set_ylim(-0.2,1.68)
    ax12.set_yticks([])

    ax13 = ax1.inset_axes([0.47, 0.615, 0.18, 0.2],transform=ax1.transAxes)
    ax13.scatter(cp_uniony['IND'],cp_uniony['model_zonal_mm_zfshp_50'],color='green',alpha=0.2)
    ax13.plot(x0,y0,':',color='k')
    plot_fitting(cp_uniony,'IND','model_zonal_mm_zfshp_50',ax13,color='green')
    ax13.set_xlim(-0.2,1.7)
    ax13.set_ylim(-0.2,1.68)
    ax13.set_yticks([])

    ######## Panel b ######## 
    y3 =Ld[:60].groupby('month').mean()['rate_year']# OK
    y_h = Hd.groupby('month').mean()['rate_ind']
    y_est = Estd['北京市']

    ax2 = fig.add_subplot(1,2,2)
    for i in range(5):
        if i==0:
            ax2.plot(x,Ld[Ld['year']==label[i]]['rate_year'],color='grey',label='Statistial data (individual year)',linewidth=1,alpha=0.5)
        else:
            ax2.plot(x,Ld[Ld['year']==label[i]]['rate_year'],color='grey',linewidth=1,alpha=0.5)

    ax2.plot(x,y3,label='Statistial data (mean)',color='r',linewidth=2.5,alpha=0.75)
    ax2.plot(x,y_est,label='CIWW',color='blue',linewidth=2.5,alpha=0.75)
    ax2.plot(x,y_h,label='Huang data',color='orange',linewidth=2.5,alpha=0.75)
    ax2.set_xticks([1,2,3,4,5,6,7,8,9,10,11,12])
    ax2.set_xticklabels(xticks1)
    ax2.set_ylim(0.04,0.14)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.set_xlabel('Month',fontsize=13)
    ax2.set_ylabel('Monthly fraction',fontsize=13)
    ax2.text(1,0.135,'Beijing',fontsize=15)
    ax2.legend(fontsize=12)
    ax2.text(-1.4,0.1405,'(b)',fontsize=15)
    ax2.set_title('Seasonal validation',fontsize=15,pad=8,weight='roman')

    ax21 = ax2.inset_axes([0.55, 0.02, 0.35, 0.27],transform=ax2.transAxes)
    ax21.grid(alpha=0.8,axis="y",ls="-")
    width = 0.5
    x21 =list(range(3))
    y21 = [33,31.04,56]
    ax21.set_ylim(0,100)
    ax21.bar(x21,y21,width,align='center',color=['red','blue','orange'],alpha=0.65)
    ax21.set_ylabel('IWW (mm)',fontsize=11)
    ax21.spines['top'].set_visible(False)
    ax21.spines['right'].set_visible(False)
    for a,b in zip(x21,y21):
            ax21.text(a, b+1.5,'%.0f'%b, ha ='center',va ='bottom',fontsize=9)
    ax21.set_xticklabels('')
    
    ## save the figure
    plt.savefig('08pre/Figure_test/数据对比_重新画图.jpg',dpi=300, bbox_inches='tight')
    return



if __name__=="__main__":
    plot_figure2() 



