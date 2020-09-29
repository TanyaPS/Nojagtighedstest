"""
Læser Excel fil Cleaned_GNSS_RTK.xlsx, fra Clean_Excel.py
"""
import pyexcel
import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
from datetime import datetime

data = pyexcel.get_sheet(file_name="Cleaned_GNSS_RTK.xlsx", name_columns_by_row=0)

# data = pyexcel.get_sheet(file_name="GNSS_RTK.xlsx", name_columns_by_row=0)


# sektor = data.column[12]
# pkt = data.column[2]
# date = data.column[9]
# sats = data.column[19]
# sats_min = data.column[20]
# diff = data.column[8]
# instrument =  data.column[14]
# net = data.column[13]
# sektor = data.column[12]

punkt = data.column[1]
dato = data.column[2]
ellipsoidehøjdekvalitet = data.column[3]
meas_num = data.column[4]
instrument = data.column[5]
net = data.column[6]
sektor = data.column[7]
satellitter = data.column[8]
satellitter_gns = data.column[9]
difference = data.column[10]

def mean_sat(list_n_i, meanby):
    mean_net_i_land = list_n_i[0].groupby(['Punkt'])[meanby].agg('mean').reset_index()
    mean_net_i_lav = list_n_i[1].groupby(['Punkt'])[meanby].agg('mean').reset_index()
    mean_net_i_høj = list_n_i[2].groupby(['Punkt'])[meanby].agg('mean').reset_index()

    d_net_i_land = list_n_i[0].groupby(['Punkt'])['Dato'].agg('min').reset_index()
    d_net_i_lav = list_n_i[1].groupby(['Punkt'])['Dato'].agg('min').reset_index()
    d_net_i_høj = list_n_i[2].groupby(['Punkt'])['Dato'].agg('min').reset_index()

    net_i_land = pd.merge(mean_net_i_land, d_net_i_land, on='Punkt')
    net_i_lav = pd.merge(mean_net_i_lav, d_net_i_lav, on='Punkt')
    net_i_høj = pd.merge(mean_net_i_høj, d_net_i_høj, on='Punkt')
    
    list_of_land_lav_høj = [net_i_land, net_i_lav, net_i_høj]
    return list_of_land_lav_høj

#satellitter = []

# for i, sat in enumerate(sats):
#     if sat == '':
#         satellitter.append(int(sats_min[i]))
#     else:
#         satellitter.append(int(sat))

#     if instrument[i] == 'S':
#         d = date[i]
#         date[i] = d[3:5] + '-' + d[0:2] + d[5:]
#     elif instrument[i] == 'G':
#         d = date[i]
#         date[i] = d[8:] + d[4:7] + '-' + d[0:4]
#     date[i] = datetime.strptime(date[i], '%d-%m-%Y')
#     diff[i] = float(diff[i])

data_dict = {'satellitter': satellitter, 'Satellitter_gns': satellitter_gns, 'Difference': difference, 'Instrument': instrument, 'Net': net, 'Sektor': sektor, 'Punkt': punkt, 'Dato': dato}
df = DataFrame(data_dict,columns=['satellitter', 'Satellitter_gns', 'Difference', 'Instrument', 'Net', 'Sektor', 'Punkt', 'Dato'])
df.sort_values(by=['Dato'])
    

#Del for antal satelitter
lav_sat = df[:][df.Satellitter_gns < 18]
mellem_sat = df[:][(df.Satellitter_gns >= 18) & (df.Satellitter_gns <= 20)]
høj_sat = df[:][df.Satellitter_gns > 20]
sat_list = [lav_sat, mellem_sat, høj_sat]

#Del for sektor
land = df[:][df.Sektor == 'land']
lav_beb = df[:][(df.Sektor == 'lav bebyg') | (df.Sektor == 'erhverv')]
høj_beb = df[:][(df.Sektor == 'hoej bebyg') | (df.Sektor == 'bykerne')]
sekt_list = [land, lav_beb, høj_beb]


net_list_H = []
net_list_S = []
net_list_G = []
k_net_list_H = []
k_net_list_G = []

