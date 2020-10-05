"""
Beregning og plot af diverse data og statistiske værdier for RTK-målingen i GNSS-nøjagtighedsundersøgelse
i relation til satellitantal.

Kør Clean_GNSS_RTK.py først
Scriptet her læser da fra Cleaned_GNSS_RTK.xlsx
"""
import pyexcel
import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
from datetime import datetime

data = pyexcel.get_sheet(file_name="Cleaned_GNSS_RTK.xlsx", name_columns_by_row=0)

punkt = data.column[1]
dato = data.column[2]
ellipsoideh = data.column[3]
ellipsoidehøjdekvalitet = data.column[4]
meas_num = data.column[5]
instrument = data.column[6]
net = data.column[7]
sektor = data.column[8]
satellitter = data.column[9]
satellitter_gns = data.column[10]
difference = data.column[11]


"""
Funktioner benyttet
"""

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


"""
Indlæsning af data i dataframe
"""
data_dict = {'Satellitter': satellitter, 'Satellitter_gns': satellitter_gns,'Ellipsoidehøjde': ellipsoideh, 
             'Difference': difference, 'Instrument': instrument, 'Net': net, 'Sektor': sektor, 'Punkt': punkt, 
             'Dato': dato}
df = DataFrame(data_dict,columns=['Satellitter', 'Satellitter_gns', 'Difference', 'Instrument', 'Net', 'Sektor',
                                  'Punkt', 'Dato'])
df.sort_values(by=['Dato'])


"""
Opdeling til statistik og plot
"""

# Fjern outliers
df = df[:][(df.Difference >= -100) & (df.Difference <= 100)]

# Del for antal satelitter
lav_sat = df[:][df.Satellitter_gns < 18]
mellem_sat = df[:][(df.Satellitter_gns >= 18) & (df.Satellitter_gns <= 20)]
høj_sat = df[:][df.Satellitter_gns > 20]
sat_list = [lav_sat, mellem_sat, høj_sat]

# Del for sektor
land = df[:][df.Sektor == 'land']
lav_beb = df[:][(df.Sektor == 'lav bebyg') | (df.Sektor == 'erhverv')]
høj_beb = df[:][(df.Sektor == 'hoej bebyg') | (df.Sektor == 'bykerne')]
sekt_list = [land, lav_beb, høj_beb]

net_list_G = []
net_list_H = []
net_list_S = []
k_net_list_G = []
k_net_list_H = []

# Del i net for sektorer
for sekt_df in sekt_list:
    net_list_G.append(sekt_df[:][sekt_df.Net == 'G'])
    net_list_H.append(sekt_df[:][sekt_df.Net == 'H'])
    net_list_S.append(sekt_df[:][sekt_df.Net == 'S'])
    


# Del i net for antal satellitter 
for sat_df in sat_list:
    k_net_list_G.append(sat_df[:][sat_df.Net == 'G'])
    k_net_list_H.append(sat_df[:][sat_df.Net == 'H'])
    
list_G_Leica = []
list_G_Trim = []
list_G_Sept = []
list_H_Leica = []
list_H_Trim = []
list_H_Sept= []
list_S_Leica = []
list_S_Trim = []
list_S_Sept = []


# Del i instrumenter for sektorer
for net_df in net_list_G:
    list_G_Leica.append(net_df[:][net_df.Instrument == 'H'])
    list_G_Trim.append(net_df[:][net_df.Instrument == 'G'])
    list_G_Sept.append(net_df[:][net_df.Instrument == 'S'])

for net_df in net_list_H:
    list_H_Leica.append(net_df[:][net_df.Instrument == 'H'])
    list_H_Trim.append(net_df[:][net_df.Instrument == 'G'])
    list_H_Sept.append(net_df[:][net_df.Instrument == 'S'])

