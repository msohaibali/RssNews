import feedparser
import traceback
import datetime
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support.ui import WebDriverWait
from pymongo import MongoClient
import dateutil.parser as parser
import arrow
import xml.etree.ElementTree as ET
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

pushto = []
pushto.append('http://feeds.bbci.co.uk/hindi/rss.xml')


def error(err):

    try:
        source = "BbcHindi News"
        time = datetime.datetime.now()
        time = time.isoformat()
        time = arrow.get(time).datetime
        collection3.insert([{"Error": err, "Source Name": source, "Time of Error": time, "Category": "International"}])
    except:
        pass


def rssFeeds():
    def parseRss(rss_url):
        return feedparser.parse(rss_url)

    def getLinks(rss_url):
        links = []
        feed = parseRss(rss_url)
        for newsitem in feed['items']:
            links.append(newsitem['link'])
            try:
                publishedTime.append(newsitem['updated'])
            except:
                pass
        return links

    global pushtolinks
    pushtolinks = []
    global publishedTime
    publishedTime = []
    for p in pushto:
        pushtolinks.extend(getLinks(p))
        print(p)


def getTarget(tg):
    driver.get(tg)


def autoscroll():
    lastHeight = driver.execute_script("return document.body.scrollHeight")
    while 1:
         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
         newHeight = driver.execute_script("return document.body.scrollHeight")
         if newHeight == lastHeight:
             break
         lastHeight = newHeight


def implicitwait(timeout):
     WebDriverWait(driver, timeout)

data = []
data.append(collection1.distinct('_id'))


def NewsContent(lnk):
    title = ''
    art = ''

    for d1 in data:
        for index in range(0, len(d1)):
            if d1[index] == lnk:
                print(d1[index])
                art = "True"
                break
            else:
                art = "False"

        if art == "True":
            print("No Result Found")
        else:
            print("new Results Found")

            getTarget(lnk)
            implicitwait(20)
            time.sleep(3)
            print(lnk)
            soup = BeautifulSoup(driver.page_source, "html.parser")

            try:
                try:

                    p_content1 = ''
                    curr_post = soup.find('div', attrs={'class': 'story-inner'})
                    targ_p = curr_post.find_all('h1')
                    for p in targ_p:
                        p_content1 = p_content1 + p.text

                    title = p_content1
                    print(title)

                except:
                    p_content1 = ''
                    curr_post = soup.find('div', attrs={'class': 'story-body'})
                    targ_p = curr_post.find_all('h1')
                    for p in targ_p:
                        p_content1 = p_content1 + p.text

                    title = p_content1
                    print(title)

            except:
                print("Didn't found the class")
                pass

            try:
                try:
                    p_content = ''
                    curr_post = soup.find('div', attrs={'class': 'story-body__inner'})
                    targ_p = curr_post.find_all('p')
                    for p in targ_p:
                        p_content = p_content + p.text

                    body = p_content
                    body = body.replace(
                        "(बीबीसी हिन्दी के एंड्रॉएड ऐप के लिए आप यहां क्लिक कर सकते हैं. आप हमें फ़ेसबुक और ट्विटर पर फ़ॉलो भी कर सकते हैं.)",
                        "")
                    print(body)

                except:
                    p_content = ''
                    curr_post = soup.find('div', attrs={'class': 'story-body'})
                    targ_p = curr_post.find_all('p')
                    for p in targ_p:
                        p_content = p_content + p.text

                    body = p_content
                    body = body.replace("(बीबीसी हिन्दी के एंड्रॉएड ऐप के लिए आप यहां क्लिक कर सकते हैं. आप हमें फ़ेसबुक और ट्विटर पर फ़ॉलो भी कर सकते हैं.)","")
                    print(body)

                date = parser.parse(publishedTime[cnt])
                publishedTime[cnt] = date.isoformat()
                publishedTime[cnt] = arrow.get(publishedTime[cnt]).datetime
                print(publishedTime[cnt])

                collection1.insert([{"Type": "Predefined List", "Category": "International", "Language": "Hindi",
                                     "Source": "BBC Hindi", "title": title, "body": body, "_id": lnk ,
                                     "published Time": publishedTime[cnt]}])

                r.rpush('news_link', lnk)
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
    for lnk in pushtolinks:
        NewsContent(lnk)
        cnt += 1
    driver.close()


try:
    main()
    print(len(pushtolinks))
except:
    tb_err = traceback.format_exc()
    error(tb_err)
    driver.close()
    pass
