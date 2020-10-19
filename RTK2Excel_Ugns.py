#%%
# # Python script til håndtering af RTK filer.
# konverterer til én excel (GNSS_RTK.xlsx) fil med kolonnerne:
# "Punkt ID","North","East","Ellipsoide højde", "Beregnet ellipsoide højde","Dato","Tid","Antenne højde",
# "Sektor","Net","Instrument type (bogstav)","Måling nr","udflytning","kote","Beregnet kote","Sats",
# "Max SV","Min SV","1D QC", "2D QC", "PDOP","HDOP","VDOP","TDOP","GDOP","Max Hz Prec","Min Hz Prec",
# "MaxV Prec","MinV Prec","Max PDOP","Min DPOP","Instrument",'Måler',"Bemærkning"
import pandas as pd
import csv
import numpy as np
import re
import pyexcel

# Måler initialer brugt i filnavne:
maaler = ["ND", "AP", "Rene"]
# undermapper
path = ["RTK_Niklas/", "RTK_Anna/", "RTK_Rene/"]

pkt_path = "Punktudvalg.xlsx"
#pkt_path = "/GRF/Medarbejdere/majws/MP4.7_2020/Nøjagtighedstest/QGIS/Punktudvalg.xlsx"

# nivellement
niv_paths = ["Anna/GNSS_niv_AP", "Niklas/GNSS_niv_ND", "Rene/GNSS_niv_Rene"]
#niv_paths = [
#    "/GRF/Medarbejdere/majws/MP4.7_2020/Nøjagtighedstest/DATA/Nivellement/Anna/GNSS_niv_AP",
#    "/GRF/Medarbejdere/majws/MP4.7_2020/Nøjagtighedstest/DATA/Nivellement/Niklas/GNSS_niv_ND",
#    "/GRF/Medarbejdere/majws/MP4.7_2020/Nøjagtighedstest/DATA/Nivellement/Rene/GNSS_niv_Rene"
#]
udflytning = []
for niv_path in niv_paths:
    niv_file = open(niv_path, "r")
    Lines = niv_file.readlines()
    for line in Lines:
        if re.match(r"^#.*", line):
            row = line.split(" ")
            if re.match(r".*_[uU].*$", row[2]):
                udflytning.append([row[1], row[6]])
    niv_file.close

udflytning_names = [r[0] for r in udflytning]
#%%

# load reference excel ark
sheet1 = pyexcel.get_sheet(
    file_name=pkt_path, sheet_name="5D_all", name_columns_by_row=0
)
for it, name in enumerate(sheet1.column["GPS_NR"]):
    sheet1[it, "GPS_NR"] = re.sub("[^A-Za-z0-9]+", "", sheet1[it, "GPS_NR"])
sheet2 = pyexcel.get_sheet(
    file_name=pkt_path, sheet_name="Ekstra G.I_G.M_10km", name_columns_by_row=0
)
for it, name in enumerate(sheet2.column["Ident"]):
    sheet2[it, "Ident"] = re.sub("[^A-Za-z0-9]+", "", sheet2[it, "Ident"])
    sheet2[it, "Landsnummer"] = re.sub("[^A-Za-z0-9]+", "", sheet2[it, "Landsnummer"])
sheet3 = pyexcel.get_sheet(
    file_name=pkt_path, sheet_name="Ekstra bolte", name_columns_by_row=0
)
for it, name in enumerate(sheet3.column["Landsnr"]):
    sheet3[it, "Landsnr"] = re.sub("[^A-Za-z0-9]+", "", sheet3[it, "Landsnr"])

