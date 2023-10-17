#!/usr/bin/env python
# coding: utf-8


import pandas as pd
import numpy as np


def replacement_water(f):
    replacements_chanye1 = {
       '产业': {
           r'电力热力的生产和供应业':'电力、热力的生产和供应业'}
    }
    f.replace(replacements_chanye1, regex=True, inplace=True)


def replacement_kind(f): 
    replacements_chanye2 = {
       '产业': {
           r'煤气生产和供应业':'燃气生产和供应业'}
    }
    f.replace(replacements_chanye2, regex=True, inplace=True)


def replacement_province(f):
    replacements_province = {
       '地区': {
           #r'全国':'China',
           r'北京':'北京市',
           r'天津':'天津市', 
           r'河北':'河北省', 
           r'山西':'山西省',
           #r'内蒙古':'内蒙古',
           r'辽宁':'辽宁省', 
           r'吉林':'吉林省',
           #r'黑龙江':'黑龙江', 
           r'上海':'上海市', 
           r'江苏':'江苏省',
           r'浙江':'浙江省', 
           r'安徽':'安徽省',
           r'福建':'福建省',
           r'江西':'江西省',
           r'山东':'山东省',
           r'河南':'河南省', 
           r'湖北':'湖北省', 
           r'湖南':'湖南省', 
           r'广东':'广东省', 
           r'广西':'广西区', 
           r'海南':'海南省',
           r'重庆':'重庆市',
           r'四川':'四川省',
           r'贵州':'贵州省',
           r'云南':'云南省',
           r'西藏':'西藏区',
           r'陕西':'陕西省',
           r'甘肃':'甘肃省',
           r'青海':'青海省',
           r'宁夏':'宁夏区',
           r'新疆':'新疆区'
       }
    }
    f.replace(replacements_province, regex=True, inplace=True)
    print('province ok')


def calcu_output_rate_mean(name):  
    """
    Calculated the monthly fraction of each product output of each province,then averaged from 2006 to 2010
    """
    if name == 'mining':
        d = pd.read_excel('采矿业全国各地产量年内变化整理.xlsx')   
    elif name == 'manufacture':
        d = pd.read_excel('制造业全国各地产量年内变化2006_2010_2.xlsx')
    else:
        d = pd.read_excel('电热全国各地产量年内变化2006-2010整理.xlsx')
        
    d1 = d[d['Unnamed: 67']!=0]#drop the product whose output is 0
    d1.set_index(['省', '产品'],inplace=True)
#     name = str(d.iloc[0:1,1:2].values)[4:5]

    f = pd.DataFrame()
    d_o_m = pd.DataFrame()
    for i in range(5):
        f= d1.iloc[:,13*i:13*(i+1)] # each year
        ##  calculated the monthly fraction of each product output of each province
        f[['01','02','03','04','05','06','07','08','09','10','11','12']] = f[f.columns[:-1]].div(f[2006+i].values,axis=0)
        f2= f.iloc[:,13:].T
        f2['year']=2006+i
        d_o_m = d_o_m.append(f2) #d_ct为采矿业全国各地产量占比年内变化2006_2010
        i = i+1

    d_o_m.reset_index(inplace=True)
    d_o_m.rename(columns={'index':'month'},inplace=True)
    # d_o_m.to_csv('全国各省产品产量占比年内变化2006_2010_'+name+'.csv',index=False)
    
    # averaged from 2006 to 2010 (之所以不算mean 是因为中间有空值，但不是一年中所有月都是空值）
    ## count months
    mon_c = d_o_m.groupby('month').count()
    mon_m = mon_c.max(axis=0).to_frame().T
    mon_m.drop(['year'],axis=1,inplace=True)
    ## sum fractions of years
    prod_s = d_o_m.groupby('month').sum()
    prod_mon = prod_s.append(mon_m).T[1:]
    ## averaged
    prod_mon[['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov',
              'Dec']] = prod_mon[['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11','12']].div(prod_mon[0].values,axis=0)
    #prod_mon[[0]] is the number of month fraction which is not 0
    
    prod_mean0 = prod_mon.iloc[:,13:]
    prod_mean = prod_mean0.reset_index()
    
#     prod_mean.to_csv('全国各省产品产量占比年内变化_5year_mean_'+name+'.csv',index=False)            
    print('rate and mean OK')  
    return prod_mean


