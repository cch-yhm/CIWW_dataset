#!/usr/bin/env python
# coding: utf-8


import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#### get_ipython().run_line_magic('matplotlib', 'inline')

def plot_figure5():
    # read the file
    df3 = xr.open_dataset('data/products/figshare/V2302/CHINA_IWW_MON_025deg_1965_2020_N.nc')
    # transform units: mm*m2/1000 = m3
    df3_m3 = df3.iww*df3.cell_area/1000 
    # sum to national & transform m3 to km3
    df3_mt = df3_m3.sum(['lat','lon'])/1000000000

    month = pd.date_range(start='19650101',periods=672,freq='M')
    # change the label 
    x_label = pd.date_range(start='1965',end='2025',freq='5Y').year
    
    fig, axes = plt.subplots(figsize=(8,4))
    axes.grid(alpha=0.8,axis="y",ls=":")
    axes.plot(month,df3_mt.values,label='monthly',color='royalblue',alpha=0.75)
    df3_mt.rolling(time=12, center=True).mean().plot(linewidth=2,label='12-month moving average',color='lightcoral')

    axes.set_xlabel('Year',fontsize=12)
    axes.set_ylabel("Industrial water withdrawal (km$^{3}$)",fontsize=11)
    axes.set_xticks(['1965','1970','1975','1980','1985','1990','1995','2000','2005','2010','2015','2020'])
    axes.set_xticklabels(x_label,)
    axes.tick_params(axis='x',labelsize=10,rotation=0)
    axes.tick_params(axis='y',labelsize=10)
    axes.set_ylim(0,15.9)
    axes.legend(frameon=False,fontsize=12)
    axes.spines['top'].set_visible(False)
    axes.spines['right'].set_visible(False)
    plt.savefig('08pre/Figure_test/long_time_serise_iww.jpg',dpi=300, bbox_inches='tight')
    return


if __name__=="__main__":
    plot_figure5() 