#%%
frames = []
extra = [None]
for j, name in enumerate(maaler):
    sept_filename = "GNSS_Sept_" + name + ".txt"
    if name == "ND":
        leica_filename = "GNSS_LEICA_" + name + ".txt"
    else:
        leica_filename = "GNSS_Leica_" + name + ".txt"
    trimble_filename = "GNSS_Trimble_" + name + ".txt"

    # Septentrio data
    sept_data = []
    try:
        with open(path[j] + sept_filename, "r") as file:
            reader = csv.reader(file)
            for row in reader:
                if not row:
                    continue
                else:
                    for i, line in enumerate(row[5:]):
                        spline = line.split(":")
                        if spline[0] == "TIME":
                            row[i + 5] = spline[1] + ":" + spline[2] + ":" + spline[3]
                        else:
                            row[i + 5] = spline[1]
                    pkt_name = row[4].split("_")
                    row[4] = pkt_name[0]
                    net = pkt_name[1][0]
                    instr_type = pkt_name[1][1]
                    maaling = pkt_name[2]
                    udtraek = ""
                    if len(pkt_name) > 3:
                        if pkt_name[1] in ['u','U']:
                            udtraek = pkt_name[1]
                            net = pkt_name[2][0]
                            instr_type = pkt_name[2][1]
                            maaling = pkt_name[3]
                        else:
                            udtraek = pkt_name[3]
                    row.extend(extra)
                    row.extend(["Sept", name, net, instr_type, maaling, udtraek])

                    sept_data.append(row)
        sept_data = np.array(sept_data)
        sept_dataFM = pd.DataFrame(
            data=sept_data[
                0:,
                [
                    0,
                    4,
                    1,
                    2,
                    3,
                    20,
                    20,
                    20,
                    17,
                    18,
                    19,
                    20,
                    24,
                    23,
                    25,
                    26,
                    20,
                    20,
                    8,
                    20,
                    20,
                    20,
                    20,
                    10,
                    11,
                    12,
                    13,
                    14,
                    20,
                    20,
                    20,
                    20,
                    20,
                    20,
                    21,
                    22,
                    20,
                    20,
                    20
                ],
            ]
        )
    except Exception as e:
        print("could not process: " + path[j] + sept_filename)
        print(e)
#%%
    # Leica data
    leica_data = []
    try:
        with open(path[j] + leica_filename, "r") as file:
            reader = csv.reader(file)
            for row in reader:
                sats = 0
                if  row == "\n" or row[1] == " Kode:                 0009":
                    continue
                for i, line in enumerate(row):
                    spline = line.split(":")
                    if spline[0] == "Tid":
                        row[i] = spline[1] + ":" + spline[2] + ":" + spline[3]
                    elif spline[0] == " 1D CQ":
                        spspline = spline[1].split(". ")
                        row[i] = spspline[0]
                        QC2 = spline[2]
                    elif spline[0] == " Kode":
                        spline[1] = spline[1].strip()
                        pkt_name = spline[1].split("_")
                        row[i] = pkt_name[0]
                        if len(pkt_name[1]) > 1:
                            net = pkt_name[1][0]
                            instr_type = pkt_name[1][1]
                        else:
                            net = None
                            instr_type = None
                        maaling = pkt_name[2]
                        udtraek = ""
                        if len(pkt_name) > 3:
                            if pkt_name[1] in ['u','U']:
                                udtraek = pkt_name[1]
                                net = pkt_name[2][0]
                                instr_type = pkt_name[2][1]
                                maaling = pkt_name[3]
                            else:
                                udtraek = pkt_name[3]
                    elif spline[0] in ["GPS Sats", "GLONASS Sats", "Galileo Sats"]:
                        sats += float(spline[1])
                    else:
                        spline[1] = spline[1].strip(" ")
                        row[i] = spline[1]
                row.extend(extra)
                row.extend(
                    [QC2, sats, "Leica", name, net, instr_type, maaling, udtraek]
                )
                leica_data.append(row)

        leica_data = np.array(leica_data)
        leica_dataFM = pd.DataFrame(
            data=leica_data[
                0:,
                [
                    0,
                    1,
                    3,
                    2,
                    4,
                    18,
                    18,
                    18,
                    16,
                    15,
                    17,
                    18,
                    24,
                    23,
                    25,
                    26,
                    18,
                    18,
                    20,
                    18,
                    18,
                    5,
                    19,
                    9,
                    8,
                    11,
                    10,
                    7,
                    18,
                    18,
                    18,
                    18,
                    18,
                    18,
                    21,
                    22,
                    18,
                    18,
                    18
                ],
            ]
        )
    except Exception as e:
        print(f"Could not process: {path[j]}{leica_filename}")
        print(e)
