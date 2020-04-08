import pandas as pd
import numpy as np
import os
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import clear_output
from dateutil import parser
from datetime import datetime, time
import itertools
from tqdm import tqdm
import sys
import warnings
import json
import datetime
import Calculate_Time_Domain as td

if not sys.warnoptions:
    warnings.simplefilter("ignore")
# pbar = tqdm(total=36)
# pbar.update(1)
# pbar.close()

def Get_Segmented_Table(File, Before, Finish):

    Before = int(Before)
    Finish = int(Finish)

    Date = File.split("\\")[-1].split("_")[:3][::-1]
    Date = datetime.datetime(int(Date[0]), int(Date[1]), int(Date[2]))
#     try:
    with open(File) as F:
        Temp_Data = F.readlines()
    Cleaned = []
    for i in Temp_Data:
        Cleaned.append(i.replace("\n", ""))

    Segmented=[]
    for C in Cleaned[:-1]:
        Sample = int(C.split(",")[0])

        if Date.replace(hour=Finish-Before) < addSecs(Date,Sample/128) < Date.replace(hour=Finish):
               Segmented.append(C)
        else:
            pass

    Table = Load_Data_Ann(Segmented) 

    return Table


#     except:
#         pass
#         print("No File to Process")

def Get_ANN_Files():
    ANN_Files = []
    for File in os.listdir("C0161//"):
        if File.endswith(".annauxmix"):
            ANN_Files.append("C0161//"+ str(File))
    return ANN_Files

def addSecs(Base, Seconds):
    return Base + datetime.timedelta(seconds=Seconds)

def Get_Pure_NNs(Test_Table):
    
    Test_Table = Test_Table
    
    Allowed_Symbols = ["N", "F"]
    Base = Test_Table["Beats"][0]
    Pure_NNs = []
    Thresh_Hold = 15
    # Output: Pandas(Index=222, _1=0.7734375, Symbols='N')
    # Pandas[0]
    # Output: 222 
    for Row in Test_Table.itertuples():
        try:
            To_Compare = Row[1]

            Percentage_Difference = abs(((Base-To_Compare)/Base)*100)

            if Percentage_Difference <= float(Thresh_Hold) and Row[3] == 1 and Row[4]==0:
                Pure_NNs.append(Row[1])
                Test_Table.loc[Row[0], "Pure"] = 1
                Base = Row[1]
                Thresh_Hold = 15

            elif Row[3] == 0:
                Base=Row[1]

            elif Row[4]==1:
                try:
                    Future_Element_One = Test_Table.loc[Row[0]+1, "RR Intervals"]
                    Future_Element_Two = Test_Table.loc[Row[0]+2, "RR Intervals"]
                    Future_Element_Three = Test_Table.loc[Row[0]+3, "RR Intervals"]
                    Base=Row[1]
                    Future_Percentage_Difference_One = abs(((Base-Future_Element_One)/Base)*100)
                    Future_Percentage_Difference_Two = abs(((Future_Element_One-Future_Element_Two)/Future_Element_One)*100)
#                     Future_Percentage_Difference_Three = abs(((Future_Element_Two-Future_Element_Three)/Future_Element_Two)*100)

#                     if Future_Percentage_Difference_One <= 5 and Future_Percentage_Difference_Two <= 15 and Future_Percentage_Difference_Three <= 15:
                    if Future_Percentage_Difference_One <= 5 and Future_Percentage_Difference_Two <= 15:

                        Pure_NNs.append(Row[1])
                        Test_Table.loc[Row[0], "Pure"] = 1
                        Thresh_Hold = 15
                        Base = Row[1]
                    else:
                        Base = Test_Table.loc[Row[0]+1, "RR Intervals"]
                        Thresh_Hold = 15
                except:
                    Pure_NNs.append(Row[1])
                    Test_Table.loc[Row[0], "Pure"] = 1
                    Base = Row[1]
                    Thresh_Hold = 15
            elif Row[4] == 0:
    #             print(Row)
                Element_1 = Test_Table.loc[Row[0], "RR Intervals"]
                Element_2 = Test_Table.loc[Row[0]+1, "RR Intervals"]
                Average = (Element_1 + Element_2)/2
                Thresh = Average*0.05
                Min = Average - Thresh
                Max = Average + Thresh

                Average_Check = Test_Table.loc[Row[0]+2, "RR Intervals"]

                if Min <= Average_Check <= Max:
                    Pure_NNs.append(Row[1])
                    Test_Table.loc[Row[0], "Pure"] = 1
                    Base = Row[1]
                    Thresh_Hold = 15
                else:
                    Base = Row[1]
                    Thresh_Hold = 15
            else:
                print("Missing Condition")
                Base = Row[1]
                Thresh_Hold = 15
        except:
            Base = Row[1]
    
    return Test_Table

