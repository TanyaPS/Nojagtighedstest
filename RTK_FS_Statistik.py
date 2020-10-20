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

# Fast static
fs_punkt = fs_data.column[1]
fs_ellipsoidehøjde = fs_data.column[4]
fs_difference = fs_data.column[5]
fs_instrument = fs_data.column[3]
fs_maaling = fs_data.column[2]
fs_dist_net1 = fs_data.column[6]
fs_dist_net2 = fs_data.column[7]



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
def mean_std(df, kolonne):
    if kolonne == 'Difference':
        new_df = df.groupby(['Punkt', 'Måling nr.'])['Difference'].agg('mean').reset_index()
    elif kolonne == 'Ellipsoidehøjde':
        new_df = df.groupby(['Punkt', 'Måling nr.'])['Ellipsoidehøjde'].agg('std').reset_index()

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
             'Satellitter_gns': satellitter_gns, 'Difference': difference, 'PDOP': PDOP, 'Afstand til reference station': dist_net}
df = pd.DataFrame(data_dict, columns = ['Punkt','Dato','Ellipsoidehøjde','Ellipsoidehøjdekvalitet','Måling nr.','Instrument',
                                        'Net','Sektor','Satellitter', 'Satellitter_gns', 'Difference', 'PDOP', 'Afstand til reference station'])

# Fast static
fs_data_dict = {'Punkt': fs_punkt, 'Ellipsoidehøjde': fs_ellipsoidehøjde, 'Måling nr.': fs_maaling, 'Instrument': fs_instrument, 
                'Difference': fs_difference, 'Afstand til GPSnet': fs_dist_net1, 'Afstand til smartnet': fs_dist_net2}
fs_df = pd.DataFrame(fs_data_dict, columns = ['Punkt', 'Ellipsoidehøjde', 'Måling nr.', 'Instrument', 'Difference', 'Afstand til GPSnet', 'Afstand til Smartnet'])

fs_df['Ellipsoidehøjde'] *=1000
df['Ellipsoidehøjde'] *=1000

#satellit gennemsnit fra RTK merges til Fast static dataframe 
fs_df =  fs_df.merge(df[['Punkt','Satellitter_gns']], how='inner', left_on=["Punkt"], right_on=["Punkt"])

#%%
"""
Find konstanter til outliers for FS
"""
print(('Median af alle FS differencer: ') + str(statistics.median(fs_df.Difference)))
print(('Median af Hs FS differencer: ') + str(statistics.median(fs_df[:][(fs_df.Instrument == 'H')].Difference)))
print(('Median af Gs FS differencer: ') + str(statistics.median(fs_df[:][(fs_df.Instrument == 'G')].Difference)))

print(('Kvantiler for alle FS differencer: ') + str(statistics.quantiles(fs_df.Difference, method='inclusive')))
print(('Kvantiler for Hs FS differencer: ') + str(statistics.quantiles(fs_df[:][(fs_df.Instrument == 'H')].Difference, method='inclusive')))
print(('Kvantiler for Gs FS differencer: ') + str(statistics.quantiles(fs_df[:][(fs_df.Instrument == 'G')].Difference, method='inclusive')))

Q1=statistics.quantiles(fs_df.Difference, method='inclusive')[0]
Q3=statistics.quantiles(fs_df.Difference, method='inclusive')[-1]
nedre=Q1-(Q3-Q1)*1.5
oevre=Q3+(Q3-Q1)*1.5

Q1S=statistics.quantiles(fs_df[:][(fs_df.Instrument == 'S')].Difference, method='inclusive')[0]
Q3S=statistics.quantiles(fs_df[:][(fs_df.Instrument == 'S')].Difference, method='inclusive')[-1]
nedreS=Q1S-(Q3S-Q1S)*1.5
oevreS=Q3S+(Q3S-Q1S)*1.5

Q1H=statistics.quantiles(fs_df[:][(fs_df.Instrument == 'H')].Difference, method='inclusive')[0]
Q3H=statistics.quantiles(fs_df[:][(fs_df.Instrument == 'H')].Difference, method='inclusive')[-1]
nedreH=Q1H-(Q3H-Q1H)*1.5
oevreH=Q3H+(Q3H-Q1H)*1.5

Q1G=statistics.quantiles(fs_df[:][(fs_df.Instrument == 'G')].Difference, method='inclusive')[0]
Q3G=statistics.quantiles(fs_df[:][(fs_df.Instrument == 'G')].Difference, method='inclusive')[-1]
nedreG=Q1G-(Q3G-Q1G)*1.5
oevreG=Q3G+(Q3G-Q1G)*1.5

# Fra Q1 - (Q3-Q1)*1.5  til Q3 + (Q3-Q1)*1.5 (standard for outliers)
print('Interne grænser for alle FS: Fra ' + str(nedre) + ' til ' + str(oevre))
print('Interne grænser for alle FS på S: Fra ' + str(nedreS) + ' til ' + str(oevreS))
print('Interne grænser for alle FS på H: Fra ' + str(nedreH) + ' til ' + str(oevreH))
print('Interne grænser for alle FS på G: Fra ' + str(nedreG) + ' til ' + str(oevreG))

#%%
"""
Opdeling til statistik og plot
"""
# Fjern outliers
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


# Fast static std for målinger (std af ca 3 målinger) (både måling 1 og 2)
fs_h_std_Leica = fs_Leica.groupby(['Punkt', 'Måling nr.'])['Ellipsoidehøjde'].agg('std').reset_index()
fs_h_std_Trimble =  fs_Trimble.groupby(['Punkt', 'Måling nr.'])['Ellipsoidehøjde'].agg('std').reset_index()
fs_h_std_Sept =  fs_Sept.groupby(['Punkt', 'Måling nr.'])['Ellipsoidehøjde'].agg('std').reset_index()

#%%
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
diff_smart_Leica = mean_std(smart_Leica, 'Difference')
diff_GPS_Leica = mean_std(GPS_Leica, 'Difference')
diff_smart_Trimble = mean_std(smart_Trimble, 'Difference')
diff_GPS_Trimble = mean_std(GPS_Trimble, 'Difference')
diff_smart_Sept = mean_std(smart_Sept, 'Difference')
diff_GPS_Sept = mean_std(GPS_Sept, 'Difference')


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

