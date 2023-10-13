#!/usr/bin/env python
# coding: utf-8

import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#### get_ipython().run_line_magic('matplotlib', 'inline')

def plot_figure_appendixC3():
    # read the file
    dep = pd.read_csv('../工业年内用水变化/ele_heat各省产量年内占比及全国产量年内占比_2006-2010mean.csv')
    dem = pd.read_csv('../工业年内用水变化/manufacture各省产量年内占比及全国产量年内占比_2006-2010mean.csv')
    dec = pd.read_csv('../工业年内用水变化/mining各省产量年内占比及全国产量年内占比_2006-2010mean.csv')
    dt_a= pd.read_csv('../工业年内用水变化/全国工业按产业用水比例得到的一级产业和总产业用水比_可画图.csv')

    ## plot
    xticks1 =['J','F','M','A','M','J','J','A','S','O','N','D']
    labels = ['All sectors','Electricity and gas production and supply','Manufacturing','Mining']
    colors_l = ['lightgreen','bisque','lightskyblue']
    data_t = [dep,dem,dec]
    colors_sh = ['lightgrey','palegreen','navajowhite','lightblue']
    colors = ['green','orange','blue']
    label=['a','b','c','d']

    fig, axes = plt.subplots(2,2,figsize=(10,10)) 
    plt.subplots_adjust(hspace=0.25)

    ### Panel a ###
    axes.flatten()[0].plot(dec.index,dec.iloc[:,-1:],color='blue',label='Mining',linewidth=3,alpha=0.65)
    axes.flatten()[0].plot(dem.index,dem.iloc[:,-1:],color='orange',label='Manufacturing',linewidth=3,alpha=0.85)
    axes.flatten()[0].plot(dep.index,dep.iloc[:,-1:],color='green',label='EGPS',linewidth=3,alpha=0.7)
    axes.flatten()[0].plot(dt_a.index,dt_a.iloc[:,-1:],color='crimson',label='Total',linewidth=4)

    ### Panel bcd ###
    for i in range(3):
        t=i+1
        axes.flatten()[t].plot(data_t[i].index,data_t[i].iloc[:,:1],color=colors_l[i],label='Each province',alpha=0.85)
        axes.flatten()[t].plot(data_t[i].index,data_t[i].iloc[:,1:-1],color=colors_l[i],alpha=0.85)

        if t==1:
            axes.flatten()[t].plot(data_t[i].index,data_t[i].iloc[:,-1:],color=colors[i],label='National',linewidth=3) 
        else:
            axes.flatten()[t].plot(data_t[i].index,data_t[i].iloc[:,-1:],color=colors[i],label='National',linewidth=3)

    for j in range(4):
        axes.flatten()[j].axvspan(0, 2, facecolor=colors_sh[j], alpha=0.3)
        axes.flatten()[j].set_title(labels[j],fontsize=15,pad=10,weight='roman')
        axes.flatten()[j].set_xticks([0,1,2,3,4,5,6,7,8,9,10,11])
        axes.flatten()[j].set_xticklabels(xticks1)
        axes.flatten()[j].spines['top'].set_visible(False)
        axes.flatten()[j].spines['right'].set_visible(False) 
        axes.flatten()[j].text(-3.25,0.145,'('+label[j]+')',fontsize=15)
        axes.flatten()[j].legend(framealpha=0.5,loc=9)#,edgecolor='grey')
    
    axes.flatten()[0].set_ylim(0.04,0.14)    
    axes.flatten()[1].set_ylim(0.04,0.14) 
    axes.flatten()[2].set_ylim(0.04,0.14) 
    axes.flatten()[3].set_ylim(0.04,0.155) 
    # shadow
    axes.flatten()[3].axvspan(4, 6, facecolor='lightblue', alpha=0.3)
    axes.flatten()[2].axvspan(4, 6, facecolor='navajowhite', alpha=0.3)
    axes.flatten()[1].axvspan(4.75, 7.25, facecolor='palegreen', alpha=0.3)
    axes.flatten()[0].axvspan(4.25, 7, facecolor='lightgrey', alpha=0.3)
    # x_label & y_label
    axes.flatten()[0].set_ylabel('Monthly fraction',fontsize=13)
    axes.flatten()[2].set_ylabel('Monthly fraction',fontsize=13)
    axes.flatten()[2].set_xlabel('Month',fontsize=14,labelpad=8)
    axes.flatten()[3].set_xlabel('Month',fontsize=14,labelpad=8)
    # save the figure
    plt.savefig('08pre/Figure_test/time_province_revision.jpg',dpi=300, bbox_inches='tight')
    return


if __name__=="__main__":
    plot_figure_appendixC3() 

