import traceback
import datetime
import arrow
from pymongo import MongoClient
import xml.etree.ElementTree as ET
import feedparser
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support.ui import WebDriverWait
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

Client = MongoClient(dbIP)
# Client = MongoClient(shardIP)
db = Client[db]
db.authenticate(user1, password1)
collection1 = db[collName]
collection3 = db[errCollName]
r = redis.StrictRedis(host=rIP, port=rPort)

# binary = FirefoxBinary('/usr/local/desktop/firefox')
# capabilities = webdriver.DesiredCapabilities().FIREFOX
# capabilities["-marionette"] = False
# binary = FirefoxBinary(r'/usr/bin/firefox')

# driver = webdriver.Firefox(firefox_binary=binary, capabilities=capabilities)

driver = webdriver.Firefox()
fox = []
fox.append('https://www.cnbc.com/id/100003114/device/rss/rss.html')


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

    global foxlinks
    foxlinks = []
    global publishedTime
    publishedTime = []
    for f in fox:
        foxlinks.extend(getLinks(f))
        publishedTime.extend(getTime(f))
        print(f)


def error(err):

    try:
        source = "Cnbc News"
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
    cnbt = ''
    title = ''
    for d1 in data:
        for index in range(0, len(d1)):
            if d1[index] == lnk:
                print(d1[index])
                cnbt = "True"
                break
            else:
                cnbt = "False"

        if cnbt == "True":
            print("No Result Found")
        else:
            print("new Results Found")
            getTarget(lnk)
            print(lnk)
            time.sleep(3)
            soup = BeautifulSoup(driver.page_source, "html.parser")

            try:
                try:
                    p_content1 = ''
                    curr_post = soup.find('div', attrs={'class': 'story-header-left twoCol'})
                    targ_p = curr_post.find_all('h1')
                    for p in targ_p:
                        p_content1 = p_content1 + p.text

                    title = (p_content1)
                    print(title)

                except:
                    curr_post = soup.find('div', attrs={'class': 'story-top'})
                    targ_p = curr_post.find('h1', attrs={'class': 'title'})
                    title = targ_p.text
                    print(title)

            except:
                print("Didn't found the class")
                pass

            try:
                p_content = ''
                curr_post = soup.find('div', attrs={'class': 'cnbc-contents'})
                targ_p = curr_post.find_all('p')
                for p in targ_p:
                    p_content = p_content + p.text

                body = p_content
                body = body.replace("For more insight from CNBC contributors, follow \n\n@CNBCopinion\n\n on Twitter.PlayingShare this video...Watch Next...","")
                body = body.replace("on Twitter.PlayingShare this video...Watch Next...","")
                body = body.replace("@CNBCopinion","")
                body = body.replace("\n","")
                print(body)
                date = parser.parse(publishedTime[cnt])
                publishedTime[cnt] = date.isoformat()
                publishedTime[cnt] = arrow.get(publishedTime[cnt]).datetime
                print(publishedTime[cnt])

                try:
                    collection1.insert([{"Type": "Predefined List", "Category": "International", "Language": "English",
                                         "Source": "CNBC", "title": title, "body": body, "_id": lnk,
                                         "published Time": publishedTime[cnt]}])
                    r.rpush('news_link', lnk)
                except:
                    pass

            except:
                print("Didn't found the class")
                pass


def main():
    time.sleep(1)
    rssFeeds()
    global cnt
    cnt = 0
    # global driver
    # driver = webdriver.Firefox(firefox_binary=binary, capabilities=capabilities)
    time.sleep(1)
    for lnk in foxlinks:
        NewsContent(lnk)
        cnt += 1
    driver.close()


try:
    main()
    print(len(foxlinks))
except:
    tb_err = traceback.format_exc()
    error(tb_err)
    driver.close()
    pass
