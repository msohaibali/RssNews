import arrow
import feedparser
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support.ui import WebDriverWait
from pymongo import MongoClient
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

pushto = []
url = "http://feeds.bbc.co.uk/persian/index.xml"
pushto.append(url)


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
    title = ''
    pubTime = ''
    pt = ''
    for d5 in data:
        for index in range(0, len(d5)):
            if d5[index] == lnk:
                print(d5[index])
                pt = "True"
                break
            else:
                pt = "False"

        if pt == "True":
            print("No Result Found")
        else:
            print("new Results Found")
            getTarget(lnk)
            implicitwait(10)
            time.sleep(5)
            soup = BeautifulSoup(driver.page_source, "html.parser")

            print(lnk)
            try:
                try:
                    try:
                        p_content1 = ''
                        curr_post = soup.find('div', attrs={'class': ['story-inner']})
                        targ_p = curr_post.find_all('h1')
                        for p in targ_p:
                            p_content1 = p_content1 + p.text

                        print(p_content1)
                        title = p_content1
                    except:
                        p_content1 = ''
                        curr_post = soup.find('div', attrs={'class': ['story-body']})
                        targ_p = curr_post.find_all('h1')
                        for p in targ_p:
                            p_content1 = p_content1 + p.text

                        print(p_content1)
                        title = p_content1

                except:
                    try:
                        p_content1 = ''
                        curr_post = soup.find('div', attrs={'class': ['gallery-intro']})
                        targ_p = curr_post.find_all('h1')
                        for p in targ_p:
                            p_content1 = p_content1 + p.text

                        print(p_content1)
                        title = p_content1

                    except:
                        driver.get(lnk)

                        try:
                            p_content1 = ''
                            targ_p = driver.find_element_by_xpath('//[@id="page"]//h1//font')
                            for p in targ_p:
                                p_content1 = p_content1 + p.text

                            print(p_content1)
                            title = p_content1
                        except:
                            p_content1 = ''
                            targ_p = driver.find_element_by_xpath('//*[@id="page"]//div//div[2]//div[1]//div//div[1]//h1//font//font')
                            for p in targ_p:
                                p_content1 = p_content1 + p.text

                            print(p_content1)
                            title = p_content1

                try:
                    dateDiv = soup.find('div', attrs={'class': 'date date--v2'})
                    val = dateDiv['data-seconds']

                    pubTime = datetime.datetime.utcfromtimestamp(float(val)).strftime('%Y-%m-%d %H:%M:%S')
                    date = parser.parse(pubTime)
                    pubTime = date.isoformat()
                    pubTime = arrow.get(pubTime).datetime

                except:
                    pass

            except Exception as ex:
                print(ex)
                pass

            try:
                try:
                    p_content = ''
                    curr_post = soup.find('div', attrs={'class': ['story-body' , 'story-body__inner']})
                    targ_p = curr_post.find_all('p')
                    for p in targ_p:
                        p_content = p_content + p.text
                    body = p_content
                    body = body.replace("همرسانی درایمیلفیسبوکMessengerMessengerتوییترگوگل +بالاترینواتس‌اپلینک را کپی کنیداین لینک‌ها خارج از بی‌بی‌سی است و در یک پنجره جدید باز می‌شود","")
                    print(body)
                except:
                    p_content = ''
                    curr_post = soup.find('div', attrs={'class': ['gallery']})
                    targ_p = curr_post.find_all('p')
                    for p in targ_p:
                        p_content = p_content + p.text
                    body = p_content
                    body = body.replace("همرسانی درایمیلفیسبوکMessengerMessengerتوییترگوگل +بالاترینواتس‌اپلینک را کپی کنیداین لینک‌ها خارج از بی‌بی‌سی است و در یک پنجره جدید باز می‌شود","")
                    print(body)

                if title is '':
                    print("This is a Photo or Video, Content doesnot Exists!")

                elif body is '':
                    print("This is a Photo or Video, Content doesnot Exists!")

                elif pubTime is '':
                    print("This is a Photo or Video, Content doesnot Exists!")

                else:
                    try:
                        collection1.insert([{"Type": "Predefined List", "Category": "International", "Language": "Persian",
                                             "published Time": pubTime, "Source": "BBC Persian", "title": title, "body": body,
                                             "_id": lnk}])
                        r.rpush('news_link', lnk)
                        print(pubTime)
                    except:
                        pass

            except:
                print("Didnot found the class")
                pass


def main():
    rssFeeds()
    # global driver
    # driver = webdriver.Firefox(firefox_binary=binary, capabilities=capabilities)
    for lnk in pushtolinks:
        NewsContent(lnk)

    driver.close()


try:
    main()

except:
    driver.close()
    pass
