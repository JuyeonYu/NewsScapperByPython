from bs4 import BeautifulSoup
import requests
from DatabaseManager import DatabaseManager
import re
import datetime
from konlpy.tag import Kkma
from konlpy.utils import pprint

title_text = []
link_text = []
source_text = []
date_cleansing = []
contents_text = []
article_dictionary = {}
date_text = []

now = datetime.datetime.now()
have_news = True

# 데이터베이트 세팅
db = DatabaseManager('54.180.88.102', 'johnny', 'qwas8800', 'newScrapper')
# db.insert_test('test')


#내용 정제화 함수
def contents_cleansing(contents):
    first_cleansing_contents = re.sub('<dl>.*?</a> </div> </dd> <dd>', '',
                                      str(contents)).strip()  #앞에 필요없는 부분 제거
    second_cleansing_contents = re.sub('<ul class="relation_lst">.*?</dd>', '',
                                       first_cleansing_contents).strip()#뒤에 필요없는 부분 제거 (새끼 기사)
    third_cleansing_contents = re.sub('<.+?>', '', second_cleansing_contents).strip()
    contents_text.append(third_cleansing_contents)


def crawler(query):
    #크롤링 전 데이터 세팅
    currnet_searching_page = 1
    have_more_page_to_search = True
    today_yy_mm_dd = datetime.datetime.now().strftime("%Y.%m.%d")
    # today_yy_mm_dd = '2020.01.22' # 테스트 코드

    print('크롤링 시작 전 값 세팅 확인 \ncurrnet_searching_page: ', currnet_searching_page, '\nhave_more_page_to_search: ', have_more_page_to_search, '\ntoday_yy_mm_dd: ', today_yy_mm_dd)

    # 해당 키워드에 해당하는 최신 기사 제목을 얻음
    latest_news_title_in_database = db.select_latest_news(query)

    # 크롤링 시작
    while have_more_page_to_search:
        url = "https://search.naver.com/search.naver?&where=news&query=" + query + "&sm=tab_pge&sort=1&photo=0&field=0&reporter_article=&pd=3&ds=" + today_yy_mm_dd + "&de=" + today_yy_mm_dd + "&mynews=0&start=" + str(currnet_searching_page) + "&refresh_start=0"

        print('크롤링 시작! url 확인 \nurl: ', url)

        req = requests.get(url)
        cont = req.content
        soup = BeautifulSoup(cont, 'html.parser')

        # 검색 결과가 없을 때 처리 (mm월 dd일 00시 mm에 기사가 올라오지 않을 때)
        noresult = soup.select('.noresult_tab')
        if noresult:
            print('no result')
            break

        # <a>태그에서 제목과 링크주소 추출
        atags = soup.select('._sp_each_title')

        # 첫번째 기사 제목 확인
        if currnet_searching_page == 1:
            print('크롤링 시작! 첫번째 기사 제목 확인 \nurl: ', atags[0].text.replace("'",""))
            first_searched_title = atags[0].text.replace("'","")

        for atag in atags:
            # 새로운 뉴스가 없음 -> 크롤링 중단
            if atag.text.replace("'", "") == latest_news_title_in_database:
                have_more_page_to_search = False
                print('새로운 뉴스가 없음 -> 크롤링 중단')
                break
            else:
                subKeywords = db.select_sub_keyword(query)
                print('sub key word: ', subKeywords)

                # 등록해놓은 서브 키워드에 맞는 기사 제목만 필터링 해서 데이터 베이스에 저장
                for sub in subKeywords:
                    if sub in atag.text:
                        db.insert_scrapped_news(atag.text, atag['href'], query)

        # 저장해놓은 첫번째 기사와 제목이 같으면 이하부터 중복 기사로 처리
        if db.is_latest_news(first_searched_title) == 0:
            db.insert_latest_news(query, first_searched_title)

        # 본문요약본
        contents_lists = soup.select('ul.type01 dl')
        for contents_list in contents_lists:
            contents_cleansing(contents_list)  # 본문요약 정제화

        # 페이지 처리 및 크롤링 계속 할지 말지 결정
        for page in soup.select(".paging"):
            if "다음페이지" in page.text:
                currnet_searching_page = currnet_searching_page + 10
            else:
                have_more_page_to_search = False
    print('finish')

# def crawler(query, s_date, e_date):
#     search_one_more_page = True
#     have_news = True
#     latest_news_title = ''
#     current_page = 1
#     search_sort = 1 # 0 = 관련도 검색, 1 = 최신순 검
#
#     db = DatabaseManager('54.180.88.102', 'johnny', 'qwas8800', 'newScrapper')
#
#     while search_one_more_page:
#         url = "https://search.naver.com/search.naver?&where=news&query=" + query + "&sm=tab_pge&sort=" + str(search_sort) + "&photo=0&field=0&reporter_article=&pd=3&ds=" + s_date + "&de=" + e_date + "&docid=&nso=so:r,p:from20200101to20200116,a:all&mynews=0&cluster_rank=28&start=" + str(current_page) + "&refresh_start=0"
#         response = requests.get(url)
#         html = response.text
#
#         soup = BeautifulSoup(html, "html.parser")
#         atags = soup.select('._sp_each_title')
#         pages = soup.select('.paging')
#
#         # 해당 키워드에 해당하는 최신 기사 제목을 얻음
#         latest_news_title = db.select_latest_news(query)
#
#         # 키워드에 해당하는 최신 기사 제목을 db에 저장해 놓음
#         # if current_page == 1:
#         first_searched_title = atags[0].text.replace("'", "")
#
#         # 단일 페이지가 아니면 계속 검색
#         for page in pages:
#             if '다음페이지' in page.text:
#                 print('현재 페이지: ', current_page)
#                 current_page = current_page + 10
#                 search_one_more_page = True
#             else:
#                 search_one_more_page = False
#                 # if search_sort == 0:
#                 #     search_sort = 1
#                 # else:
#
#         print('latest_news_title: ', latest_news_title)
#         print('first_searched_title: ', first_searched_title)
#         # 새로운 뉴스가 있으면 최신 뉴스 저장
#         if latest_news_title != first_searched_title:
#             print('# 새로운 뉴스가 있으면 최신 뉴스 저장', latest_news_title, "///", first_searched_title)
#             db.insert_latest_news(query, first_searched_title)
#         else:
#             # 새로운 뉴스가 없으므로 크롤링 중단
#             print('# 새로운 뉴스가 없으므로 크롤링 중단')
#             break
#
#         for atag in atags:
#             # 이전에 저장해놨던 최신기사까지만 저장
#             current_title = atag.text.replace("'", "")
#             if latest_news_title != current_title:
#                 # article_dictionary[atag['href']] = atag.text
#                 # title = atag.text.replace("'", "")
#                 db.insert_scrapped_news(current_title, atag['href'])
#                 # todo: 짧은 url 사용
#             # 여기부터 중복된 기사가 나옴
#             else:
#                 print('중복 기사가 나오므로 크롤링 중')
#                 break


def main():
    query = input("키워드 입력: ")
    crawler(query)


main()


    #     #신문사 추출
    #     source_lists = soup.select('._sp_each_source')
    #
    # for source_list in source_lists:
    #     source_text.append(source_list.text) #신문사
    #     #날짜 추출
    #     date_lists = soup.select('.txt_inline')
    #
    # for date_list in date_lists:
    #     source_text.append(source_list.text) #신문사
    #     #날짜 추출
    #     date_lists = soup.select('.txt_inline')