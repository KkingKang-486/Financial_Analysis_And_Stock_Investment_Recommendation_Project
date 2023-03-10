# 네이버 증권 뉴스
# 크롤링 할 내용 : 1. 아티클 title 2. 아티클 contents
# ~부터 다시 돌리기
# ver3. 일별로 저장후 리스트 비워주기

from selenium import webdriver                # pip install selenium
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import pandas as pd                           # pip install pandas
import re
import time
import datetime
from datetime import date, timedelta          # strftime 함수. 원하는 형식으로 날짜를 출력

category = ['시황,전망', '기업,종목분석', '해외증시', '채권,선물', '공시,메모', '환율']  # '해외증시', '채권/선물' 후순위로.
category_2 = [401, 402, 403, 404, 406, 429]                                     # pages라고 칭하기에 카테고리 안쪽>일별>페이지가 있어서 category_2로 지정
category_date = []                                                              # 날짜만들기(일별페이지 돌리기 위함)

url = 'https://finance.naver.com/news/'                                         # 카테고리 일별로 나뉘며, 일별로 단일페이지 or 여러페이지 이기도         # 버튼 눌러서 접속하려면 이렇게만도?(라프텔)


options = webdriver.ChromeOptions()
# options.add_argument('headless')            # 웹브라우저를 열지않고 크롤링(?)
options.add_argument('lang=kr_KR')            # 해당 국가 언어값 입력
driver = webdriver.Chrome('./chromedriver', options=options)
df_title = pd.DataFrame()                     # 타이틀 모으는 데이터프레임?! / df_titles로 나중에 통일한 걸로 기억..
driver.get(url)                               # 뉴스땐 있고 라프텔 땐 없는 부분. 필요? 하단에 있음


# <x_path 정의, ijklm 각 정리>
# category :                      //*[@id="newarea"]/div[1]/ul/li[3]/ul/li[1]/a                            xpath1_category   # => i     # 1~6
# articleSubject or 썸네일 :       //*[@id="contentarea_left"]/ul/li[1]/dl/dt[5]/a                          xpath2_title      # 1~10, 1~최대10  => 20개
# 썸네일 있는(dd) 기사 :            xpath2_article_button      //*[@id="contentarea_left"]/ul/li[{}]/dl/dd[{}]/a
# 썸네일 없는(dt) 기사 :            xpath2_article_button      //*[@id="contentarea_left"]/ul/li[{}]/dl/dt[{}]/a

# 기사 속 제목 :                    //*[@id="contentarea_left"]/div[2]/div[1]/div[2]/h3                      xpath3_title
# articleCont :                   //*[@id="content"]                                                       xpath4_content    # 기사마다 통일되어있음
# 목록보기(뒤로가기) 버튼 :           //*[@id="spiLayer"]/a                                                    xpath5_button

# 일별 기사(년월일로 조회) url :      https://finance.naver.com/news/news_list.naver?mode=LSS3D&section_id=101&section_id2=258&section_id3=401&date=20230109
# 일별 기사 > 다중페이지(1~n개):      https://finance.naver.com/news/news_list.naver?mode=LSS3D&section_id=101&section_id2=258&section_id3=402&page=8
# 일별 기사 > 다중페이지(1~n개):      //*[@id="contentarea_left"]/table/tbody/tr/td/table/tbody/tr/td[1]/a     xpath6_page

# l = li_section_1, 2
# m = 썸네일 있고 없고


today = date.today()

today = today.strftime('%Y%m%d')
# category_date.append(today)                   # 오늘 날짜
# print(category_date)

for d in range(32, 376):                        # 23년 1월 10일 ~ 22년 1월1일. (1월 11일 기준 375일 전까지)   # 20221227~. => (15, 376)  # 20221210~. => (32, 376)
    yesterday = date.today() - timedelta(d)     # 하루치 뺀 것이 yesterday. d는 1~375까지 돈다
    yesterday = yesterday.strftime('%Y%m%d')    # 날짜형식 ex) 20230110 되도록.
    category_date.append(yesterday)             # category_date 리스트에 날짜들 모아 넣을 것