for net_df in net_list_S:
    list_S_Leica.append(net_df[:][net_df.Instrument == 'H'])
    list_S_Trim.append(net_df[:][net_df.Instrument == 'G'])
    list_S_Sept.append(net_df[:][net_df.Instrument == 'S'])


# Del i instrumenter for antal satellitter (u sdfenet)
k_list_G_Leica = []
k_list_G_Trim = []
k_list_G_Sept = []
k_list_H_Leica = []
k_list_H_Trim = []
k_list_H_Sept= []


for net_df in k_net_list_G:
    k_list_G_Leica.append(net_df[:][net_df.Instrument == 'H'])
    k_list_G_Trim.append(net_df[:][net_df.Instrument == 'G'])
    k_list_G_Sept.append(net_df[:][net_df.Instrument == 'S'])

for net_df in k_net_list_H:
    k_list_H_Leica.append(net_df[:][net_df.Instrument == 'H'])
    k_list_H_Trim.append(net_df[:][net_df.Instrument == 'G'])
    k_list_H_Sept.append(net_df[:][net_df.Instrument == 'S'])


"""
Statistik
"""

# Middel for hvert punkt for sektorer
# For net G
G_Leica = mean_sat(list_G_Leica, 'Satellitter')
G_Trim = mean_sat(list_G_Trim, 'Satellitter')
G_Sept = mean_sat(list_G_Sept, 'Satellitter')

# For net H
H_Leica = mean_sat(list_H_Leica, 'Satellitter')
H_Trim = mean_sat(list_H_Trim, 'Satellitter')
H_Sept = mean_sat(list_H_Sept, 'Satellitter')

# For net S
S_Leica = mean_sat(list_S_Leica, 'Satellitter')
S_Trim = mean_sat(list_S_Trim, 'Satellitter')
S_Sept = mean_sat(list_S_Sept, 'Satellitter')


# Middel for hvert punkt for antal satellitter
# For net G
k_G_Leica = mean_sat(k_list_G_Leica, 'Difference')
k_G_Trim = mean_sat(k_list_G_Trim, 'Difference')
k_G_Sept = mean_sat(k_list_G_Sept, 'Difference')

# For net H
k_H_Leica = mean_sat(k_list_H_Leica, 'Difference')
k_H_Trim = mean_sat(k_list_H_Trim, 'Difference')
k_H_Sept = mean_sat(k_list_H_Sept, 'Difference')


"""
PLOTS
"""

# RTK-målinger delt i instrumenter og net for åbent land
ax1 = H_Leica[0].plot(kind='scatter', x='Dato', y='Satellitter', color='r', label = 'Leica på Smartnet')    
ax2 = H_Trim[0].plot(kind='scatter', x='Dato', y='Satellitter', color='r', marker = 's', ax=ax1, label = 'Trimble på Smartnet')    
ax3 = H_Sept[0].plot(kind='scatter', x='Dato', y='Satellitter', color='r', marker = '*', ax=ax1, label = 'Septentrio på Smartnet')
ax7 = G_Leica[0].plot(kind='scatter', x='Dato', y='Satellitter', color='g', ax=ax1, label = 'Leica på GPSnet')    
ax8 = G_Trim[0].plot(kind='scatter', x='Dato', y='Satellitter', color='g', marker = 's', ax=ax1, label = 'Trimble på GPSnet')    
ax9 = G_Sept[0].plot(kind='scatter', x='Dato', y='Satellitter', color='g', marker = '*', ax=ax1, label = 'Septentrio på GPSnet')

plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9, top=0.9)
plt.legend(fontsize='xx-small',loc='best')
plt.xticks(rotation=45)
plt.title('RTK-målinger for åbent land')
plt.savefig("Figurer/RTK_Sats_all_Land.png")

