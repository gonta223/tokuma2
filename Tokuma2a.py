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

browser = webdriver.Chrome()

##打ち込むワード、自由に書き換え可能
keyword = "ドライバー"
area_word = "杉並区"
employment_sta = "業務委託"


global col_names
col_names = ["会社名"]
df = pd.DataFrame(columns = col_names)

def set_browser_access():
    CHROMEDRIVER = "/Users/satousuguru/Desktop/chromedriver"
    browser.get("https://jp.indeed.com/")
    source = browser.page_source
    soup = BeautifulSoup(source,"html.parser")


def find_box():
    elem_type_search_word = browser.find_element(By.ID,"text-input-what")
    elem_type_area = browser.find_element(By.ID,"text-input-where")
    return(elem_type_search_word,elem_type_area)


def type_box(keyword,area_word):
    find_box()[0].send_keys(f'"{keyword}"')
    find_box()[1].send_keys(f'"{area_word}"')


def search_btn():
    elem_search_btn = browser.find_element(By.CLASS_NAME,"yosegi-InlineWhatWhere-primaryButton")
    elem_search_btn.click()


def get_soup():
    global soup
    source = browser.page_source
    soup = BeautifulSoup(source,"html.parser")
    return soup


def job_type_btn_find_and_click():
    elem_type_job_button = browser.find_element(By.ID,"filter-jobtype")
    elem_type_job_button.click()


def job_type_change_gyomuitaku():
    cur_url = browser.current_url
    changed_url = cur_url +"&sc=0kf%3Ajt(commission)%3B" #業務委託はこの文字列をURLに足すと選択される
    browser.get(f"{changed_url}")


def job_type_change_seisyain():
    cur_url = browser.current_url
    changed_url = cur_url +"&sc=0kf%3Ajt(fulltime)%3B&limit=35" #正社員はこの文字列をURLに足すと選択される
    browser.get(f"{changed_url}")


def job_type_change_haken():
    cur_url = browser.current_url
    changed_url = cur_url +"&sc=0kf%3Ajt(temporary)%3B&limit=35" #派遣はこの文字列をURLに足すと選択される
    browser.get(f"{changed_url}")

def reload():
    browser.refresh()

def get_companies_and_minus():
    companies = soup.find("ul",attrs={"id":"filter-cmp-menu"})
    if companies is None:
        companies = soup.find("ul",attrs={"id":"filter-fcckey-menu"})
    companies = companies.find_all("li")
    top10_list=[]
    count = 0
    for company in companies:
        company = company.text.split("(")[0]
        top10_list.append(company)
        count += 1
        if count <= 10:
            find_box()[0].send_keys(f'-"{company}"')
    df2 = pd.DataFrame(top10_list ,columns = col_names)
    global df
    df = df.append(df2)
    #トップ10社のdfを返す
    return df


def get_jobs():
    job_list = soup.find("ul",attrs={"class":"jobsearch-ResultsList css-0"})
    if job_list is None:
        print("トップ10社をマイナス検索した結果、求人はありませんでした")
    job_list = job_list.find_all("div",attrs={"class":"slider_container css-g7s71f eu4oa1w0"})#求人をそれぞれ読み込む
    return job_list

def get_kantan_or_directapply_and_to_df():
    kantan_or_directapply_list = []
    for job in get_jobs():
        if job.find("span",attrs={"class":"iaIcon"}):#indeedで応募、もしくはカンタン応募を検出(その左にある矢印アイコンを判定に使っている)
            job = job.find("span",attrs={"class":"companyName"})
            kantan_or_directapply_list.append(job.text)

    col_names = ["会社名"]
    df2 = pd.DataFrame(kantan_or_directapply_list,columns = col_names)
    global df
    df = df.append(df2)
    #トップ10社と、業務委託の時に有料ある社名を返す
    return df


def delete_same():
    global df
    global df_completed
    df_list = df['会社名'].to_list()
    re_df = list(set(df_list))
    df_completed = pd.DataFrame(re_df ,columns = col_names)
    print("sameを削除")
    print(df_completed)


def to_csv():
    global df_completed
    df_completed.to_csv("tokuma2a.csv",index=False)


def sleep():
    time.sleep(10)


def if_plural_page():
    url_count=0
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

                ##ここから次のページ

                source = browser.page_source
                soup = BeautifulSoup(source,"html.parser")

                job_list = soup.find("ul",attrs={"class":"jobsearch-ResultsList css-0"})
                if job_list is None: #2ページ目の求人数が0の時はここで何もせずループに戻る
                    print("2ページ目には求人がありませんでした😢直上の情報が最終的な情報になります。")
                    continue

                job_list = job_list.find_all("div",attrs={"class":"slider_container css-g7s71f eu4oa1w0"})#求人をそれぞれ読み込む
                print(f"このページの求人数は{len(job_list)}")



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

                print(f"有料の数は総計{pay}個")
                print(f"その他の勤務地も含めると総計{pay + more}個になります")



                if len(job_list) >= 15:
                    print("まだページがあるため、次のページに遷移します")
                else:
                    print("残りページはありません。ループに戻ります。")
                    continue

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

                 ##ここから次のページ

                source = browser.page_source
                soup = BeautifulSoup(source,"html.parser")

                job_list = soup.find("ul",attrs={"class":"jobsearch-ResultsList css-0"})
                if job_list is None: #2ページ目の求人数が0の時はここで何もせずループに戻る
                    print("2ページ目には求人がありませんでした😢直上の情報が最終的な情報になります。")
                    continue

                job_list = job_list.find_all("div",attrs={"class":"slider_container css-g7s71f eu4oa1w0"})#求人をそれぞれ読み込む
                print(f"このページの求人数は{len(job_list)}")



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



                if len(job_list) >= 15:
                    print("まだページがあるため、次のページに遷移します")
                else:
                    print("残りページはありません。ループに戻ります。")
                    continue

                continue


if __name__ == "__main__": #このプログラムから直接起動してる時のみに実行
    set_browser_access()
    find_box()
    type_box(keyword,area_word)
    search_btn()
    find_box()
    get_soup()
    get_companies_and_minus()
    search_btn()
    job_type_change_gyomuitaku()
    get_soup()
    get_jobs()
    get_kantan_or_directapply_and_to_df()
    job_type_btn_find_and_click()
    job_type_change_seisyain()
    sleep()
    get_kantan_or_directapply_and_to_df()
    job_type_btn_find_and_click()
    job_type_change_haken()
    sleep()
    get_kantan_or_directapply_and_to_df()
    delete_same()
    to_csv()
