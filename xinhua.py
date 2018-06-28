import traceback
import datetime
from pymongo import MongoClient
import xml.etree.ElementTree as ET
import feedparser
import arrow
import time
import dateutil.parser as parser
import redis
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

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


def error(err):

    try:
        source = "Xinhua News"
        time = datetime.datetime.now()
        time = time.isoformat()
        time = arrow.get(time).datetime
        collection3.insert([{"Error": err, "Source Name": source, "Time of Error": time, "Category": "International"}])
    except:
        pass


pushto = []
pushto.append('http://www.xinhuanet.com/overseas/news_overseas.xml')


def rssFeeds():

    def parseRss(rss_url):
        return feedparser.parse(rss_url)

    def getLinks(rss_url):
        links = []
        feed = parseRss(rss_url)
        for newsitem in feed['items']:
            links.append(newsitem['link'])
        return links

    global pushtolinks
    pushtolinks = []
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


def NewsContent(lnk):
    data = []
    data.append(collection1.distinct('_id'))
    pubTime = ''
    title = ''
    ct = ''
    for d8 in data:
        for index in range(0, len(d8)):
            if d8[index] == lnk:
                ct = "True"
                break
            else:
                ct = "False"

        if ct == "True":
            print("No Result Found")
        else:
            print("new Results Found")
            print (lnk)
            getTarget(lnk)
            implicitwait(10)
            time.sleep(5)
            soup = BeautifulSoup(driver.page_source, "html.parser")

            try:
                dateDiv = soup.find('span', attrs={'class': 'h-time'})
                val = dateDiv.text
                date = parser.parse(val)
                pubTime = date.isoformat()
                pubTime = arrow.get(pubTime).datetime

                try:
                    curr_post = soup.find('div', attrs={'class': 'h-title'})
                    title = curr_post.text
                    title = title.replace("\n", "")
                    print(title)

                except:
                    try:
                        targ_p = soup.find('div', attrs={'class': 'h-title'})
                        next_tag = targ_p.find('font')
                        curr_post = next_tag.find('font')
                        title = curr_post.text
                        title = title.replace("\n", "")
                        print(title)
                    except:
                        print("Issue in Date/Title!")

            except:
                pass

            try:
                try:
                    p_content = ''
                    curr_post = soup.find('div', attrs={'id': 'p-detail'})
                    targ_p = curr_post.find_all('p')
                    for p in targ_p:
                        p_content = p_content + p.text

                    body = p_content
                    body = body.replace("\n", "")
                    body = body.replace("　　", "")
                    print(body)

                except:
                    p_content = ''
                    curr_post = soup.find('div', attrs={'id': 'p-detail'})
                    targ_p = curr_post.find_all('p')
                    for p in targ_p:
                        targ_p1 = p.find('font')
                        targ_p2 = targ_p1.find('font')
                        p_content = p_content + targ_p2.text

                    body = p_content
                    body = body.replace("\n", "")
                    body = body.replace("　　", "")
                    print(body)

                if title is '':
                    print("This is a Photo or Video, Content doesnot Exists!")

                elif body is '':
                    print("This is a Photo or Video, Content doesnot Exists!")

                else:
                    collection1.insert([{"Type": "Predefined List", "Category": "International", "Language": "Chinese",
                                         "published Time": pubTime, "Source": "Xinhua News", "title": title, "body": body,
                                         "_id": lnk}])
                    r.rpush('news_link', lnk)

                print("Publish Date: ", pubTime)

            except:
                print("Didn't found the class")
                pass


def main():
    rssFeeds()
    global driver
    driver = webdriver.Firefox()
    time.sleep(2)
    for lnk in pushtolinks:
        NewsContent(lnk)
    driver.close()


try:
    main()
    print(len(pushtolinks))
except:
    tb_err = traceback.format_exc()
    error(tb_err)
    driver.close()
    pass
