#!/usr/bin/env python
# coding: utf-8


import pandas as pd
import numpy as np


def estimate_IWW_enterprise():
    """
    estimate enterprise's IWW
    """
    #read the file (d_w --Industrial water intake efficiency | d ---china industry factories)
    d_w = pd.read_csv('规模以上工业用水和工业产值汇总2008.csv')
    d = pd.read_csv('工业企业数据2008/工业企业数据2008/China_industry_2008_geolocation2.csv')
    # select useful columns
    d_ind = d[['企业匹配唯一标识码', '省（自治区、直辖市）', '地（区、市、州、盟）', '县（区、市、旗）','latitude', 'longitude',
               '行业门类代码','行业门类名称', '行业大类代码','行业大类名称', '工业总产值_当年价格(千元)']]
    # make sure two files' name(the province and the sector) consistent
    f_ind['行业大类名称'].replace('非金属矿采选业  ','非金属矿采选业',inplace = True)
    f_ind['行业大类名称'].replace('其他采矿业  ','其他采矿业',inplace = True)
    # combine the two files
    d_merge = pd.merge(d_ind,d_w,on =['省（自治区、直辖市）','行业大类名称'],how = 'left')
    # calculate every factory's water withdrawal
    d_merge['工厂取水量(单位：立方米)']=d_merge['工业总产值_当年价格(千元)'].mul(d_merge['用水效率2（单位：立方米/千元）'])
    #adjust the file 
    d_merge.drop(d_merge.columns[12:17],axis=1,inplace=True)
    
    # '其他采矿业','废弃资源和废旧材料回收加工业' --No WUE, using the WUE of sector to estimate
    df_else1 =d_merge.loc[d_merge['行业大类名称'].isin(['其他采矿业'])]#26
    df_else2 =d_merge.loc[d_merge['行业大类名称'].isin(['废弃资源和废旧材料回收加工业'])]#1087
    df1_e1 = pd.merge(df_else1,d_w[:32][['省（自治区、直辖市）',
                                         '行业大类名称','用水效率2（单位：立方米/千元）']],how='left',on=['省（自治区、直辖市）'])
    df1_e2 = pd.merge(df_else2,d_w[224:256][['省（自治区、直辖市）',
                                             '行业大类名称','用水效率2（单位：立方米/千元）']],how='left',on=['省（自治区、直辖市）'])
    df1_e1['工厂年取水量_效率（单位：立方米）2']=df1_e1['工业总产值_当年价格(千元)'].mul(df1_e1['用水效率2（单位：立方米/千元）_y'])
    df1_e2['工厂年取水量_效率（单位：立方米）2']=df1_e2['工业总产值_当年价格(千元)'].mul(df1_e2['用水效率2（单位：立方米/千元）_y'])
    t1 =pd.concat([df1_e1[['企业匹配唯一标识码','工厂年取水量_效率（单位：立方米）2']],
                   df1_e2[['企业匹配唯一标识码','工厂年取水量_效率（单位：立方米）2']]],ignore_index=True)
    
    # combine the two files
    d_merge2 = pd.merge(d_merge,t1,how='left',on=['企业匹配唯一标识码'])
    # select the re-estimate result
    d_merge2['工厂年取水量_效率（单位：立方米）3'] = np.where(d_merge2['工厂年取水量_效率（单位：立方米）2']>0,
                                              d_merge2['工厂年取水量_效率（单位：立方米）2'],d_merge2['工厂年取水量_效率（单位：立方米）'])
    d_merge2 = d_merge2[['企业匹配唯一标识码', '省（自治区、直辖市）', '地（区、市、州、盟）', '县（区、市、旗）', 'latitude',
                         'longitude', '行业门类代码', '行业门类名称', '行业大类代码', '行业大类名称',  '工业总产值_当年价格(千元)', 
                         '取水总量（单位：万立方米）','工业总产值(当年价格，单位：亿元)','用水效率2（单位：立方米/千元）',
                         '工厂年取水量_效率（单位：立方米）3']]
    d_merge2.rename(columns={'取水总量（单位：万立方米）':'省取水总量（万立方米）',
                             '工业总产值(当年价格，单位：亿元)':'省工业总产值(当年价格；亿元)',
                             '用水效率2（单位：立方米/千元）':'省行业大类用水效率（立方米/千元）',
                             '工厂年取水量_效率（单位：立方米）3':'工厂年取水量_效率（立方米）'},inplace=True)
    #save the data
    d_merge2.to_csv('../工业工厂位置数据/data/China_industry_water_withdrawal_v4.csv',index=False)
    print('water_withdrawal_calculate OK')
    return


if __name__=="__main__":
####     estimate_IWW_enterprise()