# RTK-målinger delt i instrumenter og net for lav bebyggelse
ax10 = H_Leica[1].plot(kind='scatter', x='Dato', y='Satellitter', color='r', label = 'Leica på Smartnet')    
ax20 = H_Trim[1].plot(kind='scatter', x='Dato', y='Satellitter', color='r', marker = 's', ax=ax10, label = 'Trimble på Smartnet')    
ax30 = H_Sept[1].plot(kind='scatter', x='Dato', y='Satellitter', color='r', marker = '*', ax=ax10, label = 'Septentrio på Smartnet')
ax70 = G_Leica[1].plot(kind='scatter', x='Dato', y='Satellitter', color='g', ax=ax10, label = 'Leica på GPSnet')    
ax80 = G_Trim[1].plot(kind='scatter', x='Dato', y='Satellitter', color='g', marker = 's', ax=ax10, label = 'Trimble på GPSnet')    
ax90 = G_Sept[1].plot(kind='scatter', x='Dato', y='Satellitter', color='g', marker = '*', ax=ax10, label = 'Septentrio på GPSnet')

plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9, top=0.9)
plt.legend(fontsize='xx-small',loc='best')
plt.xticks(rotation=45)
plt.title('RTK-målinger for lav bebyggelse')
plt.savefig("Figurer/RTK_Sats_all_Lav.png")

# RTK-målinger delt i instrumenter og net for høj bebyggelse
ax100 = H_Leica[2].plot(kind='scatter', x='Dato', y='Satellitter', color='r', label = 'Leica på Smartnet')    
ax200 = H_Trim[2].plot(kind='scatter', x='Dato', y='Satellitter', color='r', marker = 's', ax=ax100, label = 'Trimble på Smartnet')    
ax300 = H_Sept[2].plot(kind='scatter', x='Dato', y='Satellitter', color='r', marker = '*', ax=ax100, label = 'Septentrio på Smartnet')
ax700 = G_Leica[2].plot(kind='scatter', x='Dato', y='Satellitter', color='g', ax=ax100, label = 'Leica på GPSnet')    
ax800 = G_Trim[2].plot(kind='scatter', x='Dato', y='Satellitter', color='g', marker = 's', ax=ax100, label = 'Trimble på GPSnet')    
ax900 = G_Sept[2].plot(kind='scatter', x='Dato', y='Satellitter', color='g', marker = '*', ax=ax100, label = 'Septentrio på GPSnet')

plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9, top=0.9)
plt.legend(fontsize='xx-small',loc='best')
plt.xticks(rotation=45)
plt.title('RTK-målinger for høj bebyggelse')
plt.savefig("Figurer/RTK_Sats_all_Høj.png")



# RTK-målinger delt i instrumenter og net for under 18 satellitter
kp1 = k_H_Leica[0].plot(kind='scatter', x='Dato', y='Difference', color='r', label = 'Leica på Smartnet')    
kp2 = k_H_Trim[0].plot(kind='scatter', x='Dato', y='Difference', color='r', marker = 's', ax=kp1, label = 'Trimble på Smartnet')    
kp3 = k_H_Sept[0].plot(kind='scatter', x='Dato', y='Difference', color='r', marker = '*', ax=kp1, label = 'Septentrio på Smartnet')
kp4 = k_G_Leica[0].plot(kind='scatter', x='Dato', y='Difference', color='g', ax=kp1, label = 'Leica på GPSnet')    
kp5 = k_G_Trim[0].plot(kind='scatter', x='Dato', y='Difference', color='g', marker = 's', ax=kp1, label = 'Trimble på GPSnet')    
kp6 = k_G_Sept[0].plot(kind='scatter', x='Dato', y='Difference', color='g', marker = '*', ax=kp1, label = 'Septentrio på GPSnet')

plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9, top=0.9)
plt.legend(fontsize='xx-small',loc='best')
plt.xticks(rotation=45)
plt.title('RTK-målinger for under 18 satellitter')
plt.savefig("Figurer/RTK_all_sats18under.png")

