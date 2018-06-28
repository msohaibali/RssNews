import traceback
import arrow
from pymongo import MongoClient
import xml.etree.ElementTree as ET
import feedparser
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support.ui import WebDriverWait
import time
import datetime
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

english = []
english.append('http://feeds.bbci.co.uk/news/rss.xml')

junk = "Share this withEmailFacebookMessengerMessengerTwitterPinterestWhatsAppLinkedInCopy this linkThese are external links and will open in a new window"
junk1 = "\n                            Media playback is not supported on this device\n                        "


def rssFeeds():
    def parseRss(rss_url):
        return feedparser.parse(rss_url)

    def getLinks(rss_url):
        links = []
        feed = parseRss(rss_url)
        for newsitem in feed['items']:
            links.append(newsitem['link'])
        return links

    global englishlinks
    englishlinks = []
    for e in english:
        englishlinks.extend(getLinks(e))
        print(e)


def error(err):

    try:
        source = "BbcRss News"
        time = datetime.datetime.now()
        time = time.isoformat()
        time = arrow.get(time).datetime
        collection3.insert([{"Error": err, "Source Name": source, "Time of Error": time, "Category": "International"}])
    except:
        pass


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
    et = ''
    body = ''
    title = ''
    pubTime = ''
    for d9 in data:
        for index in range(0, len(d9)):
            if d9[index] == lnk:
                print(d9[index])
                et = "True"
                break
            else:
                et = "False"

        if et == "True":
            print("No Result Found")
        else:
            print("new Results Found")
            getTarget(lnk)
            print(lnk)
            time.sleep(3)
            soup = BeautifulSoup(driver.page_source, "html.parser")

            try:
                try:
                    try:
                        p_content1 = ''
                        curr_post = soup.find('div', attrs={'class': ['story-inner', 'story-body']})
                        targ_p = curr_post.find_all('h1')
                        for p in targ_p:
                            p_content1 = p_content1 + p.text

                        title = p_content1
                        # print(title)
                    except:
                        p_content1 = ''
                        curr_post = soup.find('div', attrs={'class': ['gel-layout__item gel-2/3@l ']})
                        targ_p = curr_post.find_all('h1')
                        for p in targ_p:
                            p_content1 = p_content1 + p.text

                        title = p_content1
                        # print(title)

                except:
                    try:
                        p_content1 = ''
                        curr_post = soup.find('div', attrs={'class': ['blog__story story-inner']})
                        targ_p = curr_post.find_all('h2')
                        for p in targ_p:
                            p_content1 = p_content1 + p.text

                        title = p_content1
                        # print(title)


                    except:
                        try:
                            p_content1 = ''
                            curr_post = soup.find('div', attrs={'class': ['vxp-media__body']})
                            targ_p = curr_post.find_all('h1')
                            for p in targ_p:
                                p_content1 = p_content1 + p.text

                            title = p_content1
                            # print(title)
                        except:
                            try:
                                p_content1 = ''
                                curr_post = soup.find('div', attrs={'class': ['gel-layout__item gel-4/12@l']})
                                targ_p = curr_post.find_all('h1')
                                for p in targ_p:
                                    p_content1 = p_content1 + p.text

                                title = p_content1
                                # print(title)
                            except:
                                p_content1 = ''
                                curr_post = soup.find('div', attrs={'class': ['gel-layout__item gel-2/3@l']})
                                targ_p = curr_post.find_all('h1')
                                for p in targ_p:
                                    p_content1 = p_content1 + p.text

                                title = p_content1
                                # print(title)

                try:
                    dateDiv = soup.find('div', attrs={'class': ['date date--v2','date date--v2 relative-time']})
                    val = dateDiv['data-seconds']

                    pubTime = datetime.datetime.utcfromtimestamp(float(val)).strftime('%Y-%m-%d %H:%M:%S')
                    date = parser.parse(pubTime)
                    pubTime = date.isoformat()
                    pubTime = arrow.get(pubTime).datetime

                except:
                    try:
                        date_el = "mini-info-list__date vxp-date date date--v2 relative-time"
                        dateDiv = soup.find('div', attrs={'class': [date_el]})
                        val = dateDiv['data-seconds']

                        pubTime = datetime.datetime.utcfromtimestamp(float(val)).strftime('%Y-%m-%d %H:%M:%S')
                        date = parser.parse(pubTime)
                        pubTime = date.isoformat()
                        pubTime = arrow.get(pubTime).datetime

                    except:
                        try:
                            date_el = "timestamp"
                            dateDiv = soup.find('span', attrs={'class': [date_el]})
                            val = dateDiv['data-timestamp']

                            pubTime = datetime.datetime.utcfromtimestamp(float(val)).strftime('%Y-%m-%d %H:%M:%S')
                            date = parser.parse(pubTime)
                            pubTime = date.isoformat()
                            pubTime = arrow.get(pubTime).datetime


                        except:

                            date_el = "mini-info-list__date vxp-date date date--v2"
                            dateDiv = soup.find('div', attrs={'class': [date_el]})
                            val = dateDiv['data-seconds']

                            pubTime = datetime.datetime.utcfromtimestamp(float(val)).strftime('%Y-%m-%d %H:%M:%S')
                            date = parser.parse(pubTime)
                            pubTime = date.isoformat()
                            pubTime = arrow.get(pubTime).datetime
            except:
                print("Didn't found the class")
                pass

            try:
                try:
                    p_content = ''
                    curr_post = soup.find('div', attrs={'class': ['story-body__inner', 'story-body']})
                    targ_p = curr_post.find_all('p')
                    for p in targ_p:
                        p_content = p_content + p.text

                    body = p_content
                    body = body.replace(junk,"")
                    # print(body)

                except:
                    try:
                        p_content = ''
                        curr_post = soup.find('div', attrs={'class': ['vxp-media__summary']})
                        targ_p = curr_post.find_all('p')
                        for p in targ_p:
                            p_content = p_content + p.text

                        body = p_content
                        body = body.replace(junk,"")
                        # print(body)

                    except:
                        p_content = ''
                        curr_post = soup.find('div', attrs={'class': ['gel-body-copy sp-c-media-collection_body-copy']})
                        targ_p = curr_post.find_all('p')
                        for p in targ_p:
                            p_content = p_content + p.text

                        body = p_content
                        body = body.replace(junk,"")
                        # print(body)

                        date_el = "gs-c-item-status__text"
                        dateDiv = soup.find('span', attrs={'class': [date_el]})
                        val = dateDiv.find('time')
                        val = val.text

                        date = parser.parse(val)
                        pubTime = date.isoformat()
                        pubTime = arrow.get(pubTime).datetime

                # print(pubTime)

                if title is '':
                    try:
                        p_content1 = ''
                        curr_post = soup.find('div', attrs={'class': ['gel-layout__item gel-2/3@l']})
                        targ_p = curr_post.find_all('h1')
                        for p in targ_p:
                            p_content1 = p_content1 + p.text

                        title = p_content1
                        # print(title)

                        try:
                            dateDiv = soup.find('span', attrs={'class': ['timestamp']})
                            val = dateDiv.find('time')
                            val = val['data-timestamp']

                            pubTime = datetime.datetime.utcfromtimestamp(float(val)).strftime('%Y-%m-%d %H:%M:%S')
                            date = parser.parse(pubTime)
                            pubTime = date.isoformat()
                            pubTime = arrow.get(pubTime).datetime

                            # print(pubTime)

                        except:
                            dateDiv = soup.find('li', attrs={'class': ['mini-info-list__item']})
                            val = dateDiv.find('div')
                            val = val['data-seconds']

                            pubTime = datetime.datetime.utcfromtimestamp(float(val)).strftime('%Y-%m-%d %H:%M:%S')
                            date = parser.parse(pubTime)
                            pubTime = date.isoformat()
                            pubTime = arrow.get(pubTime).datetime

                            # print(pubTime)

                    except:
                        print("It is a Newspaper, No Content Found!")

                elif title is 'BBC News Channel':
                    print("It is a Video, No Content Found!")

                elif body is 'BBC News Channel':
                    print("It is a Video, No Content Found!")

                elif pubTime is '':
                    print("Date of this link is not valid!!")

                else:
                    print(title)
                    body = body.replace(junk1, "")
                    body = body.replace("\n", "")
                    print(body)
                    print(pubTime)
                    try:
                        collection1.insert([{"Type": "Predefined List", "Category": "International", "Language": "English",
                                             "published Time": pubTime, "Source": "BBC English", "title": title, "body": body,
                                             "_id": lnk}])
                        r.rpush('news_link', lnk)

                    except:
                        print("Issues in Data Dumping")
                        pass

            except:
                print("Didn't found the class")
                pass


def main():
    rssFeeds()
    # global driver
    # driver = webdriver.Firefox(firefox_binary=binary, capabilities=capabilities)
    time.sleep(1)
    for lnk in englishlinks:
        NewsContent(lnk)
    driver.close()


try:
    main()
    print(len(englishlinks))
except:
    tb_err = traceback.format_exc()
    error(tb_err)
    driver.close()
    pass
