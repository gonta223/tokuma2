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
from pandas import options

from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome import service as fs

from os.path import join  # 既に開いているブラウザを取得する際のコードに必要

import chromedriver_binary  # Chromeのパスを通すためのコード

# 起動したら以下のコードをターミナルで使用、そこで開かれたブラウザでprivacypassを起動し認証を行う
# /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir="/Users/satousuguru/Desktop/Python/google chrome" ⚠️最後のクオーテーショん入れないとバグる
# https://qiita.com/mimuro_syunya/items/2464cd2404b67ea5da56:参考
#:ターミナルで使用

EXTENSION_PATH = "/Users/satousuguru/Desktop/Python/KeywordSurfer.crx"  # ⚠️拡張機能のパス。適宜書き換えて

import csv  # csvを読み込む
import datetime
dt_now = datetime.datetime.now() #現在の日時

from Tokuma2a import *

browser = webdriver.Chrome()

global keyword
keyword = "日本交通株式会社"
#ここらへんどこで宣言しようか考え中
global kantan_profile_count
global kantan_this_count
global directapply_count
global more
kantan_profile_count = 0
kantan_this_count = 0
directapply_count = 0
more = 0
global total_paid_number
total_paid_number = 0
global url_count
url_count = 0
global page_num
page_num = 0
global town_num
global hatarako_num

global previous_total_paid_number
previous_total_paid_number = 0
global no_found
no_found = 0

global breakpoint
breakpoint = 0

global date

global df_b
col_names = ["リスト日","会社名","indeed有料合計","タウンワーク","はたらこ","プロフィールでカンタン","この求人にカンタン","indeedで応募"]
df_b = pd.DataFrame(columns=col_names)
df_b = pd.options.display.precision = 0

def load_csv():
    df = pd.read_csv("tokuma2a.csv")
    global keyword
    print(df["会社名"])
    global company_list
    company_list = df["会社名"].values.tolist() #dfからリストに ⚠️覚えておくべき


def set_browser_access(): #aにもあるけどエラー吐くのでこっちにも記述
    CHROMEDRIVER = "/Users/satousuguru/Desktop/chromedriver"
    browser.get("https://jp.indeed.com/")
    source = browser.page_source
    soup = BeautifulSoup(source,"html.parser")


def get_soup():
    global soup
    source = browser.page_source
    soup = BeautifulSoup(source,"html.parser")
    return soup


def search_btn():
    elem_search_btn = browser.find_element(By.CLASS_NAME,"yosegi-InlineWhatWhere-primaryButton")
    elem_search_btn.click()


def find_box():
    global elem_type_search_word

    elem_type_search_word = browser.find_element(By.ID,"text-input-what")
    elem_type_area = browser.find_element(By.ID,"text-input-where")
    return(elem_type_search_word,elem_type_area)


def type_box(keyword):
    find_box()[0].send_keys(f'"{keyword}"')


def save_total_number(key):
    total_number = soup.find("div", attrs={"class": "jobsearch-JobCountAndSortPane-jobCount"})
    total_number = total_number.text
    total_number = total_number.split("件")[0]
    total_number = total_number.replace(",","")
    total_number = int(total_number)

    if key == 0:
        print(f"総求人数は{total_number}です")
        global total_num
        total_num = total_number
    if key == 1:
        print(f"おすすめを引いた求人数は{total_number}です")
        global osusume_num
        osusume_num = total_number
    if key == 2:
        print(f"応募後を引いた求人数は{total_number}です")
        global obogo_num
        obogo_num = total_number

    return total_number

def minus_search():
    global town_num
    global hatarako_num

    elem_type_search_word = browser.find_element(By.ID,"text-input-what")
    elem_type_search_word.send_keys(' -"おススメポイント"')
    search_btn()
    get_soup()
    save_total_number(1)
    town_num = total_num - osusume_num
    print(f"タンワークの求人数は{town_num}です")
    time.sleep(1)
    browser.refresh()
    elem_type_search_word = browser.find_element(By.ID,"text-input-what")
    elem_type_search_word.send_keys(' -"応募後プロセス"')
    search_btn()
    get_soup()
    save_total_number(2)
    hatarako_num = total_num - town_num - obogo_num
    print(f"はたらこネットの求人数は{hatarako_num}です")
    time.sleep(1)
    browser.refresh()


