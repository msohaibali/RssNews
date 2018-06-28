import json
from pymongo import MongoClient
import xml.etree.ElementTree as ET

# tree = ET.parse('project_variables.xml')
# root = tree.getroot()
# Mip = ''
# dab = ''
# rip = ''
# for country in root.findall('Project'):
#      Mip = country.find('MongoIP').text
#      dab = country.find('Database').text
#      rip = country.find('RedisIP').text



client = MongoClient('192.168.100.6',27017)
db = client['EM']


sharescoll = db['EM']





count = 0
llist = []

foo = open("/home/hduser/Documents/emmadata1.json", "r")
next_post_element = foo.readlines()
for elem in next_post_element:
    print (elem)
    sharescoll.insert(json.dumps(elem))

    # print elem

    # try:
    #     post = sharescoll.insert_one(Jstr).inserted_id
    # except Exception as val:
    #     print val.message
    #     pass

# print json.dumps(llist,indent=4)
# print data

