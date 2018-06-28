import traceback
from pymongo import MongoClient
import arrow
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

pushto = []
pushto.append('http://feeds.bbci.co.uk/urdu/rss.xml')

junk = "اس پوسٹ کو شیئر کریںای میلفیس بکMessengerMessengerٹوئٹرگوگل پلسوٹس ایپاس لنک کو کاپی کیجیےیہ بیرونی لنک ہیں جو ایک نئی ونڈو میں کُھلیں گے"


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


def error(err):

    try:
        source = "BbcUrdu News"
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

data = []
data.append(collection1.distinct('_id'))


def NewsContent(lnk):
    ut = ''
    title = ''
    for d6 in data:

        for index in range(0, len(d6)):
            if d6[index] == lnk:
                print(d6[index])
                ut = "True"
                break
            else:
                ut = "False"

        if ut == "True":
            print("No Result Found")
        else:
            print("new Results Found")
            getTarget(lnk)
            print(lnk)
            implicitwait(10)
            time.sleep(5)
            soup = BeautifulSoup(driver.page_source, "html.parser")

            try:
                try:
                    p_content1 = ''
                    curr_post = soup.find('div', attrs={'class': ['story-inner','story-body']})
                    targ_p = curr_post.find_all('h1')
                    for p in targ_p:
                        p_content1 = p_content1 + p.text

                    title = p_content1
                    print(title)
                except:
                    p_content1 = ''
                    curr_post = soup.find('div', attrs={'class': 'gallery-intro'})
                    targ_p = curr_post.find_all('h1')
                    for p in targ_p:
                        p_content1 = p_content1 + p.text

                    title = p_content1
                    print(title)

                try:
                    dateDiv = soup.find('div', attrs={'class': ['date date--v2','date date--v2 relative-time']})
                    val = dateDiv['data-seconds']
                    global pubTime
                    pubTime = datetime.datetime.utcfromtimestamp(float(val)).strftime('%Y-%m-%d %H:%M:%S')
                    print(pubTime)
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
                    curr_post = soup.find('div', attrs={'class': ['story-body__inner', 'story-body']})
                    targ_p = curr_post.find_all('p')
                    for p in targ_p:
                        p_content = p_content + p.text
                    body = p_content

                except:
                    p_content = ''
                    curr_post = soup.find('div', attrs={'class': 'gallery'})
                    targ_p = curr_post.find_all('p')
                    for p in targ_p:
                        p_content = p_content + p.text
                    body = p_content

                body = body.replace(junk, "")
                print(body)

                try:
                    collection1.insert([{"Type": "Predefined List", "Category": "International", "Language": "Urdu",
                                         "published Time": pubTime, "Source": "BBC Urdu", "title": title, "body": body,
                                         "_id": lnk}])
                    r.rpush('news_link', lnk)
                except:
                    pass
            except:
                print("Didn't found the class")
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
    print(len(pushtolinks))
except:
    tb_err = traceback.format_exc()
    error(tb_err)
    driver.close()
    pass
