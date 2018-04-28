# -*- coding:utf-8 -*-
import os
import time
import sys

import json

from DingDingapi import send_mess
from kafka.client import KafkaClient
from kafka.protocol.commit import OffsetFetchRequest_v1, OffsetFetchResponse_v1, OffsetFetchRequest_v0, \
    OffsetFetchResponse_v0
from kafka.protocol.offset import OffsetRequest_v0, OffsetResponse_v0

from influxdb import InfluxDBClient







# 监控数据上报间隔 秒
time_interval = 2.5
# 历史全量数据上报间隔
history_time_interval = 5 * 60
duration = 0
client = None
conn = None
partition_cache = {}
brokers_cache = []
kafka_type = []
zk_type = []
db_type = 'influxdb'



def influxdb_store(param):
    db_json = json.load(open(r'data_db_info.json'))[0]
    influxdb_client = InfluxDBClient(db_json['connect_address'], db_json['port'], db_json['username'], db_json['passwd'], db_json['dbname'])
    json_body = [
        {
            "measurement": "kafka_monitor_info",
            "tags": {
                'group': param[0],
                'topic': param[1],
                'partition': param[2]
            },
            # "time": "2017-03-12T22:00:00Z",
            "fields": {
                'offset': param[3],
                'logsize': param[4],
                'lag': int(param[4]) - int(param[3])
            }
        }
    ]
    influxdb_client.write_points(json_body)

def get_brokers():
    if not brokers_cache:
        brokers = client.cluster.brokers()
        if brokers:
            brokers_cache.extend([x.nodeId for x in brokers])
    return brokers_cache


def get_partitions(topic):
    if not partition_cache or topic not in partition_cache:
        partitions = client.cluster.available_partitions_for_topic(topic)
        if partitions:
            partition_cache[topic] = [x for x in partitions]
        else:
            return []
    return partition_cache[topic]

def get_logsize(topic):
    """
        获取topic 下每个partition的logsize(各个broker的累加)
    :return:
    """
    tp = {}  # topic : partition_dict
    brokers = get_brokers()
    partitions = get_partitions(topic)
    pl = {}  # partition : logsize
    for broker in brokers:
        # 这里取笛卡尔积可能有问题,但是不影响parse中解析了
        for partition in partitions:
            client.send(broker, OffsetRequest_v0(replica_id=-1, topics=[(topic, [(partition, -1, 1)])]))
            responses = client.poll()
            pdict = parse_logsize(topic, partition, responses)
            append(pl, pdict)
    tp[topic] = pl
    return tp


def append(rdict, pdict):
    if rdict:
        # 已经有记录,累加
        for k, v in pdict.items():
            if k in rdict:
                rdict[k] = rdict[k] + v
            else:
                rdict[k] = v
    else:
        rdict.update(pdict)

def parse_logsize(t, p, responses):
    """
        单个broker中单个partition的logsize
    :param responses:
    :param p:
    :param t:
    :return:
    """
    for response in responses:
        if not isinstance(response, OffsetResponse_v0):
            return {}
        tps = response.topics
        topic = tps[0][0]
        partition_list = tps[0][1]
        partition = partition_list[0][0]
        # 异步poll来的数据可能不准
        if topic == t and partition == p and partition_list[0][1] == 0:
            logsize_list = partition_list[0][2]
            logsize = logsize_list[0]
            return {partition: logsize}
    return {}


def parse_offsets(t, responses):
    dr = {}
    for response in responses:
        if not isinstance(response, (OffsetFetchResponse_v1, OffsetFetchResponse_v0)):
            return {}
        tps = response.topics
        topic = tps[0][0]
        partition_list = tps[0][1]
        if topic == t:
            for partition_tunple in partition_list:
                if partition_tunple[3] == 0:
                    offset = partition_tunple[1]
                    dr[partition_tunple[0]] = offset
    return dr
#获取消费位置
def get_offsets(topic,monitor_group_ids):
    # {gid: dict}
    gd = {}
    for gid in monitor_group_ids:
        td = {}  # {topic:dict}
        pd = {}  # {partition:dict}
        for broker in get_brokers():
            partitions = get_partitions(topic)
            if not partitions:
                return {}
            else:
                responses = optionnal_send(broker, gid, topic, partitions)
                dr = parse_offsets(topic, responses)
                append(pd, dr)
        td[topic] = pd
        gd[gid] = td
    return gd