# RTK std for målinger (std af ca 3 målinger) (både måling 1 og 2)
smart_Leica_h_std = mean_std(smart_Leica, 'Ellipsoidehøjde')
GPS_Leica_h_std =  mean_std(GPS_Leica, 'Ellipsoidehøjde')
smart_Trimble_h_std =  mean_std(smart_Trimble, 'Ellipsoidehøjde')
GPS_Trimble_h_std =  mean_std(GPS_Trimble, 'Ellipsoidehøjde')
smart_Sept_h_std = mean_std(smart_Sept, 'Ellipsoidehøjde')
GPS_Sept_h_std =  mean_std(GPS_Sept, 'Ellipsoidehøjde')

# Opdel std i måling 1 og 2
first_smart_Leica_h_std= smart_Leica_h_std[:][smart_Leica_h_std['Måling nr.'] == 1]
second_smart_Leica_h_std= smart_Leica_h_std[:][smart_Leica_h_std['Måling nr.'] == 2]
first_GPS_Leica_h_std= GPS_Leica_h_std[:][GPS_Leica_h_std['Måling nr.'] == 1]
second_GPS_Leica_h_std= GPS_Leica_h_std[:][GPS_Leica_h_std['Måling nr.'] == 2]
first_smart_Trimble_h_std= smart_Trimble_h_std[:][smart_Trimble_h_std['Måling nr.'] == 1]
second_smart_Trimble_h_std= smart_Trimble_h_std[:][smart_Trimble_h_std['Måling nr.'] == 2]
first_GPS_Trimble_h_std= GPS_Trimble_h_std[:][GPS_Trimble_h_std['Måling nr.'] == 1]
second_GPS_Trimble_h_std= GPS_Trimble_h_std[:][GPS_Trimble_h_std['Måling nr.'] == 2]
first_smart_Sept_h_std= smart_Sept_h_std[:][smart_Sept_h_std['Måling nr.'] == 1]
second_smart_Sept_h_std= smart_Sept_h_std[:][smart_Sept_h_std['Måling nr.'] == 2]
first_GPS_Sept_h_std= GPS_Sept_h_std[:][GPS_Sept_h_std['Måling nr.'] == 1]
second_GPS_Sept_h_std= GPS_Sept_h_std[:][GPS_Sept_h_std['Måling nr.'] == 2]

#%%
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

smart_Leica_dd = diff_diff(first_smart_Leica, second_smart_Leica)
GPS_Leica_dd = diff_diff(first_GPS_Leica, second_GPS_Leica)
smart_Trimble_dd = diff_diff(first_smart_Trimble, second_smart_Trimble)
GPS_Trimble_dd = diff_diff(first_GPS_Trimble, second_GPS_Trimble)
smart_Sept_dd = diff_diff(first_smart_Sept, second_smart_Sept)
GPS_Sept_dd = diff_diff(first_GPS_Sept, second_GPS_Sept)

"""
mean difference af alle målinger for hvert punkt (uden outliers) med konfidensinterval
"""
RTK_mean = []
RTK_ned = []
RTK_op = []
RTK_dist = []
unikke_pkter = np.unique(df.Punkt)
unikke_pkter.sort()
for pkt in unikke_pkter:
    pkt_df = df[:][df.Punkt == pkt]
    RTK_dist.append(pkt_df['Afstand til reference station'].mean())
    pkt_m_c = mean_confidence_interval(pkt_df.Difference)
    RTK_mean.append(pkt_m_c[0])
    RTK_ned.append(pkt_m_c[0]-pkt_m_c[1])
    RTK_op.append(pkt_m_c[2]-pkt_m_c[0])

konfidens_dict = {'Punkt': unikke_pkter, 'Middel difference': RTK_mean, 'Nedre grænse': RTK_ned, 'Øvre grænse': RTK_op, 'Afstand til net': RTK_dist}
konfidens_df = pd.DataFrame(konfidens_dict, columns = ['Punkt', 'Middel difference', 'Nedre grænse', 'Øvre grænse', 'Afstand til net'])
#konfidens_df.sort_values(by=['Afstand til net'])


fs_mean = []
fs_ned = []
fs_op = []
fs_unikke_pkter = np.unique(fs_df.Punkt)
fs_unikke_pkter.sort()
for pkt in fs_unikke_pkter:
    fs_pkt = fs_df[:][fs_df.Punkt == pkt]
    fs_pkt_m_c = mean_confidence_interval(fs_pkt.Difference)
    fs_mean.append(fs_pkt_m_c[0])
    fs_ned.append(fs_pkt_m_c[0]-fs_pkt_m_c[1])
    fs_op.append(fs_pkt_m_c[2]-fs_pkt_m_c[0])

fs_konfidens_dict = {'Punkt': fs_unikke_pkter, 'Middel difference': fs_mean, 'Nedre grænse': fs_ned, 'Øvre grænse': fs_op}
fs_konfidens_df = pd.DataFrame(fs_konfidens_dict, columns = ['Punkt', 'Middel difference', 'Nedre grænse', 'Øvre grænse'])


