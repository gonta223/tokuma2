import random
import time
from selenium import webdriver
from selenium.webdriver.chrome import service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import requests
from bs4 import BeautifulSoup

import re

import pandas as pd

from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome import service as fs

from os.path import join #既に開いているブラウザを取得する際のコードに必要

import chromedriver_binary   #Chromeのパスを通すためのコード
#起動したら以下のコードをターミナルで使用、そこで開かれたブラウザでprivacypassを起動し認証を行う
#/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir="/Users/satousuguru/Desktop/Python/google chrome" ⚠️最後のクオーテーショん入れないとバグる
#https://qiita.com/mimuro_syunya/items/2464cd2404b67ea5da56:参考
#:ターミナルで使用

EXTENSION_PATH = "/Users/satousuguru/Desktop/Python/KeywordSurfer.crx" #⚠️拡張機能のパス。適宜書き換えて

import csv #csvを読み込む

#csvの読み込み及び会社名だけに絞る
df = pd.read_csv('ハロワ_ドライバー_東京 - トクマ案件.csv')
df_company_name_only = df['会社名']

#for文の下準備
need_deleted = "支店"or"事業部"or"営業所"or"事業所"
company_name_list=[]

#dfからlistに変換と不要部分の削除作業
for company_name in df_company_name_only:
    for row in df_company_name_only:

        #支店などがある場合、その部分を削除
        if "支店" in row or "事業部" in row or "営業所" in row or "営業所" in row or "事業所" in row or "支社" in row :
        #⚠️if 文字列inなんとかの時は、文字列or文字列or.. in rowではなく、このような形で書かないとバグる
            print(f"削除する文字列を検知しました、「{row}」から")
            row_need_delete = row.split("\u3000")[-1]
            row = row.replace(row_need_delete,"")
            print(f"「{row}」に変更しました")
        company_name_list.append(row)

#set型を用いて、重複する会社名を削除
company_name_list = list(set(company_name_list))
print(company_name_list)


##ここから上のリストを用いて実際に検索していく

#ブラウザーの準備
CHROMEDRIVER = "/Users/satousuguru/Desktop/chromedriver"

root = join(__file__, "..")

# webdriverオブジェクトを作る（ブラウザが開く）
browser_path=join(root, "/Users/satousuguru/Desktop/chromedriver")

# 起動時にオプションをつける。（ポート指定により、起動済みのブラウザのドライバーを取得）
options = webdriver.ChromeOptions()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
browser = webdriver.Chrome(executable_path=browser_path, options=options)

#拡張機能を設定
chrome_service = fs.Service(executable_path=CHROMEDRIVER)
"""
options = webdriver.ChromeOptions()
"""
options.add_argument(f'service={chrome_service}')
options.add_extension(EXTENSION_PATH)
browser = webdriver.Chrome(options=options)




#拡張機能でpassを獲得している間、中断
k = 0
while k == 0:
    start = input(print("ブラウザの拡張機能(privacy pass)を選択し、get more passを行ってください。求人読み込みを開始する場合はcと書いてください"))
    if start == "c":
        break
    else:
        continue

#indeedのメインページに移動、またそのソースコードの取得
browser.get("https://jp.indeed.com/?from=gnav-viewjob")
source = browser.page_source
soup = BeautifulSoup(source,"html.parser")

actions = ActionChains(browser)


ini_or_not = 0 #初回かどうか判定
count = 0 #
error_count = 0
url_count = 0 #URl内のstart=以降のカウント
page_num=0 #ページが複数に渡る場合の番号