#Del i net for sektorer
for sekt_df in sekt_list:
    net_list_H.append(sekt_df[:][sekt_df.Net == 'H'])
    net_list_S.append(sekt_df[:][sekt_df.Net == 'S'])
    net_list_G.append(sekt_df[:][sekt_df.Net == 'G'])



#Del i net for antal satellitter 
for sat_df in sat_list:
    k_net_list_H.append(sat_df[:][sat_df.Net == 'H'])
    k_net_list_G.append(sat_df[:][sat_df.Net == 'G'])


list_H_Leica = []
list_H_Trim = []
list_H_Sept= []
list_S_Leica = []
list_S_Trim = []
list_S_Sept = []
list_G_Leica = []
list_G_Trim = []
list_G_Sept = []

#Del i instrumenter for sektorer
for net_df in net_list_H:
    list_H_Leica.append(net_df[:][net_df.Instrument == 'H'])
    list_H_Trim.append(net_df[:][net_df.Instrument == 'G'])
    list_H_Sept.append(net_df[:][net_df.Instrument == 'S'])


for net_df in net_list_S:
    list_S_Leica.append(net_df[:][net_df.Instrument == 'H'])
    list_S_Trim.append(net_df[:][net_df.Instrument == 'G'])
    list_S_Sept.append(net_df[:][net_df.Instrument == 'S'])

for net_df in net_list_G:
    list_G_Leica.append(net_df[:][net_df.Instrument == 'H'])
    list_G_Trim.append(net_df[:][net_df.Instrument == 'G'])
    list_G_Sept.append(net_df[:][net_df.Instrument == 'S'])


#Del i instrumenter for antal satellitter (u sdfenet)
k_list_H_Leica = []
k_list_H_Trim = []
k_list_H_Sept= []
k_list_G_Leica = []
k_list_G_Trim = []
k_list_G_Sept = []


for net_df in k_net_list_H:
    k_list_H_Leica.append(net_df[:][net_df.Instrument == 'H'])
    k_list_H_Trim.append(net_df[:][net_df.Instrument == 'G'])
    k_list_H_Sept.append(net_df[:][net_df.Instrument == 'S'])

for net_df in k_net_list_G:
    k_list_G_Leica.append(net_df[:][net_df.Instrument == 'H'])
    k_list_G_Trim.append(net_df[:][net_df.Instrument == 'G'])
    k_list_G_Sept.append(net_df[:][net_df.Instrument == 'S'])

#mean for hvert punkt for sektorer
#For net H
H_Leica = mean_sat(list_H_Leica, 'satellitter')
H_Trim = mean_sat(list_H_Trim, 'satellitter')
H_Sept = mean_sat(list_H_Sept, 'satellitter')

#for net S
S_Leica = mean_sat(list_S_Leica, 'satellitter')
S_Trim = mean_sat(list_S_Trim, 'satellitter')
S_Sept = mean_sat(list_S_Sept, 'satellitter')

#for net G
G_Leica = mean_sat(list_G_Leica, 'satellitter')
G_Trim = mean_sat(list_G_Trim, 'satellitter')
G_Sept = mean_sat(list_G_Sept, 'satellitter')


#mean for hvert punkt for antal satellitter
#For net H
k_H_Leica = mean_sat(k_list_H_Leica, 'Difference')
k_H_Trim = mean_sat(k_list_H_Trim, 'Difference')
k_H_Sept = mean_sat(k_list_H_Sept, 'Difference')

#for net G
k_G_Leica = mean_sat(k_list_G_Leica, 'Difference')
k_G_Trim = mean_sat(k_list_G_Trim, 'Difference')
k_G_Sept = mean_sat(k_list_G_Sept, 'Difference')