#%%
"""
Statistik skrevet til fil
"""
with open("stats.txt", "w") as output:
    output.write("Middelværdi og spredning for samtlige FS-beregninger (6 stk) \n og RTK-målinger (36 stk) for hvert instrument \n")
    
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
    output.write('Septentrio fast static. Gnst: ' + str(round(fs_mean_Sept,2)) + ' std: ' + str(round(fs_std_Sept,2)) + '\n\n')
    
    output.write('****************************************************\n')
    output.write("Middelværdi og spredning for punkter under 18 satelitter \n")
    output.write('****************************************************\n\n')
    output.write('Leica på Smartnet. Gnst: ' + str(round(statistics.mean(smart_Leica[:][smart_Leica.Satellitter_gns < 18].Difference),2)) + ' std: ' + str(round(statistics.stdev(smart_Leica[:][smart_Leica.Satellitter_gns < 18].Difference),2)) + '\n')
    output.write('Leica på GPSnet. Gnst: ' + str(round(statistics.mean(GPS_Leica[:][GPS_Leica.Satellitter_gns < 18].Difference),2)) + ' std: ' + str(round(statistics.stdev(GPS_Leica[:][GPS_Leica.Satellitter_gns < 18].Difference),2)) + '\n')
    output.write('Leica fast static. Gnst: ' + str(round(statistics.mean(fs_Leica[:][fs_Leica.Satellitter_gns < 18].Difference),2)) + ' std: ' + str(round(statistics.stdev(fs_Leica[:][fs_Leica.Satellitter_gns < 18].Difference),2)) + '\n\n')

    output.write('----------------------------------------------------\n')
    output.write('Trimble på Smartnet. Gnst: ' + str(round(statistics.mean(smart_Trimble[:][smart_Trimble.Satellitter_gns < 18].Difference),2)) + ' std: ' + str(round(statistics.stdev(smart_Trimble[:][smart_Trimble.Satellitter_gns < 18].Difference),2)) + '\n')
    output.write('Trimble på GPSnet. Gnst: ' + str(round(statistics.mean(GPS_Trimble[:][GPS_Trimble.Satellitter_gns < 18].Difference),2)) + ' std: ' + str(round(statistics.stdev(GPS_Trimble[:][GPS_Trimble.Satellitter_gns < 18].Difference),2)) + '\n')
    output.write('Trimble fast static. Gnst: ' + str(round(statistics.mean(fs_Trimble[:][fs_Trimble.Satellitter_gns < 18].Difference),2)) + ' std: ' + str(round(statistics.stdev(fs_Trimble[:][fs_Trimble.Satellitter_gns < 18].Difference),2)) + '\n\n')
    
    output.write('----------------------------------------------------\n')
    output.write('Septentrio på Smartnet. Gnst: ' + str(round(statistics.mean(smart_Sept[:][smart_Sept.Satellitter_gns < 18].Difference),2)) + ' std: ' + str(round(statistics.stdev(smart_Sept[:][smart_Sept.Satellitter_gns < 18].Difference),2)) + '\n')
    output.write('Septentrio på GPSnet. Gnst: ' + str(round(statistics.mean(GPS_Sept[:][GPS_Sept.Satellitter_gns < 18].Difference),2)) + ' std: ' + str(round(statistics.stdev(GPS_Sept[:][GPS_Sept.Satellitter_gns < 18].Difference),2)) + '\n\n')
    output.write('Septentrio fast static. Gnst: ' + str(round(statistics.mean(fs_Sept[:][fs_Sept.Satellitter_gns < 18].Difference),2)) + ' std: ' + str(round(statistics.stdev(fs_Sept[:][fs_Sept.Satellitter_gns < 18].Difference),2)) + '\n\n')
    
    output.write('****************************************************\n')
    output.write("Middelværdi og spredning for punkter ml. 18 og 20 satelitter \n")
    output.write('****************************************************\n\n')
    output.write('Leica på Smartnet. Gnst: ' + str(round(statistics.mean(smart_Leica[:][(smart_Leica.Satellitter_gns >= 18) & (smart_Leica.Satellitter_gns <= 20)].Difference),2)) + ' std: ' + str(round(statistics.stdev(smart_Leica[:][(smart_Leica.Satellitter_gns >= 18) & (smart_Leica.Satellitter_gns <= 20)].Difference),2)) + '\n')
    output.write('Leica på GPSnet. Gnst: ' + str(round(statistics.mean(GPS_Leica[:][(GPS_Leica.Satellitter_gns >= 18) & (GPS_Leica.Satellitter_gns <= 20)].Difference),2)) + ' std: ' + str(round(statistics.stdev(GPS_Leica[:][(GPS_Leica.Satellitter_gns >= 18) & (GPS_Leica.Satellitter_gns <= 20)].Difference),2)) + '\n')
    output.write('Leica fast static. Gnst: ' + str(round(statistics.mean(fs_Leica[:][(fs_Leica.Satellitter_gns >= 18) & (fs_Leica.Satellitter_gns <= 20)].Difference),2)) + ' std: ' + str(round(statistics.stdev(fs_Leica[:][(fs_Leica.Satellitter_gns >= 18) & (fs_Leica.Satellitter_gns <= 20)].Difference),2)) + '\n\n')

    output.write('----------------------------------------------------\n')
    output.write('Trimble på Smartnet. Gnst: ' + str(round(statistics.mean(smart_Trimble[:][(smart_Trimble.Satellitter_gns >= 18) & (smart_Trimble.Satellitter_gns <= 20)].Difference),2)) + ' std: ' + str(round(statistics.stdev(smart_Trimble[:][(smart_Trimble.Satellitter_gns >= 18) & (smart_Trimble.Satellitter_gns <= 20)].Difference),2)) + '\n')
    output.write('Trimble på GPSnet. Gnst: ' + str(round(statistics.mean(GPS_Trimble[:][(GPS_Trimble.Satellitter_gns >= 18) & (GPS_Trimble.Satellitter_gns <= 20)].Difference),2)) + ' std: ' + str(round(statistics.stdev(GPS_Trimble[:][(GPS_Trimble.Satellitter_gns >= 18) & (GPS_Trimble.Satellitter_gns <= 20)].Difference),2)) + '\n')
    output.write('Trimble fast static. Gnst: ' + str(round(statistics.mean(fs_Trimble[:][(fs_Trimble.Satellitter_gns >= 18) & (fs_Trimble.Satellitter_gns <= 20)].Difference),2)) + ' std: ' + str(round(statistics.stdev(fs_Trimble[:][(fs_Trimble.Satellitter_gns >= 18) & (fs_Trimble.Satellitter_gns <= 20)].Difference),2)) + '\n\n')
    
    output.write('----------------------------------------------------\n')
    output.write('Septentrio på Smartnet. Gnst: ' + str(round(statistics.mean(smart_Sept[:][(smart_Sept.Satellitter_gns >= 18) & (smart_Sept.Satellitter_gns <= 20)].Difference),2)) + ' std: ' + str(round(statistics.stdev(smart_Sept[:][(smart_Sept.Satellitter_gns >= 18) & (smart_Sept.Satellitter_gns <= 20)].Difference),2)) + '\n')
    output.write('Septentrio på GPSnet. Gnst: ' + str(round(statistics.mean(GPS_Sept[:][(GPS_Sept.Satellitter_gns >= 18) & (GPS_Sept.Satellitter_gns <= 20)].Difference),2)) + ' std: ' + str(round(statistics.stdev(GPS_Sept[:][(GPS_Sept.Satellitter_gns >= 18) & (GPS_Sept.Satellitter_gns <= 20)].Difference),2)) + '\n\n')
    output.write('Septentrio fast static. Gnst: ' + str(round(statistics.mean(fs_Sept[:][(fs_Sept.Satellitter_gns >= 18) & (fs_Sept.Satellitter_gns <= 20)].Difference),2)) + ' std: ' + str(round(statistics.stdev(fs_Sept[:][(fs_Sept.Satellitter_gns >= 18) & (fs_Sept.Satellitter_gns <= 20)].Difference),2)) + '\n\n')
    
    output.write('****************************************************\n')
    output.write("Middelværdi og spredning for punkter over 20 satelitter \n")
    output.write('****************************************************\n\n')
    output.write('Leica på Smartnet. Gnst: ' + str(round(statistics.mean(smart_Leica[:][smart_Leica.Satellitter_gns > 20].Difference),2)) + ' std: ' + str(round(statistics.stdev(smart_Leica[:][smart_Leica.Satellitter_gns > 20].Difference),2)) + '\n')
    output.write('Leica på GPSnet. Gnst: ' + str(round(statistics.mean(GPS_Leica[:][GPS_Leica.Satellitter_gns > 20].Difference),2)) + ' std: ' + str(round(statistics.stdev(GPS_Leica[:][GPS_Leica.Satellitter_gns > 20].Difference),2)) + '\n')
    output.write('Leica fast static. Gnst: ' + str(round(statistics.mean(fs_Leica[:][fs_Leica.Satellitter_gns > 20].Difference),2)) + ' std: ' + str(round(statistics.stdev(fs_Leica[:][fs_Leica.Satellitter_gns > 20].Difference),2)) + '\n\n')

    output.write('----------------------------------------------------\n')
    output.write('Trimble på Smartnet. Gnst: ' + str(round(statistics.mean(smart_Trimble[:][smart_Trimble.Satellitter_gns > 20].Difference),2)) + ' std: ' + str(round(statistics.stdev(smart_Trimble[:][smart_Trimble.Satellitter_gns > 20].Difference),2)) + '\n')
    output.write('Trimble på GPSnet. Gnst: ' + str(round(statistics.mean(GPS_Trimble[:][GPS_Trimble.Satellitter_gns > 20].Difference),2)) + ' std: ' + str(round(statistics.stdev(GPS_Trimble[:][GPS_Trimble.Satellitter_gns > 20].Difference),2)) + '\n')
    output.write('Trimble fast static. Gnst: ' + str(round(statistics.mean(fs_Trimble[:][fs_Trimble.Satellitter_gns > 20].Difference),2)) + ' std: ' + str(round(statistics.stdev(fs_Trimble[:][fs_Trimble.Satellitter_gns > 20].Difference),2)) + '\n\n')
    
    output.write('----------------------------------------------------\n')
    output.write('Septentrio på Smartnet. Gnst: ' + str(round(statistics.mean(smart_Sept[:][smart_Sept.Satellitter_gns > 20].Difference),2)) + ' std: ' + str(round(statistics.stdev(smart_Sept[:][smart_Sept.Satellitter_gns > 20].Difference),2)) + '\n')
    output.write('Septentrio på GPSnet. Gnst: ' + str(round(statistics.mean(GPS_Sept[:][GPS_Sept.Satellitter_gns > 20].Difference),2)) + ' std: ' + str(round(statistics.stdev(GPS_Sept[:][GPS_Sept.Satellitter_gns > 20].Difference),2)) + '\n')
    output.write('Septentrio fast static. Gnst: ' + str(round(statistics.mean(fs_Sept[:][fs_Sept.Satellitter_gns > 20].Difference),2)) + ' std: ' + str(round(statistics.stdev(fs_Sept[:][fs_Sept.Satellitter_gns > 20].Difference),2)) + '\n\n')