def transfer_output_kind(name):
    """
    Estimate the monthly fractions for the subsector using the arithmetic mean of the monthly fractions of the different products 
    belonging to a subsector 
    name ---- "ele_heat","mining","manufacture"
    
    """
    if name == 'ele_heat':
        d = calcu_output_rate_mean(name)
        replacements_chanpin_chanye= {
           '产品': {
               r'发电量':'电力、热力的生产和供应业',
               r'煤气生产量':'燃气生产和供应业', 
           }
        }

        d.replace(replacements_chanpin_chanye, regex=True, inplace=True)
        d.rename(columns={'产品':'产业','Jan':'01', 'Feb':'02', 'Mar':'03', 'Apr':'04', 'May':'05', 'Jun':'06',
                          'Jul':'07', 'Aug':'08', 'Sep':'09', 'Oct':'10','Nov':'11', 'Dec':'12'},inplace=True)
        d.to_csv('全国各省产业产量占比年内变化_5year_mean_'+str(name)+'.csv',index=False)
    else: 
        # read the file
        if name == 'mining':
            d_min = calcu_output_rate_mean(name)
            coal = d_min.loc[d_min['产品'].isin(['原煤', '洗煤'])]
            oilgas = d_min.loc[d_min['产品'].isin(['天然原油', '天然气'])]
            blackmetal = d_min.loc[d_min['产品'].isin(['铁矿石原矿'])]
            colorfulmetal = d_min.loc[d_min['产品'].isin(['铜金属含量', '锌金属含量','铅金属含量', '钼精矿折合量（折纯钼４５％）',
                                                          '锡金属含量', '钨精矿折合量（折三氧化钨６５％）', '锑金属含量'])]
            no_metal = d_min.loc[d_min['产品'].isin(['原盐','硫铁矿石（折含硫35%）', '磷矿石（折含五氧化二磷30%）',])]
            
            n = 5
            sort = [coal,oilgas,blackmetal,colorfulmetal,no_metal]
            labels = ['煤炭开采和洗选业', '石油和天然气开采业', '黑色金属矿采选业', '有色金属矿采选业', '非金属矿采选业']
        else:
            d_man = calcu_output_rate_mean(name)
            nongfufood =d_man.loc[d_man['产品'].isin(['小麦粉', '大米', '饲料', '精制食用植物油','成品糖','鲜、冷藏肉', '冻肉'])]
            foodmaking =d_man.loc[d_man['产品'].isin(['糕点','饼干','糖果','速冻米面食品','方便面','乳制品','罐头','味精（谷氨酸钠）',
                                                                         '酱油','冷冻饮品'])]
            drinking = d_man.loc[d_man['产品'].isin([  '发酵酒精（折96度,商品量）', '饮料酒', '软饮料', '精制茶'])]
            yancao = d_man.loc[d_man['产品'].isin(['卷烟'])]
            fangzhi= d_man.loc[d_man['产品'].isin(['纱','布','印染布','绒线（俗称毛线）','毛机织物（呢绒）','亚麻布（含亚麻≥55%）','帘子布',
                                                                      '无纺布（无纺织物）','蚕丝及交织机织物（含蚕丝≥50%）','苎麻布（含苎麻≥55%）','生丝'])]
            clothing = d_man.loc[d_man['产品'].isin(['服装', '针织服装', '梭织服装'])]
            leather = d_man.loc[d_man['产品'].isin([ '轻革', '皮革鞋靴', '皮革服装','天然皮革制手提包（袋）、背包', '天然毛皮服装'])]
            woodenusing =  d_man.loc[d_man['产品'].isin(['人造板', '人造板表面装饰板', '复合木地板','实木木地板'])]
            furniture = d_man.loc[d_man['产品'].isin([ '家具'])]
            papermaking = d_man.loc[d_man['产品'].isin([ '纸浆（原生浆及废纸浆）', '机制纸及纸板（外购原纸加工除外）', '纸制品'])]
            yinshuaye = d_man.loc[d_man['产品'].isin([ '本册'])]
            wenjiaotiyu  = d_man.loc[d_man['产品'].isin([ '木杆铅笔','圆珠笔'])]
            oilmaking = d_man.loc[d_man['产品'].isin([ '原油加工量','汽油', '煤油', '柴油', '润滑油', '燃料油', '液化石油气', '石油沥青', '焦炭'])]
            chemicalyuan = d_man.loc[d_man['产品'].isin(['硫酸（折100％）','盐酸（氯化氢,含量31%）', '烧碱（折100％）', '乙烯', '纯苯','合成橡胶',
                                                       '农用氮、磷、钾化学肥料总计（折纯）','磷酸铵肥（实物量）', '化学农药原药（折有效成分100％）', 
                                                        '涂料', '油墨', '颜料', '染料','初级形态的塑料', '其中:聚乙烯树酯', '聚丙烯树脂', '精甲醇',
                                                        '聚氯乙烯树脂','合成纤维单体','合成纤维聚合物','肥（香）皂','合成洗涤剂', '冰乙酸（冰醋酸）',
                                                        '牙膏（折65克标准支）', '香精','纯碱（碳酸钠）', '碳化钙（电石,折300升／千克）', 
                                                        '浓硝酸（折100%）','合成氨（无水氨）', '火柴（折50支标准盒）'])]
            medicine = d_man.loc[d_man['产品'].isin([ '化学药品原药', '中成药'])]
            huauxuexianwei = d_man.loc[d_man['产品'].isin([ '化学纤维用浆粕','化学纤维', '合成纤维'])]
            xiangjiaozhipin = d_man.loc[d_man['产品'].isin([ '橡胶轮胎外胎', '胶鞋类'])]
            plasticmaking = d_man.loc[d_man['产品'].isin([ '塑料制品'])]
            feijinshukuangwu = d_man.loc[d_man['产品'].isin(['水泥熟料', '水泥', '商品混凝土','水泥混凝土排水管', '水泥混凝土压力管', '预应力混凝土桩', 
                                                             '石膏板', '砖', '瓦', '瓷质砖', '细炻砖','炻质砖','天然大理石建筑板材', '天然花岗石建筑板材', 
                                                             '平板玻璃', '钢化玻璃', '夹层玻璃', '中空玻璃', '日用玻璃制品','玻璃保温容器', '玻璃纤维纱', 
                                                             '卫生陶瓷制品', '耐火材料制品', '石墨及炭素制品','水泥混凝土电杆', '日用陶瓷制品','陶质砖',
                                                             '炻瓷砖'])]
            blackmetalyelian = d_man.loc[d_man['产品'].isin([ '生铁', '粗钢', '钢材','用外购国产钢材再加工生产的钢', '铁合金'])]
            yousemetalyelian = d_man.loc[d_man['产品'].isin(['十种有色金属', '精炼铜（电解铜）', '锡','锌','原铝（电解铝）', '镁', '海绵钛', '黄金',
                                                             '白银（银锭）','铝合金', '铜材', '铝材','铅', '氧化铝', '镍','锑品'])]
            metalzhiping = d_man.loc[d_man['产品'].isin([ '金属切削工具', '钢绞线', '锁具', '搪瓷制品', '不锈钢日用制品','金属集装箱'])]
            tongyongshebei =  d_man.loc[d_man['产品'].isin(['电站锅炉', '工业锅炉', '电站用汽轮机', '电站水轮机','金属切削机床', '金属成形机床', 
                                                            '铸造机械', '电焊机', '起重机','电动车辆（电动叉车）', '内燃叉车', '泵', '气体压缩机', '阀门',
                                                            '液压元件', '气动元件', '滚动轴承','工业电炉', '风机', '气体分离及液化设备','电动手提式工具', 
                                                            '包装专用设备', '减速机', '粉末冶金零件', '燃气轮机'])]
            specialshebei = d_man.loc[d_man['产品'].isin(['采矿专用设备', '挖掘、铲土运输机械', '压实机械', '水泥专用设备', '混凝土机械',
                                                          '金属冶炼设备','金属轧制设备', '塑料加工专用设备', '模具', '粮食加工机械', '饲料生产专用设备',
                                                          '印刷专用设备', '缝纫机','农作物收获机械', '环境污染防治专用设备', '中型拖拉机', '小型拖拉机',
                                                          '棉花加工机械','大型拖拉机', '场上作业机械'])]
            jiaotongyunshu = d_man.loc[d_man['产品'].isin([ '铁路机车', '铁路货车','汽车', '改装汽车', '两轮脚踏自行车', '铁路客车','摩托车整车',
                                                            '民用钢质船舶'])]
            dianqijixie = d_man.loc[d_man['产品'].isin(['发电机组（发电设备）', '交流电动机', '变压器', '高压开关板', '低压开关板','通信及电子网络用电缆',
                                                        '电力电缆', '光缆', '绝缘制品', '铅酸蓄电池', '碱性蓄电池', '锂离子电池','原电池及原电池组（折R20标准只）',
                                                        '家用电冰箱', '商用冷藏展示柜', '家用电热烘烤器具','家用洗衣机','家用燃气灶具','微波炉', 
                                                        '家用电热水器','家用吸尘器','家用燃气热水器','电光源','灯具及照明装置','家用冷柜（家用冷冻箱）',
                                                        '房间空气调节器','家用吸排油烟机','电饭锅','家用电风扇' ])]
            communication = d_man.loc[d_man['产品'].isin([ '微波终端机', '程控交换机', '其中:数字程控交换机', '电话单机','移动通信基站设备', 
                                                           '移动通信手持机（手机）', '电子计算机整机', '显示器', '打印机', '彩色显像管','半导体分立器件',
                                                           '集成电路', '集成电路圆片', '彩色电视机', '组合音响','传真机', '数字激光音、视盘机'])]
            yiqiyibiao = d_man.loc[d_man['产品'].isin(['工业自动调节仪表与控制系统', '电工仪器仪表','分析仪器及装置','试验机','照相机',
                                                       '环境监测专用仪器仪表','汽车仪器仪表','表','光学仪器', '眼镜成镜', '复印和胶版印制设备'])]
            umberlla = d_man.loc[d_man['产品'].isin(['伞类制品'])]

            n = 29
            sort =[nongfufood,foodmaking,drinking,yancao,fangzhi,clothing,leather,woodenusing,furniture,papermaking ,yinshuaye,#11
                      wenjiaotiyu,oilmaking,chemicalyuan,medicine,huauxuexianwei,xiangjiaozhipin,plasticmaking,feijinshukuangwu,# 8
                      blackmetalyelian,yousemetalyelian,metalzhiping,tongyongshebei,specialshebei,jiaotongyunshu,dianqijixie,# 7
                      communication,yiqiyibiao,umberlla]#3

            labels = ['农副食品加工业', '食品制造业', '饮料制造业', '烟草制品业', '纺织业工业', '纺织服装鞋帽制造业',
                      '皮革毛皮羽毛(绒)及其制品业', '木材加工及木竹藤棕草制品业', '家具制造业', '造纸及纸制品业',#10
                      '印刷业和记录媒介的复制业', '文教体育用品制造业', '石油加工炼焦及核燃料加工业', '化学原料及化学制品制造业',
                      '医药制造业', '化学纤维制造业', '橡胶制品业', '塑料制品业', '非金属矿物制品业', '黑色金属冶炼及压延加工业',#10
                      '有色金属冶炼及压延加工业', '金属制品业', '通用设备制造业', '专用设备制造业', '交通运输设备制造业',
                      '电气机械及器材制造业', '通信设备计算机及其他电子设备制造业', '仪器仪表及文化办公用机械制造业', '工艺品及其他制造业']#9

        kind = pd.DataFrame()
        for j in range(n):
            a =  sort[j]
            a_j = a.groupby('省').sum() 
            a_j['产品数']=a.groupby('省').count().max(axis=1)
            a_j.reset_index(inplace=True)
            a_j[['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11',
                 '12']] = a_j[['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']].div(a_j['产品数'].values,axis=0)
            a_j.set_index('省',inplace=True)
            a1 =a_j.iloc[:,13:]
            a1['sum']=a1.apply(lambda x:sum(x),axis=1)
            a1['产业']=labels[j]
            kind = kind.append(a1)

