#%%
"""
Beregning og plot af diverse data og statistiske værdier for RTK- og FS-målingen i GNSS-nøjagtighedsundersøgelse

Kør Clean_GNSS_FS.py først og Clean_GNSS_RTK.py
Scriptet her læser da fra Cleaned_*.xlsx 
"""


import pyexcel
import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
import statistics
import re
import numpy as np
import scipy.stats as st
from mpl_toolkits.axes_grid1 import host_subplot
from datetime import datetime
from math import remainder




data = pyexcel.get_sheet(file_name="Cleaned_GNSS_RTK.xlsx", name_columns_by_row=0)
fs_data = pyexcel.get_sheet(file_name="Cleaned_GNSS_FS.xlsx", name_columns_by_row=0)

# RTK
punkt = data.column[1]
dato = data.column[2]
ellipsoidehøjde = data.column[3]
ellipsoidehøjdekvalitet = data.column[4]
meas_num = data.column[5]
instrument = data.column[6]
net = data.column[7]
sektor = data.column[8]
satellitter = data.column[9]
satellitter_gns = data.column[10]
difference = data.column[11]
PDOP = data.column[12]
dist_net = data.column[13]
noj = data.column[14]
femd = data.column[15]

# Fast static
fs_punkt = fs_data.column[1]
fs_ellipsoidehøjde = fs_data.column[4]
fs_difference = fs_data.column[5]
fs_instrument = fs_data.column[3]
fs_maaling = fs_data.column[2]
fs_dist_net1 = fs_data.column[6]
fs_dist_net2 = fs_data.column[7]
fs_noj = fs_data.column[8]
fs_femd = fs_data.column[9]


# Spring tomme felter over
for i, m in enumerate(fs_maaling):
    if not m in ['', ' ']:
        fs_maaling[i] = int(m)

for i, m in enumerate(meas_num):
    if not m in ['', ' ']:
        meas_num[i] = int(m)

#%%
"""
Funktioner benyttet
"""
def mean_std(df, kolonne, act=str):
    new_df = df.groupby(['Punkt', 'Måling nr.'])[str(kolonne)].agg(str(act)).reset_index()
    
    dato_df = df.groupby(['Punkt', 'Måling nr.'])['Dato'].agg('min').reset_index()
    sat_df = df.groupby(['Punkt', 'Måling nr.'])['Satellitter_gns'].agg('min').reset_index()
    PDOP_df = df.groupby(['Punkt', 'Måling nr.'])['PDOP'].agg('mean').reset_index()

    tem = new_df.merge(dato_df, how='inner', left_on=["Punkt", "Måling nr."], right_on=["Punkt","Måling nr."])
    temp = tem.merge(PDOP_df, how='inner', left_on=["Punkt", "Måling nr."], right_on=["Punkt","Måling nr."])
    mean_std = temp.merge(sat_df, left_on=["Punkt", "Måling nr."], right_on=["Punkt","Måling nr."])
    return mean_std

def diff_diff(first,second):
    first = first.set_index(['Punkt'])
    second = second.set_index(['Punkt'])
    fix = first.index
    six = second.index
    if not fix.equals(six):
        for f in fix:
            if not f in six:
                first.drop(f)

        for s in six:
            if not s in fix:
                second = second.drop(s)


    sr_diff_diff = first['Difference'] - second['Difference']
    first['til_2.maaling'] = sr_diff_diff.values

    return first

def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), st.sem(a)
    h = se * st.t.ppf((1 + confidence) / 2., n-1)
    return m, m-h, m+h

#%%
"""
Indlæsning af data i dataframe
"""

# RTK
data_dict = {'Punkt': punkt, 'Dato': dato,'Ellipsoidehøjde': ellipsoidehøjde,'Ellipsoidehøjdekvalitet': ellipsoidehøjdekvalitet,
             'Måling nr.': meas_num, 'Instrument': instrument, 'Net': net, 'Sektor': sektor, 'Satellitter': satellitter, 
             'Satellitter_gns': satellitter_gns, 'Difference': difference, 'PDOP': PDOP, 'Afstand til referencestation': dist_net, 'Forventet nøjagtighed': noj, '5D': femd}
df = pd.DataFrame(data_dict, columns = ['Punkt','Dato','Ellipsoidehøjde','Ellipsoidehøjdekvalitet','Måling nr.','Instrument',
                                        'Net','Sektor','Satellitter', 'Satellitter_gns', 'Difference', 'PDOP', 'Afstand til referencestation', 'Forventet nøjagtighed', '5D'])

