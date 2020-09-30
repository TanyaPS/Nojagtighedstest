"""
Beregning og plot af diverse data og statistiske værdier for FS-målingen i GNSS-nøjagtighedsundersøgelse

Kør Clean_GNSS_FS.py først og Clean_GNSS_RTK.py
Scriptet her læser da fra Cleaned_*.xlsx 
"""


import pyexcel
import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
import statistics
import re


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

# Fast static
fs_punkt = fs_data.column[1]
fs_ellipsoidehøjde = fs_data.column[4]
fs_difference = fs_data.column[5]
fs_instrument = fs_data.column[3]
fs_maaling = fs_data.column[2]


# Spring tomme felter over
for i, m in enumerate(fs_maaling):
    if not m in ['', ' ']:
        fs_maaling[i] = int(m)

for i, m in enumerate(meas_num):
    if not m in ['', ' ']:
        meas_num[i] = int(m)


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



"""
Indlæsning af data i dataframe
"""
# RTK
data_dict = {'Punkt': punkt, 'Dato': dato,'Ellipsoidehøjde': ellipsoidehøjde,'Ellipsoidehøjdekvalitet': ellipsoidehøjdekvalitet,
             'Måling nr.': meas_num, 'Instrument': instrument, 'Net': net, 'Sektor': sektor, 'Satellitter': satellitter, 
             'Satellitter_gns': satellitter_gns, 'Difference': difference, 'PDOP': PDOP}
df = pd.DataFrame(data_dict, columns = ['Punkt','Dato','Ellipsoidehøjde','Ellipsoidehøjdekvalitet','Måling nr.','Instrument',
                                        'Net','Sektor','Satellitter', 'Satellitter_gns', 'Difference', 'PDOP'])

# Fast static
fs_data_dict = {'Punkt': fs_punkt, 'Ellipsoidehøjde': fs_ellipsoidehøjde, 'Måling nr.': fs_maaling, 'Instrument': fs_instrument, 
                'Difference': fs_difference}
fs_df = pd.DataFrame(fs_data_dict, columns = ['Punkt', 'Ellipsoidehøjde', 'Måling nr.', 'Instrument', 'Difference'])


"""
Opdeling til statistik og plot
"""
# Fjern outliers
df = df[:][(df.Difference > -950) & (df.Difference < 950)]
fs_df = fs_df[:][(fs_df.Difference > -950) & (fs_df.Difference < 950)]

"""
Opdel fast static
"""
# Del fast static i instrumenter
fs_Leica = fs_df[:][fs_df.Instrument == 'H']
fs_Trimble = fs_df[:][fs_df.Instrument == 'G']
fs_Sept = fs_df[:][fs_df.Instrument == 'S']


# Fast static mean difference for punkter (både måling 1 og 2)
fs_diff_Leica = fs_Leica.groupby(['Punkt', 'Måling nr.'])['Difference'].agg('mean').reset_index()
fs_diff_Trimble =  fs_Trimble.groupby(['Punkt', 'Måling nr.'])['Difference'].agg('mean').reset_index()
fs_diff_Sept =  fs_Sept.groupby(['Punkt', 'Måling nr.'])['Difference'].agg('mean').reset_index()


# Del fast static i måling nr 1 og 2
fs_first_Leica= fs_diff_Leica[:][fs_diff_Leica['Måling nr.'] == 1]
fs_second_Leica= fs_diff_Leica[:][fs_diff_Leica['Måling nr.'] == 2]
fs_first_Trimble= fs_diff_Trimble[:][fs_diff_Trimble['Måling nr.'] == 1]
fs_second_Trimble= fs_diff_Trimble[:][fs_diff_Trimble['Måling nr.'] == 2]
fs_first_Sept= fs_diff_Sept[:][fs_diff_Sept['Måling nr.'] == 1]
fs_second_Sept= fs_diff_Sept[:][fs_diff_Sept['Måling nr.'] == 2]

"""
Opdel RTK
"""
# Del i net (GPSnet og Smartnet)
GPS_df = df[:][df.Net == 'G']
smart_df = df[:][df.Net == 'H']