#%%
    # Trimble data
    trimble_data = []
    try:
        data = open(path[j] + trimble_filename, "r")
        for line in data:
            line = line.strip()
            if re.match(r"^==*", line) or line == "":
                continue
            elif re.match(r"^Nr.*", line):
                header = line.split("  ")
                trimble_header = []
                for item in header:
                    if not item:
                        continue
                    else:
                        trimble_header.append(item.strip())
            elif re.match(r"^\S{5}.*", line):
                continue
            else:
                row = line.split("  ")
                trimble_row = []
                for item in row:
                    item.strip()
                    if not item:
                        continue
                    elif re.match(r"^%[a-zA-Z]{2}.*", item):
                        continue
                    else:
                        trimble_row.append(item.strip())

                pkt_name = trimble_row[1].split("_")
                trimble_row[1] = pkt_name[0]
                net = pkt_name[1][0]
                instr_type = pkt_name[1][1]
                maaling = pkt_name[2]
                udtraek = ""
                if len(pkt_name) > 3:
                    if pkt_name[1] in ['u','U']:
                        udtraek = pkt_name[1]
                        net = pkt_name[2][0]
                        instr_type = pkt_name[2][1]
                        maaling = pkt_name[3]
                    else:
                        udtraek = pkt_name[3]
                trimble_row.extend(extra)
                trimble_row.extend(["Trimble", name, net, instr_type, maaling, udtraek])
                trimble_data.append(trimble_row)
        data.close()
        trimble_data = np.array(trimble_data)
        trimble_dataFM = pd.DataFrame(
            data=trimble_data[
                0:,
                [
                    0,
                    1,
                    4,
                    5,
                    9,
                    29,
                    29,
                    29,
                    21,
                    22,
                    20,
                    29,
                    33,
                    32,
                    34,
                    35,
                    6,
                    29,
                    29,
                    10,
                    11,
                    29,
                    29,
                    29,
                    29,
                    29,
                    29,
                    29,
                    12,
                    13,
                    14,
                    15,
                    17,
                    16,
                    30,
                    31,
                    29,
                    29,
                    29
                ],
            ]
        )
    except Exception as e:
        print(f"Could not process: {path[j]}{trimble_filename}")
        print(e)
        data.close()


    frames.extend([sept_dataFM, leica_dataFM, trimble_dataFM])

#%%
# sammensæt DataFrames, giv kolonne navne og skriv excel fil
result = pd.concat(frames, ignore_index=True)
result.columns = [
    "Punkt-ID",
    "Punktnavn",
    "North",
    "East",
    "Ellipsoidehøjde",
    "DB Ellipsoidehøjde",
    "Ellipsoidehøjdekvalitet",
    "Diff [mm]",
    "Dato",
    "Tid",
    "Antennehøjde",
    "Sektor",
    "Net",
    "Instrumenttype",
    "Måling nr.",
    "Udflytning",
    "Kote",
    "DB kote",
    "Sats",
    "Max SV",
    "Min SV",
    "1D QC",
    "2D QC",
    "PDOP",
    "HDOP",
    "VDOP",
    "TDOP",
    "GDOP",
    "Max Hz Prec",
    "Min Hz Prec",
    "MaxV Prec",
    "MinV Prec",
    "Max PDOP",
    "Min DPOP",
    "Instrument",
    "Måler",
    "Bemærkning",
    "Afstand til GPSnet",
    "Afstand til Smartnet"
]
for ind in result.index:
    punkt_name = re.sub("[^A-Za-z0-9]+", "", result["Punktnavn"][ind])
    if punkt_name in sheet1.column["GPS_NR"]:
        index = sheet1.column["GPS_NR"].index(punkt_name)
        # print(sheet1[index,"Sektor"])
        result["Sektor"][ind] = sheet1[index, "Sektor"]
        result["DB Ellipsoidehøjde"][ind] = sheet1[index, "Ellipsoidehøjde"]
        result["DB kote"][ind] = sheet1[index, "Kote"]
        result["Ellipsoidehøjdekvalitet"][ind] = sheet1[
            index, "Ellipsoidehøjdekvalitet"]
        result["Afstand til GPSnet"][ind] = sheet1[index, "Afstand_GPSnet"]
        result["Afstand til Smartnet"][ind] = sheet1[index, "Afstand_Smartnet"]
    elif punkt_name in sheet2.column["Ident"]:
        index = sheet2.column["Ident"].index(punkt_name)
        # print(sheet2[index,"Sektor"])
        result["Sektor"][ind] = sheet2[index, "Sektor"]
        result["DB Ellipsoidehøjde"][ind] = sheet2[index, "Ellipsoidehøjde"]
        result["DB kote"][ind] = sheet2[index, "Kote"]
        result["Ellipsoidehøjdekvalitet"][ind] = sheet2[
            index, "Ellipsoidehøjdekvalitet"]
        result["Afstand til GPSnet"][ind] = sheet2[index, "Afstand_GPSnet"]
        result["Afstand til Smartnet"][ind] = sheet2[index, "Afstand_Smartnet"]
    elif punkt_name in sheet2.column["Landsnummer"]:
        index = sheet2.column["Landsnummer"].index(punkt_name)
        result["Sektor"][ind] = sheet2[index, "Sektor"]
        result["DB Ellipsoidehøjde"][ind] = sheet2[index, "Ellipsoidehøjde"]
        result["DB kote"][ind] = sheet2[index, "Kote"]
        result["Ellipsoidehøjdekvalitet"][ind] = sheet2[
            index, "Ellipsoidehøjdekvalitet"]
        result["Afstand til GPSnet"][ind] = sheet2[index, "Afstand_GPSnet"]
        result["Afstand til Smartnet"][ind] = sheet2[index, "Afstand_Smartnet"]
    elif punkt_name in sheet3.column["Landsnr"]:
        index = sheet3.column["Landsnr"].index(punkt_name)
        # print(sheet3[index,"Sektor"])
        result["Sektor"][ind] = sheet3[index, "Sektor"]
        result["DB Ellipsoidehøjde"][ind] = sheet3[index, "Ellipsoidehøjde"]
        result["DB kote"][ind] = sheet3[index, "Kote"]
        result["Ellipsoidehøjdekvalitet"][ind] = sheet3[
            index, "Ellipsoidehøjdekvalitet"]
        result["Afstand til GPSnet"][ind] = sheet3[index, "Afstand_GPSnet"]
        result["Afstand til Smartnet"][ind] = sheet3[index, "Afstand_Smartnet"]


