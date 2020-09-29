"""
Beregning og plot af diverse data og statistiske værdier for RTK-målingen i GNSS-nøjagtighedsundersøgelse

Kør Clean_GNSS_RTK.py først
Scriptet her læser da fra Cleaned_GNSS_RTK.xlsx
"""
import pyexcel
import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
import matplotlib as mpl
import statistics
import numpy as np

data = pyexcel.get_sheet(file_name="Cleaned_GNSS_RTK.xlsx", name_columns_by_row=0)

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


"""
Funktioner benyttet
"""
def mean_diff(df):
    mean_df = df.groupby(['Punkt', 'Måling nr.'])['Difference'].agg('mean').reset_index()

    dato_df = df.groupby(['Punkt', 'Måling nr.'])['Dato'].agg('min').reset_index()
    sat_df = df.groupby(['Punkt', 'Måling nr.'])['Satellitter_gns'].agg('min').reset_index()
    PDOP_df = df.groupby(['Punkt', 'Måling nr.'])['PDOP'].agg('mean').reset_index()

    tem = mean_df.merge(dato_df, how='inner', left_on=["Punkt", "Måling nr."], right_on=["Punkt","Måling nr."])
    temp = tem.merge(PDOP_df, how='inner', left_on=["Punkt", "Måling nr."], right_on=["Punkt","Måling nr."])
    mean_diff = temp.merge(sat_df, left_on=["Punkt", "Måling nr."], right_on=["Punkt","Måling nr."])
    return mean_diff

def diff_diff(df):
    first = df[:][(df['Måling nr.'] == '1')]
    second = df[:][(df['Måling nr.'] == '2')]
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
    sr_gns_PDOP = (first['PDOP'] + second['PDOP'])/2
    first['PDOP'] = sr_gns_PDOP 
    first['til_2.maaling'] = sr_diff_diff.values

    return first


"""
Indlæsning af data i dataframe
"""

data_dict = {'Punkt': punkt, 'Dato': dato, 'Ellipsoidehøjde': ellipsoidehøjde, 'Ellipsoidehøjdekvalitet': ellipsoidehøjdekvalitet,
             'Måling nr.': meas_num, 'Instrument': instrument, 'Net': net, 'Sektor': sektor, 'Satellitter': satellitter, 
             'Satellitter_gns': satellitter_gns, 'Difference': difference, 'PDOP': PDOP}
df = pd.DataFrame(data_dict, columns = ['Punkt','Dato','Ellipsoidehøjde','Ellipsoidehøjdekvalitet','Måling nr.','Instrument','Net',
                                        'Sektor','Satellitter', 'Satellitter_gns', 'Difference', 'PDOP'])


"""
Opdeling til statistik og plot
"""

# Fjern outliers
df = df[:][(df.Difference >= -950) & (df.Difference <= 950)]


# Kun 5D-punkter
femD_df = df[:][df.Ellipsoidehøjdekvalitet == 1]


# Del i net (GPSnet og Smartnet)
GPS_df = femD_df[:][femD_df.Net == 'G']
smart_df = femD_df[:][femD_df.Net == 'H']

# Del i instrumenter
smart_Leica = smart_df[:][smart_df.Instrument == 'H']
GPS_Leica = GPS_df[:][GPS_df.Instrument == 'H']
smart_Trimble = smart_df[:][smart_df.Instrument == 'G']
GPS_Trimble= GPS_df[:][GPS_df.Instrument == 'G']
smart_Sept = smart_df[:][smart_df.Instrument == 'S']
GPS_Sept = GPS_df[:][GPS_df.Instrument == 'S']


# Få middeldifference for punkter (både måling 1 og 2)
diff_smart_Leica = mean_diff(smart_Leica)
diff_GPS_Leica = mean_diff(GPS_Leica)
diff_smart_Trimble = mean_diff(smart_Trimble)
diff_GPS_Trimble = mean_diff(GPS_Trimble)
diff_smart_Sept = mean_diff(smart_Sept)
diff_GPS_Sept = mean_diff(GPS_Sept)


# Differencen mellem 1. og 2. målings differencer
smart_Leica_dd = diff_diff(diff_smart_Leica)
GPS_Leica_dd = diff_diff(diff_GPS_Leica)
smart_Trimble_dd = diff_diff(diff_smart_Trimble)
GPS_Trimble_dd = diff_diff(diff_GPS_Trimble)
smart_Sept_dd = diff_diff(diff_smart_Sept)
GPS_Sept_dd = diff_diff(diff_GPS_Sept)



"""
Statistik
"""

# Middel og spredning uden outliers (både måling 1 og 2)
mean_smart_Leica = statistics.mean(diff_smart_Leica.Difference)
mean_GPS_Leica = statistics.mean(diff_GPS_Leica.Difference)
mean_smart_Trimble = statistics.mean(diff_smart_Trimble.Difference)
mean_GPS_Trimble = statistics.mean(diff_GPS_Trimble.Difference)
mean_smart_Sept = statistics.mean(diff_smart_Sept.Difference)
mean_GPS_Sept = statistics.mean(diff_GPS_Sept.Difference)