# Del i instrumenter
smart_Leica = smart_df[:][smart_df.Instrument == 'H']
GPS_Leica = GPS_df[:][GPS_df.Instrument == 'H']
smart_Trimble = smart_df[:][smart_df.Instrument == 'G']
GPS_Trimble= GPS_df[:][GPS_df.Instrument == 'G']
smart_Sept = smart_df[:][smart_df.Instrument == 'S']
GPS_Sept = GPS_df[:][GPS_df.Instrument == 'S']


# Få mean difference for punkter (både måling 1 og 2)
diff_smart_Leica = mean_diff(smart_Leica)
diff_GPS_Leica = mean_diff(GPS_Leica)
diff_smart_Trimble = mean_diff(smart_Trimble)
diff_GPS_Trimble = mean_diff(GPS_Trimble)
diff_smart_Sept = mean_diff(smart_Sept)
diff_GPS_Sept = mean_diff(GPS_Sept)


# Del i måling 1 og 2
first_smart_Leica= diff_smart_Leica[:][diff_smart_Leica['Måling nr.'] == 1]
second_smart_Leica= diff_smart_Leica[:][diff_smart_Leica['Måling nr.'] == 2]
first_GPS_Leica= diff_GPS_Leica[:][diff_GPS_Leica['Måling nr.'] == 1]
second_GPS_Leica= diff_GPS_Leica[:][diff_GPS_Leica['Måling nr.'] == 2]
first_smart_Trimble= diff_smart_Trimble[:][diff_smart_Trimble['Måling nr.'] == 1]
second_smart_Trimble= diff_smart_Trimble[:][diff_smart_Trimble['Måling nr.'] == 2]
first_GPS_Trimble= diff_GPS_Trimble[:][diff_GPS_Trimble['Måling nr.'] == 1]
second_GPS_Trimble= diff_GPS_Trimble[:][diff_GPS_Trimble['Måling nr.'] == 2]
first_smart_Sept= diff_smart_Sept[:][diff_smart_Sept['Måling nr.'] == 1]
second_smart_Sept= diff_smart_Sept[:][diff_smart_Sept['Måling nr.'] == 2]
first_GPS_Sept= diff_GPS_Sept[:][diff_GPS_Sept['Måling nr.'] == 1]
second_GPS_Sept= diff_GPS_Sept[:][diff_GPS_Sept['Måling nr.'] == 2]



"""
Statistik
"""
# Beregn middel og spredning
mean_smart_Leica = statistics.mean(smart_Leica.Difference)
mean_GPS_Leica = statistics.mean(GPS_Leica.Difference)
mean_smart_Trimble = statistics.mean(smart_Trimble.Difference)
mean_GPS_Trimble = statistics.mean(GPS_Trimble.Difference)
mean_smart_Sept = statistics.mean(smart_Sept.Difference)
mean_GPS_Sept = statistics.mean(GPS_Sept.Difference)

std_smart_Leica = statistics.stdev(smart_Leica.Difference)
std_GPS_Leica = statistics.stdev(GPS_Leica.Difference)
std_smart_Trimble = statistics.stdev(smart_Trimble.Difference)
std_GPS_Trimble = statistics.stdev(GPS_Trimble.Difference)
std_smart_Sept = statistics.stdev(smart_Sept.Difference)
std_GPS_Sept = statistics.stdev(GPS_Sept.Difference)

fs_mean_Leica = statistics.mean(fs_Leica.Difference)
fs_mean_Trimble = statistics.mean(fs_Trimble.Difference)
fs_mean_Sept = statistics.mean(fs_Sept.Difference)

fs_std_Leica = statistics.stdev(fs_Leica.Difference)
fs_std_Trimble = statistics.stdev(fs_Trimble.Difference)
fs_std_Sept = statistics.stdev(fs_Sept.Difference)

"""
Difference mellem 1. og 2. måling
"""
fs_Leica_dd = diff_diff(fs_first_Leica, fs_second_Leica)
fs_Trimble_dd = diff_diff(fs_first_Trimble, fs_second_Trimble)
fs_Sept_dd = diff_diff(fs_first_Sept, fs_second_Sept)


