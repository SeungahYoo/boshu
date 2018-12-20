# -*- coding: utf-8 -*-

import urllib.request
from urllib import parse
from bs4 import BeautifulSoup
from slackclient import SlackClient
from flask import Flask, request, make_response, render_template

app = Flask(__name__)

slack_token = "xoxb-503818135714-506852761857-ElsWv0jr7wBR2dXzJPUqlSAO"
slack_client_id = "503818135714.507348866547"
slack_client_secret = "1fb4309701edc44269c681c494bed569"
slack_verification = "cupsHgeL0hFVq3B6kz3IWAbY"
sc = SlackClient(slack_token)


# 크롤링 함수 구현하기
def _crawl_naver_keywords(text):

    text = parse.quote(text+" 편성표")


    url = "https://search.naver.com/search.naver?sm=top_hty&fbm=1&ie=utf8&query="+text

    req = urllib.request.Request(url)

    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")

    # 함수를 구현해 주세요
    titles = []
    info=[]
    sche=[]
    table=[]
    date=[]
    result = []
    timetable=[]
    times=[]
    idx=[]


    if "naver" in url:

        for data in soup.find_all("div", class_="brcs_thumb"): #썸네일
            result.append(data.find('img')['src'])



        for data in soup.find_all("div", class_="title padr"): #프로그램 제목
            if not data.get_text() in titles:
                titles.append(data.get_text().strip("\n").strip(" "))

        for data in soup.find_all("div", class_="info_bar"): #프로그램 장르
            content = data.get_text()
            contents = []
            contents = content.split("|")
            if not content in info:
                info.append(contents[0].strip(" "))

        for data in soup.find_all("span", class_="inline"): #프로그램 편성시간
            if not data.get_text() in sche:
                if len(sche) >= 1:
                    break

                sche.append(data.get_text().strip("\n").replace("|", " "))

        for data in soup.find_all("th", class_="today"): #오늘 날짜
            if not data.get_text() in date:
                date.append(data.get_text().strip("\n").strip(" "))


        for data in soup.find_all("td", class_="first"): #편성 채널
            channel = data.get_text()
            if not channel in table:
                    table.append("["+channel.strip("\n").strip(" ")+"]")





        i=0
        for detail in soup.find_all("td", class_="today"): #편성 시간, 회차

            times.clear()
            idx.clear()
            for time in detail.find_all("span", class_="time_min"):



                if not time.get_text() in times:
                    times.append(time.get_text())

            # for index in detail.find_all("em", class_="count"):
            #     print(idx)
            #
            #     if index == -1:
            #         idx.append("1")
            #     else:
            #         idx.append(index.get_text())


            if(len(times)!=0):
                for j in range(len(times)):
                    table[i] = table[i] + " " + times[j] +  " |"
                timetable.append(table[i])

            i += 1







# '''
#     for i in range(1, 11):
#         result.append(str(i) + "위: " + titles[i - 1] + " / " + artists[i - 1])
# '''

    result.append("*"+titles[0]+"*" + " (" + info[0] + ")")
    result.append(sche[0])
    result.append("_<오늘의 편성표>_ "+date[0])

    for i in range(0,len(timetable)):
        result.append(timetable[i])
    #result.append(timetable)


    #print(result)


    # 한글 지원을 위해 앞에 unicode u를 붙혀준다.

    # return u'\n'.join(result)
    return result

if __name__ == '__main__':
    text="시사 생생정보"
    _crawl_naver_keywords(text)

