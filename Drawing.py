import matplotlib.pyplot as plt
import matplotlib as mt
import matplotlib.ticker as ticker
from matplotlib.pyplot import MultipleLocator
import random
import numpy as np
import os
import json

chinese = mt.font_manager.FontProperties(fname='C:\\Windows\\Fonts\\kaiu.ttf')
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False
pathRoot = globals()


def get_ColorCycle(color_list):
    while True:
        color = ["#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)])]  # 隨機色碼
        if color not in color_list and color != "#FFFFFF" and color != "#000000":
            return color


def Plot_for_Selected_Frequency_and_Times(pathRoot, Filtered_data, titleName, Median, locator):
    colorList = []

    for time in Median.keys():
        print("[*] Now Drawing Image for Frequency and Level")

        if time not in Filtered_data.keys():
            continue
        fig, ax = plt.subplots()
        # x y 軸資料
        freq = []
        level = []
        for data in Filtered_data[time]:
            freq.append(float(data[1]) / pow(10, 6))  # 用MHz作為單位
            level.append(data[2])

        if len(range(int(freq[0]), int(freq[-1]), 100000)) > 78000:
            print("  [*] 頻率選擇太過寬廣")
            return

        # 設定顏色
        color = get_ColorCycle(colorList)  # 獲取新顏色
        colorList.append(color)  # 記錄這個顏色已經出現過

        ax.set_prop_cycle(color=color)
        ax.plot(freq, level)

        ## 中位數抓取
        freq = list()
        median = list()
        for frequency in Median[time].keys():
            freq.append(float(frequency) / pow(10, 6))
            median.append(Median[time][frequency])
        plt.figure(figsize=(len(freq), len(median)))
        ax.plot(freq, median, linewidth=4, color="#FF0000")

        # 表示哪條線是哪條 (照繪圖順序排成清單)
        legList = [time]
        ax.legend(legList, prop=chinese, loc="lower left")

        ax.set_xlabel("Frequency (MHz)")
        ax.set_ylabel("Level (dBµV/m)")

        x_major_locator = MultipleLocator(locator)
        ax.xaxis.set_major_locator(x_major_locator)

        ax.set_title(titleName)  ## 幾年幾月幾號

        width = len(np.arange(int(freq[0]), int(freq[-1]), locator))
        fig.set_figheight(10)
        fig.set_figwidth(width)

        if not os.path.exists(pathRoot + '/FT_line'):
            os.mkdir(pathRoot + '/FT_line')
        path = pathRoot + '/FT_line/'

        # category = title.replace("\\", "/").split('.')[0].split("/")[:-1]
        # for c in category:
        # if not os.path.exists(path + c):
        # os.mkdir(path + c)
        # path += c + "/"
        title = titleName  ## day
        if not os.path.exists(path + title):
            os.mkdir(path + title)

        path = path + "{}/{}.png".format(title, time.replace(":", ""))
        fig.savefig(path)
    plt.close('all')


def Plot_for_STD_of_Selected_Frequency(pathRoot, STD, index):
    # 依照時間點有多少就會有多少個標準差
    print("[*] Now Drawing Image for STD in Several Days")
    colorList = []
    #### 給使用者輸入刻度
    locator = float(input('輸入x軸刻度間距: '))
    for time in STD.keys():
        title = ("STD of " + time.replace(":", ""))

        freq = list()
        std = list()
        # 蒐集頻率、標準差
        for f in STD[time].keys():
            freq.append(float(f) / pow(10, 6))
            std.append(STD[time][f])

        # 繪圖
        fig, ax = plt.subplots()
        color = get_ColorCycle(colorList)  # 獲取新顏色
        colorList.append(color)  # 記錄這個顏色已經出現過
        ax.set_prop_cycle(color=color)
        ax.plot(freq, std)
        ## 修飾
        ax.set_xlabel("Frequency (MHz)")
        ax.set_ylabel("STD of Level (dBµV/m)")


        x_major_locator = MultipleLocator(locator)
        ax.xaxis.set_major_locator(x_major_locator)

        ax.set_title(title.split('.')[0])

        width = len(np.arange(int(freq[0]), int(freq[-1]), locator))
        fig.set_figheight(10)
        fig.set_figwidth(width)

        if not os.path.exists(pathRoot + '/STD'):
            os.mkdir(pathRoot + '/STD')

        fig.savefig(pathRoot + '/STD/' + time.replace(":", "") + ".png")
    plt.close('all')


def Plot_for_Median_of_Selected_Frequency(pathRoot, Median):
    # 依照時間點有多少就會有多少個標準差
    print("[*] Now Drawing Image for Median in Several Days")
    colorList = []

    #### 給使用者輸入刻度
    locator = float(input('輸入x軸刻度間距: '))
    for time in Median.keys():
        title = ("Median_of_" + time.replace(":", ""))

        freq = list()
        med = list()
        # 蒐集頻率、標準差
        for f in Median[time].keys():
            freq.append(float(f) / pow(10, 6))
            med.append(Median[time][f])

        # 繪圖
        fig, ax = plt.subplots()
        color = get_ColorCycle(colorList)  # 獲取新顏色
        colorList.append(color)  # 記錄這個顏色已經出現過
        ax.set_prop_cycle(color=color)
        ax.plot(freq, med)
        ## 修飾
        ax.set_xlabel("Frequency (MHz)")
        ax.set_ylabel("Medain of Level (dBµV/m)")


        x_major_locator = MultipleLocator(locator)
        ax.xaxis.set_major_locator(x_major_locator)

        ax.set_title(title.split('.')[0])

        width = len(np.arange(int(freq[0]), int(freq[-1]), locator))
        fig.set_figheight(10)
        fig.set_figwidth(width)

        if not os.path.exists(pathRoot + '/Median'):
            os.mkdir(pathRoot + '/Median')

        fig.savefig(pathRoot + '/Median/' + title.split('.')[0] + ".png")
    plt.close('all')


def Plot_for_Usage_of_Selected_Frequency(pathRoot, UsageList):
    print("[*] Now Drawing Image for Usage in Several Days")
    colorList = []
    locator = float(input('輸入x軸刻度間距: '))
    ## x軸頻率 y軸場強
    ## 每一天一張圖
    for day in UsageList.keys():
        usage = []

        freqList = []
        for freq in UsageList[day].keys():
            freqList.append(float(freq) / pow(10, 6))
            usage.append(UsageList[day][freq])

        fig, ax = plt.subplots()
        color = get_ColorCycle(colorList)  # 獲取新顏色
        colorList.append(color)  # 記錄這個顏色已經出現過
        ax.set_prop_cycle(color=color)
        ax.set_ylim(0, 100)
        ax.bar(freqList, usage, width=0.8)

        ## 修飾文字
        ax.set_xlabel("Frequency (MHz)")
        ax.set_ylabel("Usage (%)")

        title = "Usage" + day.replace("/", "")
        ax.set_title(title.split('.')[0])

        width = len(np.arange(int(freqList[0]), int(freqList[-1]), locator))

        fig.set_figheight(10)
        fig.set_figwidth(width)

        if not os.path.exists(pathRoot + '/Usage/'):
            os.mkdir(pathRoot + '/Usage/')

        fig.savefig(pathRoot + '/Usage/' + title.split('.')[0] + ".png")
    plt.close('all')


def Plot_for_Usage_Trend_of_Selected_Frequency(pathRoot, Dect_Days, UsageTrend, index):
    colorList = []
    fig, ax = plt.subplots()
    freq = list()
    # 分段畫 10個一張
    Page_Index = 0

    for usagetrend in UsageTrend[:index + 10]:
        for frequency in usagetrend.keys():
            usageList = [u * 100 for u in usagetrend[frequency]]  # 取得該頻率數天之使用率

            color = get_ColorCycle(colorList)  # 獲取新顏色
            colorList.append(color)  # 記錄這個顏色已經出現過
            ax.set_prop_cycle(color=color)
            ax.bar(Dect_Days, usageList, width=0.8)

            freq.append(frequency) if frequency not in freq else None

        ## 修飾文字
        ax.set_xlabel("Frequency (MHz)")
        ax.set_ylabel("Usage (%)")
        ax.set_yticks(np.linspace(0, 100, 5))  # 限制 y軸為 0~100%

        ax.xaxis.set_major_locator(ticker.MultipleLocator(index))
        title = "Usage Trend From {} to {} ({})".format(Dect_Days[0].replace("/", '-'), Dect_Days[-1].replace("/", '-'),
                                                        int((Page_Index / 10)))
        ax.set_title(title)
        ax.legend(freq, prop=chinese, loc="lower left")

        fig.set_figheight(10)
        fig.set_figwidth(19)

        if not os.path.exists(pathRoot + "/Usage_Trend/"):
            os.mkdir(pathRoot + "/Usage_Trend/")

        fig.savefig(pathRoot + "/Usage_Trend/" + title + ".png")
        Page_Index += 10
    plt.close('all')


def Plot_for_Specturm_of_Selected_Frequency_and_Times(pathRoot, Filtered_data, choosed_frequency, index):
    print("[*] Now Drawing Image for Spectrum in Several Days")
    # x軸: 頻率, y軸: 時間點
    freq = list()
    for f in choosed_frequency:
        freq.append(float(f) / pow(10, 6))

    ### 檢查那些時間點的數量有誤 參考圖問題-2
    probelm_List = []
    for date in Filtered_data.keys():

        # 一天一天
        level = list()
        day = ""

        ### For Check
        dataAmount = {}  # 這個時間點有多少筆資料 看哪一天時間有少
        flag = False  # 檢查結果

        for time in Filtered_data[date].keys():
            tmp = list()
            for data in Filtered_data[date][time]:
                tmp.append(data[2])  # 單一時間點 的 場強值
                if day == "":
                    day = data[0].split(" ")[0].replace("/", "-")
            level.append(tmp)
            dataAmount[time] = len(Filtered_data[date][time])

        tmp = dataAmount[list(dataAmount.keys())[0]]
        for time in dataAmount.keys():
            if tmp != dataAmount[time]:
                flag = True
        if flag:  ## 如果有誤這一天就別畫了
            continue

        # 繪圖
        fig, ax = plt.subplots()
        # 畫圖之前應該在分析那塊進行檢查
        image = ax.pcolormesh(freq, list(Filtered_data[date].keys()), level, edgecolors='face', cmap='YlOrRd')

        ax.xaxis.set_major_locator(ticker.MultipleLocator(index))
        ax.set_title("Spectrum for {}".format(day))
        fig.colorbar(image, ax=ax)
        ax.set_xlabel = "Frequency (MHz)"
        ax.set_ylabel = "Time"

        fig.set_figheight(10)
        fig.set_figwidth(19)
        # 建立分類資料夾

        if not os.path.exists(pathRoot + '/Spectrum'):
            os.mkdir(pathRoot + '/Spectrum')

        fig.savefig(pathRoot + '/Spectrum' + "/Spectrum for {}.png".format(day))
    plt.close('all')


def Output_Result(pathRoot, Detect_Days, alert_Dict):
    Firstday = Detect_Days[0]
    Endday = Detect_Days[-1]

    result = dict()

    for color in alert_Dict.keys():
        result[color] = []  #### 結果用json 表示
        for freq in alert_Dict[color]:
            result[color].append(freq)
    result = json.dumps(result)

    if not os.path.exists(pathRoot + '/Results'):
        os.mkdir(pathRoot + '/Results')

    with open('{}/Results/{}_to_{}_result.txt'.format(pathRoot, Firstday, Endday), 'w') as file:
        file.write(str(result))
        file.close()


def Plot_for_Output_Result(pathRoot, Detect_Date, freq):
    print("[*]  Now Drawing image for Alert FT image")

    if len(range(int(freq[0]), int(freq[-1]), 100000)) > 78000:
        print("頻率選擇太過寬廣")
        return

    ### 取得頻率後，用result把特定區段化上顏色
    ## 從 Result.txt 撈資料
    # 檔名
    fileName = "{}/Results/{}_to_{}_result.txt".format(pathRoot, Detect_Date[0].replace('/', '_'),
                                                       Detect_Date[-1].replace('/', '_'))
    Alert_Dict = None
    with open(fileName, 'r') as file:
        Alert_Dict = file.readline()
    Alert_Dict = json.loads(Alert_Dict)

    colors = {
        'Red': "#AE0000",
        'Green': "#00D600",
        'Yellow': '#E0E000'
    }
    #### 給使用者輸入刻度
    locator = float(input('輸入x軸刻度間距: '))
    # 將頻率表除以 10^6的頻率表

    for color in Alert_Dict.keys():
        for i in range(0, len(Alert_Dict[color])):
            Alert_Dict[color][i] = float(Alert_Dict[color][i] / pow(10, 6))

    red_level = [1 for i in range(0, len(Alert_Dict['Red']))]
    yellow_level = [1 for i in range(0, len(Alert_Dict['Yellow']))]
    green_level = [1 for i in range(0, len(Alert_Dict['Green']))]

    ## 繪圖
    fig, ax = plt.subplots()
    plt.figure(figsize=(len(freq), len(freq)))

    for i in range(0, len(freq)):
        freq[i] /= pow(10, 6)
    width = len(np.arange(int(freq[0]), int(freq[-1]), locator))

    fig.set_figheight(10)
    fig.set_figwidth(width)
    x_major_locator = MultipleLocator(locator)
    ax.xaxis.set_major_locator(x_major_locator)

    title = "Result from {} to {}".format(Detect_Date[0], Detect_Date[-1])
    ax.set_title(title)

    ax.bar(
        Alert_Dict['Red'],
        red_level,
        color=colors['Red'],
        width=0.01) if len(Alert_Dict['Red']) != 0 else None
    ax.bar(
        Alert_Dict['Green'],
        green_level,
        color=colors['Green'],
        width=0.01) if len(Alert_Dict['Green']) != 0 else None
    ax.bar(
        Alert_Dict['Yellow'],
        yellow__level,
        color=colors['Yellow'],
        width=0.01) if len(Alert_Dict['Yellow']) != 0 else None

    ax.set_xlabel("Frequency (MHz)")
    ax.set_ylabel("Level (dBµV/m)")

    if not os.path.exists(pathRoot + '/Results'):
        os.mkdir(pathRoot + '/Results')
    path = pathRoot + '/Results/'

    path += "Result from {} to {}.png".format(Detect_Date[0].replace('/', '_'),
                                              Detect_Date[-1].replace('/', '_'))
    fig.savefig(path)

    plt.close()