#%%
"""
PLOTS
"""

# Histogrammer
fs_Leica.hist(column= 'Difference', bins =50)
plt.axvline(fs_mean_Leica, color='w', linestyle='dashed', linewidth=2)
plt.title('Fast Static Leica \n Gnst: ' + str(round(fs_mean_Leica,2)) + 'mm', fontsize=10)
plt.xlabel("Difference [mm]")
plt.ylabel("Antal")
plt.savefig("Figurer/FS_Histogram_Diff_H_all.png")

fs_Trimble.hist(column= 'Difference', bins = 50)
plt.axvline(fs_mean_Trimble, color='w', linestyle='dashed', linewidth=2)
plt.xlabel("Difference [mm]")
plt.ylabel("Antal")
plt.title('Fast Static Trimble \n Gnst: ' + str(round(fs_mean_Trimble,2)) + 'mm', fontsize=10)
plt.savefig("Figurer/FS_Histogram_Diff_G_all.png")

fs_Sept.hist(column= 'Difference', bins = 50)
plt.axvline(fs_mean_Sept, color='w', linestyle='dashed', linewidth=2)
plt.title('Fast Static Septentrio \n Gnst: ' + str(round(fs_mean_Sept,2)) + 'mm', fontsize=10)
plt.xlabel("Difference [mm]")
plt.ylabel("Antal")
plt.savefig("Figurer/FS_Histogram_Diff_S_all.png")

fs_Leica_dd.hist(column= 'til_2.maaling', bins =50)
plt.title('Fast Static Leica \n Difference mellem 1. og 2. måling', fontsize=10)
plt.xlabel("Difference [mm]")
plt.ylabel("Antal")
plt.savefig("Figurer/FS_Histogram_Forskel_H_all.png")

fs_Trimble_dd.hist(column= 'til_2.maaling', bins = 50)
plt.xlabel("Difference [mm]")
plt.ylabel("Antal")
plt.title('Fast Static Trimble \n Difference mellem 1. og 2. måling', fontsize=10)
plt.savefig("Figurer/FS_Histogram_Forskel_G_all.png")

fs_Sept_dd.hist(column= 'til_2.maaling', bins = 50)
plt.xlabel("Difference [mm]")
plt.ylabel("Antal")
plt.title('Fast Static Septentrio \n Difference mellem 1. og 2. måling', fontsize=10)
plt.savefig("Figurer/FS_Histogram_Forskel_S_all.png")

