import traceback
import datetime
import redis
import feedparser
import time
import xml.etree.ElementTree as ET
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from pymongo import MongoClient
import dateutil.parser as parser
import arrow

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

driver = webdriver.Firefox()


def error(err):

    try:
        source = "CNN News"
        time = datetime.datetime.now()
        time = time.isoformat()
        time = arrow.get(time).datetime
        collection3.insert([{"Error": err, "Source Name": source, "Time of Error": time, "Category": "International"}])
    except:
        pass


fox = []
fox.append('http://rss.cnn.com/rss/edition_world.rss')
publishTime = []


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

    global foxlinks
    foxlinks = []
    global publishedTime
    publishedTime = []
    for f in fox:
        foxlinks.extend(getLinks(f))
        print(f)


def getTarget(tg):
    driver.get(tg)


def implicitwait(timeout):
    WebDriverWait(driver, timeout)


data = []
data.append(collection1.distinct('_id'))


def NewsContent(lnk):
    art = ''
    title = ''
    body = ''
    pubtime = ''
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
            print(lnk)
            implicitwait(20)
            time.sleep(5)

            try:

                try:
                    targ_p = driver.find_element_by_xpath("//div/h1")
                    title = title + targ_p.text
                except:
                    pass

                try:
                    p_content = ''
                    targ_p = driver.find_elements_by_xpath('//div[@id = "storytext"]/p')
                    for p in targ_p:
                        p_content = p_content + p.text

                    body = body + p_content

                except:
                    pass

                if body is '':
                    p_content = ''
                    try:
                        targ_p = driver.find_elements_by_xpath('//div[@class="zn-body__read-all"]/div')
                        for p in targ_p:
                            p_content = p_content + p.text

                        body = body + p_content
                    except:
                        pass

                if title is '':
                    try:
                        targ_p = driver.find_element_by_css_selector('h1.media__video-headline')
                        title = title + targ_p.text
                    except:
                        pass

                if body is '':
                    p_content = ''
                    try:
                        targ_p = driver.find_elements_by_xpath('//div[@class="media__video-description media__video-description--inline"]')
                        for p in targ_p:
                            p_content = p_content + p.text
                        body = body + p_content
                    except:
                        pass

                if title is '':
                    try:
                        targ_p = driver.find_element_by_xpath('//*[@id="headline"]')
                        title = title + targ_p.text
                    except:
                        pass

                if body is '':
                    p_content = ''
                    try:
                        targ_p = driver.find_elements_by_xpath('//div[@id="content"]/p')
                        for p in targ_p:
                            p_content = p_content + p.text
                        body = body + p_content
                    except:
                        pass

                if body is '':
                    p_content = ''
                    try:
                        targ_p = driver.find_elements_by_xpath('//p/span')
                        for p in targ_p:
                            p_content = p_content + p.text
                        body = body + p_content
                    except:
                        pass

                if title is '':
                    try:
                        targ_p = driver.find_element_by_xpath('//div[@class="el__video-collection__meta-wrapper"]/h1')
                        title = title + targ_p.text
                    except:
                        pass

                if pubtime is '':
                    try:
                        date = parser.parse(publishedTime[cnt])
                        publishedTime[cnt] = date.isoformat()
                        publishedTime[cnt] = arrow.get(publishedTime[cnt]).datetime
                        pubtime = publishedTime[cnt]

                    except:
                        pass

                if pubtime is '':
                     date = datetime.datetime.now()
                     pubtime = date.isoformat()
                     pubtime = arrow.get(pubtime).datetime

                try:
                    title = title.replace("\n                                    ", "")
                    title = title.replace("                                    ", "")
                    title = title.replace("\n", "")
                    body = body.replace("\n                                    ", "")
                    body = body.replace("                                    ", "")
                    body = body.replace("\n", "")
                except:
                    pass

                print(title)
                print(body)

                print(pubtime)

                if title is '':
                    print("This is a Photo or Video, Content doesnot Exists!")

                elif body is '':
                    print("This is a Photo or Video, Content doesnot Exists!")

                else:
                    collection1.insert([{"Type": "Predefined", "Category": "International", "Language": "English", "Source": "CNN",
                                         "title": title, "body": body, "_id": lnk, "published Time": pubtime}])
                    r.rpush('news_link', lnk)

            except Exception as ex:
                print(ex)
                print("Its a Video!!!")
                pass


def main():
    time.sleep(1)
    rssFeeds()
    global cnt
    cnt = 0
    time.sleep(2)
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
