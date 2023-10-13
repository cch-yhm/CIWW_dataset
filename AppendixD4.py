#!/usr/bin/env python
# coding: utf-8

import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import sklearn.metrics
import scipy.stats as stats
#### get_ipython().run_line_magic('matplotlib', 'inline')

## fitting lines
def plot_fitting_np(x_txt, y_txt, ax, order=1,lw=1.5,color='r',fontsize=10):
    """x_txt and y_txt are np_series"""
    y_max = np.max(y_txt)
    parameter=np.polyfit(x_txt,y_txt,order)
    p = np.poly1d(parameter)
    y= parameter[0] * x_txt  + parameter[1] 
    xp = np.linspace(np.min(x_txt), np.max(x_txt), 50)
    correlation = np.corrcoef(x_txt,y_txt)[0][1]
    correlation=("%.2f" %correlation)
    c=str(correlation)
    
    mse = sklearn.metrics.mean_squared_error(y_txt,y)
    rmse = math.sqrt(mse)
    m = str('%.2f'%rmse)
    
    p_=stats.pearsonr(x_txt, y_txt)
    p_value=p_[1]
    s=""
    if p_value <0.05 and (p_value > 0.01 or p_value == 0.01):
        s="*"
    elif p_value < 0.01 and (p_value > 0.001 or p_value == 0.001):
        s="**"
    elif p_value <0.001:
        s="***"
    ax.plot(xp, p(xp), '--',color=color,lw=lw)
    return (c,s,m)

def plot_figure_appendixD4():
    ## read the file 
    d13nc025 = xr.open_dataset('data/process/verify_sec_025_2013.nc')
    d13nc010=xr.open_dataset('data/process/verify_sec_010_2013.nc')
    d08nc025=xr.open_dataset('data/products/figshare/V2302/CHINA_IWW_MAPPING_SUBSECTER_025deg_2008.nc')
    d08nc010=xr.open_dataset('data/products/figshare/V2302/CHINA_IWW_MAPPING_SUBSECTER_010deg_2008.nc')

    ## make sure the same subsectors of two years
    new_d13nc025 = d13nc025.sel(sector=[6,  7,  8, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 
                                        32, 34, 35, 36, 37, 39, 40, 41, 42, 43, 44, 45,])
    new_d13nc010 = d13nc010.sel(sector=[6,  7,  8, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 
                                        32, 34, 35, 36, 37, 39, 40, 41, 42, 43, 44, 45,])
    ## sum the output of all subsectors
    a_d13nc025 = new_d13nc025.sum('sector')
    a_d08nc025 = d08nc025.sum('subsector')
    a_d13nc010 = new_d13nc010.sum('sector')
    a_d08nc010 = d08nc010.sum('subsector')

    ## convert 0 values to nan 
    a_d08nc025['iov'].values[a_d08nc025['iov'].values==0]=np.nan
    a_d13nc025['production'].values[a_d13nc025['production'].values==0]=np.nan
    a_d08nc010['iov'].values[a_d08nc010['iov'].values==0]=np.nan
    a_d13nc010['production'].values[a_d13nc010['production'].values==0]=np.nan

    ## calculate the proportion*100 (%)
    d08_25rate100 = a_d08nc025['iov']/a_d08nc025['iov'].sum().values*100
    d13_25rate100 = a_d13nc025['production']/a_d13nc025['production'].sum().values*100
    d08_10rate100 = a_d08nc010['iov']/a_d08nc010['iov'].sum().values*100
    d13_10rate100 = a_d13nc010['production']/a_d13nc010['production'].sum().values*100
    ### flatten 
    pa_d08nc025 = d08_25rate100.values.flatten()
    pa_d13nc025 = d13_25rate100.values.flatten()
    pa_d08nc010 = d08_10rate100.values.flatten()
    pa_d13nc010 = d13_10rate100.values.flatten()
    
    ## plot
    x0= np.arange(0, 0.7, 0.01)
    y0=x0
    x1= np.arange(0, 1.5, 0.01)
    y1=x1

    fig = plt.figure(figsize=(11,5))  
    ### Panel A ###
    ax1 = fig.add_subplot(1,2,1)
    ax1.scatter(pa_d08nc010[~np.isnan(pa_d13nc010)&~np.isnan(pa_d08nc010)],
                              pa_d13nc010[~np.isnan(pa_d13nc010)&~np.isnan(pa_d08nc010)],label='08vs13',color='blue',alpha=0.5)
    ax1.set_ylabel("Proportion of grids' IOV in 2013 (%)",fontsize=12)
    ax1.set_xlabel("Proportion of grids' IOV in 2008 (%)" ,fontsize=12)
    r1,s1,m1 = plot_fitting_np(pa_d08nc010[~np.isnan(pa_d13nc010)&~np.isnan(pa_d08nc010)],
                               pa_d13nc010[~np.isnan(pa_d13nc010)&~np.isnan(pa_d08nc010)],ax1,color='blue')
    ax1.text(0,0.61,'R$^{2}$:'+r1+' RMSE:'+m1,color='blue',fontsize=12 )
    ax1.text(0.54,0.63,'x=y',color='grey',fontsize=12)
    ax1.plot(x0,y0,':',color='grey')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.legend(fontsize=12)

    ax1.set_title('0.1$^\circ$',fontsize=15,pad=8,weight='roman')
    ax1.text(-0.15,0.74,'(a)',fontsize=15)

    ### Panel B ###
    ax2 = fig.add_subplot(1,2,2)
    ax2.scatter(pa_d08nc025[~np.isnan(pa_d13nc025)&~np.isnan(pa_d08nc025)],
                              pa_d13nc025[~np.isnan(pa_d13nc025)&~np.isnan(pa_d08nc025)],label='08vs13',color='blue',alpha=0.5)
    ax2.set_ylabel("Proportion of grids' IOV in 2013 (%)",fontsize=12)
    ax2.set_xlabel("Proportion of grids' IOV in 2008 (%)" ,fontsize=12)
    r2,s2,m2 = plot_fitting_np(pa_d08nc025[~np.isnan(pa_d13nc025)&~np.isnan(pa_d08nc025)],
                               pa_d13nc025[~np.isnan(pa_d13nc025)&~np.isnan(pa_d08nc025)],ax2,color='blue')
    ax2.text(0,1.3,'R$^{2}$:'+r2+' RMSE:'+m2,color='blue',fontsize=12 )
    ax2.plot(x1,y1,':',color='grey')       
    ax2.text(1.2,1.35,'x=y',color='grey',fontsize=12)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    ax2.legend(fontsize=12)
    ax2.text(-0.25,1.605,'(b)',fontsize=15)
    ax2.set_title('0.25$^\circ$',fontsize=15,pad=8,weight='roman')

    # save the figure
    plt.savefig('../工业工厂位置数据/08pre/Figure_test/IOV格局变化.jpg',dpi=300, bbox_inches='tight')
    return

if __name__=="__main__":
    plot_figure_appendixD4() 