for search_company_name in company_name_list:
    #初回の検索とそれ以降は、最初のページが違うのでバグを避けるためにも一応便宜上分けてる。ただ結果的に見たらそんな意味ない
    if ini_or_not == 0:

        print(f"初回の検索です。現在の検索キーワードは{search_company_name}です")

        word_number = len(search_company_name)
        print(word_number)

        elem_type_search_word = browser.find_element(By.ID,"text-input-what")
        elem_type_search_word.send_keys(f'"{search_company_name}"')

        elem_search_btn = browser.find_element(By.CLASS_NAME,"yosegi-InlineWhatWhere-primaryButton")
        elem_search_btn.click()

        source = browser.page_source
        soup = BeautifulSoup(source,"html.parser")

        job_list = soup.find("ul",attrs={"class":"jobsearch-ResultsList css-0"})
        if job_list is None: #求人数が0の時はここでループ最初に戻る
            print("このページの求人はありませんでした😢")
            time.sleep(3)
            continue

        job_list = job_list.find_all("div",attrs={"class":"slider_container css-g7s71f eu4oa1w0"})#求人をそれぞれ読み込む
        print(f"このページの求人数は{len(job_list)}")

        pay = 0
        more = 0
        for job in job_list:
            if job.find("span",attrs={"class":"iaIcon"}) and job.find("span",attrs={"class":"more_loc_container"}):#応募があり、かつその他の勤務地が入っている場合
                other_area = job.find("span",attrs={"class":"more_loc_container"}).text #その他の勤務地(3)
                other_area_num = re.findall(r"\d+", other_area) #数字部分のみを取り出す
                other_area_num = other_area_num[0]
                other_area_num = int(other_area_num)
                more += other_area_num

            if job.find("span",attrs={"class":"iaIcon"}):#indeedで応募、もしくはカンタン応募を検出(その左にある矢印アイコンを判定に使っている)
                pay +=1

            else:
                continue

        print(f"有料の数は{pay}個")
        print(f"その他の勤務地も含めると{pay + more}個になります")


        ini_or_not+=1

    else:

        ##まだ前のページ##
        sleep_time = random.uniform(10,12)
        time.sleep(sleep_time)



        elem_type_search_word = browser.find_element(By.ID,"text-input-what")
        k = 0
        while k < word_number*2: #特に二倍の意味はないけどなんとなく怖いから。バグが出るならここの可能性あり
            elem_type_search_word.send_keys(Keys.BACK_SPACE)
            k+=1
        elem_type_search_word.send_keys(f'"{search_company_name}"')

        print(f"現在の検索キーワードは{search_company_name}です")
        word_number = len(search_company_name)


        elem_search_btn = browser.find_element(By.CLASS_NAME,"yosegi-InlineWhatWhere-primaryButton")
        elem_search_btn.click()

        ##ここから次のページ##

        source = browser.page_source
        soup = BeautifulSoup(source,"html.parser")

        job_list = soup.find("ul",attrs={"class":"jobsearch-ResultsList css-0"})
        if job_list is None: #求人数が0の時はここでループ最初に戻る
            print("このページの求人はありませんでした😢")
            continue

        if len(job_list)>=15:
            print("ページが複数に渡ります。直下に記載する情報は1ページ目のみについての情報です。")

        job_list = job_list.find_all("div",attrs={"class":"slider_container css-g7s71f eu4oa1w0"})#求人をそれぞれ読み込む
        print(f"このページの求人数は{len(job_list)}")

        pay = 0
        more = 0
        for job in job_list:
            if job.find("span",attrs={"class":"iaIcon"}) and job.find("span",attrs={"class":"more_loc_container"}):#応募があり、かつその他の勤務地が入っている場合
                other_area = job.find("span",attrs={"class":"more_loc_container"}).text #その他の勤務地(3)
                other_area_num = re.findall(r"\d+", other_area) #数字部分のみを取り出す
                other_area_num = other_area_num[0]
                other_area_num = int(other_area_num)

                more += other_area_num

            if job.find("span",attrs={"class":"iaIcon"}):#indeedで応募、もしくはカンタン応募を検出(その左にある矢印アイコンを判定に使っている)
                pay +=1

            else:
                continue

        print(f"有料の数は{pay}個")
        print(f"その他の勤務地も含めると{pay + more}個になります")

        count += 1

        if len(job_list) is None:
            break

        additional_pay_none = 0
        while len(job_list) == 15: #ページがまだ続く場合、次のページに移動
            if url_count == 0: #最初の場合(urlの構造が違う)
                print("求人数が規定数以上のため、ページを遷移します")
                url_count+=10
                cur_url = browser.current_url
                cur_url = cur_url.split("&")[0]
                cur_url_next = cur_url +"&&start=" + str(url_count)
                print(cur_url)
                print(cur_url_next)
                browser.get(f"{cur_url_next}")
                page_num +=1

                sleep_time = random.uniform(8,12) #遷移前に時間を置く
                time.sleep(sleep_time)

                ##ここから次のページ

                source = browser.page_source
                soup = BeautifulSoup(source,"html.parser")

                job_list = soup.find("ul",attrs={"class":"jobsearch-ResultsList css-0"})
                if job_list is None: #2ページ目の求人数が0の時はここで何もせずループに戻る
                    print("2ページ目には求人がありませんでした😢直上の情報が最終的な情報になります。")
                    continue

                job_list = job_list.find_all("div",attrs={"class":"slider_container css-g7s71f eu4oa1w0"})#求人をそれぞれ読み込む
                print(f"このページの求人数は{len(job_list)}")


                additional_pay = 0 #複数ページ分の有料求人は、2回連続で0だった場合はループに戻させるため別個カウント
                for job in job_list:
                    if job.find("span",attrs={"class":"iaIcon"}) and job.find("span",attrs={"class":"more_loc_container"}):#応募があり、かつその他の勤務地が入っている場合
                        other_area = job.find("span",attrs={"class":"more_loc_container"}).text #その他の勤務地(3)
                        other_area_num = re.findall(r"\d+", other_area) #数字部分のみを取り出す
                        other_area_num = other_area_num[0]
                        other_area_num = int(other_area_num)
                        more += other_area_num

                    if job.find("span",attrs={"class":"iaIcon"}):#indeedで応募、もしくはカンタン応募を検出(その左にある矢印アイコンを判定に使っている)
                        additional_pay += 1

                    else:
                        continue

                print(f"このページの有料の数は{additional_pay}個")
                print(f"今までの有料の数は総計{pay + additional_pay}個")
                print(f"その他の勤務地も含めると総計{pay +additional_pay + more}個になります")


                if len(job_list) is None:#0の場合、ループに戻る
                    print("残りページはありません。ループに戻ります。")
                    url_count = 0
                    break

                if len(job_list) >= 15:
                    if soup.find("a",attrs={"data-testid":"pagination-page-next"}): #→(以降のページがあると消える）があるとループ終了（ページにマックス求人あるけど、以降のページがない時の対処)
                        print("まだページがあるため、次のページに遷移します")
                        continue
                    else:
                        print("このページの求人数は15ですが、以降のページは存在しないのでループに戻ります。")
                        url_count = 0
                        break

                if len(job_list) < 15:
                    url_count = 0
                    print("求人数が15未満のため、このページは最終ページとなります。ループに戻ります。")
                    break


            if url_count >= 10: #2回目以降(3ページ目遷移時以降)
                print("求人数が規定数以上のため、ページを遷移します")
                url_count+=10
                cur_url = browser.current_url
                cur_url = cur_url.replace(cur_url.split("&")[2],"")
                cur_url_next = cur_url +"&&start=" + str(url_count)
                print(cur_url)
                print(cur_url_next)
                browser.get(f"{cur_url_next}")
                page_num +=1


                sleep_time = random.uniform(8,12) #遷移前に時間を置く
                time.sleep(sleep_time)

                 ##ここから次のページ

                source = browser.page_source
                soup = BeautifulSoup(source,"html.parser")

                job_list = soup.find("ul",attrs={"class":"jobsearch-ResultsList css-0"})
                if job_list is None: #複数ページ目の求人数が0の時はここで何もせずループに戻る
                    print("このページ目には求人がありませんでした😢直上の情報が最終的な情報になります。")
                    continue

                job_list = job_list.find_all("div",attrs={"class":"slider_container css-g7s71f eu4oa1w0"})#求人をそれぞれ読み込む
                print(f"このページの求人数は{len(job_list)}")


                additional_pay = 0
                for job in job_list:
                    if job.find("span",attrs={"class":"iaIcon"}) and job.find("span",attrs={"class":"more_loc_container"}):#応募があり、かつその他の勤務地が入っている場合
                        other_area = job.find("span",attrs={"class":"more_loc_container"}).text #その他の勤務地(3)
                        other_area_num = re.findall(r"\d+", other_area) #数字部分のみを取り出す
                        other_area_num = other_area_num[0]
                        other_area_num = int(other_area_num)
                        more += other_area_num

                    if job.find("span",attrs={"class":"iaIcon"}):#indeedで応募、もしくはカンタン応募を検出(その左にある矢印アイコンを判定に使っている)
                        additional_pay += 1

                    else:
                        continue
                # 追加求人の判定のために使用(0なら１足す、もしあった場合は0にリセット)
                if additional_pay == 0:
                    additional_pay_none +=1
                if additional_pay > 0:
                    additional_pay_none = 0

                print(f"このページの有料の数は{additional_pay}個")
                print(f"今までの有料の数は総計{pay + additional_pay}個")
                print(f"その他の勤務地も含めると総計{pay +additional_pay + more}個になります")


                if additional_pay_none >= 2:
                    print("二回連続で有料求人数が0だったので複数ページ遷移を終了します。")
                    url_count = 0
                    break

                if len(job_list) is None:#0の場合、ループに戻る
                    print("残りページはありません。ループに戻ります。")
                    url_count = 0
                    break

                if len(job_list) >= 15:
                    if soup.find("a",attrs={"data-testid":"pagination-page-next"}): #→(以降のページがあると消える）があるとループ終了（ページにマックス求人あるけど、以降のページがない時の対処)
                        print("まだページがあるため、次のページに遷移します")
                        continue
                    else:
                        print("このページの求人数は15ですが、以降のページは存在しないのでループに戻ります。")
                        url_count =0
                        break

                if len(job_list) < 15:
                    url_count = 0
                    print("求人数が15未満のため、このページは最終ページとなります。ループに戻ります。")
                    break



        if "誰よりも早く" in soup.text: #邪魔なポップアップを検出しリロードで削除
            print("邪魔者を検出")
            error_count+=1
            print(count)
            print(f"エラーカウント:{error_count}")
            browser.refresh()
            """  sleep_time = random.uniform(8,12)
            time.sleep(sleep_time)"""

            #更新することで消えるようになった

            """
            whole_page = browser.find_element(By.TAG_NAME,"html")
            print("全体を取得")
            browser.maximize_window()
            actions.move_to_element_with_offset(whole_page,1,1)
            actions.click()
            """


"""
    kyujins = soup.find_all("ul",attrs={"class":"jobsearch-ResultsList css-0"})
    kyujins = soup.find_all("li")
    count = 0
    print(len(kyujins))

    for kyujin in kyujins:
        indeed_Apllys = kyujin.find_all("td",attrs={"class":"shelfItem indeedApply"})
        if indeed_Apllys is None:
            print("この部分の求人にはありません")
            continue
        else:
            count+=len(indeed_Apllys)

    print(count)
"""