# RTK-målinger delt i instrumenter og net for 18-20 satellitter
kp1 = k_H_Leica[1].plot(kind='scatter', x='Dato', y='Difference', color='r', label = 'Leica på Smartnet')    
kp2 = k_H_Trim[1].plot(kind='scatter', x='Dato', y='Difference', color='r', marker = 's', ax=kp1, label = 'Trimble på Smartnet')    
kp3 = k_H_Sept[1].plot(kind='scatter', x='Dato', y='Difference', color='r', marker = '*', ax=kp1, label = 'Septentrio på Smartnet')
kp4 = k_G_Leica[1].plot(kind='scatter', x='Dato', y='Difference', color='g', ax=kp1, label = 'Leica på GPSnet')    
kp5 = k_G_Trim[1].plot(kind='scatter', x='Dato', y='Difference', color='g', marker = 's', ax=kp1, label = 'Trimble på GPSnet')    
kp6 = k_G_Sept[1].plot(kind='scatter', x='Dato', y='Difference', color='g', marker = '*', ax=kp1, label = 'Septentrio på GPSnet')

plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9, top=0.9)
plt.legend(fontsize='xx-small',loc='best')
plt.xticks(rotation=45)
plt.title('RTK-målinger for mellem 18-20 satellitter')
plt.savefig("Figurer/RTK_all_sats18-20.png")

# RTK-målinger delt i instrumenter og net for over 20 satellitter
kp1 = k_H_Leica[2].plot(kind='scatter', x='Dato', y='Difference', color='r', label = 'Leica på Smartnet')    
kp2 = k_H_Trim[2].plot(kind='scatter', x='Dato', y='Difference', color='r', marker = 's', ax=kp1, label = 'Trimble på Smartnet')    
kp3 = k_H_Sept[2].plot(kind='scatter', x='Dato', y='Difference', color='r', marker = '*', ax=kp1, label = 'Septentrio på Smartnet')
kp4 = k_G_Leica[2].plot(kind='scatter', x='Dato', y='Difference', color='g', ax=kp1, label = 'Leica på GPSnet')    
kp5 = k_G_Trim[2].plot(kind='scatter', x='Dato', y='Difference', color='g', marker = 's', ax=kp1, label = 'Trimble på GPSnet')    
kp6 = k_G_Sept[2].plot(kind='scatter', x='Dato', y='Difference', color='g', marker = '*', ax=kp1, label = 'Septentrio på GPSnet')

plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9, top=0.9)
plt.legend(fontsize='xx-small',loc='best')
plt.xticks(rotation=45)
plt.title('RTK-målinger for over 20 satellitter')
plt.savefig("Figurer/RTK_all_sats20over.png")


# RTK-målinger Leica på GPSnet for under 18 satellitter
IL1 = k_G_Leica[0].plot(kind='scatter', x='Dato', y='Difference', color='r', marker = 's')  
plt.subplots_adjust(left=0.25, bottom=0.25, right=0.9, top=0.9)
plt.xticks(rotation=45)
plt.title('Leica på GPSnet \n RTK-målinger med under 18 satellitter')
plt.savefig("Figurer/RTK_G_G_sats18under.png")

# RTK-målinger Leica på GPSnet for 18-20 satellitter
IL2 = k_G_Leica[1].plot(kind='scatter', x='Dato', y='Difference', color='r', marker = 's')  
plt.subplots_adjust(left=0.25, bottom=0.25, right=0.9, top=0.9)
plt.xticks(rotation=45)
plt.title('Leica på GPSnet \n RTK-målinger med mellem 18-20 satellitter')
plt.savefig("Figurer/RTK_G_G_sats18-20.png")

# RTK-målinger Leica på GPSnet for over 20 satellitter
IL3 = k_G_Leica[2].plot(kind='scatter', x='Dato', y='Difference', color='r', marker = 's')  
plt.subplots_adjust(left=0.25, bottom=0.25, right=0.9, top=0.9)
plt.xticks(rotation=45)
plt.title('Leica på GPSnet \n RTK-målinger med over 20 satellitter')
plt.savefig("Figurer/RTK_G_G_sats20over.png")


