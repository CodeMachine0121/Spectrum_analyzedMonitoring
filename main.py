from Analysis import Analysis
import Drawing as draw
import os
import datetime

analy = Analysis()


## 統整檢測資料日期
def Dates_to_Detecting(BusinessType, start_Date, end_Date):
    date_list = []
    start_Date = datetime.datetime.strptime(start_Date, '%Y_%m_%d')
    end_Date = datetime.datetime.strptime(end_Date, '%Y_%m_%d')

    while start_Date <= end_Date:
        date_str = start_Date.strftime('%Y_%m_%d')


        if date_str[5] == "0":
            s = ""
            for i in range(0, len(date_str)):
                if i != 5:
                    s += date_str[i]
            date_str = s

        if date_str[7] == "0":
            s = ""
            for i in range(0, len(date_str)):
                if i != 7:
                    s += date_str[i]
            date_str = s

        date_list.append(date_str)

        start_Date += datetime.timedelta(days=1)

    ## 取 日期與實際上有的日期 的交集
    Actual_file = set(os.listdir(BusinessType))
    date_list = list(set.intersection(set(date_list), Actual_file))

    ## 排序問題
    date_list = sorted([datetime.datetime.strptime(dt, '%Y_%m_%d') for dt in date_list])
    date_list = [dt.strftime('%Y_%m_%d') for dt in date_list]
    ## 因為被打回原形 所以要再過塞

    returnList =[]
    for date in date_list:
        if date[5] == "0":
            s = ""
            for i in range(0, len(date)):
                if i != 5:
                    s += date[i]
            date = s

        if date[7] == "0":
            s = ""
            for i in range(0, len(date)):
                if i != 7:
                    s += date[i]
            date = s

        returnList.append(date)
    analy.day_list = returnList
    return returnList


## 統整檢測資料時間
def Time_to_Detecting(firstTime, endTime, stampTime):
    timeList = []
    firstTime = datetime.datetime.strptime(firstTime, '%H:%M')
    endTime = datetime.datetime.strptime(endTime, '%H:%M')
    while firstTime <= endTime:
        time_str = firstTime.strftime('%H')
        timeList.append(time_str)
        firstTime += datetime.timedelta(hours=int(stampTime))

    return timeList


## 輸出: 總體資料、輸入資料完整路徑、 pathRoot
def Import_Files(BusinessType, importDate):
    files = []
    DataType = input("   [*] Input Data Type: ")
    PlaceName = input("   [*] Input Station Place: ")

    # DateRange = input("[*] Input Date Range(ex 2021_4_2): ")
    pathRoot = BusinessType + "-" + PlaceName
    if not os.path.exists(pathRoot):
        os.mkdir(pathRoot)

    if BusinessType == "高原站":
        for dateFile in os.listdir(BusinessType):
            if dateFile in importDate:
                for placeFolder in os.listdir(os.path.join(BusinessType, dateFile)):
                    path = os.path.join(os.path.join(BusinessType, dateFile), placeFolder)
                    for file in os.listdir(path):
                        if "dbf" in file:
                            files.append(os.path.join(path, file))
    else:
        for dateFiles in os.listdir(BusinessType):  # 檢測業務
            if dateFiles in importDate:
                now_path = os.path.join(BusinessType, dateFiles)  # 紀錄目前位置
                for placeFiles in os.listdir(now_path):  # 站台位置
                    if placeFiles == PlaceName:
                        now_path = os.path.join(now_path, placeFiles)
                        if "(" in BusinessType:
                            Type = BusinessType.split("(")[0]
                        else:
                            Type = BusinessType
                        file = os.listdir(os.path.join(now_path, Type))
                        detectData = file[0] if len(file) > 0 else ""  # 檢測檔案檔名
                        if DataType in detectData:
                            files.append(os.path.join(now_path, Type) + "/" + detectData)
                    else:
                        continue
            else:
                continue
    Multi_Day_DataList = list()

    time_list = []
    for f in files:
        if BusinessType == "高原站":
            file, time_tmp = analy.Read_File_For_DBF(f)
        else:
            file, time_tmp = analy.Read_File_For_Access(f)

        Multi_Day_DataList.append(file)
        time_list.append(time_tmp)

    ### 整理時間表應該用哪一天的時間
    end = len(time_list[0])
    timeList = []  ## 最後挑選出來 每天都有的時間點
    for tmp_timeList in time_list:
        if end <= len(tmp_timeList):
            end = len(tmp_timeList)
            timeList = tmp_timeList
    analy.time_list = timeList

    return Multi_Day_DataList, files, pathRoot


## 參數: 業務類型、總體資料
def Selecting_Frequency_and_Time(BusinessType, Multi_Day_DataList):
    # 依照測試日期依序排列
    # 690000000, 760000000
    Frequency_for_Business = {
        'Mobile': [3300000000, 3610000000],  # 間距: 100000
        '業餘(上)': [144000000, 146000000],  # 間距: 10000
        '業餘(下)': [430000000, 440000000],  # 間距: 10000
        'TV': [530000000, 608000000],  # 間距: 100000
        '廣播': [88000000, 108000000],  # 間距: 100000
        '飛航(上)': [108000000, 136000000],  # 間距: 10000
        '飛航(下)': [228000000, 341000000],  # 間距: 10000
        "高原站": [690000000, 760000000],
        '業餘(上)DF': [144000000, 146000000],  # 間距: 10000
        '業餘(下)DF': [430000000, 440000000],  # 間距: 10000
    }

    while True:
        #### 選擇頻段的範圍及間隔
        start_Frequency = int(input("   [*]檢測起始頻段(Hz)=>: ").strip())
        end_Frequency = int(input("   [*]檢測結束頻段(Hz)=>: ").strip())
        if start_Frequency < Frequency_for_Business[BusinessType][0] or end_Frequency > \
                Frequency_for_Business[BusinessType][1]:
            print("頻段選擇錯誤")
            continue
        else:
            break
    timeList = []
    while True:
        try:
            firstTime = input('   [*]檢測開始時間點(%H:%M): ').strip()
            endTime = input('   [*]檢測結束時間點(%H:%M): ').strip()
            stampTime = input("   [*]檢測時間間隔(小時): ").strip()
            ## 設定要檢測的時段
            timeList = Time_to_Detecting(firstTime, endTime, stampTime)
            break
        except Exception as e:
            print('時間輸入錯誤')
            continue

    #### 選擇要檢測的範圍
    dataList = [analy.Filter_Data(data, [start_Frequency, end_Frequency], timeList) for data in Multi_Day_DataList]
    analy.Combine_FilteredData(dataList)

    return analy.Multi_Day_data