ax1 = H_Leica[0].plot(kind='scatter', x='Dato', y='satellitter', color='r', label = 'Leica på Smartnet')    
ax2 = H_Trim[0].plot(kind='scatter', x='Dato', y='satellitter', color='r', marker = 's', ax=ax1, label = 'Trimble på Smartnet')    
ax3 = H_Sept[0].plot(kind='scatter', x='Dato', y='satellitter', color='r', marker = '*', ax=ax1, label = 'Septentrio Smartnet')
#ax4 = S_Leica[0].plot(kind='scatter', x='Dato', y='satellitter', color='b', ax=ax1, label = 'Leica på SDFEnet')    
#ax5 = S_Trim[0].plot(kind='scatter', x='Dato', y='satellitter', color='b', marker = 's', ax=ax1, label = 'Trimble på SDFEnet')    
#ax6 = S_Sept[0].plot(kind='scatter', x='Dato', y='satellitter', color='b', marker = '*', ax=ax1, label = 'Septentrio på SDFEnet')
ax7 = G_Leica[0].plot(kind='scatter', x='Dato', y='satellitter', color='g', ax=ax1, label = 'Leica på GPSnet')    
ax8 = G_Trim[0].plot(kind='scatter', x='Dato', y='satellitter', color='g', marker = 's', ax=ax1, label = 'Trimble på GPSnet')    
ax9 = G_Sept[0].plot(kind='scatter', x='Dato', y='satellitter', color='g', marker = '*', ax=ax1, label = 'Septentrio på GPSnet')

plt.subplots_adjust(left=0.1, bottom=0.25, right=0.6, top=0.9)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.xticks(rotation='vertical')
plt.title('Åbent land')


ax10 = H_Leica[1].plot(kind='scatter', x='Dato', y='satellitter', color='r', label = 'Leica på Smartnet')    
ax20 = H_Trim[1].plot(kind='scatter', x='Dato', y='satellitter', color='r', marker = 's', ax=ax10, label = 'Trimble på Smartnet')    
ax30 = H_Sept[1].plot(kind='scatter', x='Dato', y='satellitter', color='r', marker = '*', ax=ax10, label = 'Septentrio Smartnet')
#ax40 = S_Leica[1].plot(kind='scatter', x='Dato', y='satellitter', color='b', ax=ax10, label = 'Leica på SDFEnet')    
#ax50 = S_Trim[1].plot(kind='scatter', x='Dato', y='satellitter', color='b', marker = 's', ax=ax10, label = 'Trimble på SDFEnet')    
#ax60 = S_Sept[1].plot(kind='scatter', x='Dato', y='satellitter', color='b', marker = '*', ax=ax10, label = 'Septentrio på SDFEnet')
ax70 = G_Leica[1].plot(kind='scatter', x='Dato', y='satellitter', color='g', ax=ax10, label = 'Leica på GPSnet')    
ax80 = G_Trim[1].plot(kind='scatter', x='Dato', y='satellitter', color='g', marker = 's', ax=ax10, label = 'Trimble på GPSnet')    
ax90 = G_Sept[1].plot(kind='scatter', x='Dato', y='satellitter', color='g', marker = '*', ax=ax10, label = 'Septentrio på GPSnet')

plt.subplots_adjust(left=0.1, bottom=0.25, right=0.6, top=0.9)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.xticks(rotation='vertical')
plt.title('Lav bebyggelse')




ax100 = H_Leica[2].plot(kind='scatter', x='Dato', y='satellitter', color='r', label = 'Leica på Smartnet')    
ax200 = H_Trim[2].plot(kind='scatter', x='Dato', y='satellitter', color='r', marker = 's', ax=ax100, label = 'Trimble på Smartnet')    
ax300 = H_Sept[2].plot(kind='scatter', x='Dato', y='satellitter', color='r', marker = '*', ax=ax100, label = 'Septentrio Smartnet')
#ax400 = S_Leica[2].plot(kind='scatter', x='Dato', y='satellitter', color='b', ax=ax100, label = 'Leica på SDFEnet')    
#ax500 = S_Trim[2].plot(kind='scatter', x='Dato', y='satellitter', color='b', marker = 's', ax=ax100, label = 'Trimble på SDFEnet')    
#ax600 = S_Sept[2].plot(kind='scatter', x='Dato', y='satellitter', color='b', marker = '*', ax=ax100, label = 'Septentrio på SDFEnet')
ax700 = G_Leica[2].plot(kind='scatter', x='Dato', y='satellitter', color='g', ax=ax100, label = 'Leica på GPSnet')    
ax800 = G_Trim[2].plot(kind='scatter', x='Dato', y='satellitter', color='g', marker = 's', ax=ax100, label = 'Trimble på GPSnet')    
ax900 = G_Sept[2].plot(kind='scatter', x='Dato', y='satellitter', color='g', marker = '*', ax=ax100, label = 'Septentrio på GPSnet')