stdev_smart_Leica = statistics.stdev(diff_smart_Leica.Difference)
stdev_GPS_Leica = statistics.stdev(diff_GPS_Leica.Difference)
stdev_smart_Trimble = statistics.stdev(diff_smart_Trimble.Difference)
stdev_GPS_Trimble = statistics.stdev(diff_GPS_Trimble.Difference)
stdev_smart_Sept = statistics.stdev(diff_smart_Sept.Difference)
stdev_GPS_Sept = statistics.stdev(diff_GPS_Sept.Difference)




"""
PLOTS
"""

# Differencer (kronologisk) på hvert net og instrument, for 5D kun
diff_smart_Leica.plot(kind='scatter', x='Dato', y='Difference', c=diff_smart_Leica.PDOP, vmin=0.8, vmax=2, cmap="plasma")  
plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9, top=0.9)
plt.xticks(rotation='vertical')
plt.ylabel("Difference [mm]")
plt.ylim(-70,70)
plt.title('Leica på Smartnet \n Gnst: ' + str(round(mean_smart_Leica,2)) + ' std: ' + str(round(stdev_smart_Leica,2)) )
plt.savefig("Figurer/Diffkronologisk_H_H_5D.png")

diff_GPS_Leica.plot(kind='scatter', x='Dato', y='Difference', c=diff_GPS_Leica.PDOP, vmin=0.8, vmax=2, cmap="plasma")
plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9, top=0.9)
plt.xticks(rotation='vertical')
plt.ylabel("Difference [mm]")
plt.ylim(-70,70)
plt.title('Leica på GPSnet \n Gnst: ' + str(round(mean_GPS_Leica,2)) + ' std: ' + str(round(stdev_GPS_Leica,2)))
plt.savefig("Figurer/Diffkronologisk_H_G_5D.png")

diff_smart_Trimble.plot(kind='scatter', x='Dato', y='Difference', c=diff_smart_Trimble.PDOP, vmin=0.8, vmax=2, cmap="plasma")
plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9, top=0.9)
plt.xticks(rotation='vertical')
plt.ylabel("Difference [mm]")
plt.ylim(-70,70)
plt.title('Trimble på Smartnet \n Gnst: ' + str(round(mean_smart_Trimble,2)) + ' std: ' + str(round(stdev_smart_Trimble,2)))
plt.savefig("Figurer/Diffkronologisk_G_H_5D.png")

diff_GPS_Trimble.plot(kind='scatter', x='Dato', y='Difference', c=diff_GPS_Trimble.PDOP, vmin=0.8, vmax=2, cmap="plasma")
plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9, top=0.9)
plt.xticks(rotation='vertical')
plt.ylabel("Difference [mm]")
plt.ylim(-70,70)
plt.title('Trimble på GPSnet \n Gnst: ' + str(round(mean_GPS_Trimble,2)) + ' std: ' + str(round(stdev_GPS_Trimble,2)))
plt.savefig("Figurer/Diffkronologisk_G_G_5D.png")

diff_smart_Sept.plot(kind='scatter', x='Dato', y='Difference', c=diff_smart_Sept.PDOP, vmin=0.8, vmax=2, cmap="plasma")
plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9, top=0.9)
plt.xticks(rotation='vertical')
plt.ylabel("Difference [mm]")
plt.ylim(-70,70)
plt.title('Septentrio på Smartnet \n Gnst: ' + str(round(mean_smart_Sept,2)) + ' std: ' + str(round(stdev_smart_Sept,2)))
plt.savefig("Figurer/Diffkronologisk_S_H_5D.png")

diff_GPS_Sept.plot(kind='scatter', x='Dato', y='Difference', c=diff_GPS_Sept.PDOP, vmin=0.8, vmax=2, cmap="plasma")
plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9, top=0.9)
plt.xticks(rotation='vertical')
plt.ylabel("Difference [mm]")
plt.ylim(-70,70)
plt.title('Septentrio på GPSnet \n Gnst: ' + str(round(mean_GPS_Sept,2)) + ' std: ' + str(round(stdev_GPS_Sept,2)))
plt.savefig("Figurer/Diffkronologisk_S_G_5D.png")


# Histogram plot af differencer på hvert net og instrument
smart_Leica.hist(column= 'Difference', bins=50)
plt.axvline(mean_smart_Leica, color='w', linestyle='dashed', linewidth=2)
plt.title('Leica på Smartnet. Gnst: ' + str(round(mean_smart_Leica,2)))
plt.ylabel("Antal")
plt.xlabel("Difference [mm]")
plt.savefig("Figurer/Histogram_H_H_5D.png")

GPS_Leica.hist(column= 'Difference', bins=50)
plt.axvline(mean_GPS_Leica, color='w', linestyle='dashed', linewidth=2)
plt.title('Leica på GPSnet. Gnst: ' + str(round(mean_GPS_Leica,2)))
plt.ylabel("Antal")
plt.xlabel("Difference [mm]")
plt.savefig("Figurer/Histogram_H_G_5D.png")

