from newspaper import Article
import newspaper
from bs4 import BeautifulSoup
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium import webdriver

# foxlinks = []
source = newspaper.build("http://dunyanews.tv/")
for news in source.articles:
    link = news.url
    # link = link.replace("#comments", "")
    link = link.replace("https", "fetcherprotocol")
    link = link.replace("http","fetcherprotocol")
    link = link.replace("fetcherprotocol", "https")
    print(link)
    # foxlinks.append(link)
    # continue

# article = Article(soup)

# print(article.html)
# source = soup.articles
#
# source.download()
# print(len(link))