# print(category_date)

for i in category_2:
    for j in category_date:
        titles = []                             # 일별로 저장후 리스트 비워주기 !!
        contents = []
        for k in range(1, 11):
            try:
                date_page = 'https://finance.naver.com/news/news_list.naver?mode=LSS3D&section_id=101&section_id2=258&section_id3={}&date={}&page={}'.format(i, j, k)  # 카테고리, 일별, 페이지 format
                print(date_page)
                driver.get(date_page)
                time.sleep(1)
                for l in range(1, 3):                           # li_section_1 # li_section_2 : 페이지 내 리스트 10개, 10(-n)개 2개 섹션으로 나뉨
                    for m in range(1, 20, 2):                   # 썸네일 있는(dd) 기사의 경우 1, 3, 5,,,순으로(홀수or짝수) 따로 ~19까지 전개됨.   # 다 제목으로 접속하는데 dd와 dt로 두번
                        try:                                    # 썸네일 있는(dd) 기사의 제목, 내용 긁고 저장
                            xpath2_article_button = '//*[@id="contentarea_left"]/ul/li[{}]/dl/dd[{}]/a'.format(l, m)
                            driver.find_element('xpath', xpath2_article_button).click()
                            time.sleep(1)

                            xpath3_title = '//*[@id="contentarea_left"]/div[2]/div[1]/div[2]/h3'  # 기사 속 제목의 xpath
                            xpath4_contents = '//*[@id="content"]'                                # 기사 속 내용의 xpath
                            title = driver.find_element('xpath', xpath3_title).text               # 변수명, 기사 속 제목
                            content = driver.find_element('xpath', xpath4_contents).text
                            # title = re.compile('[^가-힣 ]').sub(' ', title)                        # 전처리(한글만 남길)
                            # content = re.compile('[^가-힣 ]').sub(' ', content)
                            titles.append(title)                # 기사제목 append
                            contents.append(content)            # 기사내용 append
                            print(title)
                            print(content)
                            driver.back()                       # 뒤로가기
                            time.sleep(1)


                        except NoSuchElementException as E:     # 썸네일 없는(dt) 기사의 제목, 내용 긁고 저장
                            xpath2_article_button = '//*[@id="contentarea_left"]/ul/li[{}]/dl/dt[{}]/a'.format(l, m)
                            driver.find_element('xpath', xpath2_article_button).click()
                            time.sleep(1)

                            xpath3_title = '//*[@id="contentarea_left"]/div[2]/div[1]/div[2]/h3'  # 기사 속 제목의 xpath
                            xpath4_contents = '//*[@id="content"]'                                # 기사 속 내용의 xpath
                            title = driver.find_element('xpath', xpath3_title).text               # 변수명, 기사 속 제목
                            content = driver.find_element('xpath', xpath4_contents).text
                            # title = re.compile('[^가-힣 ]').sub(' ', title)                        # 전처리(한글만 남길)
                            # content = re.compile('[^가-힣 ]').sub(' ', content)
                            titles.append(title)                # 기사제목 append
                            contents.append(content)            # 기사내용 append
                            print(title)
                            print(content)
                            driver.back()                       # 뒤로가기
                            time.sleep(1)

                        except:
                            pass                                # 기사 접속 시 dd도 아니고 dt도 아니면 넘어가기
                            print('pass')


            except NoSuchElementException as E:
                print(i, j, k, l, m)

        # 저장
        df = pd.DataFrame(zip(titles, contents))                # 일별로 저장. # 기사제목, 기사내용, 카테고리순으로
        df.columns = ['titles', 'contents']
        df['category'] = category[category_2.index(i)]
        print(df)
        df.to_csv('./crawling_data/news_crawling_data_{}_{}.csv'.format(category[category_2.index(i)], j), index=True)