plt.close('all')
#%%
# # Vi ændrer lige figurstørrelsen:
# get current size
fig_size = plt.rcParams["figure.figsize"]
#print ("Current size:", fig_size)
# let's make the plots a bit bigger than the default
# set figure width to 14 and height to 6
fig_size[0] = 14
fig_size[1] = 6
plt.rcParams["figure.figsize"] = fig_size
#print ("Current size:", fig_size)


# Plot alle FS-data alene
fs_df.plot(x='Punkt', y='Difference', s=3, kind='scatter').grid(axis='y')
plt.title('Alle FS-målinger')
plt.xlabel('Punkt')
plt.ylabel('Differencer [mm]')
plt.xticks(rotation='vertical')
plt.savefig("Figurer/FS_Diffkronologisk_all.png")


# FS-data for Leica
gr1 = fs_first_Leica.plot(kind='scatter', x='Punkt', y='Difference', color='darkgreen', marker = '.', label = 'Fast static: 1. måling')
gr2 = fs_second_Leica.plot(kind='scatter', x='Punkt', y='Difference', color='darkgreen', marker = 'x',  ax=gr1, label = 'Fast static: 2. måling')    

plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9, top=0.9)
plt.legend(fontsize='xx-small',loc='best')
plt.xticks(rotation='vertical')
plt.ylim(-100,100)
plt.ylabel("Difference [mm]")
plt.title('Fast static for Leica')
plt.savefig("Figurer_Leica/FS_H_all.png")


# FS for Leica: Difference for måling 1 og 2, samt forskel ml. differencerne 
# generate the twin axes
plt.figure(3)
host = host_subplot(111)
par = host.twinx()

# plot the bars (use host. instead of plt.)
x = np.array(fs_Leica_dd.reset_index().sort_values(by=['Punkt'])['Punkt'])
y = np.array(fs_Leica_dd.sort_values(by=['Punkt'])['til_2.maaling'])
p1 = host.bar(x, y, color='steelblue', label = 'Forskel ml. 1. og 2. måling')

# plot the scatter plot (use par. instead of plt.)
x = np.array(fs_first_Leica.sort_values(by=['Punkt'])['Punkt'])
y = np.array(fs_first_Leica.sort_values(by=['Punkt'])['Difference'])
p2 = par.scatter(x, y, s=6, color='darkorange', label = 'Diff. 1. måling')
x = np.array(fs_second_Leica.sort_values(by=['Punkt'])['Punkt'])
y = np.array(fs_second_Leica.sort_values(by=['Punkt'])['Difference'])
p3 = par.scatter(x, y, s=6, color='purple', label = 'Diff. 2. måling')

plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9, top=0.9)
plt.legend(fontsize='xx-small',loc='best')
plt.xticks(rotation='vertical')
host.set_ylim(-100, 100)
par.set_ylim(-100, 100)
host.set_ylabel("Forskel ml. 1. og 2. måling [mm]")
par.set_ylabel("Difference [mm]")
plt.title('FS Leica \n \n Difference på 1. og 2. måling samt forskel mellem 1. og 2. måling', fontsize=10)
plt.savefig("Figurer_Leica/FS_RTK_diff_diff_H_H.png")


# FS-data for Trimble
gr7 = fs_first_Trimble.plot(kind='scatter', x='Punkt', y='Difference', color='firebrick', marker = '.', label = 'Fast static: 1. måling')
gr8 = fs_second_Trimble.plot(kind='scatter', x='Punkt', y='Difference', color='firebrick', marker = 'x',  ax=gr7, label = 'Fast static: 2. måling') 

plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9, top=0.9)
plt.legend(fontsize='xx-small',loc='best')
plt.xticks(rotation='vertical')
plt.ylim(-100,100)
plt.ylabel("Difference [mm]")
plt.title('Fast static for Leica')
plt.savefig("Figurer_Trimble/FS_G_all.png")


# FS for Trimble: Difference for måling 1 og 2, samt forskel ml. differencerne 
# generate the twin axes
plt.figure(5)
host = host_subplot(111)
par = host.twinx()

# plot the bars (use host. instead of plt.)
x = np.array(fs_Trimble_dd.reset_index().sort_values(by=['Punkt'])['Punkt'])
y = np.array(fs_Trimble_dd.sort_values(by=['Punkt'])['til_2.maaling'])
p1 = host.bar(x, y, color='steelblue', label = 'Forskel ml. 1. og 2. måling')

# plot the scatter plot (use par. instead of plt.)
x = np.array(fs_first_Trimble.sort_values(by=['Punkt'])['Punkt'])
y = np.array(fs_first_Trimble.sort_values(by=['Punkt'])['Difference'])
p2 = par.scatter(x, y, s=6, color='darkorange', label = 'Diff. 1. måling')
x = np.array(fs_second_Trimble.sort_values(by=['Punkt'])['Punkt'])
y = np.array(fs_second_Trimble.sort_values(by=['Punkt'])['Difference'])
p3 = par.scatter(x, y, s=6, color='purple', label = 'Diff. 2. måling')

plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9, top=0.9)
plt.legend(fontsize='xx-small',loc='best')
plt.xticks(rotation='vertical')
host.set_ylim(-100, 100)
par.set_ylim(-100, 100)
host.set_ylabel("Forskel ml. 1. og 2. måling [mm]")
par.set_ylabel("Difference [mm]")
plt.title('FS Trimble \n \n Difference på 1. og 2. måling samt forskel mellem 1. og 2. måling', fontsize=10)
plt.savefig("Figurer_Trimble/FS_RTK_diff_diff_G_G.png")