smart_Trimble.hist(column= 'Difference', bins=50)
plt.axvline(mean_smart_Trimble, color='w', linestyle='dashed', linewidth=2)
plt.title('Trimble på Smartnet. Gnst: ' + str(round(mean_smart_Trimble,2)))
plt.ylabel("Antal")
plt.xlabel("Difference [mm]")
plt.savefig("Figurer/Histogram_G_H_5D.png")

GPS_Trimble.hist(column= 'Difference', bins=50)
plt.axvline(mean_GPS_Trimble, color='w', linestyle='dashed', linewidth=2)
plt.title('Trimble på GPSnet. Gnst: ' + str(round(mean_GPS_Trimble,2)))
plt.ylabel("Antal")
plt.xlabel("Difference [mm]")
plt.savefig("Figurer/Histogram_G_G_5D.png")

smart_Sept.hist(column= 'Difference', bins=50)
plt.axvline(mean_smart_Sept, color='w', linestyle='dashed', linewidth=2)
plt.title('Septentrio på Smartnet. Gnst: ' + str(round(mean_smart_Sept,2)))
plt.ylabel("Antal")
plt.xlabel("Difference [mm]")
plt.savefig("Figurer/Histogram_S_H_5D.png")

GPS_Sept.hist(column= 'Difference', bins=50)
plt.axvline(mean_GPS_Sept, color='w', linestyle='dashed', linewidth=2)
plt.title('Septentrio på GPSnet. Gnst: ' + str(round(mean_GPS_Sept,2)))
plt.ylabel("Antal")
plt.xlabel("Difference [mm]")
plt.savefig("Figurer/Histogram_S_G_5D.png")


# Difference mellem 1. og 2. RTK-måling
smart_Leica_dd.reset_index().plot(kind='scatter', x='Punkt', y='til_2.maaling', c=smart_Leica_dd.PDOP, vmin=0.8, vmax=2, cmap="plasma")  
plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9, top=0.9)
plt.xticks(rotation='vertical')
plt.ylabel("Difference [mm]")
plt.ylim(-70,70)
plt.title('Leica på Smartnet \n Forskel mellem 1. og 2. RTK-målings middelværdi')
plt.savefig("Figurer/Forskel1og2_H_H_5D.png")

GPS_Leica_dd.reset_index().plot(kind='scatter', x='Punkt', y='til_2.maaling', c=GPS_Leica_dd.PDOP, vmin=0.8, vmax=2, cmap="plasma")  
plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9, top=0.9)
plt.xticks(rotation='vertical')
plt.ylabel("Difference [mm]")
plt.ylim(-70,70)
plt.title('Leica på GPSnet \n Forskel mellem 1. og 2. RTK-målings middelværdi')
plt.savefig("Figurer/Forskel1og2_H_G_5D.png")

smart_Trimble_dd.reset_index().plot(kind='scatter', x='Punkt', y='til_2.maaling', c=smart_Trimble_dd.PDOP, vmin=0.8, vmax=2, cmap="plasma")  
plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9, top=0.9)
plt.xticks(rotation='vertical')
plt.ylabel("Difference [mm]")
plt.ylim(-70,70)
plt.title('Trimble på Smartnet \n Forskel mellem 1. og 2. RTK-målings middelværdi')
plt.savefig("Figurer/Forskel1og2_G_H_5D.png")

GPS_Trimble_dd.reset_index().plot(kind='scatter', x='Punkt', y='til_2.maaling', c=GPS_Trimble_dd.PDOP, vmin=0.8, vmax=2, cmap="plasma")  
plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9, top=0.9)
plt.xticks(rotation='vertical')
plt.ylabel("Difference [mm]")
plt.ylim(-70,70)
plt.title('Trimble på GPSnet \n Forskel mellem 1. og 2. RTK-målings middelværdi')
plt.savefig("Figurer/Forskel1og2_G_G_5D.png")

smart_Sept_dd.reset_index().plot(kind='scatter', x='Punkt', y='til_2.maaling', c=smart_Sept_dd.PDOP, vmin=0.8, vmax=2, cmap="plasma")  
plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9, top=0.9)
plt.xticks(rotation='vertical')
plt.ylabel("Difference [mm]")
plt.ylim(-70,70)
plt.title('Septentrio på Smartnet \n Forskel mellem 1. og 2. RTK-målings middelværdi')
plt.savefig("Figurer/Forskel1og2_S_H_5D.png")

GPS_Sept_dd.reset_index().plot(kind='scatter', x='Punkt', y='til_2.maaling', c=GPS_Sept_dd.PDOP, vmin=0.8, vmax=2, cmap="plasma")  
plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9, top=0.9)
plt.xticks(rotation='vertical')
plt.ylabel("Difference [mm]")
plt.ylim(-70,70)
plt.title('Septentrio på GPSnet \n Forskel mellem 1. og 2. RTK-målings middelværdi')
plt.savefig("Figurer/Forskel1og2_S_G_5D.png")

#plt.show()