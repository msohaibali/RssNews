import traceback
import datetime
import feedparser
import time
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support.ui import WebDriverWait
from pymongo import MongoClient
import dateutil.parser as parser
import redis
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


def error(err):

    try:
        source = "LA Times"
        time = datetime.datetime.now()
        time = time.isoformat()
        time = arrow.get(time).datetime
        collection3.insert([{"Error": err, "Source Name": source, "Time of Error": time, "Category": "International"}])
    except:
        pass


fox = []
fox.append('http://www.latimes.com/rss2.0.xml')


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


def getTarget(tg):
    driver.get(tg)


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
                # TITLE / HEADER
                try:
                    try:
                        p_content1 = ''
                        curr_post = soup.find('div', attrs={'class': 'card-content align-left'})
                        targ_p = curr_post.find_all('h1')

                        for div in targ_p:
                            p_content1 = p_content1 + div.text

                        title = p_content1
                        print(title)

                    except:
                        p_content1 = ''
                        curr_post = soup.find('div', attrs={'class': 'card-content align-center'})
                        targ_p = curr_post.find_all('h1')

                        for div in targ_p:
                            p_content1 = p_content1 + div.text

                        title = p_content1
                        print(title)

                except:
                    p_content1 = ''
                    curr_post = soup.find('header', attrs={'class': 'dark-theme mobile-drop'})
                    targ_p = curr_post.find_all('h2')

                    for div in targ_p:
                        p_content1 = p_content1 + div.text

                    targ_p = curr_post.find_all('h1')

                    for div in targ_p:
                        p_content1 = p_content1 + div.text

                    title = p_content1
                    print(title)

                    try:
                        p_content1 = ''
                        curr_post = soup.find('div', attrs={'class': 'width-100 flex-container-column'})
                        targ_p = curr_post.find_all('h3')

                        for div in targ_p:
                            p_content1 = p_content1 + div.text

                        title = p_content1
                        print(title)

                    except:
                        print("Title not found because its a Video!")
                        pass

            except:
                print("This is not a Story its a Video!")
                pass

            # BODY
            try:
                try:
                    p_content = ''
                    curr_post = soup.find('div', attrs={'class':'collection collection-cards'})
                    targ_p = curr_post.find_all('p')
                    for p in targ_p:
                        p_content = p_content + p.text

                    body = p_content
                    print(body)

                except:
                    try:
                        p_content = ''
                        curr_post = soup.find('div', attrs={'class': 'card-content'})
                        targ_p = curr_post.find_all('p')
                        for p in targ_p:
                            p_content = p_content + p.text

                        body = p_content
                        print(body)

                    except:
                        p_content = ''
                        curr_post = soup.find('div', attrs={'class': 'container'})
                        targ_p = curr_post.find_all('p')
                        for p in targ_p:
                            p_content = p_content + p.text

                        body = p_content
                        print(body)

                date = parser.parse(publishedTime[cnt])
                publishedTime[cnt] = date.isoformat()
                publishedTime[cnt] = arrow.get(publishedTime[cnt]).datetime
                print(publishedTime[cnt])

                if title is '':
                    print("This is a Photo or Video, Content doesnot Exists!")

                elif body is '':
                    print("This is a Photo or Video, Content doesnot Exists!")

                else:
                    collection1.insert([{"Type": "Predefined List", "Category": "International", "Language": "English",
                                         "Source": "Los Angeles Times", "title": title, "body": body, "_id": lnk,
                                         "published Time": publishedTime[cnt]}])

                    r.rpush('news_link', lnk)
            except:
                print("This is not a Story its a Video!")
                pass


def main():
    time.sleep(1)
    rssFeeds()
    # global driver
    global cnt
    cnt = 0
    # driver = webdriver.Firefox(firefox_binary=binary, capabilities=capabilities)
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