plt.subplots_adjust(left=0.1, bottom=0.25, right=0.6, top=0.9)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.xticks(rotation='vertical')
plt.title('Høj bebyggelse')

kp1 = k_H_Leica[0].plot(kind='scatter', x='Dato', y='Difference', color='r', label = 'Leica på Smartnet')    
kp2 = k_H_Trim[0].plot(kind='scatter', x='Dato', y='Difference', color='r', marker = 's', ax=kp1, label = 'Trimble på Smartnet')    
kp3 = k_H_Sept[0].plot(kind='scatter', x='Dato', y='Difference', color='r', marker = '*', ax=kp1, label = 'Septentrio Smartnet')
kp4 = k_G_Leica[0].plot(kind='scatter', x='Dato', y='Difference', color='g', ax=kp1, label = 'Leica på GPSnet')    
kp5 = k_G_Trim[0].plot(kind='scatter', x='Dato', y='Difference', color='g', marker = 's', ax=kp1, label = 'Trimble på GPSnet')    
kp6 = k_G_Sept[0].plot(kind='scatter', x='Dato', y='Difference', color='g', marker = '*', ax=kp1, label = 'Septentrio på GPSnet')

plt.subplots_adjust(left=0.1, bottom=0.25, right=0.6, top=0.9)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.xticks(rotation='vertical')
plt.title('Under 18 satellitter')


kp1 = k_H_Leica[1].plot(kind='scatter', x='Dato', y='Difference', color='r', label = 'Leica på Smartnet')    
kp2 = k_H_Trim[1].plot(kind='scatter', x='Dato', y='Difference', color='r', marker = 's', ax=kp1, label = 'Trimble på Smartnet')    
kp3 = k_H_Sept[1].plot(kind='scatter', x='Dato', y='Difference', color='r', marker = '*', ax=kp1, label = 'Septentrio Smartnet')
kp4 = k_G_Leica[1].plot(kind='scatter', x='Dato', y='Difference', color='g', ax=kp1, label = 'Leica på GPSnet')    
kp5 = k_G_Trim[1].plot(kind='scatter', x='Dato', y='Difference', color='g', marker = 's', ax=kp1, label = 'Trimble på GPSnet')    
kp6 = k_G_Sept[1].plot(kind='scatter', x='Dato', y='Difference', color='g', marker = '*', ax=kp1, label = 'Septentrio på GPSnet')

plt.subplots_adjust(left=0.1, bottom=0.25, right=0.6, top=0.9)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.xticks(rotation='vertical')
plt.title('Mellem 18-20 satellitter')

kp1 = k_H_Leica[2].plot(kind='scatter', x='Dato', y='Difference', color='r', label = 'Leica på Smartnet')    
kp2 = k_H_Trim[2].plot(kind='scatter', x='Dato', y='Difference', color='r', marker = 's', ax=kp1, label = 'Trimble på Smartnet')    
kp3 = k_H_Sept[2].plot(kind='scatter', x='Dato', y='Difference', color='r', marker = '*', ax=kp1, label = 'Septentrio Smartnet')
kp4 = k_G_Leica[2].plot(kind='scatter', x='Dato', y='Difference', color='g', ax=kp1, label = 'Leica på GPSnet')    
kp5 = k_G_Trim[2].plot(kind='scatter', x='Dato', y='Difference', color='g', marker = 's', ax=kp1, label = 'Trimble på GPSnet')    
kp6 = k_G_Sept[2].plot(kind='scatter', x='Dato', y='Difference', color='g', marker = '*', ax=kp1, label = 'Septentrio på GPSnet')