#%%
# RTK og FS plottet sammen for Leica
gr1 = fs_first_Leica.plot(kind='scatter', x='Punkt', y='Difference', color='r', marker = '.', label = 'Fast static: 1. måling')
gr2 = fs_second_Leica.plot(kind='scatter', x='Punkt', y='Difference', color='r', marker = 'x',  ax=gr1, label = 'Fast static: 2. måling')    
gr3 = first_smart_Leica.plot(kind='scatter', x='Punkt', y='Difference', color='b', marker = '.', ax=gr1, label = 'Smartnet: 1. måling')
gr4 = second_smart_Leica.plot(kind='scatter', x='Punkt', y='Difference', color='b', marker = 'x', ax=gr1, label = 'Smartnet: 2. måling')
gr5 = first_GPS_Leica.plot(kind='scatter', x='Punkt', y='Difference', color='g', marker = '.', ax=gr1, label = 'GPSnet: 1. måling')
gr6 = second_GPS_Leica.plot(kind='scatter', x='Punkt', y='Difference', color='g', marker = 'x', ax=gr1, label = 'GPSnet: 2. måling')

plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9, top=0.9)
plt.legend(fontsize='xx-small',loc='best')
plt.xticks(rotation='vertical')
plt.ylim(-100,100)
plt.ylabel("Difference [mm]")
plt.title('Leica')
#plt.grid(color='light grey', ls='--', zorder=0)
#manager = plt.get_current_fig_manager()
#manager.resize(*manager.window.maxsize())
plt.savefig("Figurer/FS_RTK_H_all.png")

# RTK og FS plottet sammen for Trimble
gr7 = fs_first_Trimble.plot(kind='scatter', x='Punkt', y='Difference', color='r', marker = '.', label = 'Fast static: 1. måling')
gr8 = fs_second_Trimble.plot(kind='scatter', x='Punkt', y='Difference', color='r', marker = 'x',  ax=gr7, label = 'Fast static: 2. måling')    
gr9 = first_smart_Trimble.plot(kind='scatter', x='Punkt', y='Difference', color='b', marker = '.', ax=gr7, label = 'Smartnet: 1. måling')
gr10 = second_smart_Trimble.plot(kind='scatter', x='Punkt', y='Difference', color='b', marker = 'x', ax=gr7, label = 'Smartnet: 2. måling')
gr11 = first_GPS_Trimble.plot(kind='scatter', x='Punkt', y='Difference', color='g', marker = '.', ax=gr7, label = 'GPSnet: 1. måling')
gr12 = second_GPS_Trimble.plot(kind='scatter', x='Punkt', y='Difference', color='g', marker = 'x', ax=gr7, label = 'GPSnet: 2. måling')

plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9, top=0.9)
plt.legend(fontsize='xx-small',loc='best')
plt.xticks(rotation='vertical')
plt.ylim(-100,100)
plt.ylabel("Difference [mm]")
plt.title('Trimble')
#manager = plt.get_current_fig_manager()
#manager.resize(*manager.window.maxsize())
plt.savefig("Figurer/FS_RTK_G_all.png")

# RTK og FS plottet sammen for Septentrio
gr13 = fs_first_Sept.plot(kind='scatter', x='Punkt', y='Difference', color='r', marker = '.', label = 'Fast static: 1. måling')
gr14 = fs_second_Sept.plot(kind='scatter', x='Punkt', y='Difference', color='r', marker = 'x',  ax=gr13, label = 'Fast static: 2. måling')    
gr15 = first_smart_Sept.plot(kind='scatter', x='Punkt', y='Difference', color='b', marker = '.', ax=gr13, label = 'Smartnet: 1. måling')
gr16 = second_smart_Sept.plot(kind='scatter', x='Punkt', y='Difference', color='b', marker = 'x', ax=gr13, label = 'Smartnet: 2. måling')
gr17 = first_GPS_Sept.plot(kind='scatter', x='Punkt', y='Difference', color='g', marker = '.', ax=gr13, label = 'GPSnet: 1. måling')
gr18 = second_GPS_Sept.plot(kind='scatter', x='Punkt', y='Difference', color='g', marker = 'x', ax=gr13, label = 'GPSnet: 2. måling')

plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9, top=0.9)
plt.legend(fontsize='xx-small',loc='best')
plt.xticks(rotation='vertical')
plt.ylim(-100,100)
plt.ylabel("Difference [mm]")
plt.title('Septentrio')
#manager = plt.get_current_fig_manager()
#manager.resize(*manager.window.maxsize())
plt.savefig("Figurer/FS_RTK_S_all.png")

#%%
# RTK og FS plottet sammen for Leica - men uden data fra GPSnet
gr1 = fs_first_Leica.plot(kind='scatter', x='Punkt', y='Difference', color='b', marker = '.', label = 'Fast static: 1. måling')
gr2 = fs_second_Leica.plot(kind='scatter', x='Punkt', y='Difference', color='b', marker = 'x',  ax=gr1, label = 'Fast static: 2. måling')    
gr3 = first_smart_Leica.plot(kind='scatter', x='Punkt', y='Difference', color='darkgreen', marker = '.', ax=gr1, label = 'Smartnet: 1. måling')
gr4 = second_smart_Leica.plot(kind='scatter', x='Punkt', y='Difference', color='darkgreen', marker = 'x', ax=gr1, label = 'Smartnet: 2. måling')

plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9, top=0.9)
plt.legend(fontsize='xx-small',loc='best')
plt.xticks(rotation='vertical')
plt.ylim(-100,100)
plt.ylabel("Difference [mm]")
plt.title('Leica')
plt.savefig("Figurer_Leica/FS_RTK_H_all.png")

# RTK og FS plottet sammen for Trimble - men uden data fra Smartnet 
gr7 = fs_first_Trimble.plot(kind='scatter', x='Punkt', y='Difference', color='b', marker = '.', label = 'Fast static: 1. måling')
gr8 = fs_second_Trimble.plot(kind='scatter', x='Punkt', y='Difference', color='b', marker = 'x',  ax=gr7, label = 'Fast static: 2. måling')    
gr11 = first_GPS_Trimble.plot(kind='scatter', x='Punkt', y='Difference', color='firebrick', marker = '.', ax=gr7, label = 'GPSnet: 1. måling')
gr12 = second_GPS_Trimble.plot(kind='scatter', x='Punkt', y='Difference', color='firebrick', marker = 'x', ax=gr7, label = 'GPSnet: 2. måling')

plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9, top=0.9)
plt.legend(fontsize='xx-small',loc='best')
plt.xticks(rotation='vertical')
plt.ylim(-100,100)
plt.ylabel("Difference [mm]")
plt.title('Trimble')
plt.savefig("Figurer_Trimble/FS_RTK_G_all.png")

