# 네이버에서 mediacode를 가져오기 위한 크롤링 파일 (각 언론사마다의 pcode)
import logging
import ssl
from urllib.request import urlopen
from bs4 import BeautifulSoup
import html5lib
import re

def main():
    print("~~~~~ start ~~~~~")

    newsstand = 'https://www.naver.com/'

    context = ssl._create_unverified_context()
    html = urlopen(newsstand, context=context)
    source = html.read()
    html.close()

    try:
        soup = BeautifulSoup(source, "html5lib")
        script = soup.find_all('script')
        myScript = script[len(script)-1]

        # pcode 추출
        pid = re.search(r'headlineList : (.*)', myScript.get_text()) 
        pgrp = pid.group(1).split('"')

        #for r in range(3,len(pgrp)-5,+2):
            #print(pgrp[r])

        # 언론사명 추출
        pressCategory = re.search(r'"ct1":(.*)', myScript.get_text())
        myCate = pressCategory.group(1)
        #print(myCate.find('032').get_text())
        print(re.search(r'"pid":"930","name":"(.*?)"', myCate))
        tt = re.search(r'"pid":"930","name":"(.*?)"', myCate)
        print(tt.group().split('"'))
        ttt = tt.group().split('"')
        print(ttt[7])

    except:
        logging.error("main error(2)")

if __name__ == '__main__':
    try:
        main()
    except:
        logging.error("main error(1)")