# Fast static
fs_data_dict = {'Punkt': fs_punkt, 'Ellipsoidehøjde': fs_ellipsoidehøjde, 'Måling nr.': fs_maaling, 'Instrument': fs_instrument, 
                'Difference': fs_difference, 'Afstand1': fs_dist_net1, 'Afstand2': fs_dist_net2, 'Forventet nøjagtighed': fs_noj, '5D': fs_femd}
fs_df = pd.DataFrame(fs_data_dict, columns = ['Punkt', 'Ellipsoidehøjde', 'Måling nr.', 'Instrument', 'Difference', 'Afstand1', 'Afstand2', 'Forventet nøjagtighed', '5D'])
#%%
# CRAAAAAAAAAAAAAAAAAAAAP
#satellit gennemsnit fra RTK merges til Fast static dataframe 
#fs_df['Satellitter_gns'] = fs_df.merge(df, on='Punkt')['Satellitter_gns']
fs_dftest = fs_df.merge(df, left_on='Punkt', right_on='Punkt', how="inner")


#%%
"""
Fjern outliers
"""
df = df[:][(df.Difference >= -47.5) & (df.Difference <= 60.5)]
df = df[:][(df.PDOP < 3.5)]
fs_df = fs_df[:][(fs_df.Difference > -39.9 ) & (fs_df.Difference < 50.0)]
#%%
"""
Opdel fast static
"""
# Del fast static i instrumenter
fs_Leica = fs_df[:][fs_df.Instrument == 'H']
fs_Trimble = fs_df[:][fs_df.Instrument == 'G']
fs_Sept = fs_df[:][fs_df.Instrument == 'S']


# Fast static mean difference for punkter (både måling 1 og 2)
fs_mean_Leica = fs_Leica.groupby(['Punkt', 'Måling nr.'])['Difference'].agg('mean').reset_index()
fs_mean_Trimble =  fs_Trimble.groupby(['Punkt', 'Måling nr.'])['Difference'].agg('mean').reset_index()
fs_mean_Sept =  fs_Sept.groupby(['Punkt', 'Måling nr.'])['Difference'].agg('mean').reset_index()


# Del fast static i måling nr 1 og 2
fs_first_Leica= fs_mean_Leica[:][fs_mean_Leica['Måling nr.'] == 1]
fs_second_Leica= fs_mean_Leica[:][fs_mean_Leica['Måling nr.'] == 2]
fs_first_Trimble= fs_mean_Trimble[:][fs_mean_Trimble['Måling nr.'] == 1]
fs_second_Trimble= fs_mean_Trimble[:][fs_mean_Trimble['Måling nr.'] == 2]
fs_first_Sept= fs_mean_Sept[:][fs_mean_Sept['Måling nr.'] == 1]
fs_second_Sept= fs_mean_Sept[:][fs_mean_Sept['Måling nr.'] == 2]


#%%
"""
Opdel RTK
"""
# Del i net (GPSnet og Smartnet)
GPS_df = df[:][df.Net == 'G']
smart_df = df[:][df.Net == 'H']

# Del i instrumenter
Leica_df = df[:][df.Instrument == 'H']
Trimble_df = df[:][df.Instrument == 'G']
Sept_df = df[:][df.Instrument == 'S']

#%%
"""
Beregn middeldifferencer og standardafvigelser
"""

# RTK: Få middeldifference for punkter (måling 1 og 2)
mean_Leica = mean_std(Leica_df, 'Difference', "mean")
mean_Trimble = mean_std(Trimble_df, 'Difference', "mean")
mean_Sept = mean_std(Sept_df, 'Difference', "mean")
mean_GPS = mean_std(GPS_df, 'Difference', "mean")
mean_smart = mean_std(smart_df, 'Difference', "mean")


# RTK: Få standardafvigelse for difference for punkter (måling 1 og 2)
std_Leica = mean_std(Leica_df, 'Difference', "std")
std_Trimble = mean_std(Trimble_df, 'Difference', "std")
std_Sept = mean_std(Sept_df, 'Difference', "std")
std_GPS = mean_std(GPS_df, 'Difference', "std")
std_smart = mean_std(smart_df, 'Difference', "std")


# FS: middeldifferencer for målinger
fs_h_mean = fs_df.groupby(['Punkt', 'Måling nr.'])['Ellipsoidehøjde'].agg('mean').reset_index()
fs_h_mean = fs_h_mean.rename(columns={"Ellipsoidehøjde":"Difference"})