#plt.close('all')

#%%
# RTK Leica på smartnet: Spredning af måling 1 og 2, samt difference mellem middelværdierne 
# generate the twin axes
plt.figure(11)
host = host_subplot(111)
par = host.twinx()

# plot the bars (use host. instead of plt.)
x = np.array(smart_Leica_dd.reset_index().sort_values(by=['Satellitter_gns'])['Punkt'])
y = np.array(smart_Leica_dd.sort_values(by=['Satellitter_gns'])['Difference'])
p1 = host.bar(x, y, color='steelblue', label = 'Difference')

# plot the scatter plot (use par. instead of plt.)
x = np.array(first_smart_Leica_h_std.sort_values(by=['Satellitter_gns'])['Punkt'])
y = np.array(first_smart_Leica_h_std.sort_values(by=['Satellitter_gns'])['Ellipsoidehøjde'])
p2 = par.scatter(x, y, s=6, color='darkorange', label = 'std 1. måling')
x = np.array(second_smart_Leica_h_std.sort_values(by=['Satellitter_gns'])['Punkt'])
y = np.array(second_smart_Leica_h_std.sort_values(by=['Satellitter_gns'])['Ellipsoidehøjde'])
p3 = par.scatter(x, y, s=6, color='purple', label = 'std 2. måling')

plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9, top=0.9)
plt.legend(fontsize='xx-small',loc='best')
plt.xticks(rotation='vertical')
host.set_ylim(-100, 100)
par.set_ylim(0, 30)
host.set_ylabel("Difference [mm]")
par.set_ylabel("Spredning [mm]")
plt.title('Leica på Smartnet \n \n Spredning på 1. og 2. måling samt differencen mellem middelværdi på 1. og 2. måling', fontsize=10)
#manager = plt.get_current_fig_manager()
#manager.resize(*manager.window.maxsize())
plt.savefig("Figurer_Leica/RTK_std_diff_H_H.png")


# RTK Leica på GPSnet: Spredning af måling 1 og 2, samt difference mellem middelværdierne
# generate the twin axes
plt.figure(12)
host = host_subplot(111)
par = host.twinx()

# plot the bars (use host. instead of plt.)
x = np.array(GPS_Leica_dd.reset_index().sort_values(by=['Satellitter_gns'])['Punkt'])
y = np.array(GPS_Leica_dd.sort_values(by=['Satellitter_gns'])['Difference'])
p1 = host.bar(x, y, color='steelblue', label = 'Difference')

# plot the scatter plot (use par. instead of plt.)
x = np.array(first_GPS_Leica_h_std.sort_values(by=['Satellitter_gns'])['Punkt'])
y = np.array(first_GPS_Leica_h_std.sort_values(by=['Satellitter_gns'])['Ellipsoidehøjde'])
p2 = par.scatter(x, y, s=6, color='darkorange', label = 'std 1. måling')
x = np.array(second_GPS_Leica_h_std.sort_values(by=['Satellitter_gns'])['Punkt'])
y = np.array(second_GPS_Leica_h_std.sort_values(by=['Satellitter_gns'])['Ellipsoidehøjde'])
p3 = par.scatter(x, y, s=6, color='purple', label = 'std 2. måling')

plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9, top=0.9)
plt.legend(fontsize='xx-small',loc='best')
plt.xticks(rotation='vertical')
host.set_ylim(-100, 100)
par.set_ylim(0, 30)
host.set_ylabel("Difference [mm]")
par.set_ylabel("Spredning [mm]")
plt.title('Leica på GPSnet \n \n Spredning på 1. og 2. måling samt differencen mellem middelværdi på 1. og 2. måling', fontsize=10)
#manager = plt.get_current_fig_manager()
#manager.resize(*manager.window.maxsize())
plt.savefig("Figurer/RTK_std_diff_H_G.png")


# RTK Trimble på smartnet: Spredning af måling 1 og 2, samt difference mellem middelværdierne
# generate the twin axes
plt.figure(13)
host = host_subplot(111)
par = host.twinx()

# plot the bars (use host. instead of plt.)
x = np.array(smart_Trimble_dd.reset_index().sort_values(by=['Satellitter_gns'])['Punkt'])
y = np.array(smart_Trimble_dd.sort_values(by=['Satellitter_gns'])['Difference'])
p1 = host.bar(x, y, color='steelblue', label = 'Difference')

# plot the scatter plot (use par. instead of plt.)
x = np.array(first_smart_Trimble_h_std.sort_values(by=['Satellitter_gns'])['Punkt'])
y = np.array(first_smart_Trimble_h_std.sort_values(by=['Satellitter_gns'])['Ellipsoidehøjde'])
p2 = par.scatter(x, y, s=6, color='darkorange', label = 'std 1. måling')
x = np.array(second_smart_Trimble_h_std.sort_values(by=['Satellitter_gns'])['Punkt'])
y = np.array(second_smart_Trimble_h_std.sort_values(by=['Satellitter_gns'])['Ellipsoidehøjde'])
p3 = par.scatter(x, y, s=6, color='purple', label = 'std 2. måling')

plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9, top=0.9)
plt.legend(fontsize='xx-small',loc='best')
plt.xticks(rotation='vertical')
host.set_ylim(-100, 100)
par.set_ylim(0, 30)
host.set_ylabel("Difference [mm]")
par.set_ylabel("Spredning [mm]")
plt.title('Trimble på Smartnet \n \n Spredning på 1. og 2. måling samt differencen mellem middelværdi på 1. og 2. måling', fontsize=10)
#manager = plt.get_current_fig_manager()
#manager.resize(*manager.window.maxsize())
plt.savefig("Figurer/RTK_std_diff_G_H.png")


# RTK Trimble på GPSnet: Spredning af måling 1 og 2, samt difference mellem middelværdierne
# generate the twin axes
plt.figure(14)
host = host_subplot(111)
par = host.twinx()

# plot the bars (use host. instead of plt.)
x = np.array(GPS_Trimble_dd.reset_index().sort_values(by=['Satellitter_gns'])['Punkt'])
y = np.array(GPS_Trimble_dd.sort_values(by=['Satellitter_gns'])['Difference'])
p1 = host.bar(x, y, color='steelblue', label = 'Difference')

