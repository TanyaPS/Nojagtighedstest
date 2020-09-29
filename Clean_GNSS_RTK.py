"""
Læser Excel fil fra RTK2Excel_Ugns.py og tilføjer kolonne med gennemsnitligt antal satelitter for pkt
"""
import pyexcel
import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
from datetime import datetime
import re


data = pyexcel.get_sheet(file_name="GNSS_RTK.xlsx", name_columns_by_row=0)


sektor = data.column[12]
pkter = data.column[2]
date = data.column[9]
tid = data.column[10]
ellipsoideh = data.column[5]
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

satellitter = []

for i, sat in enumerate(sats):
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


    date[i] = date[i] + ' ' + tid[i]
    date[i] = datetime.strptime(date[i], '%d-%m-%Y %H:%M:%S')
    diff[i] = float(diff[i])
    PDOP[i] = PDOP[i].replace(',', '.')
    PDOP[i] = float(PDOP[i])


data_dict = {'Punkt': pkter, 'Dato': date, 'Ellipsoidehøjde': ellipsoideh,'Ellipsoidehøjdekvalitet': kval, 'Måling nr.': meas_num, 'Instrument': instrument, 'Net': net, 'Sektor': sektor, 'Satellitter': satellitter, 'Satellitter_gns': satellitter, 'Difference i mm': diff, 'PDOP': PDOP}
df = DataFrame(data_dict,columns=['Punkt', 'Dato', 'Ellipsoidehøjde', 'Ellipsoidehøjdekvalitet', 'Måling nr.', 'Instrument', 'Net', 'Sektor', 'Satellitter', 'Satellitter_gns', 'Difference i mm', 'PDOP'])

mean_sat = df.groupby(['Punkt'])['Satellitter'].agg('mean').reset_index()
list_mean_sat = list(mean_sat.Punkt)

for i, pkt in enumerate(pkter):
    index = list_mean_sat.index(pkt)
    satellitter[i] = round(mean_sat.Satellitter[index],1)

df.Satellitter_gns = satellitter

df.to_excel('Cleaned_GNSS_RTK.xlsx')