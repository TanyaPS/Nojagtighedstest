"""
Læser Excel-fil fra kørsel af RTK2Excel_Ugns.py og tilføjer kolonne med gennemsnitligt antal satelitter for hvert punkt.
Kun relevante kolonner er taget med i output.
"""
import pyexcel
import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
from datetime import datetime
import re


data = pyexcel.get_sheet(file_name="GNSS_RTK.xlsx", name_columns_by_row=0)

# Relevante kolonner udtages
sektor = data.column[12]
pkter = data.column[2]
date = data.column[9]
tid = data.column[10]
ellipsoideh = data.column[5]
db_h = data.column[6]
sats = data.column[19]
sats_min = data.column[20]
diff = data.column[8]
instrument =  data.column[14]
net = data.column[13]
sektor = data.column[12]
meas_num = data.column[15]
kval = data.column[7]
PDOP = data.column[24]
PDOP_max = data.column[33]
dist_GPSnet = data.column[38]
dist_smart = data.column[39]

#Lister oprettes til at fylde korrekt formateret data ind i
satellitter = []
punkter = []
dato = []
e_h = []
kvalitet = []
meas_number = []
instr = []
netv = []
sekt = []
difference = []
p_dop = []
dist_net = []

# Her ensrettes datostempling og parametre for de forskellige instrumenter
for i, sat in enumerate(sats):
    if net[i] == 'S':
        continue
    if db_h[i] == '':
        continue
    if date[i][0:4] == 'Dato':
        date[i]= date[i][5:]
    if PDOP[i][0:4] == 'PDOP':
        PDOP[i]= PDOP[i][5:]
    if sat == '':
        satellitter.append(int(sats_min[i]))
    else:
        satellitter.append(int(sat))

    if instrument[i] == 'S':
        d = date[i]
        date[i] = d[3:5] + '-' + d[0:2] + d[5:]
    elif instrument[i] == 'G':
        PDOP[i] = PDOP_max[i]
        d = date[i]
        date[i] = d[8:] + d[4:7] + '-' + d[0:4]

    if not re.match(r"\d{2}:\d{2}:\d{2}",tid[i]):
        hrms = tid[i].split(':')
        for j, nmbr in enumerate(hrms):
            nmbr = nmbr.strip()
            if not re.match(r"\d{2}",nmbr):
                hrms[j] = '0' + nmbr
        tid[i] = hrms[0] + ':' + hrms[1] + ':' + hrms[2]

    if re.match(r".*60$",tid[i]):
        hrms = tid[i].split(':')
        hrms[2] = '00'
        hrms[1] = str(int(hrms[1]) + 1)

        tid[i] = hrms[0] + ':' + hrms[1] + ':' + hrms[2] 

    if net[i] == 'H':
        dist_net.append(dist_smart[i])
    elif net[i] == 'G':
        dist_net.append(dist_GPSnet[i])

    date[i] = date[i] + ' ' + tid[i]
    dato.append(datetime.strptime(date[i], '%d-%m-%Y %H:%M:%S'))
    difference.append(float(diff[i]))
    PDOP[i] = PDOP[i].replace(',', '.')
    p_dop.append(float(PDOP[i]))
    ellipsoideh[i] = ellipsoideh[i].replace(',', '.')
    e_h.append(float(ellipsoideh[i]))
    kvalitet.append(kval[i])
    meas_number.append(meas_num[i])
    instr.append(instrument[i])
    netv.append(net[i])
    sekt.append(sektor[i])
    punkter.append(pkter[i])


"""
Indlæsning af data i dataframe
"""

data_dict = {'Punkt': punkter, 'Dato': dato, 'Ellipsoidehøjde': e_h,'Ellipsoidehøjdekvalitet': kvalitet, 'Måling nr.': meas_number,
             'Instrument': instr, 'Net': netv, 'Sektor': sekt, 'Satellitter': satellitter, 'Difference i mm': difference, 'PDOP': p_dop, 'Afstand til reference station': dist_net}
# Dataframe for alt data
df = DataFrame(data_dict,columns=['Punkt', 'Dato', 'Ellipsoidehøjde', 'Ellipsoidehøjdekvalitet', 'Måling nr.', 'Instrument', 'Net', 
                                  'Sektor', 'Satellitter', 'Difference i mm', 'PDOP', 'Afstand til reference station'])
# Dataframes for hvert instrument på eget net
df_HH = df[:][(df.Instrument == 'H') & (df.Net == 'H')] 
df_GG = df[:][(df.Instrument == 'G') & (df.Net == 'G')]


'''
Beregn en værdi for det gennemsnitlige antal satelitter pr. punkt
'''

# For alt data
mean_sat = df.groupby(['Punkt'])['Satellitter'].agg('mean').reset_index()
df = pd.merge(df, mean_sat, left_on='Punkt', right_on='Punkt', how='outer', suffixes=(None, '_gns'))
# Omarrangerer kolonner, så det passer med andre scripts
cols = df.columns.tolist()
cols = cols[:9] + cols[-1:] + cols[9:-1]
df = df[cols]

# For HH
mean_sat = df_HH.groupby(['Punkt'])['Satellitter'].agg('mean').reset_index()
df_HH = pd.merge(df_HH, mean_sat, left_on='Punkt', right_on='Punkt', how='outer', suffixes=(None, '_gns'))
df_HH = df_HH[cols]

# For GG
mean_sat = df_GG.groupby(['Punkt'])['Satellitter'].agg('mean').reset_index()
df_GG = pd.merge(df_GG, mean_sat, left_on='Punkt', right_on='Punkt', how='outer', suffixes=(None, '_gns'))
df_GG = df_GG[cols]


'''
Gem dataframes i excel-fil
'''

df.to_excel('Cleaned_GNSS_RTK.xlsx')

df_HH.to_excel('Cleaned_GNSS_RTK_HH.xlsx')

df_GG.to_excel('Cleaned_GNSS_RTK_GG.xlsx')