# 計算/統計數據
def Do_Calculate():
    Data = {}
    # 先標準差繪圖吧
    std, median = analy.Get_STD_from_FilteredData()
    Data['std'] = std
    Data['median'] = median

    # 挑出高標準差
    high_std_Freq = analy.Get_Frequency_with_High_STD()
    level2List = analy.Get_Frequency_with_High_STD_and_Median()
    Data['level2List'] = level2List

    # 使用率
    usage_list = analy.Get_Level2_Frequency_Usage()
    Data['usage_list'] = usage_list

    # 使用率趨勢
    usage_Trend = analy.Get_Usage_Trend()
    Data['usage_Trend'] = usage_Trend

    ### 顏色分類
    alert_Dict = analy.Alert_Setting()
    Data['alert_Dict'] = alert_Dict

    return Data


def Output_Pics(BusinessType, pathRoot, Data, detectDate, files):
    # Data => 字典透過索引擲去找要的類型
    # 依照業務評判x軸間距，但因為我這邊單位為M所以間距也要是M
    Index_Map = {
        'Mobile': 10,  # 100000 / pow(10, 6),
        '業餘(上)': 1,  # 10000 / pow(10, 6),
        '業餘(下)': 1,  # 10000 / pow(10, 6),
        'TV': 10,  # 100000 / pow(10, 6),
        '廣播': 1,  # 100000 / pow(10, 6),
        '飛航(上)': 1,  # 10000 / pow(10, 6),
        '飛航(下)': 10,  # 10000 / pow(10, 6),
        '高原站': 10,
        '業餘(上)DF': 1,  # 10000 / pow(10, 6),
        '業餘(下)DF': 1,  # 10000 / pow(10, 6),
    }

    index = Index_Map[BusinessType]
    while True:
        command = input("[Drawing]##: ")

        if command == "std":
            draw.Plot_for_STD_of_Selected_Frequency(pathRoot, Data['std'], index)
        elif command == "med":
            draw.Plot_for_Median_of_Selected_Frequency(pathRoot, Data['median'])
        elif command == "usage":
            # 使用率
            draw.Plot_for_Usage_of_Selected_Frequency(pathRoot, Data['usage_list'])
        elif command == "trend":
            # 使用率趨勢
            draw.Output_Result(pathRoot, detectDate, Data['alert_Dict'])
            while True:
                draw.Plot_for_Output_Result(pathRoot, dateList, analy.freq)
                break


        elif command == "spe":
            # 色塊頻譜
            draw.Plot_for_Specturm_of_Selected_Frequency_and_Times(pathRoot, analy.Multi_Day_data, analy.freq, index)
        elif command == "ft":
            # FT圖
            locator = -1
            for day in analy.Multi_Day_data.keys():
                if locator == -1:
                    locator = float(input('輸入x軸刻度間距: '))
                draw.Plot_for_Selected_Frequency_and_Times(pathRoot, analy.Multi_Day_data[day], day.replace("/", "_"),
                                                           analy.median, locator)
        elif command == 'help':
            print("*************")
            print('   std: 標準差頻譜圖')
            print('   med: 中位數頻譜圖')
            print('   usage: 使用率直方圖')
            print('   trend: 告警分類圖')
            print('   spe: 色塊頻譜圖')
            print('   ft: 頻譜圖')
            print("*************")
        elif command == "quit":
            return


dateList = []
BusinessType = ""
Multi_Day_DataList = None
Filtered_Data = None
pathRoot = ""
Calculated_Data = ""
files = ""

while True:

    command = input("##: ").strip()
    if command == 'import':
        analy = Analysis()
        BusinessType = input("   [*]業務類型: ").strip()
        firstDay = input('   [*]檢測初始日期: ').strip()
        endDay = input('   [*]檢測結束日期: ').strip()

        dateList = Dates_to_Detecting(BusinessType, firstDay, endDay)

        ## 匯入完整資料
        Multi_Day_DataList, files, pathRoot = Import_Files(BusinessType, dateList)
    elif command == "analysis":
        ## 過濾資料
        Filtered_Data = Selecting_Frequency_and_Time(BusinessType, Multi_Day_DataList)
    elif command == 'cal':
        Calculated_Data = Do_Calculate()
    elif command == 'pic':
        Output_Pics(BusinessType, pathRoot, Calculated_Data, dateList, files)
    elif command == 'help':
        print("*************")
        print('##   import: 匯入檢測資料')
        print("##   analysis: 過濾資料")
        print('##   cal: 計算環節')
        print('##   pic: 輸出圖檔')
        print("*************")
        # BusinessType, pathRoot, Data, detectDate, files
    print()

# draw.Plot_for_Usage_Trend_of_Selected_Frequency(analy.day_list, usage_Trend)


print()