def get_number_kantan_and_directapply_innner():
    global kantan_profile_count
    global kantan_this_count
    global directapply_count
    global more
    get_soup()

    for job in job_list:
        if job.find("span",attrs={"class":"ialbl iaTextBlack"}):#とりあえずどっちかは入っている
            hantei = job.find("span",attrs={"class":"ialbl iaTextBlack"})

            if "プロフィールだけでカンタン" in str(hantei):
                kantan_profile_count += 1
                if job.find("span",attrs={"class":"more_loc_container"}):
                    other_area = job.find("span",attrs={"class":"more_loc_container"}).text #その他の勤務地
                    other_area_num = re.findall(r"\d+", other_area) #数字部分のみを取り出す
                    other_area_num = other_area_num[0]
                    other_area_num = int(other_area_num)
                    more += other_area_num

            if "この求人にカンタン" in str(hantei):
                kantan_this_count += 1
                if job.find("span",attrs={"class":"more_loc_container"}):
                    other_area = job.find("span",attrs={"class":"more_loc_container"}).text #その他の勤務地
                    other_area_num = re.findall(r"\d+", other_area) #数字部分のみを取り出す
                    other_area_num = other_area_num[0]
                    other_area_num = int(other_area_num)
                    more += other_area_num

            if "indeed" in str(hantei):
                directapply_count += 1
                if job.find("span",attrs={"class":"more_loc_container"}):
                    other_area = job.find("span",attrs={"class":"more_loc_container"}).text #その他の勤務地
                    other_area_num = re.findall(r"\d+", other_area) #数字部分のみを取り出す
                    other_area_num = other_area_num[0]
                    other_area_num = int(other_area_num)
                    more += other_area_num

            global total_paid_number
            total_paid_number = kantan_profile_count + kantan_this_count + directapply_count + more
            print(f"総計有料求人数:{total_paid_number}カンタンプロ：{kantan_profile_count}, カンタンこの:{kantan_this_count},indeedから:{directapply_count},その他の勤務地:{more}")



def get_number_kantan_and_directapply():
    global job_list
    global previous_total_paid_number
    global no_found
    global total_paid_number
    global kantan_profile_count
    global kantan_this_count
    global directapply_count
    global more
    global breakpoint
    global url_count
    global page_num

    total_paid_number = 0
    kantan_profile_count = 0
    kantan_this_count = 0
    directapply_count = 0
    more = 0
    url_count = 0
    page_num = 0


    get_soup()
    job_list = soup.find("ul", attrs={"class": "jobsearch-ResultsList css-0"})

    if job_list is None:  # 求人数が0の時はここでループ最初に戻る
        print("このページの求人はありませんでした😢")
        breakpoint = 1

    if breakpoint == 0:
        job_list = job_list.find_all("div", attrs={"class": "slider_container css-g7s71f eu4oa1w0"})

        get_number_kantan_and_directapply_innner()


        while total_paid_number <= 30:
            if "pagination-page-next" in str(soup): #一番下にみぎ→があるかどうかで判定。⚠️ここ覚えた方がいい
                print("有料求人が30未満でかつ、まだページがあるので次のページにいきます")
                next_page(len(job_list))
                get_number_kantan_and_directapply_innner()
                print(f"このページの総計有料求人数:{total_paid_number}カンタンプロ：{kantan_profile_count}, カンタンこの:{kantan_this_count},indeedから:{directapply_count},その他の勤務地:{more}")
                if total_paid_number == previous_total_paid_number: #2回連続で有料求人が0ならループ中止
                    no_found += 1
                    total_paid_number = previous_total_paid_number
                if no_found >= 2:
                    print("有料求人が30未満ですが、有料求人が連続して2ページ存在していないためこの単語の検索を終わります")
                    break
            else:
                print("有料求人が30未満ですが、もうページがないのでこの単語の検索を終わります")
                print(browser.current_url)
                break
        if total_paid_number > 30:
            print("有料求人数が30を超えたので、まだページが残っていますが、このページでこの単語の検索を終わります。")



def next_page(count):
    global url_count
    global page_num

    url_count += count
    cur_url = browser.current_url
    cur_url = cur_url.split("&")[0]
    cur_url_next = cur_url +"&&start=" + str(url_count)
    print(cur_url)
    print(cur_url_next)
    browser.get(f"{cur_url_next}")
    page_num +=1


def to_csv():
    ###どちらにも手間だから、先にtokuma2b.csvを作成しといてください
    global town_num
    global hatarako_num

    #日付の読み込み
    global date
    date = f"{dt_now.month}月{dt_now.day}日"
    #追記するdfの読み込み
    df_b = pd.read_csv("Tokuma2b.csv")
    company_list = df["会社名"].values.tolist()

    dict = {"リスト日": [date],"会社名":[keyword],"indeed有料合計":[total_paid_number],"タウンワーク":[town_num],"はたらこ":[hatarako_num],"プロフィールでカンタン":[kantan_profile_count],"この求人にカンタン":[kantan_this_count],"indeedで応募":[directapply_count]}
    df2 = pd.DataFrame(dict)
    df_b = df_b.append(df2)
    print(df_b)
    df_b.to_csv("Tokuma2b.csv",index=False)




if __name__ == "__main__":
    load_csv()
    global company_list
    for company in company_list:
        keyword = company
        print(f"次の検索ワードは「{keyword}」です")
        set_browser_access()
        find_box()
        type_box(keyword)
        search_btn()
        get_soup()
        save_total_number(0)
        minus_search()
        get_number_kantan_and_directapply()
        if breakpoint == 1: #求人が0だったらbreak
            break
        to_csv()