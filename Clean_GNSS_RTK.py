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

for i, sat in enumerate(sats):
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


data_dict = {'Punkt': punkter, 'Dato': dato, 'Ellipsoidehøjde': e_h,'Ellipsoidehøjdekvalitet': kvalitet, 'Måling nr.': meas_number, 'Instrument': instr, 'Net': netv, 'Sektor': sekt, 'Satellitter': satellitter, 'Satellitter_gns': satellitter, 'Difference i mm': difference, 'PDOP': p_dop}
df = DataFrame(data_dict,columns=['Punkt', 'Dato', 'Ellipsoidehøjde', 'Ellipsoidehøjdekvalitet', 'Måling nr.', 'Instrument', 'Net', 'Sektor', 'Satellitter', 'Satellitter_gns', 'Difference i mm', 'PDOP'])

mean_sat = df.groupby(['Punkt'])['Satellitter'].agg('mean').reset_index()
list_mean_sat = list(mean_sat.Punkt)

for i, pkt in enumerate(pkter):
    index = list_mean_sat.index(pkt)
    satellitter[i] = round(mean_sat.Satellitter[index],1)

df.Satellitter_gns = satellitter

df.to_excel('Cleaned_GNSS_RTK.xlsx')