# FS: standardafvigelse for målinger (std af ca 3 målinger for hhv. måling 1 og 2)
fs_h_std = fs_df.groupby(['Punkt', 'Måling nr.'])['Ellipsoidehøjde'].agg('std').reset_index()
fs_h_std = fs_h_std.rename(columns={"Ellipsoidehøjde":"Standardafvigelse"})


#%%
# Find tid mellem 1. og 2. måling
first_df = df[:][df['Måling nr.'] == 1]
second_df = df[:][df['Måling nr.'] == 2]

dato_diff = []
dato_diff_pkt = []
dato_fd = []
unikke_pkter = np.unique(df.Punkt)
for pkt in unikke_pkter:
    first = first_df[:][first_df['Punkt'] == pkt]
    second = second_df[:][second_df['Punkt'] == pkt]
    if len(first.index) > 0 and len(second.index) > 0:
        min_first = first.Dato.min()
        min_second = second.Dato.min()
        d_diff = min_second - min_first
        dato_diff.append(d_diff.days*24 + d_diff.seconds/3600)
        dato_diff_pkt.append(pkt)
        dato_fd.append(first.iloc[0]['5D'])

dato_dict = {'Punkt': dato_diff_pkt, 'Dato difference': dato_diff, '5D': dato_fd}
dato_df = pd.DataFrame(dato_dict, columns = ['Punkt', 'Dato difference', '5D'])

dato_df['modulo'] = dato_df['Dato difference'] % 24


#%%
"""
Middeldifference og forventet nøjagtighed for hvert punkt delt i net
"""
# RTK: Middeldifference uafhængig af instrument og tid, splittet i net i hvert sit dataframe
mean_GPS_df = GPS_df.groupby(['Punkt'])['Difference'].agg('mean').reset_index()
fd_df = GPS_df.groupby(['Punkt'])['5D'].first().reset_index()
usik_df = GPS_df.groupby(['Punkt'])['Forventet nøjagtighed'].agg('min').reset_index()
temp = mean_GPS_df.merge(fd_df, how='inner', left_on=["Punkt"], right_on=["Punkt"])
mean_usik_GPS = temp.merge(usik_df, how='inner', left_on=["Punkt"], right_on=["Punkt"])
#Del i 5D punkter og ikke 5D punkter
mean_usik_GPS_fd = mean_usik_GPS[:][mean_usik_GPS['5D'] == '5D']
mean_usik_GPS_ufd = mean_usik_GPS[:][mean_usik_GPS['5D'] == '']

mean_smart_df = smart_df.groupby(['Punkt'])['Difference'].agg('mean').reset_index()
fd_df = smart_df.groupby(['Punkt'])['5D'].first().reset_index()
usik_df = smart_df.groupby(['Punkt'])['Forventet nøjagtighed'].agg('min').reset_index()
temp = mean_smart_df.merge(fd_df, how='inner', left_on=["Punkt"], right_on=["Punkt"])
mean_usik_smart = temp.merge(usik_df, how='inner', left_on=["Punkt"], right_on=["Punkt"])
#Del i 5D punkter og ikke 5D punkter
mean_usik_smart_fd = mean_usik_smart[:][mean_usik_smart['5D'] == '5D']
mean_usik_smart_ufd = mean_usik_smart[:][mean_usik_smart['5D'] == '']

# RTK: Middeldifference uafhængig af instrument, tid og net 
mean_rtk_df = df.groupby(['Punkt'])['Difference'].agg('mean').reset_index()
fd_df = df.groupby(['Punkt'])['5D'].first().reset_index()
usik_dfmin = df.groupby(['Punkt'])['Forventet nøjagtighed'].agg('min').reset_index()
usik_dfmaks = df.groupby(['Punkt'])['Forventet nøjagtighed'].agg('max').reset_index()
temp = mean_rtk_df.merge(fd_df, how='inner', left_on=["Punkt"], right_on=["Punkt"])
temp2 = temp.merge(usik_dfmin, how='inner', left_on=["Punkt"], right_on=["Punkt"])
mean_usik_RTK = temp2.merge(usik_dfmaks, how='inner', left_on=["Punkt"], right_on=["Punkt"])
#Del i 5D punkter og ikke 5D punkter
mean_usik_rtk_fd = mean_usik_RTK[:][mean_usik_RTK['5D'] == '5D']
mean_usik_rtk_ufd = mean_usik_RTK[:][mean_usik_RTK['5D'] == '']