# udskift punktum med komma
for column in result[
    [
        "North",
        "East",
        "Ellipsoidehøjde",
        "DB Ellipsoidehøjde",
        "Antennehøjde",
        "Kote",
        "DB kote",
        "Sats",
        "Max SV",
        "Min SV",
        "1D QC",
        "2D QC",
        "PDOP",
        "HDOP",
        "VDOP",
        "TDOP",
        "GDOP",
        "Max Hz Prec",
        "Min Hz Prec",
        "MaxV Prec",
        "MinV Prec",
        "Max PDOP",
        "Min DPOP"
    ]
]:
    for i, number in enumerate(result[column]):
        if column == "DB kote":
            if result["Punktnavn"][i] in udflytning_names:
                index = udflytning_names.index(result["Punktnavn"][i])
                if number not in [None, ""]:
                    number = float(number) + float(udflytning[index][1])
                    number = str(number)
        if column == "DB Ellipsoidehøjde":
            if result["Punktnavn"][i] in udflytning_names:
                index = udflytning_names.index(result["Punktnavn"][i])
                if number not in [None, ""]:
                    number = float(number) + float(udflytning[index][1])
                    number = str(number)         
        if isinstance(number, str) and re.match(r"^[\d\.]*$", number):
            result[column][i] = re.sub(r"\.", ",", number)

for i, number in enumerate(result["Diff [mm]"]):
    if not (result["Ellipsoidehøjde"][i] in [None, ""] or result["DB Ellipsoidehøjde"][i] in [None, ""]):
        if re.match(r'.*Ellipsoid Højde.*', str(result["Ellipsoidehøjde"][i])):
            result["Ellipsoidehøjde"][i] = re.sub('Ellipsoid Højde:', '', result["Ellipsoidehøjde"][i])
            result["Ellipsoidehøjde"][i] = result["Ellipsoidehøjde"][i].strip()
        try:
            DB_E_h = result["DB Ellipsoidehøjde"][i]
            E_h = result["Ellipsoidehøjde"][i]
            if isinstance(result["DB Ellipsoidehøjde"][i], str):
                DB_E_h = float(re.sub(r",", ".", result["DB Ellipsoidehøjde"][i]))           
            if isinstance(result["Ellipsoidehøjde"][i], str):
                E_h = float(re.sub(r",", ".", result["Ellipsoidehøjde"][i]))
            number = int((E_h - DB_E_h) * 1000)
            number = str(number)
            result["Diff [mm]"][i] = re.sub(r"\.", ",", number)
        except:
            pass 

result.to_excel("GNSS_RTK.xlsx")
selected_columns = result[["Punktnavn", "Måling nr.", "Instrumenttype"]]

selected_columns["pkt_name_instr"] = selected_columns["Punktnavn"].str.cat(
    selected_columns["Instrumenttype"], sep=" "
)
count = selected_columns.groupby(by="pkt_name_instr", as_index=False).agg(
    {"Måling nr.": pd.Series.nunique}
)

count = count.values.tolist()
with open("counting.txt", "w") as output:
    output.write("første kolonne tæller antallet af forskellige målenr.\n Altså 2 betyder der både er en måling 1 og 2\n")
    output.write("#  Pkt navn instr\n")
    for line in count: 
        output.write(f"{line[1]}    {line[0]}\n")