def optionnal_send(broker, gid, topic, partitions):
    if gid in kafka_type:
        return kafka_send(broker, gid, topic, partitions)
    elif gid in zk_type:
        return zk_send(broker, gid, topic, partitions)
    else:
        responses = zk_send(broker, gid, topic, partitions)
        dct = parse_offsets(topic, responses)
        if is_suitable(dct):
            zk_type.append(gid)
            return responses
        responses = kafka_send(broker, gid, topic, partitions)
        dct = parse_offsets(topic, responses)
        if is_suitable(dct):
            kafka_type.append(gid)
        return responses


def is_suitable(dct):
    for x in dct.values():
        if x != -1:
            return True
#kafka发送请求接口
def kafka_send(broker, gid, topic, partitions):
    client.send(broker, OffsetFetchRequest_v1(consumer_group=gid, topics=[(topic, partitions)]))
    return client.poll()

#zk发送请求接口
def zk_send(broker, gid, topic, partitions):
    client.send(broker, OffsetFetchRequest_v0(consumer_group=gid, topics=[(topic, partitions)]))
    return client.poll()






#发起请求，并且解析返回的结果，并且将结果写入influxdb
def do_task(topic,monitor_group_ids,contact_name_address,lag_threshold,partention_merge,topic_info_web):
    for groupid in monitor_group_ids:
        offset_dict = get_offsets(topic, monitor_group_ids)
        logsize_dict = get_logsize(topic)
        print offset_dict
        print logsize_dict
        #用来添加topic信息临时字典
        total_lag = 0
        offset_total = 0
        logsize_total = 0
        for gk, gv in offset_dict.items():
            for tk, tv in gv.items():
                for pk, pv in tv.items():
                    if logsize_dict and tk in logsize_dict:
                        dr = logsize_dict[tk]  # partition:logsize
                        if dr and pk in dr:
                            param = (gk, tk, pk, pv, dr[pk],
                                     time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
                            print param
                            total_lag += int(param[4]) - int(param[3])
                            offset_total += int(pv)
                            logsize_total += int(dr[pk])
                            if partention_merge != 'yes':
                                influxdb_store(param)
        data_temp = {
            'topic' : topic,
            'groupid' : groupid,
            'offset_total' : offset_total,
            'logsize_total' : logsize_total,
            'total_lag' : total_lag
        }
        topic_info_web.append(data_temp)
        if partention_merge == 'yes':
            param = (groupid,topic,'total',offset_total, logsize_total,total_lag)
            influxdb_store(param)
        if total_lag >= lag_threshold:
            time.sleep(10)
            send_mess(("kafka %s, consumer %s lag is more than you set!!! now the lag is %s ") % (topic,groupid, total_lag),
                      contact_name_address)




if __name__ == "__main__":
    while True:
        contact_info_json = json.load(open('data_contact_info.json', 'r'))
        kafka_info_json = json.load(open('data_kafka_info.json', 'r'))
        topic_info_json = json.load(open('data_topic_info.json', 'r'))
        print topic_info_json
        print contact_info_json
        print kafka_info_json
        #用来展示给web使用
        topic_info_web = []
        for topic_data in topic_info_json:
            # topic名称
            topic = topic_data['name']
            # 消费id
            groupid = topic_data['groupid']
            # 积压阈值
            lag_threshold = topic_data['lag_threshold']
            # 是否合并分区，减少influxdb存储
            partention_merge = topic_data['partention_merge']
            # 关联kafka集群名称
            kafka_broker_name = topic_data['kafka_broker_name']
            # 获取kafka_broker地址
            kafka_broker_address = kafka_info_json[kafka_broker_name]
            # 关联告警组名称
            contact_name_name = topic_data['contact_name_name']
            # 获取告警组发送地址
            contact_name_address = contact_info_json[contact_name_name]
            client = KafkaClient(bootstrap_servers=kafka_broker_address, request_timeout_ms=3000)
            # 要监控的groupid
            if groupid.find(',') != -1:
                monitor_group_ids = groupid.split(',')
            else:
                monitor_group_ids = [groupid]
            do_task(topic, monitor_group_ids,contact_name_address,lag_threshold,partention_merge,topic_info_web)
        if os.path.exists(r'data_topic_info_web.json'):
            os.remove(r'data_topic_info_web.json')
        with open(r'data_topic_info_web.json', 'w') as f:
            f.write(json.dumps(topic_info_web))
        time.sleep(time_interval)
        duration += time_interval