# RTK-målinger Trimble på Smartnet for under 18 satellitter
IT1 = k_H_Trim[0].plot(kind='scatter', x='Dato', y='Difference', color='r', marker = 's')  
plt.subplots_adjust(left=0.25, bottom=0.25, right=0.9, top=0.9)
plt.xticks(rotation=45)
plt.title('Trimble på Smartnet \n RTK-målinger med under 18 satellitter')
plt.savefig("Figurer/RTK_H_H_sats18under.png")

# RTK-målinger Trimble på Smartnet for 18-20 satellitter
IT2 = k_H_Trim[1].plot(kind='scatter', x='Dato', y='Difference', color='r', marker = 's')  
plt.subplots_adjust(left=0.25, bottom=0.25, right=0.9, top=0.9)
plt.xticks(rotation=45)
plt.title('Trimble på Smartnet \n RTK-målinger med mellem 18-20 satellitter')
plt.savefig("Figurer/RTK_H_H_sats18-20.png")

# RTK-målinger Trimble på Smartnet for over 20 satellitter
IT3 = k_H_Trim[2].plot(kind='scatter', x='Dato', y='Difference', color='r', marker = 's')  
plt.subplots_adjust(left=0.25, bottom=0.25, right=0.9, top=0.9)
plt.xticks(rotation=45)
plt.title('Trimble på Smartnet \n RTK-målinger med over 20 satellitter')
plt.savefig("Figurer/RTK_H_H_sats20over.png")


# RTK-målinger Septentrio (på begge net) for under 18 satellitter
IS1 = k_H_Sept[0].plot(kind='scatter', x='Dato', y='Difference', color='r', marker = 's', label = 'Septentrio på Smartnet')
IS11 = k_G_Sept[0].plot(kind='scatter', x='Dato', y='Difference', color='b', marker = 's', ax=IS1, label = 'Septentrio på GPSnet')
plt.subplots_adjust(left=0.15, bottom=0.25, right=0.9, top=0.9)
plt.xticks(rotation=45)
plt.legend(fontsize='xx-small',loc='best')
plt.title('Septentrio \n RTK-målinger med under 18 satellitter')
plt.savefig("Figurer/RTK_S_begge_sats18under.png")

# RTK-målinger Septentrio (på begge net) for 18-20 satellitter
IS2 = k_H_Sept[1].plot(kind='scatter', x='Dato', y='Difference', color='r', marker = 's', label = 'Septentrio på Smartnet')
IS21 = k_G_Sept[1].plot(kind='scatter', x='Dato', y='Difference', color='b', marker = 's', ax=IS2, label = 'Septentrio på GPSnet')
plt.subplots_adjust(left=0.15, bottom=0.25, right=0.9, top=0.9)
plt.xticks(rotation=45)
plt.legend(fontsize='xx-small',loc='best')
plt.title('Septentrio \n RTK-målinger med mellem 18-20 satellitter')
plt.savefig("Figurer/RTK_S_begge_sats18-20.png")

# RTK-målinger Septentrio (på begge net) for over 20 satellitter
IS3 = k_H_Sept[2].plot(kind='scatter', x='Dato', y='Difference', color='r', marker = 's', label = 'Septentrio på Smartnet')
IS31 = k_G_Sept[2].plot(kind='scatter', x='Dato', y='Difference', color='b', marker = 's', ax=IS3, label = 'Septentrio på GPSnet')
plt.subplots_adjust(left=0.15, bottom=0.25, right=0.9, top=0.9)
plt.xticks(rotation=45)
plt.legend(fontsize='xx-small',loc='best')
plt.title('Septentrio \n RTK-målinger med over 20 satellitter')
plt.savefig("Figurer/RTK_S_begge_sats20over.png")

#plt.show()
