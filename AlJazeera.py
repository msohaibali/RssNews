import traceback
import datetime
import arrow
from pymongo import MongoClient
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support.ui import WebDriverWait
import feedparser
import xml.etree.ElementTree as ET
import time
import dateutil.parser as parser
import redis

tree = ET.parse('config.xml')
root = tree.getroot()
dbIP = ''
rIP = ''
db = ''
user1 = ''
password1 = ''
collName = ''
errCollName = ''
rPort = ''
shardIP = ''

for itm in root.findall('Project'):
    dbIP = itm.find('MongoIP').text
    shardIP = itm.find('ShardIP').text
    rIP = itm.find('RedisIP').text
    rPort = itm.find('RedisPort').text
    db = itm.find('Database').text
    user1 = itm.find('userName').text
    password1 = itm.find('pass').text
    collName = itm.find('collection').text
    errCollName = itm.find('collection2').text

# Client = MongoClient(dbIP)
Client = MongoClient(shardIP)
db = Client[db]
# db.authenticate(user1, password1)
collection1 = db[collName]
collection3 = db[errCollName]
r = redis.StrictRedis(host=rIP, port=rPort)

# binary = FirefoxBinary('/usr/local/desktop/firefox')
# capabilities = webdriver.DesiredCapabilities().FIREFOX
# capabilities["-marionette"] = False
# binary = FirefoxBinary(r'/usr/bin/firefox')

# driver = webdriver.Firefox(firefox_binary=binary, capabilities=capabilities)

driver = webdriver.Firefox()

rt = []

rt.append('https://www.aljazeera.com/xml/rss/all.xml')


def rssFeeds():
    def parseRss(rss_url):
        return feedparser.parse(rss_url)

    def getLinks(rss_url):
        links = []
        feed = parseRss(rss_url)
        for newsitem in feed['items']:
            links.append(newsitem['link'])
        return links

    def getTime(rss_url):
        n_time = []
        feed = parseRss(rss_url)
        for newsitem in feed['items']:
            n_time.append(newsitem['published'])
        return n_time

    global indialinks
    indialinks = []
    global publishedTime
    publishedTime = []
    for i in rt:
        indialinks.extend(getLinks(i))
        publishedTime.extend(getTime(i))
        print(i)


def error(err):

    try:
        source = "Al Jazeera News"
        time = datetime.datetime.now()
        time = time.isoformat()
        time = arrow.get(time).datetime
        collection3.insert([{"Error": err, "Source Name": source, "Time of Error": time, "Category": "International"}])
    except:
        pass


def getTarget(tg):
    driver.get(tg)


def implicitwait(timeout):
    WebDriverWait(driver, timeout)


data = []
data.append(collection1.distinct('_id'))


def NewsContent(lnk):
    ht = ''
    title = ''
    for d4 in data:
        for index in range(0, len(d4)):
            if d4[index] == lnk:
                print(d4[index])
                ht = "True"
                break
            else:
                ht = "False"

        if ht == "True":
            print("No Result Found")
        else:
            print("new Results Found")
            getTarget(lnk)
            print(lnk)
            time.sleep(3)
            soup = BeautifulSoup(driver.page_source, "html.parser")

            try:
                curr_post = soup.find('div', attrs={'class': 'article-heading'})
                targ_p = curr_post.find('h1', attrs={'class': 'post-title'})

                title = targ_p.text
                title = title.replace("\n", "")

                print(title)

            except:
                print("This is a Video/Photo. No Content found!!")
                pass

            try:
                p_content = ''
                curr_post = soup.find('div', attrs={'class': 'article-p-wrapper'})
                targ_p = curr_post.findAll('p')
                for p in targ_p:
                    p_content = p_content + p.text

                body = p_content
                body = body.replace("\n", "")

                print(body)

                date = parser.parse(publishedTime[cnt])
                publishedTime[cnt] = date.isoformat()
                publishedTime[cnt] = arrow.get(publishedTime[cnt]).datetime
                print(publishedTime[cnt])

                try:

                    collection1.insert([{"Type": "Predefined List", "Category": "International", "Language": "English",
                                         "Source": "Al Jazeera News", "title": title, "body": body, "_id": lnk,
                                         "published Time": publishedTime[cnt]}])
                    r.rpush('news_link', lnk)
                except:
                    pass

            except:
                print("This is a Video/Photo. No Content found!!")
                pass


def main():
    time.sleep(1)
    rssFeeds()
    global cnt
    cnt = 0
    # global driver
    # driver = webdriver.Firefox(firefox_binary=binary, capabilities=capabilities)
    time.sleep(1)
    for lnk in indialinks:
        NewsContent(lnk)
        cnt += 1
    driver.close()


try:
    main()
    print(len(indialinks))
except:
    tb_err = traceback.format_exc()
    error(tb_err)
    driver.close()
    pass