#         kind.to_csv('全国各省产业产量占比年内变化_5year_mean_'+str(name)+'.csv')
    print('success')
    return kind


def calcul_weighted_factor_subsector(name):
    """ fraction of subsector IWW to national"""
#     read the file
    if name =='mining':
        d_minw = pd.read_excel('../工业企业用水效率/raw_data/用水情况/规模以上采矿业工业用水情况2008.xlsx')
        d = d_minw 
        name_C = '采矿业'
    elif name == 'manufacture':
        d_mauw =pd.read_excel('../工业企业用水效率/raw_data/用水情况/规模以上制造业工业用水情况2008.xls')
        d = d_mauw[:-2]  
        name_C = '制造业'
    else:
        d_ew =pd.read_excel('../工业企业用水效率/raw_data/用水情况/规模以上电力、燃气工业用水情况2008.xlsx')
        d = d_ew
        name_C = '电力、燃气的生产和供应业'

    d_c =d[~d['地区'].isin(['全国'])].groupby('产业').sum().iloc[:,:1]
    d_c.reset_index(inplace=True)
    d_c.rename(columns={'取水总量（单位：万立方米）':str(name)+'_water (10000 m3)'},inplace=True)

    ## national sector IWW
    C_value = float(d_c[~d_c['产业'].isin([name_C])].sum().values[1]) 
    #calculate the fraction of national subsector IWW to national sector 
    d_c['rate_sub_c'] = d_c[str(name)+'_water (10000 m3)']/C_value 

    # merge
    d_s = pd.merge(d.iloc[32:,:3],d_c,on='产业',how='left')
    #calculate the fraction
    d_s['rate_sub_p'] = d_s.apply(lambda x:x['取水总量（单位：万立方米）']/x[str(name)+'_water (10000 m3)'],axis=1)
