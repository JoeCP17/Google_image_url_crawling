"""
멀티 프로세싱을이용하여

각각 프로세스당 URL 이미지를 긁어오는 프로그램을작성해라

OOP programming (주석 필수) AND functional programming 선택해서 진행 (주석 필수)

예) 프로세스 1 은 url 만 긁어오는 프로세스

      프로세스 2 는 이미지만 긁어오는 프로세스

만약 안되면 그 이유와 다른걸 로 설득 할 수 있으면 변호한걸로 인정하겠음

 정 어쩔 수 없으면 def 사용하면 사용하되 이유는 꼭 남길것

"""

import multiprocessing
import requests
from bs4 import BeautifulSoup
import pandas as pd

##################### bs만을 활용하여 url 크롤링 ################################

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import urllib.request

data_input = input('검색할 단어를 입력해주세요 ----> ')

def html(): # html은 공통으로 필요하다 판단하여 html 불러오는 def 선언 따로만듬
    url = requests.get(f'https://www.google.com/search?q={data_input}').content
    soup = BeautifulSoup(url, 'html.parser')
    return soup

def get_url(tag): #url 채집 부분
    url_list = []
    for i in tag.find_all("a"):
        url_real = i.get('href')
        url_list.append(url_real)

    text_dict = {"url" : url_list}
    test_frame = pd.DataFrame(text_dict)
    test_frame.to_csv('url_info.csv' , index_label=False , index= False)

def get_image(): # 이미지 채집 부분 (셀레니움 이용)
    driver = webdriver.Chrome()
    driver.get('https://www.google.co.kr/imghp?hl=ko')
    elem = driver.find_element_by_name('q')
    elem.send_keys(data_input)
    elem.send_keys(Keys.RETURN)

    scroll_pause_time = 1  #스크롤 내린 후 기다리는 초 설정
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True: # 스크롤을 밑까지 내리는 내용 (js의 부분 인용하여 사용)
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
        time.sleep(scroll_pause_time)  #더보기 버튼 나올때까지 기다림

        new_height = driver.execute_script("return document.body.scrollHeight") #새로 나올시 해당부분 기다림
        if new_height == last_height: #만약 더보기까지 창이 내려왔을 경우
            try:
                driver.find_element_by_css_selector(".mye4qd").click() # 더보기 버튼 누르기 시도
            except: #없을 경우 맨 밑까지 내려간 것이니
                break# 반복문 빠져나오기
        last_height = new_height # 맨위로 다시 스크롤 이동

    images = driver.find_elements_by_css_selector('.rg_i.Q4LuWd') # 작은 이미지의 css 찾기
    count = 1 #카운트로 이미지 저장
    for image in images: # 각 images를 돌면서
        image.click() #이미지 클릭
        time.sleep(3) #3초 타임슬립
        img_url = driver.find_element_by_css_selector(".n3VNCb").get_attribute("src") #눌렀을때 크게 나왔을때 나오는 이미지의 태그 + src 결합
        # 다운받기 위해 해당 부분 실행
        urllib.request.urlretrieve(img_url, str(count) + ".jpg") # 카운트 번호로 다운로드 진행
        count += 1 #다운이 마칠때마다 1씩 증가

    driver.close() #다 저장이 되었을때 close를 통한 마무리

def multi_process(): #한번 응용을 해봅시다....
# 왜 오류가 날까 진짜 알고싶다....
    mul_url = multiprocessing.Process(target=get_url, args=(html, ))
    img_url = multiprocessing.Process(target=get_image, args=( ))

    mul_url.start()
    img_url.start()

    mul_url.join()
    img_url.join()

if __name__ == '__main__':
    multi_process()
