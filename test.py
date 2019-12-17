import ssl
from bs4 import BeautifulSoup
import urllib.request

html = "https://www.edaily.co.kr/news/contents/NewsStand/vbs_real/brg.asp?bCode=G04pt&sgb=E&newsid=G36079"

context = ssl._create_unverified_context()
html = urllib.request.urlopen(html, context=context)
source = html.read()
html.close()
soup = BeautifulSoup(source, "html5lib")

txt = soup.find_all("meta")
print(txt)