#     d_s.to_csv('全国规模以上各产业工业用水占'+name+'的权重&各省占全国权重_2008v2.csv',index=False)
    print('weighted_sub ok')
    return d_s


def calcu_rate_ind(name):
    """
    estimate the seasonal variations in each industrial subsector
    """
#     d_w = pd.read_csv('全国规模以上各产业工业用水占'+str(name)+'的权重&各省占全国权重_2008.csv')
    d_w = calcul_weighted_factor_subsector(name)
    replacement_province(d_w)
    d_w.rename(columns={'地区':'省'},inplace=True)
#     kind_e = pd.read_csv('全国各省产业产量占比年内变化_5year_mean_'+str(name)+'.csv')
    kind = transfer_output_kind(name)
    if name == 'ele_heat':
        replacement_water(d_w)
        replacement_kind(kind)

    # monthly fraction of subsector IWW to national IWW 
    d_i_pre = pd.merge(kind,d_w,on=['省','产业'],how= 'left')
    #other mining ---ratio:0.000159 ,ignored
    d_i_pre[['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9', 'R10', 'R11',
             'R12']] = d_i_pre[['01', '02', '03', '04', '05', '06', '07', '08','09', '10', '11', 
                                '12']].mul(d_i_pre[d_i_pre.columns[-1]].values,axis=0)
    
    d_i = d_i_pre.groupby(['产业']).sum().iloc[:,-12:].T
    
    #工艺品及其他制造业----0.778703 
    #### output fraction is not equal to 1(just 15/31 provincial data)----the fraction of national IWW is little---0.008494    
    if name == 'manufacture':
        s_gyp = pd.DataFrame(d_i.T[d_i.T.index.isin(['工艺品及其他制造业'])].sum())#.sum()#0.778703
        s_gyp['工艺品及其他制造业'] = s_gyp[0]/0.778703
        d_i['工艺品及其他制造业'] = s_gyp.iloc[:,1:].values
        
    #总产业用水取水占比计算
    d_a_pre =  pd.merge(d_i.T,d_w.loc[d_w['省'].isin(['全国'])],on='产业',how='left')
    # d_mm_pre
    d_a_pre[['RR1', 'RR2', 'RR3', 'RR4', 'RR5', 'RR6', 'RR7', 'RR8', 'RR9', 'RR10', 'RR11',
             'RR12']] = d_a_pre[['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9', 'R10', 'R11',
                                 'R12']].mul(d_a_pre[d_a_pre.columns[-2]].values,axis=0)
    # d_mm_pre
    d_a = pd.DataFrame(d_a_pre.iloc[:,-12:].sum())#.sum()#0.997752
    d_a.rename(columns={0:'China_'+name}, inplace=True)
    d_a.reset_index(inplace=True)
    d_a.drop(['index'],axis=1,inplace=True)
    # d_mm
    
    #combine two sheets
    d_total = pd.concat([d_i.reset_index(),d_a],axis=1)
    d_total.drop(['index'],axis=1,inplace=True)
    
    # save the data
    d_total.to_csv(name+'产量年内占比及各二级产业全国产量年内占比_2006-2010mean.csv',index=False)
    print('calculate_rate_ind OK')
    return


if __name__=="__main__":
####     calcu_rate_ind('mining')
####     calcu_rate_ind('manufacture')
####     calcu_rate_ind('ele_heat')

