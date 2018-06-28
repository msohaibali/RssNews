import traceback
import arrow
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from pymongo import MongoClient
import xml.etree.ElementTree as ET
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


def error(err):

    try:
        source = "Dunya News"
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
                curr_post = soup.find('h2', attrs={'class': 'page-title'})
                p_content1 = curr_post.text

                title = p_content1
                print(title)

            except:
                print("Didn't found the class1")
                pass

            try:
                p_content = ''
                curr_post = soup.find('div', attrs={'class': 'post_content'})
                targ_p = curr_post.find_all('p')
                for p in targ_p:
                    p_content = p_content + p.text

                body = p_content
                body = body.replace("\n", "")
                body = body.replace("(Dunya News) – ", "")
                body = body.replace("For more on this, watch a report by Dunya News below. ", "")
                body = body.replace("(Online) - ", "")
                body = body.replace("(Web Desk) – ", "–")
                body = body.replace("(Web Desk) - ", "")
                body = body.replace("(Reuters) - ", "")
                body = body.replace("(Web Desk) - ", "")
                body = body.replace("(AFP) -", "")
                print(body)

                # Grabbing DATE
                try:
                    global pubTime
                    dateDiv = soup.find('div', attrs={'class': 'post_date'})
                    pubTime = dateDiv.text
                    pubTime = pubTime.replace(" 	Last Updated On  ", "")
                    date = parser.parse(pubTime)
                    pubTime = date.isoformat()
                    pubTime = arrow.get(pubTime).datetime
                    print("Published Date: ", pubTime)

                except:
                    print("Issue in DATE!!")
                    pass

                if title is '':
                    print("This is a Photo or Video, Content doesnot Exists!")

                elif body is '':
                    print("This is a Photo or Video, Content doesnot Exists!")

                else:
                    try:

                        collection1.insert([{"Type": "Predefined List", "Category": "National", "Language": "English",
                                             "Source": "Dunya News", "title": title, "body": body, "_id": lnk,
                                             "published Time": pubTime}])
                        r.rpush('news_link', lnk)

                    except:
                        pass

            except:
                print("Didn't found the class")
                pass


# Function for grabbing News links
def get_results():
    url = "http://dunyanews.tv/en/home"
    driver.get(url)

    try:
        # Grabbing Link Tags
        try:
            links = driver.find_elements_by_xpath("//div[@class='edwn']//h2//a")

        except:
            links = driver.find_elements_by_xpath("//h2//a")

        for link in links:
            # Grabbing Links
            href = link.get_attribute("href")
            foxlinks.append(href)

        # Grabbing Headline Tags
        try:
            links = driver.find_elements_by_xpath("//div[@class='ovrtexts']//a")

        except:
            links = driver.find_elements_by_xpath("//a")

        for link in links:
            # Grabbing Links
            href = link.get_attribute("href")
            foxlinks.append(href)

        # Grabbing Extra Link Tags
        try:
            links = driver.find_elements_by_xpath("//div[@class='featurt']//p//a")

        except:
            links = driver.find_elements_by_xpath("//p//a")

        for link in links:
            # Grabbing Links
            href = link.get_attribute("href")
            foxlinks.append(href)

            # Grabbing 3rd Extra Link Tags
            try:
                links = driver.find_elements_by_xpath("//div[@class='post-content']//div//a")

            except:
                links = driver.find_elements_by_xpath("//div//a")

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