# RTK: Middeldifference uafhængig af instrument og tid, splittet op i net i samme dataframe
mean_df = df.groupby(['Punkt', 'Net'])['Difference'].agg('mean').reset_index()
fd_df = df.groupby(['Punkt', 'Net'])['5D'].first().reset_index()
usik_df = df.groupby(['Punkt', 'Net'])['Forventet nøjagtighed'].first().reset_index()
temp = mean_df.merge(fd_df, how='inner', left_on=["Punkt", 'Net'], right_on=["Punkt", 'Net'])
mean_usik = temp.merge(usik_df, how='inner', left_on=["Punkt", 'Net'], right_on=["Punkt", 'Net'])
#Del i 5D punkter og ikke 5D punkter
mean_usik_fd = mean_usik[:][mean_usik['5D'] == '5D']
mean_usik_ufd = mean_usik[:][mean_usik['5D'] == '']
#%%

# FS: Middeldifference uafhængig af instrument og tid
mean_fs_df = fs_df.groupby(['Punkt'])['Difference'].agg('mean').reset_index()
fd_df = fs_df.groupby(['Punkt'])['5D'].first().reset_index()
usik_df = fs_df.groupby(['Punkt'])['Forventet nøjagtighed'].agg('min').reset_index()
temp = mean_fs_df.merge(fd_df, how='inner', left_on=["Punkt"], right_on=["Punkt"])
mean_usik_fs = temp.merge(usik_df, how='inner', left_on=["Punkt"], right_on=["Punkt"])
#Del i 5D punkter og ikke 5D punkter
mean_usik_fs_fd = mean_usik_fs[:][mean_usik_fs['5D'] == '5D']
mean_usik_fs_ufd = mean_usik_fs[:][mean_usik_fs['5D'] == '']
#%%

"""
Dataframes for middeldifference af alle målinger for hvert punkt (uden outliers) med konfidensinterval og forventet nøjagtighed
"""
rtk_fn = []
rtk_mean = []
rtk_ned = []
rtk_op = []
rtk_yerr = []
rtk_fd = []
df['konfplotpunkt'] = df['Punkt'] + '_' + df['Net']
unikke_pkter = np.unique(df.konfplotpunkt)
unikke_pkter.sort()
for pkt in unikke_pkter:
    pkt_df = df[:][df.konfplotpunkt == pkt]
    pkt_m_c = mean_confidence_interval(pkt_df.Difference)
    rtk_fn.append(pkt_df['Forventet nøjagtighed'].min())
    rtk_mean.append(pkt_m_c[0])
    rtk_ned.append(pkt_m_c[1])
    rtk_op.append(pkt_m_c[2])
    rtk_yerr.append(pkt_m_c[2]-pkt_m_c[0])
    rtk_fd.append(pkt_df.iloc[0]['5D'])


konfi_dict = {'Plotpunkt': unikke_pkter, 'Middeldifference': rtk_mean, 'Nedre grænse': rtk_ned, 'Øvre grænse': rtk_op, 'Yerror':rtk_yerr, 
             'Forventet nøjagtighed': rtk_fn,'5D': rtk_fd}
konfi_df = pd.DataFrame(konfi_dict, columns = ['Plotpunkt', 'Middeldifference', 'Nedre grænse', 'Øvre grænse', 'Yerror', 
                                                   'Forventet nøjagtighed', '5D'])

fs_fn = []
fs_mean = []
fs_ned = []
fs_op = []
fs_yerr = []
fs_fd = []
fs_unikke_pkter = np.unique(fs_df.Punkt)
fs_unikke_pkter.sort()
for pkt in fs_unikke_pkter:
    fs_pkt = fs_df[:][fs_df.Punkt == pkt]
    fs_pkt_m_c = mean_confidence_interval(fs_pkt.Difference)
    fs_fn.append(fs_pkt['Forventet nøjagtighed'].min())
    fs_mean.append(fs_pkt_m_c[0])
    fs_ned.append(fs_pkt_m_c[1])
    fs_op.append(fs_pkt_m_c[2])
    fs_yerr.append(fs_pkt_m_c[2]-fs_pkt_m_c[0])
    fs_fd.append(fs_pkt.iloc[0]['5D'])
    

