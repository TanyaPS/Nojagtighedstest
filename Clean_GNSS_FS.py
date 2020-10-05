"""
Læser fast statik beregning Excel fil og laver en ny, ren fast static excel fil
"""
import pyexcel
import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
from datetime import datetime
import re

FS_path = "../FS-beregninger/Resultater_SROK/GNSS_FS_resultat.xlsx"
#FS_path = "GNSS_FS_resultat.xlsx"

#pkt_path = "Punktudvalg.xlsx"
pkt_path = "/GRF/Medarbejdere/majws/MP4.7_2020/Nøjagtighedstest/QGIS/Punktudvalg.xlsx"

# nivellement
#niv_paths = ["Anna/GNSS_niv_AP", "Niklas/GNSS_niv_ND", "Rene/GNSS_niv_Rene"]
niv_paths = [
   "/GRF/Medarbejdere/majws/MP4.7_2020/Nøjagtighedstest/DATA/Nivellement/Anna/GNSS_niv_AP",
   "/GRF/Medarbejdere/majws/MP4.7_2020/Nøjagtighedstest/DATA/Nivellement/Niklas/GNSS_niv_ND",
   "/GRF/Medarbejdere/majws/MP4.7_2020/Nøjagtighedstest/DATA/Nivellement/Rene/GNSS_niv_Rene",
]
udflytning = []
for niv_path in niv_paths:
    niv_file = open(niv_path, "r")
    Lines = niv_file.readlines()
    for line in Lines:
        if re.match(r"^#.*", line):
            row = line.split(" ")
            if re.match(r".*[uU]$", row[2]):
                udflytning.append([row[1], row[6]])
    niv_file.close

udflytning_names = [r[0] for r in udflytning]


#fast static data
data = pyexcel.get_sheet(file_name=FS_path, sheet_name = "Fast Static-målinger", name_columns_by_row=0)

punkt = data.column[2]
h_m= data.column[4]
h_db = data.column[6]
difference = data.column[7]
instrument = data.column[8]
maaling = data.column[10]

# load reference excel ark
sheet1 = pyexcel.get_sheet(
    file_name=pkt_path, sheet_name="5D_all", name_columns_by_row=0
)
#for it, name in enumerate(sheet1.column["GPS_NR"]):
#    sheet1[it, "GPS_NR"] = re.sub("[^A-Za-z0-9]+", "", sheet1[it, "GPS_NR"])
sheet2 = pyexcel.get_sheet(
    file_name=pkt_path, sheet_name="Ekstra G.I_G.M_10km", name_columns_by_row=0
)
#for it, name in enumerate(sheet2.column["Ident"]):
#    sheet2[it, "Ident"] = re.sub("[^A-Za-z0-9]+", "", sheet2[it, "Ident"])
#    sheet2[it, "Landsnummer"] = re.sub("[^A-Za-z0-9]+", "", sheet2[it, "Landsnummer"])
sheet3 = pyexcel.get_sheet(
    file_name=pkt_path, sheet_name="Ekstra bolte", name_columns_by_row=0
)
#for it, name in enumerate(sheet3.column["Landsnr"]):
#    sheet3[it, "Landsnr"] = re.sub("[^A-Za-z0-9]+", "", sheet3[it, "Landsnr"])

punkter = []
pkt = []
elip_m = []
elip_db = []
udflyt = []
diff = []
instr = []
meas = []
h = 0

for i, p in enumerate(punkt):
    if re.match(r'.*_[Uu]$', str(p)):
        udflyt.append('U')
        p = re.sub(r'_[12HGSU]_*[12HGSU]*_*[12U]*', '', str(p))
    elif re.match(r'.*_[12HGSU]_*[12HGSU]*_*[12U]*$', str(p)):
        udflyt.append('')
        p = re.sub(r'_[12HGSU]_*[12HGSU]*_*[12U]*', '', str(p))
    else:
        udflyt.append('')



    if not (p == '' or h_m[i] == ''):
        


        if p in sheet1.column["GPS_NR"]:
            index = sheet1.column["GPS_NR"].index(p)
            # print(sheet1[index,"Sektor"])
            elip_db.append(sheet1[index, "Ellipsoidehøjde"])
        elif p in sheet2.column["Ident"]:
            index = sheet2.column["Ident"].index(p)
            elip_db.append(sheet2[index, "Ellipsoidehøjde"])
        elif p in sheet2.column["Landsnummer"]:
            index = sheet2.column["Landsnummer"].index(p)
            elip_db.append(sheet2[index, "Ellipsoidehøjde"])
        elif p in sheet3.column["Landsnr"]:
            index = sheet3.column["Landsnr"].index(p)
            elip_db.append(sheet3[index, "Ellipsoidehøjde"])
        else:
            continue
        if elip_db[-1] == '':
            continue
        else:
            if p in udflytning_names:
                ind = udflytning_names.index(p)
                h = float(h_m[i]) - float(udflytning[ind][1])
            else:
                h = float(h_m[i])
            diff.append((h-elip_db[-1])*1000)
            pkt.append(p)
            elip_m.append(float(h_m[i]))
            instr.append(instrument[i])
            meas.append(maaling[i])







data_dict = {'Punkt': pkt, 'Måling nr.': meas, 'Instrument': instr, 'Ellipsoideh': elip_m, 'Difference': diff}
df = DataFrame(data_dict,columns=['Punkt', 'Måling nr.', 'Instrument', 'Ellipsoideh', 'Difference'])

df.to_excel('Cleaned_GNSS_FS.xlsx')