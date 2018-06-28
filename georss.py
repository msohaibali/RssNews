import datetime
import traceback
import arrow
from pymongo import MongoClient
import xml.etree.ElementTree as ET
import feedparser
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support.ui import WebDriverWait
import dateutil.parser as parser
import redis
import time

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

geo = []
geo.append('https://www.geo.tv/rss/1/2')


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

    global geolinks
    geolinks = []
    global publishedTime
    publishedTime = []

    for g in geo:
        geolinks.extend(getLinks(g))
        publishedTime.extend(getTime(g))
        print(g)


def getTarget(tg):
    driver.get(tg)


def implicitwait(timeout):
    WebDriverWait(driver, timeout)

data = []
data.append(collection1.distinct('_id'))


def error(err):

    try:
        source = "Geo News"
        time = datetime.datetime.now()
        time = time.isoformat()
        time = arrow.get(time).datetime
        collection3.insert([{"Error": err, "Source Name": source, "Time of Error": time, "Category": "National"}])
    except:
        pass


def NewsContent(lnk):
    title = ''
    it = ''
    for d3 in data:
        for index in range(0, len(d3)):
            if d3[index] == lnk:
                print(d3[index])
                it = "True"
                break
            else:
                it = "False"

        if it == "True":
            print("No Result Found")
        else:
            print("new Results Found")

            getTarget(lnk)
            implicitwait(10)
            time.sleep(5)
            soup = BeautifulSoup(driver.page_source, "html.parser")

            try:
                p_content1 = ''
                curr_post = soup.find('div', attrs={'class': 'story-area'})
                targ_p = curr_post.find_all('h1')
                for p in targ_p:
                    p_content1 = p_content1 + p.text

                title = p_content1
                print(title)

            except:
                print("Didn't found the class")
                pass

            try:
                p_content = ''
                curr_post = soup.find('div', attrs={'class': 'content-area'})
                targ_p = curr_post.find_all('p')
                for p in targ_p:
                    p_content = p_content + p.text

                body = p_content
                print(body)

                date = parser.parse(publishedTime[cnt])
                publishedTime[cnt] = date.isoformat()
                publishedTime[cnt] = arrow.get(publishedTime[cnt]).datetime
                print(publishedTime[cnt])

                try:
                    collection1.insert([{"Type": "Predefined List", "Category": "National", "Language": "English",
                                         "Source": "Geo News", "title": title, "body": body, "_id": lnk,
                                         "published Time": publishedTime[cnt]}])
                    r.rpush('news_link', lnk)
                except:
                    pass

            except:
                print("Didn't found the class")
                pass


def main():
    rssFeeds()
    # global driver
    global cnt
    cnt = 0
    # driver = webdriver.Firefox(firefox_binary=binary, capabilities=capabilities)
    time.sleep(2)
    for lnk in geolinks:
        NewsContent(lnk)
        cnt += 1
    driver.close()


try:
    main()
    print(len(geolinks))
except:
    tb_err = traceback.format_exc()
    error(tb_err)
    driver.close()
    pass