fs_konfi_dict = {'Punkt': fs_unikke_pkter, 'Middeldifference': fs_mean, 'Nedre grænse': fs_ned, 'Øvre grænse': fs_op, 
                     'Yerror':fs_yerr, 'Forventet nøjagtighed': fs_fn, '5D': fs_fd}
fs_konfi_df = pd.DataFrame(fs_konfi_dict, columns = ['Punkt', 'Middeldifference', 'Nedre grænse', 'Øvre grænse', 
                                                     'Yerror', 'Forventet nøjagtighed', '5D'])


#%%
"""
PLOTS
"""
n=1
# # Vi ændrer lige figurstørrelsen:
fig_size = plt.rcParams["figure.figsize"]
# let's make the plots a bit bigger than the default
# set figure width to 14 and height to 6
fig_size[0] = 14
fig_size[1] = 8
plt.rcParams["figure.figsize"] = fig_size


'''
Plots med konfidensinterval
'''
# Plot RTK: Nøjagtighed (mean) med konfidensinterval og forventet nøjagtighed 
plt.figure(n)
host = host_subplot(111)
par = host.twinx()

x = konfi_df.sort_values(by='Forventet nøjagtighed', ascending=False)
host.errorbar(x.Plotpunkt, x.Middeldifference, yerr=x.Yerror,capsize=0.8, fmt='.')
y = x['Forventet nøjagtighed']
y2 = -y
par.bar(x.Plotpunkt, y, color='silver', label = 'Expected accuracy')
par.bar(x.Plotpunkt, y2, color='silver')
host.set_ylim(-60, 60)
par.set_ylim(-60, 60)
plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9, top=0.8)
plt.legend(fontsize='xx-small',loc='best')
plt.xticks(rotation='vertical')
plt.ylabel("Difference [mm]")
plt.title('RTK: Difference with confidence interval \n \n all points')
plt.savefig("Figurer/RTK_conf_all_sort.png")
n+=1


# Plot RTK 5D punkter. Nøjagtighed (mean) med konfidensinterval og forventet nøjagtighed 
plt.figure(n)
host = host_subplot(111)
par = host.twinx()

x = konfi_df[:][konfi_df['5D'] == '5D'].sort_values(by='Forventet nøjagtighed', ascending=False)
host.errorbar(x.Plotpunkt, x.Middeldifference, yerr=x.Yerror,capsize=0.8, fmt='.')
y = x['Forventet nøjagtighed']
y2 = -y
par.bar(x.Plotpunkt, y, color='silver', label = 'Expected accuracy')
par.bar(x.Plotpunkt, y2, color='silver')
host.set_ylim(-60, 60)
par.set_ylim(-60, 60)
plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9, top=0.8)
plt.legend(fontsize='xx-small',loc='best')
plt.xticks(rotation='vertical')
plt.ylabel("Difference [mm]")
plt.title('RTK: Difference with confidence interval \n \n 5D points')
plt.savefig("Figurer/RTK_conf_5D_sort.png")
n+=1

# Plot RTK non-5D punkter. Nøjagtighed (mean) med konfidensinterval og forventet nøjagtighed 
plt.figure(n)
host = host_subplot(111)
par = host.twinx()

x = konfi_df[:][konfi_df['5D'] == ''].sort_values(by='Forventet nøjagtighed', ascending=False)
host.errorbar(x.Plotpunkt, x.Middeldifference, yerr=x.Yerror,capsize=0.8, fmt='.')
y = x['Forventet nøjagtighed']
y2 = -y
par.bar(x.Plotpunkt, y, color='silver', label = 'Expected accuracy')
par.bar(x.Plotpunkt, y2, color='silver')
host.set_ylim(-60, 60)
par.set_ylim(-60, 60)
plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9, top=0.8)
plt.legend(fontsize='xx-small',loc='best')
plt.xticks(rotation='vertical')
plt.ylabel("Difference [mm]")
plt.title('RTK: Difference with confidence interval \n \n non-5D points')
plt.savefig("Figurer/RTK_conf_non5D_sort.png")
n+=1
#%%

# Plot FS alle: Middel med konfidensinterval og forventet nøjagtighed
plt.figure(n)
host = host_subplot(111)
par = host.twinx()