"""
Statistik skrevet til fil
"""
with open("stats.txt", "w") as output:
    output.write("Middelværdi og spredning for samtlige FS-beregninger (6 stk) og RTK-målinger (36 stk) for hvert instrument \n")
    
    output.write('****************************************************\n')
    output.write('Mean og std\n')
    output.write('****************************************************\n\n')
    output.write('Leica på Smartnet. Gnst: ' + str(round(mean_smart_Leica,2)) + ' std: ' + str(round(std_smart_Leica,2)) + '\n')
    output.write('Leica på GPSnet. Gnst: ' + str(round(mean_GPS_Leica,2)) + ' std: ' + str(round(std_GPS_Leica,2)) + '\n')
    output.write('Leica fast static. Gnst: ' + str(round(fs_mean_Leica,2)) + ' std: ' + str(round(fs_std_Leica,2)) + '\n\n')

    output.write('----------------------------------------------------\n')
    output.write('Trimble på Smartnet. Gnst: ' + str(round(mean_smart_Trimble,2)) + ' std: ' + str(round(std_smart_Trimble,2)) + '\n')
    output.write('Trimble på GPSnet. Gnst: ' + str(round(mean_GPS_Trimble,2)) + ' std: ' + str(round(std_GPS_Trimble,2)) + '\n')
    output.write('Trimble fast static. Gnst: ' + str(round(fs_mean_Trimble,2)) + ' std: ' + str(round(fs_std_Trimble,2)) + '\n\n')
    
    output.write('----------------------------------------------------\n')
    output.write('Septentrio på Smartnet. Gnst: ' + str(round(mean_smart_Sept,2)) + ' std: ' + str(round(std_smart_Sept,2)) + '\n')
    output.write('Septentrio på GPSnet. Gnst: ' + str(round(mean_GPS_Sept,2)) + ' std: ' + str(round(std_GPS_Sept,2)) + '\n')
    output.write('Septentrio fast static. Gnst: ' + str(round(fs_mean_Sept,2)) + ' std: ' + str(round(fs_std_Sept,2)) + '\n')



"""
PLOTS
"""
# RTK og FS plottet sammen for Leica
gr1 = fs_first_Leica.plot(kind='scatter', x='Punkt', y='Difference', color='r', marker = '.', label = 'Fast static: 1. måling')
gr2 = fs_second_Leica.plot(kind='scatter', x='Punkt', y='Difference', color='r', marker = 'x',  ax=gr1, label = 'Fast static: 2. måling')    
gr3 = first_smart_Leica.plot(kind='scatter', x='Punkt', y='Difference', color='b', marker = '.', ax=gr1, label = 'Smartnet: 1. måling')
gr4 = second_smart_Leica.plot(kind='scatter', x='Punkt', y='Difference', color='b', marker = 'x', ax=gr1, label = 'Smartnet: 2. måling')
gr5 = first_GPS_Leica.plot(kind='scatter', x='Punkt', y='Difference', color='g', marker = '.', ax=gr1, label = 'GPSnet: 1. måling')
gr6 = second_GPS_Leica.plot(kind='scatter', x='Punkt', y='Difference', color='g', marker = 'x', ax=gr1, label = 'GPSnet: 2. måling')

plt.subplots_adjust(left=0.1, bottom=0.25, right=0.855, top=0.9)
plt.legend(fontsize='xx-small',loc='best')
plt.xticks(rotation='vertical')
plt.ylim(-300,300)
plt.ylabel("Difference [mm]")
plt.title('Leica')
#manager = plt.get_current_fig_manager()
#manager.resize(*manager.window.maxsize())
plt.savefig("Figurer/FS_RTK_Leica_tot.png")

# RTK og FS plottet sammen for Trimble
gr7 = fs_first_Trimble.plot(kind='scatter', x='Punkt', y='Difference', color='r', marker = '.', label = 'Fast static: 1. måling')
gr8 = fs_second_Trimble.plot(kind='scatter', x='Punkt', y='Difference', color='r', marker = 'x',  ax=gr7, label = 'Fast static: 2. måling')    
gr9 = first_smart_Trimble.plot(kind='scatter', x='Punkt', y='Difference', color='b', marker = '.', ax=gr7, label = 'Smartnet: 1. måling')
gr10 = second_smart_Trimble.plot(kind='scatter', x='Punkt', y='Difference', color='b', marker = 'x', ax=gr7, label = 'Smartnet: 2. måling')
gr11 = first_GPS_Trimble.plot(kind='scatter', x='Punkt', y='Difference', color='g', marker = '.', ax=gr7, label = 'GPSnet: 1. måling')
gr12 = second_GPS_Trimble.plot(kind='scatter', x='Punkt', y='Difference', color='g', marker = 'x', ax=gr7, label = 'GPSnet: 2. måling')

