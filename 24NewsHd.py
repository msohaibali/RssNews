import arrow
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from pymongo import MongoClient
import xml.etree.ElementTree as ET
from selenium.webdriver.support.ui import WebDriverWait
import time
import traceback
import datetime
import dateutil.parser as parser
import redis
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

driver = webdriver.Firefox()


def error(err):

    try:
        source = "24 News HD"
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
                curr_post = soup.find('div', attrs={'class': 'zm-post-header'})
                targ_p = curr_post.find('h2')
                p_content1 = targ_p.text

                title = p_content1
                title = title.replace("  ", "")
                print(title)

            except:
                print("Didn't found the title")
                pass

            try:
                p_content = ''
                curr_post = soup.find('div', attrs={'class': 'zm-post-content'})
                targ_p = curr_post.find_all('p')
                for p in targ_p:
                    p_content = p_content + p.text

                body = p_content
                body = body.replace("\n", "")
                print(body)

                try:
                    global pubTime, date
                    dateDiv = soup.find('li', attrs={'class': 's-meta s-meta-custom-a'})
                    datte = dateDiv.text
                    translator = Translator()
                    datte = translator.translate(datte)
                    datte = datte.text
                    date = parser.parse(datte)

                    date = date.strftime('%I:%M %p, %b %-d, %Y')
                    date = parser.parse(date)
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

                elif pubTime is '':
                    print("This is a Photo or Video, Content doesnot Exists!")


                else:
                    try:

                        collection1.insert([{"Type": "Predefined List", "Category": "National", "Language": "Urdu",
                                             "Source": "24 News HD", "title": title, "body": body, "_id": lnk,
                                             "published Time": pubTime}])
                        r.rpush('news_link', lnk)

                    except:
                        pass

            except:
                print("Didn't found the class")
                pass


# Function for grabbing News links
def get_results():
    url = "https://www.24newshd.tv/latest"
    driver.get(url)

    try:
        try:
            links = driver.find_elements_by_xpath("//div[@class='zm-post-header']//h2//a")

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
