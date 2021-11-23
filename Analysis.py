import pyodbc as pyo
import matplotlib.pyplot as plt
import matplotlib as mt
import numpy as np
from dbfread import DBF
from datetime import datetime


def Calculate_Time(time1, time2):
    time1 = datetime.strptime(time1, "%H:%M")
    time2 = datetime.strptime(time2, "%H:%M")
    return (time2 - time1).seconds


class Analysis:
    def __init__(self, ):

        self.Total_Multi_Day = dict()
        self.Multi_Day_data = dict()  # 存放數天內的的所有資料
        self.day_list = list()  # 存放檢測天數
        self.time_list = list()  # 存放檢測時段
        self.hhList = list()  # 用來紀錄那些時間點已經有放了(以hh的角度)

        self.freq = list()  # 記錄想過濾的頻段

        self.Filtered_Data = dict()  # 放過濾後的頻段資料

        self.std = dict()  # 放每個頻段的標準差
        self.median = dict()  # 放每個頻段的中位數

        self.high_std_Freq = dict()  # 放高標準差的頻段
        self.Lv2_List = dict()  # 放高於標準差又高於中位數的頻段

        self.usage_List = dict()  # 放等級二頻段的使用率
        self.trend = dict()  # 紀錄趨勢值
        self.Alert = dict()  # 記錄哪種顏色告警

    def Read_File_For_DBF(self, filePath, ):
        ### 要在這分析出這天中每隔一小時的時間點
        print("[*] Now Reading: ./{}".format(filePath))
        Multiple_Data = dict()
        Single_Data = list()

        timeList = list()
        hhList = list()
        time = ""

        day = ""
        for dbfData in DBF(filePath, encoding='big5'):  # 單一時段最多700筆資料

            dictData = dict(dbfData)
            date = dictData["時間"]
            frequency = dictData['頻率']
            level = dictData['LEVEL']

            if date.split(" ")[2].split('.')[0][:2] in hhList:
                continue

            if time != "" and date.split(" ")[2].split('.')[0][:8] != time:

                if time[:2] not in hhList:
                    Multiple_Data[time[:5]] = Single_Data
                    hhList.append(time[:2])
                    timeList.append(time[:5])
                Single_Data = list()
            time = date.split(" ")[2].split('.')[0][:8]  # HH:mm
            Single_Data.append((date, frequency, level))

        self.hhList = hhList
        return Multiple_Data, timeList

    def Read_File_For_Access(self, filePath):
        Multi_time_data = dict()  # 用來放時段內的資料
        global data
        print("[*] Now Reading: ./{}".format(filePath))
        conn_String = (r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};"
                       r"DBQ=./" + filePath)

        conn = pyo.connect(conn_String)
        cur = conn.cursor()
        tableName = [t.table_name for t in cur.tables(tableType='TABLE')][0]

        SQL = 'SELECT * FROM "' + tableName + '"'
        cur.execute(SQL)

        rows = cur.fetchall()  # 資料都在這
        cur.close()
        conn.close()

        ### 9/15 問題: 有些資料時間是挑的 請參考圖問題-1
        # 設定初始值 (用時間去做區分)
        # tmp_time = rows[0][0].split(" ")[2].split('.')[0][:8]  # 時間單位抓到秒

        Multi_time_data = dict()
        Single_time_data = list()  # 用來放一個時段內所有的資料
        time_list = list()
        hh_list = list()
        day = ""
        time = ""
        # 分析 rows
        for data in rows:
            date = data[0]
            frequency = data[1]
            level = data[2]

            if date.split(" ")[2].split(".")[0][:2] in hh_list:
                continue

            if time != "" and time != date.split(" ")[2].split('.')[0][:8]:

                # 比較時間
                if time[:2] not in hh_list:
                    # 存放到上個時間為止的資料
                    Multi_time_data[time[:5]] = Single_time_data
                    time_list.append(time[:5])
                    hh_list.append(time[:2])

                Single_time_data = list()

            # 存放新時間的資料
            Single_time_data.append((date, frequency, level))
            time = date.split(" ")[2].split('.')[0][:8]

        self.hhList = hh_list
        return Multi_time_data, time_list

    # 合併多天的資料
    def Combine_FilteredData(self, FilteredDataList):

        for day, filterdata in zip(self.day_list, FilteredDataList):
            self.Multi_Day_data[day] = filterdata

    # 資料分析 - 一段時間 一段頻率
    def Filter_Data(self, Multi_time_data, choosed_Frequency, choosed_Time):
        # choosed_Time 包含全部的時間 (可以是離散)
        # choosed_Frequency 只需要頭尾即可  (不可以是離散)

        #  tlist = list()
        print("[*] Now Filtering Data ...")
        Filtered_Data = {}

        freq_uplink = choosed_Frequency[1]
        freq_downlink = choosed_Frequency[0]

        for time in Multi_time_data.keys():
            if time[:2] not in choosed_Time:
                continue

            if time[:2] not in self.hhList:
                continue
            #  elif time not in tlist:
            #  tlist.append(time)

            Filtered_Data[time] = []
            for data in Multi_time_data[time]:
                freq = data[1]
                if float(freq_uplink) >= float(freq) >= float(freq_downlink):
                    self.freq.append(freq) if freq not in self.freq else None
                    Filtered_Data[time].append(data)
                continue

        # self.time_list = choosed_Time
        self.Filtered_Data = Filtered_Data
        return Filtered_Data

    # 資料分析 - 標準差, 中位數
    def Get_STD_from_FilteredData(self, ):
        ## 單一頻率在 單個時間點 於數天以來的標準差
        ## ex. 頻率100 在05/10~05/20 10點 之標準差
        print("[*] Now Calculating STD and Median ...")
        std = {}
        median = {}
        for time in self.time_list:
            std[time] = {}
            median[time] = {}
            for freq in self.freq:
                level = list()  # 紀錄單一個頻率在數天下來的場強值
                for day in self.Multi_Day_data.keys():
                    if not time in list(self.Multi_Day_data[day].keys()):
                        continue
                    for data in self.Multi_Day_data[day][time]:
                        if freq == data[1]:
                            level.append(data[2])
                """  
                for day in self.day_list: # 不同天的同個時間點
                    for data in self.Multi_Day_data[day][time]:
                        if freq == data[1]:
                            level.append(data[2])
                """
                std[time][freq] = np.std(level, ddof=1)
                median[time][freq] = np.mean(level)

        self.std = std
        self.median = median
        return self.std, self.median

    # 資料分析 - 取得高標準差的頻段
    def Get_Frequency_with_High_STD(self, ):
        ## flag 是用來判定藥膏標準差還是低標準差
        flag = int(input("[*] (0) High STD / (1) Low STD: "))

        print("[*] Now Calculating High STD ...")
        # 在特定時間點內那些頻率標準差過高
        for time in self.time_list:
            stdList = list()
            self.high_std_Freq[time] = list()

            for frequency in self.std[time].keys():
                stdList.append(self.std[time][frequency])
            Maxstd = np.amax(stdList)
            stdLimit = float(Maxstd * (3 / 4))

            # for frequency in self.std[time].keys():
            # stdList.append(self.std[time][frequency])
            # stdSum = np.amax(stdList)
            # stdMean = np.mean(stdList)
            # stdSum *= 3 / 4

            for freq in self.std[time].keys():
                if flag:
                    if self.std[time][freq] <= stdLimit:
                        self.high_std_Freq[time].append(freq)
                else:
                    if self.std[time][freq] >= stdLimit:
                        self.high_std_Freq[time].append(freq)
        return self.high_std_Freq

    # 資訊分析 - 從高於標準差之頻段 取得 高於中位數之頻段
    def Get_Frequency_with_High_STD_and_Median(self):
        ## flag 是用來判定藥膏標準差還是低標準差
        flag = int(input("[*] (0) High Median / (1) Low Median: "))
        print("[*] Now Calculating High Median ...")
        freq_level_dict = {}
        for day in self.Multi_Day_data.keys():
            freq_level_dict[day] = {}
            for time in self.std.keys():
                if not time in list(self.Multi_Day_data[day].keys()):
                    continue
                freq_level_dict[day][time] = {}
                for d in self.Multi_Day_data[day][time]:
                    freq_level_dict[day][time][d[1]] = d[2]

        Lv2_list = {}  # 哪一天的哪一個時間點之哪個頻率超出中位數
        # 把每一天的資料撈出
        for date in self.Multi_Day_data.keys():
            Lv2_list[date] = {}  # 哪一天哪個時間點之哪個頻率超出中位數
            # 在特定時間點內那些頻率 場強值過中位數
            for time in self.std.keys():
                if not time in list(self.Multi_Day_data[date].keys()):
                    continue

                Lv2_list[date][time] = list()  # 哪些頻率超出中位數
                # for freq in self.median[time].keys():
                for freq in freq_level_dict[date][time].keys():
                    # if freq not in list(freq_level_dict[date][time].keys()):
                    # continue
                    if flag:
                        if freq_level_dict[date][time][freq] <= self.median[time][freq]:  # 需要取得 [頻率:場強] 的對照清單
                            Lv2_list[date][time].append(freq)
                    else:
                        if freq_level_dict[date][time][freq] >= self.median[time][freq]:  # 需要取得 [頻率:場強] 的對照清單
                            Lv2_list[date][time].append(freq)
        self.Lv2_List = Lv2_list
        return self.Lv2_List

    # 資訊分析 - 計算等級二頻段清單之使用率
    def Get_Level2_Frequency_Usage(self):
        # 總時間長度
        total_time = 0
        # 建立一個 frequency字典用來記錄出現次數
        Frequency_Dict = {}  ## [day][nonce]
        for day in self.Lv2_List.keys():

            freq_dict = {}
            for freq in self.freq:
                freq_dict[freq] = 0

            total_time = len(list(self.Lv2_List[day].keys()))
            for time in self.Lv2_List[day].keys():
                for frequnecy in self.Lv2_List[day][time]:
                    freq_dict[frequnecy] += 1

            Frequency_Dict[day] = freq_dict

        print()
        ### 計算完比後開始計算占比
        for day in Frequency_Dict.keys():
            for frequency in Frequency_Dict[day]:
                Frequency_Dict[day][frequency] /= total_time
                Frequency_Dict[day][frequency] *= 100

        self.usage_List = Frequency_Dict

        return Frequency_Dict

    ## 計算使用率趨勢
    def Get_Usage_Trend(self, ):
        trend = dict()

        days = list(self.usage_List.keys())
        first_day = days[0]
        last_day = days[-1]

        for frequency in self.freq:
            u0 = self.usage_List[first_day][frequency]
            un = self.usage_List[last_day][frequency]

            if max(u0, un) == 0:
                trend[frequency] = 0
                continue

            # 負值上升， 正值下降
            trend[frequency] = (u0 - un) / max(u0, un)

        self.trend = trend
        return trend

    ## 告警分類
    def Alert_Setting(self):
        ## 分成 綠黃紅這三種

        alert = {'Red': [], 'Yellow': [], 'Green': []}

        for frequency in self.trend.keys():
            trend = self.trend[frequency] * 100

            if 0 <= trend <= 20:
                alert['Green'].append(frequency)
            elif 50 <= trend <= 100 and -50 <= trend <= -30:
                alert['Yellow'].append(frequency)
            elif -100 <= trend <= -51:
                alert['Red'].append(frequency)
        self.Alert = alert
        return alert