# plot the scatter plot (use par. instead of plt.)
x = np.array(first_GPS_Trimble_h_std.sort_values(by=['Satellitter_gns'])['Punkt'])
y = np.array(first_GPS_Trimble_h_std.sort_values(by=['Satellitter_gns'])['Ellipsoidehøjde'])
p2 = par.scatter(x, y, s=6, color='darkorange', label = 'std 1. måling')
x = np.array(second_GPS_Trimble_h_std.sort_values(by=['Satellitter_gns'])['Punkt'])
y = np.array(second_GPS_Trimble_h_std.sort_values(by=['Satellitter_gns'])['Ellipsoidehøjde'])
p3 = par.scatter(x, y, s=6, color='purple', label = 'std 2. måling')

plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9, top=0.9)
plt.legend(fontsize='xx-small',loc='best')
plt.xticks(rotation='vertical')
host.set_ylim(-100, 100)
par.set_ylim(0, 30)
host.set_ylabel("Difference [mm]")
par.set_ylabel("Spredning [mm]")
plt.title('Trimble på GPSnet \n \n Spredning på 1. og 2. måling samt differencen mellem middelværdi på 1. og 2. måling', fontsize=10)
#manager = plt.get_current_fig_manager()
#manager.resize(*manager.window.maxsize())
plt.savefig("Figurer_Trimble/RTK_std_diff_G_G.png")


# RTK Septentrio på Smartnet: Spredning af måling 1 og 2, samt difference mellem middelværdierne
# generate the twin axes
plt.figure(15)
host = host_subplot(111)
par = host.twinx()

# plot the bars (use host. instead of plt.)
x = np.array(smart_Sept_dd.reset_index().sort_values(by=['Satellitter_gns'])['Punkt'])
y = np.array(smart_Sept_dd.sort_values(by=['Satellitter_gns'])['Difference'])
p1 = host.bar(x, y, color='steelblue', label = 'Difference')

# plot the scatter plot (use par. instead of plt.)
x = np.array(first_smart_Sept_h_std.sort_values(by=['Satellitter_gns'])['Punkt'])
y = np.array(first_smart_Sept_h_std.sort_values(by=['Satellitter_gns'])['Ellipsoidehøjde'])
p2 = par.scatter(x, y, s=6, color='darkorange', label = 'std 1. måling')
x = np.array(second_smart_Sept_h_std.sort_values(by=['Satellitter_gns'])['Punkt'])
y = np.array(second_smart_Sept_h_std.sort_values(by=['Satellitter_gns'])['Ellipsoidehøjde'])
p3 = par.scatter(x, y, s=6, color='purple', label = 'std 2. måling')

plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9, top=0.9)
plt.legend(fontsize='xx-small',loc='best')
plt.xticks(rotation='vertical')
host.set_ylim(-100, 100)
par.set_ylim(0, 30)
host.set_ylabel("Difference [mm]")
par.set_ylabel("Spredning [mm]")
plt.title('Septentrio på Smartnet \n \n Spredning på 1. og 2. måling samt differencen mellem middelværdi på 1. og 2. måling', fontsize=10)
#manager = plt.get_current_fig_manager()
#manager.resize(*manager.window.maxsize())
plt.savefig("Figurer/RTK_std_diff_S_H.png")


# RTK Septentrio på GPSnet: Spredning af måling 1 og 2, samt difference mellem middelværdierne
# generate the twin axes
plt.figure(16)
host = host_subplot(111)
par = host.twinx()

# plot the bars (use host. instead of plt.)
x = np.array(GPS_Sept_dd.reset_index().sort_values(by=['Satellitter_gns'])['Punkt'])
y = np.array(GPS_Sept_dd.sort_values(by=['Satellitter_gns'])['Difference'])
p1 = host.bar(x, y, color='steelblue', label = 'Difference')

# plot the scatter plot (use par. instead of plt.)
x = np.array(first_GPS_Sept_h_std.sort_values(by=['Satellitter_gns'])['Punkt'])
y = np.array(first_GPS_Sept_h_std.sort_values(by=['Satellitter_gns'])['Ellipsoidehøjde'])
p2 = par.scatter(x, y, s=6, color='darkorange', label = 'std 1. måling')
x = np.array(second_GPS_Sept_h_std.sort_values(by=['Satellitter_gns'])['Punkt'])
y = np.array(second_GPS_Sept_h_std.sort_values(by=['Satellitter_gns'])['Ellipsoidehøjde'])
p3 = par.scatter(x, y, s=6, color='purple', label = 'std 2. måling')

plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9, top=0.8)
plt.legend(fontsize='xx-small',loc='best')
plt.xticks(rotation='vertical')
host.set_ylim(-100, 100)
par.set_ylim(0, 30)
host.set_ylabel("Difference [mm]")
par.set_ylabel("Spredning [mm]")
plt.title('Septentrio på GPSnet \n \n Spredning på 1. og 2. måling samt differencen mellem middelværdi på 1. og 2. måling', fontsize=10)
#manager = plt.get_current_fig_manager()
#manager.resize(*manager.window.maxsize())
plt.savefig("Figurer/RTK_std_diff_S_G.png")

#Plot RTK mean med konfidensinterval
plt.figure(17)
x = konfidens_df['Punkt']
y = konfidens_df['Middel difference']
konf = [list(konfidens_df['Nedre grænse']), list(konfidens_df['Øvre grænse'])]
plt.errorbar(x, y, yerr=konf,capsize=0.8, fmt='.')
plt.xticks(rotation='vertical')
plt.ylabel("Difference [mm]")
plt.title('RTK nøjagtighed med konfidensinterval')
plt.savefig("Figurer/RTK_conf_all.png")

#Plot FS mean med konfidensinterval
plt.figure(18)
x = fs_konfidens_df['Punkt']
y = fs_konfidens_df['Middel difference']
konf = [list(fs_konfidens_df['Nedre grænse']), list(fs_konfidens_df['Øvre grænse'])]
plt.errorbar(x, y, yerr=konf,capsize=0.8, fmt='.')
plt.xticks(rotation='vertical')
plt.ylabel("Difference [mm]")
plt.title('Fast Static nøjagtighed med konfidensinterval')
plt.savefig("Figurer/FS_conf_all.png")

plt.show()