x = fs_konfi_df.sort_values(by='Forventet nøjagtighed', ascending=False)
host.errorbar(x.Punkt, x.Middeldifference, yerr=x.Yerror,capsize=0.8, fmt='.')
y = x['Forventet nøjagtighed']
y2 = -y
par.bar(x.Punkt, y, color='silver', label = 'Expected accuracy')
par.bar(x.Punkt, y2, color='silver')
host.set_ylim(-60, 60)
par.set_ylim(-60, 60)
plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9, top=0.8)
plt.legend(fontsize='xx-small',loc='best')
plt.xticks(rotation='vertical')
plt.ylabel("Difference [mm]")
plt.title('FS: Difference with confidence interval \n \n all points')
plt.savefig("Figurer/FS_conf_all_sort.png")
n+=1


# Plot FS 5D punkter: Middel med konfidensinterval og forventet nøjagtighed
plt.figure(n)
host = host_subplot(111)
par = host.twinx()

x = fs_konfi_df[:][fs_konfi_df['5D'] == '5D'].sort_values(by='Forventet nøjagtighed', ascending=False)
host.errorbar(x.Punkt, x.Middeldifference, yerr=x.Yerror,capsize=0.8, fmt='.')
y = x['Forventet nøjagtighed']
y2 = -y
par.bar(x.Punkt, y, color='silver', label = 'Expected accuracy')
par.bar(x.Punkt, y2, color='silver')
host.set_ylim(-60, 60)
par.set_ylim(-60, 60)
plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9, top=0.8)
plt.legend(fontsize='xx-small',loc='best')
plt.xticks(rotation='vertical')
plt.ylabel("Difference [mm]")
plt.title('FS: Difference with confidence interval \n \n 5D points')
plt.savefig("Figurer/FS_conf_5D_sort.png")
n+=1


# Plot FS non-5D punkter: Middel med konfidensinterval og forventet nøjagtighed
plt.figure(n)
host = host_subplot(111)
par = host.twinx()

x = fs_konfi_df[:][fs_konfi_df['5D'] == ''].sort_values(by='Forventet nøjagtighed', ascending=False)
host.errorbar(x.Punkt, x.Middeldifference, yerr=x.Yerror,capsize=0.8, fmt='.')
y = x['Forventet nøjagtighed']
y2 = -y
par.bar(x.Punkt, y, color='silver', label = 'Expected accuracy')
par.bar(x.Punkt, y2, color='silver')
host.set_ylim(-60, 60)
par.set_ylim(-60, 60)
plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9, top=0.8)
plt.legend(fontsize='xx-small',loc='best')
plt.xticks(rotation='vertical')
plt.ylabel("Difference [mm]")
plt.title('FS: Difference with confidence interval \n \n non-5D points')
plt.savefig("Figurer/FS_conf_non5D_sort.png")
n+=1
#%%


# Plot tid mellem 1. og 2. måling for alle punkter
plt.figure(n)
dato_df.plot(kind='scatter', x='Punkt', y='modulo', color='b', marker = '.')

plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9, top=0.9)
plt.xticks(rotation='vertical')
plt.ylabel("Time difference [hr]")
plt.grid(axis='y')
plt.axhline(y=5) # døgn plus 5 timer
plt.axhline(y=19) # døgn minus 5 timer
plt.title('Time difference between 1. and 2. measurement \n \n For all points')
plt.savefig("Figurer/RTK_tidsforskel_ml_1_2_all.png")
n+=1

# Plot tid mellem 1. og 2. måling for 5D
plt.figure(n)
dato_df[:][dato_df['5D'] == '5D'].plot(kind='scatter', x='Punkt', y='modulo', color='b', marker = '.')

plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9, top=0.9)
plt.xticks(rotation='vertical')
plt.ylabel("Time difference [hr]")
plt.grid(axis='y')
plt.axhline(y=5) # døgn plus 5 timer
plt.axhline(y=19) # døgn minus 5 timer
plt.title('Time difference between 1. and 2. measurement \n \n For 5D points')
plt.savefig("Figurer/RTK_tidsforskel_ml_1_2_5D.png")
n+=1


# Plot tid mellem 1. og 2. måling for ikke-5D
plt.figure(n)
dato_df[:][dato_df['5D'] == ''].plot(kind='scatter', x='Punkt', y='modulo', color='b', marker = '.')

plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9, top=0.9)
plt.xticks(rotation='vertical')
plt.ylabel("Time difference [hr]")
plt.grid(axis='y')
plt.axhline(y=5) # døgn plus 5 timer
plt.axhline(y=19) # døgn minus 5 timer
plt.title('Time difference between 1. and 2. measurement \n \n For non-5D points')
plt.savefig("Figurer/RTK_tidsforskel_ml_1_2_non-5D.png")
n+=1


# %%
