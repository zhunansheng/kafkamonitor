#coding:utf-8
import json
f_topic = open('data_topic_info.json','r')
topic_json = json.load(f_topic)
print topic_json
for data in topic_json:
    print data