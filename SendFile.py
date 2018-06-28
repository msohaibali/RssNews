import redis
r = redis.StrictRedis(host='192.168.100.3', port=6379)

r = r.rpush("Testing", "http://feeds.bbci.co.uk/zhongwen/simp/rss.xml")