def Calculate_Pure_Td(Pure_NNs):
    Pure_SDNN = td.Calculate_SDNN(Pure_NNs)
    Pure_ASDNN = td.Calculate_ASDNN(Pure_NNs)
    Pure_SDANN = td.Calculate_SDANN(Pure_NNs)
    Pure_NN50 = td.Calculate_NN50(Pure_NNs)
    Pure_pNN50 = td.Calculate_pNN50(Pure_NNs, Pure_NN50)
    Pure_rMSSD = td.Calculate_rMSSD(Pure_NNs)
    
    Collection = {
                    "Pure_SDNN" : Pure_SDNN,
                    "Pure_ASDNN" : Pure_ASDNN,
                    "Pure_SDANN" : Pure_SDANN,
                    "Pure_NN50" : Pure_NN50,
                    "Pure_pNN50" : Pure_pNN50,
                    "Pure_rMSSD" : Pure_rMSSD
                 }
    
    return Collection

def Load_Data_Ann(Segmented):
    List = Segmented
    Frequency = 128
    Peaks = []
    Symbols = []
    for i in List:
        if not i.strip(): continue
        Temp = i.split(",")
        Peaks.append(int(Temp[0]))
        Symbols.append(",".join(Temp[1:]))
            

    annotation = pd.DataFrame(columns=["Peaks","Symbols"])
    annotation["Peaks"] = Peaks
    annotation["Symbols"] = Symbols
    del Peaks
    del Symbols

    if pd.isnull(annotation).all()["Symbols"] == True:
        Symbol = "N"
        annotation["Symbols"] = Symbol
    else:
        pass

    Arr = np.array(annotation.Symbols)
    Arr

    Table = pd.DataFrame(columns=["RR Peaks", "RR Intervals", "Symbols", "Mask", "Elements_To_Skip", "To_Skip_NN50"])
    Table

    Table["RR Peaks"]  = np.array(annotation.Peaks)

    Table["RR Intervals"] = np.insert(np.diff(annotation.Peaks)/int(Frequency), 0, annotation.Peaks[0], axis=0)

    Table["Symbols"] = annotation.Symbols

    Table.head()

    np.unique(Arr)

    if np.unique(Arr).size > 1:
        None_N_Symbols = list(np.unique(Arr))
        try:
            None_N_Symbols.remove("N")
        except:
            pass
        try:
            None_N_Symbols.remove("F")
        except:
            pass
        try:
            None_N_Symbols.remove("L")
        except:
            pass
        try:
            None_N_Symbols.remove("R")
        except:
            pass
        try:
            None_N_Symbols.remove("B")
        except:
            pass

        Mask = np.empty(0)
        Elements_To_Skip = np.empty(0)
        To_Skip_NN50 = np.empty(0)
        for S in None_N_Symbols:
            Temp = np.array([i for i, v in enumerate(Arr) if str(S) in v])
            Temp_1 = np.array([i for i, v in enumerate(Arr) if str(S) in v]) + 1
            Temp_2 = np.array([i for i, v in enumerate(Arr) if str(S) in v]) + 2
            Mask = np.concatenate((Mask, Temp))
            Elements_To_Skip = np.concatenate((Elements_To_Skip, Temp_1))
            To_Skip_NN50 = np.concatenate((To_Skip_NN50, Temp_2))
            del Temp
            del Temp_1
            del Temp_2

        Table.loc[Mask, "Mask"] = 1
        Temp = np.delete(np.array(Table.index), Mask)
        Table.loc[Temp, "Mask"] = 0
        del Temp

        try:
            Elements_To_Skip = np.delete(Elements_To_Skip, np.argwhere(Elements_To_Skip == Elements_To_Skip.max()))
        except:
            pass
        Table.loc[Elements_To_Skip, "Elements_To_Skip"] = 1
        Temp = np.delete(np.array(Table.index), Elements_To_Skip)
        Table.loc[Temp, "Elements_To_Skip"] = 0
        del Temp

        try:
            To_Skip_NN50 = np.delete(To_Skip_NN50, np.argwhere(To_Skip_NN50 == To_Skip_NN50.max()))
            To_Skip_NN50 = np.delete(To_Skip_NN50, np.argwhere(To_Skip_NN50 == To_Skip_NN50.max()))
        except:
            pass
        Table.loc[To_Skip_NN50, "To_Skip_NN50"] = 1
        Temp = np.delete(np.array(Table.index), To_Skip_NN50)
        Table.loc[Temp, "To_Skip_NN50"] = 0
        del Temp
    else:
        Table["Mask"] = 0
        Table["Elements_To_Skip"] = 0
        Table["To_Skip_NN50"] = 0

    return Table