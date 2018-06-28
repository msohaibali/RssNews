import time
import datetime
import dateutil.parser as parser
import redis
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from bs4 import BeautifulSoup



r = redis.StrictRedis(host='192.168.100.3', port=6379)


def getTarget(tg):
    print(" in get taret")
    driver.get(tg)
    print("Getting target")


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
body=''
title=''


def NewsContent(lnk):
        print(lnk)
        getTarget(lnk)
        implicitwait(10)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        try:
            p_content1 = ''
            curr_post = soup.find('div', attrs={'class': ['story-inner','story-body']})
            targ_p = curr_post.find_all('h1')
            for p in targ_p:
                p_content1 = p_content1 + p.text

            title = p_content1
            print(title)
            try:
                dateDiv = soup.find('div', attrs={'class': 'date date--v2'})
                val = dateDiv['data-seconds']
                pubTime = datetime.datetime.utcfromtimestamp(float(val)).strftime('%Y-%m-%d %H:%M:%S')

                date = parser.parse(pubTime)
                pubTime = date.isoformat()
                import arrow
                pubTime = arrow.get(pubTime).datetime
                print (pubTime)
            except:
                pass
        except Exception as ex:
            print(ex)
            pass

        try:
            p_content = ''
            curr_post = soup.find('div', attrs={'class': ['story-body__inner', 'story-body']})
            targ_p = curr_post.find_all('p')
            for p in targ_p:
                p_content = p_content + p.text
            print (p_content)
            body = p_content
        except:
            print("Didnot found the class")
            pass


def main():

    global driver
    driver = webdriver.Firefox()
    lnk = 'http://www.bbc.com/zhongwen/simp/world-43319272'
    NewsContent(lnk)
    driver.close()


main()




