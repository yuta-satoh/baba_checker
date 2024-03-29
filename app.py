import requests
import schedule
import os
from time import sleep
from dotenv import load_dotenv
from datetime import datetime
from bs4 import BeautifulSoup as bs4

def babasearch():

    now_weekday = datetime.now().weekday()

    message = ""

    url = ("https://www.jra.go.jp/keiba/baba/")

    # エラーハンドリング
    try:
        res = requests.get(url)
        pass
    except requests.RequestException as e:
        print(f"Request error: {e}")

    soup = bs4(res.content, "html.parser")

    tabs = soup.select("div.nav")[0].find_all("a")

    for tab in tabs:
        full_url = url + tab["href"]
        res = requests.get(full_url)
        soup = bs4(res.content, "html.parser")

        kaisai = soup.select("#condition > div.contents_header.opt > div > div > h2")
        condition = soup.select("div.cell.weather, div.cell.turf, div.cell.dirt")
        course = soup.select("#turf_info > div.grid > div.cell.data > div.course > ul > li > div > div.content > p")
        grass = soup.select("#turf_info > div.grid > div.cell.data > div.turf_condition > ul > li > div > div.content > p")
        weather_table = soup.find("table",{"class":"basic simple narrow"})
        weather_table_day = weather_table.select("th.sat, th.sun")
        weather_table_weather = weather_table.select("td.weather")

        output_parts = []

        # 天候の情報を抽出
        weather = condition[0].find("div", class_="cell txt")
        if weather:
            weather_text = weather.get_text(strip=True)  # strip=Trueで余分な空白を除去
            output_parts.append(weather_text)

        # 芝の状態を抽出
        turf = condition[1].find("div", class_="content").p
        if turf:
            turf_condition = turf.get_text(strip=True)
            output_parts.append(f"芝：{turf_condition}")

        # ダートの状態を抽出
        dirt = condition[2].find("div", class_="content").p
        if dirt:
            dirt_condition = dirt.get_text(strip=True)
            output_parts.append(f"ダート：{dirt_condition}")

        # 開催情報
        kaisai_info = "\n【" + kaisai[0].contents[0].text + kaisai[0].contents[1].text + "】\n"
        # 天候と馬場状態
        baba_info = "\n".join(output_parts)
        # 使用コース
        course_info = "【使用コース】\n" + course[0].contents[0].text + course[0].contents[1].text
        # 芝の状態
        grass_condition = "【芝の状態】\n" + grass[0].contents[0].text
        # 土曜日の天気
        weather_info_sat = weather_table_day[len(weather_table_day) - 2].text + ":" + weather_table_weather[len(weather_table_weather) - 2].text
        # 日曜日の天気
        weather_info_sun = weather_table_day[len(weather_table_day) - 1].text + ":" + weather_table_weather[len(weather_table_weather) - 1].text

        if now_weekday == 5:
            info_message = kaisai_info + baba_info + "\n" + course_info + "\n" +  grass_condition + "\n" + "【天候】\n" + weather_info_sat + "\n"
            message += info_message
        
        elif now_weekday == 6:
            info_message = kaisai_info + baba_info + "\n" + course_info + "\n" +  grass_condition + "\n" + "【天候】\n" + weather_info_sun + "\n"
            message += info_message

        else:
            info_message = kaisai_info + baba_info + "\n" + course_info + "\n" +  grass_condition + "\n" + "【天候】\n" + weather_info_sat + "\n" + weather_info_sun + "\n"
            message += info_message

    # print(message)
    lineNotify(message)


def lineNotify(message):
    load_dotenv()
    line_notify_token = os.environ['LINE_TOKEN']
    line_notify_api = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': f'Bearer {line_notify_token}'}
    data = {'message': f'{message}'}
    try:
        response = requests.post(line_notify_api, headers=headers, data=data)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Line Notify error: {e}")


schedule.every().saturday.at("09:00").do(babasearch)
schedule.every().sunday.at("09:00").do(babasearch)

while(True):
    schedule.run_pending()
    sleep(1)

# babasearch()