plt.subplots_adjust(left=0.1, bottom=0.25, right=0.6, top=0.9)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.xticks(rotation='vertical')
plt.title('Over 20 satellitter')


IT1 = k_H_Trim[0].plot(kind='scatter', x='Dato', y='Difference', color='r', marker = 's')  
plt.subplots_adjust(left=0.25, bottom=0.25, right=0.9, top=0.9)
plt.xticks(rotation='vertical')
plt.title('Trimble på Smartnet. Målinger med under 18 satellitter')

IT2 = k_H_Trim[1].plot(kind='scatter', x='Dato', y='Difference', color='r', marker = 's')  
plt.subplots_adjust(left=0.25, bottom=0.25, right=0.9, top=0.9)
plt.xticks(rotation='vertical')
plt.title('Trimble på Smartnet. Målinger med mellem 18-20 satellitter')

IT3 = k_H_Trim[2].plot(kind='scatter', x='Dato', y='Difference', color='r', marker = 's')  
plt.subplots_adjust(left=0.25, bottom=0.25, right=0.9, top=0.9)
plt.xticks(rotation='vertical')
plt.title('Trimble på Smartnet. Målinger med over 20 satellitter')


IL1 = k_G_Leica[0].plot(kind='scatter', x='Dato', y='Difference', color='r', marker = 's')  
plt.subplots_adjust(left=0.25, bottom=0.25, right=0.9, top=0.9)
plt.xticks(rotation='vertical')
plt.title('Leica på GPSnet. Målinger med under 18 satellitter')

IL2 = k_G_Leica[1].plot(kind='scatter', x='Dato', y='Difference', color='r', marker = 's')  
plt.subplots_adjust(left=0.25, bottom=0.25, right=0.9, top=0.9)
plt.xticks(rotation='vertical')
plt.title('Leica på GPSnet. Målinger med mellem 18-20 satellitter')

IL3 = k_G_Leica[2].plot(kind='scatter', x='Dato', y='Difference', color='r', marker = 's')  
plt.subplots_adjust(left=0.25, bottom=0.25, right=0.9, top=0.9)
plt.xticks(rotation='vertical')
plt.title('Leica på GPSnet. Målinger med over 20 satellitter')


IS1 = k_H_Sept[0].plot(kind='scatter', x='Dato', y='Difference', color='r', marker = 's', label = 'Septentrio på Smartnet')
IS11 = k_G_Sept[0].plot(kind='scatter', x='Dato', y='Difference', color='b', marker = 's', ax=IS1, label = 'Septentrio på GPSnet')
plt.subplots_adjust(left=0.15, bottom=0.25, right=0.6, top=0.9)
plt.xticks(rotation='vertical')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.title('Septentrio. Målinger med under 18 satellitter')

IS2 = k_H_Sept[1].plot(kind='scatter', x='Dato', y='Difference', color='r', marker = 's', label = 'Septentrio på Smartnet')
IS21 = k_G_Sept[1].plot(kind='scatter', x='Dato', y='Difference', color='b', marker = 's', ax=IS2, label = 'Septentrio på GPSnet')
plt.subplots_adjust(left=0.15, bottom=0.25, right=0.6, top=0.9)
plt.xticks(rotation='vertical')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.title('Septentrio. Målinger med mellem 18-20 satellitter')

IS3 = k_H_Sept[2].plot(kind='scatter', x='Dato', y='Difference', color='r', marker = 's', label = 'Septentrio på Smartnet')
IS31 = k_G_Sept[2].plot(kind='scatter', x='Dato', y='Difference', color='b', marker = 's', ax=IS3, label = 'Septentrio på GPSnet')
plt.subplots_adjust(left=0.15, bottom=0.25, right=0.6, top=0.9)
plt.xticks(rotation='vertical')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.title('Septentrio. Målinger med over 20 satellitter')

plt.show()
#plt.savefig('C:\dev\PLAYGROUND\GNSS\Figurer\fig1.png', bbox_inches="tight") 