plt.subplots_adjust(left=0.1, bottom=0.25, right=0.855, top=0.9)
plt.legend(fontsize='xx-small',loc='best')
plt.xticks(rotation='vertical')
plt.ylim(-300,300)
plt.ylabel("Difference [mm]")
plt.title('Trimble')
#manager = plt.get_current_fig_manager()
#manager.resize(*manager.window.maxsize())
plt.savefig("Figurer/FS_RTK_Trimble_tot.png")

# RTK og FS plottet sammen for Septentrio
gr13 = fs_first_Sept.plot(kind='scatter', x='Punkt', y='Difference', color='r', marker = '.', label = 'Fast static: 1. måling')
gr14 = fs_second_Sept.plot(kind='scatter', x='Punkt', y='Difference', color='r', marker = 'x',  ax=gr13, label = 'Fast static: 2. måling')    
gr15 = first_smart_Sept.plot(kind='scatter', x='Punkt', y='Difference', color='b', marker = '.', ax=gr13, label = 'Smartnet: 1. måling')
gr16 = second_smart_Sept.plot(kind='scatter', x='Punkt', y='Difference', color='b', marker = 'x', ax=gr13, label = 'Smartnet: 2. måling')
gr17 = first_GPS_Sept.plot(kind='scatter', x='Punkt', y='Difference', color='g', marker = '.', ax=gr13, label = 'GPSnet: 1. måling')
gr18 = second_GPS_Sept.plot(kind='scatter', x='Punkt', y='Difference', color='g', marker = 'x', ax=gr13, label = 'GPSnet: 2. måling')

plt.subplots_adjust(left=0.1, bottom=0.25, right=0.855, top=0.9)
plt.legend(fontsize='xx-small',loc='best')
plt.xticks(rotation='vertical')
plt.ylim(-300,300)
plt.ylabel("Difference [mm]")
plt.title('Septentrio')
#manager = plt.get_current_fig_manager()
#manager.resize(*manager.window.maxsize())
plt.savefig("Figurer/FS_RTK_Septentrio_tot.png")


# Histogrammer
fs_Leica.hist(column= 'Difference', bins =100)
plt.axvline(fs_mean_Leica, color='w', linestyle='dashed', linewidth=2)
plt.title('Fast Static Leica \n Gnst: ' + str(round(fs_mean_Leica,2)) + 'mm')
plt.savefig("Figurer/Histogram_Diff_H_FS_all.png")

fs_Trimble.hist(column= 'Difference', bins = 100)
plt.axvline(fs_mean_Trimble, color='w', linestyle='dashed', linewidth=2)
plt.title('Fast Static Trimble \n Gnst: ' + str(round(fs_mean_Trimble,2)) + 'mm')
plt.savefig("Figurer/Histogram_Diff_G_FS_all.png")

fs_Sept.hist(column= 'Difference', bins = 100)
plt.axvline(fs_mean_Sept, color='w', linestyle='dashed', linewidth=2)
plt.title('Fast Static Septentrio \n Gnst: ' + str(round(fs_mean_Sept,2)) + 'mm')
plt.savefig("Figurer/Histogram_Diff_S_FS_all.png")

fs_Leica_dd.hist(column= 'til_2.maaling', bins =100)
plt.title('Fast Static Leica \n Difference mellem 1. og 2. måling')
plt.savefig("Figurer/Histogram_Forskel_H_FS_all.png")

fs_Trimble_dd.hist(column= 'til_2.maaling', bins = 100)
plt.title('Fast Static Trimble \n Difference mellem 1. og 2. måling')
plt.savefig("Figurer/Histogram_Forskel_G_FS_all.png")

fs_Sept_dd.hist(column= 'til_2.maaling', bins = 100)
plt.title('Fast Static Septentrio \n Difference mellem 1. og 2. måling')
plt.savefig("Figurer/Histogram_Forskel_S_FS_all.png")


plt.show()