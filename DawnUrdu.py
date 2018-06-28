import traceback
import arrow
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from pymongo import MongoClient
import xml.etree.ElementTree as ET
from selenium.webdriver.support.ui import WebDriverWait
import time
import dateutil.parser as parser
import redis
import datetime
from googletrans import Translator

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

# Tags of Main Page Links
tag1 = "box  story    mb-4  pb-1  border--bottom"
tag2 = "box  story    mb-5"
tag3 = "box  story    mb-4  border--bottom  pb-4"



def error(err):

    try:
        source = "Dawn News Urdu"
        time = datetime.datetime.now()
        time = time.isoformat()
        time = arrow.get(time).datetime
        collection3.insert([{"Error": err, "Source Name": source, "Time of Error": time, "Category": "National"}])
    except:
        pass


def implicitwait(timeout):
    WebDriverWait(driver, timeout)


foxlinks = []

data = []
data.append(collection1.distinct('_id'))


def NewsContent(lnk):
    wqt = ''
    body = ''
    title = ''
    for d26 in data:
        for index in range(0, len(d26)):
            if d26[index] == lnk:
                print(d26[index])
                wqt = "True"
                break
            else:
                wqt = "False"

        if wqt == "True":
            print("This Link Already Exists")
        else:
            print("New Results Found")
            driver.get(lnk)
            time.sleep(3)
            print(lnk)
            soup = BeautifulSoup(driver.page_source, "html.parser")

            try:
                curr_post = driver.find_element_by_xpath('//html//body//div[2]//div//div[1]//main//div//div//article//div[1]//div//div[1]//h2//a')
                p_content1 = curr_post.text

                title = p_content1
                print(title)
            except:
                try:
                    curr_post = driver.find_element_by_xpath('//div//h2//a')
                    p_content1 = curr_post.text

                    title = p_content1
                    print(title)

                except:
                    print("Didn't found the Title")
                    pass

            try:
                p_content = ''
                curr_post1 = driver.find_element_by_xpath('//html//body//div[2]//div//div[1]//main//div//div//article//div[1]//div//div[2]//div')
                targ_p1 = curr_post1.find_elements_by_xpath('//p')

                for p in targ_p1:
                    p_content = p_content + p.text

                body = p_content
                body = body.replace("\n", "")
                body = body.replace("کاپی رائٹ © 2018","")

                print(body)

            except:
                try:
                    p_content = ''
                    curr_post1 = soup.find('div', attrs={'class': 'story__content          pt-0  pt-sm-4'})
                    targ_p1 = curr_post1.find_all('p')

                    for p in targ_p1:
                        p_content = p_content + p.text

                    body = p_content
                    body = body.replace("\n","")
                    body = body.replace("کاپی رائٹ © 2018","")
                    print(body)

                except:
                    try:
                        p_content = ''
                        curr_post1 = soup.find('div', attrs={'class': 'story__content size-six'})
                        targ_p1 = curr_post1.find_all('p')

                        for p in targ_p1:
                            p_content = p_content + p.text

                        body = p_content
                        body = body.replace("\n", "")
                        body = body.replace("کاپی رائٹ © 2018", "")
                        print(body)

                    except:
                        print("Didn't found Body")
                        pass

            try:
                # Grabbing DATE
                try:
                    global pubTime
                    dateDiv = driver.find_element_by_xpath('//html//body//div[2]//div//div[1]//main//div//div//article//div[1]//div//div[1]//div[1]//span[3]')
                    pubTime = dateDiv.text
                    pubTime = pubTime.replace("اپ ڈیٹ ","")
                    translator = Translator()
                    pubTime = translator.translate(pubTime)
                    pubTime = pubTime.text
                    t = datetime.datetime.now().time()
                    tim = t.strftime('%H:%M:%S.%f')
                    pubTime = pubTime + "T"+tim
                    date = parser.parse(pubTime)
                    pubTime = date.isoformat()
                    pubTime = arrow.get(pubTime).datetime
                    print("Published Date: ", pubTime)

                except:
                    try:
                        dateDiv = driver.find_element_by_xpath('//html//body//div[4]//div[2]//span[3]//span[2]')
                        pubTime = dateDiv.text
                        date = parser.parse(pubTime)
                        pubTime = date.isoformat()
                        pubTime = arrow.get(pubTime).datetime
                        print("Published Date: ", pubTime)

                    except:
                        print("Issue in DATE!!")
                        pass

                if title is '':
                    print("This is a Photo or Video, Content doesn't Exists!")

                elif body is '':
                    print("This is a Photo or Video, Content doesn't Exists!")

                else:
                    try:

                        collection1.insert([{"Type": "Predefined List", "Category": "National", "Language": "Urdu",
                                             "Source": "Dawn News Urdu", "title": title, "body": body, "_id": lnk,
                                             "published Time": pubTime}])
                        r.rpush('news_link', lnk)

                    except:
                        pass

            except:
                print ("Issues at Dumping Level")
                pass


# Function for grabbing News links
def get_results():


    try:
        # Grabbing Latest Link Tags
        try:
            url = "https://www.dawnnews.tv/latest-news"
            driver.get(url)
            links = driver.find_elements_by_xpath("//article[@class='box  story    mb-4  pb-1  border--bottom']//h2//a")

        except:
            links = driver.find_elements_by_xpath("//h2//a")

        for link in links:
            # Grabbing Links
            href = link.get_attribute("href")
            foxlinks.append(href)

        # Grabbing Health Tags
        try:
            url = "https://www.dawnnews.tv/health"
            driver.get(url)
            links = driver.find_elements_by_xpath("//article[@class='box  story    mb-5']//h2//a")

        except:
            links = driver.find_elements_by_xpath("//h2//a")

        for link in links:
            # Grabbing Links
            href = link.get_attribute("href")
            foxlinks.append(href)

        # Grabbing Extra Link Tags
        try:
            url = "https://www.dawnnews.tv/sport"
            driver.get(url)
            links = driver.find_elements_by_xpath("//article[@class='box  story    mb-4  border--bottom  pb-4']//h2//a")

        except:
            links = driver.find_elements_by_xpath("//h2//a")

        for link in links:
            # Grabbing Links
            href = link.get_attribute("href")
            foxlinks.append(href)

        # Grabbing Entertainment Tags https://www.dawnnews.tv/tech
        try:
            url = "https://www.dawnnews.tv/entertainment"
            driver.get(url)
            links = driver.find_elements_by_xpath("//article[@class='box  story    mb-4  border--bottom  pb-4']//h2//a")

        except:
            links = driver.find_elements_by_xpath("//h2//a")

        for link in links:
            # Grabbing Links
            href = link.get_attribute("href")
            foxlinks.append(href)

        # Grabbing Technology Tags
        try:
            url = "https://www.dawnnews.tv/tech"
            driver.get(url)
            links = driver.find_elements_by_xpath("//article[@class='box  story    mb-5']//h2//a")

        except:
            links = driver.find_elements_by_xpath("//h2//a")

        for link in links:
            # Grabbing Links
            href = link.get_attribute("href")
            foxlinks.append(href)

    except Exception as ex:
        print(ex)
        print("Issues in Links Grabbing")

    # Total number of Links Grabbed
    print("\nTotal Links Grabbed: ", len(foxlinks))


def main():

    time.sleep(1)
    get_results()

    for lnk in foxlinks:
        NewsContent(lnk)

    driver.close()


try:
    main()
    print(len(foxlinks))
except:
    tb_err = traceback.format_exc()
    error(tb_err)
    driver.close()
    pass
