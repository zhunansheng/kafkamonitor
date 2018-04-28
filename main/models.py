# -*- coding: utf-8 -*-

from django.db import models
from uuidfield import UUIDField
#保存kafka集群信息
class kafkabrokerModel(models.Model):
    id = UUIDField(auto=True, primary_key=True)
    broker_name = models.CharField(max_length=100, verbose_name="集群名称")
    broker_address = models.CharField(max_length=100, verbose_name="集群地址")
    remark = models.CharField(max_length=100, verbose_name="备注")

#保存topic连接信息
class topicinfoModel(models.Model):
    id = UUIDField(auto=True, primary_key=True)
    name = models.CharField(max_length=100, verbose_name="topic名称")
    groupid = models.CharField(max_length=100, verbose_name="groupid")
    lag_threshold = models.CharField(max_length=100, verbose_name="积压阈值")
    kafka_broker_name = models.CharField(max_length=100, verbose_name="kafka集群id")
    contact_name_name = models.CharField(max_length=100, verbose_name="报警组信息id")
    partention_merge = models.CharField(max_length=100, verbose_name="是否合并分区数据")
    state = models.CharField(max_length=100, verbose_name="是否启用")
    remark = models.CharField(max_length=100, verbose_name="备注")

#保存数据库连接信息
class dbinfoModel(models.Model):
    id = UUIDField(auto=True, primary_key=True)
    connect_name = models.CharField(max_length=100, verbose_name="连接名称")
    connect_address = models.CharField(max_length=100, verbose_name="地址")
    username = models.CharField(max_length=100, verbose_name="用户名")
    passwd = models.CharField(max_length=100, verbose_name="密码")
    port = models.CharField(max_length=100, verbose_name="端口")
    dbname = models.CharField(max_length=100, verbose_name="数据库名",default='log4x')
    dbtype = models.CharField(max_length=100, verbose_name="db类型")

#保存告警发送地址，这里以钉钉为推送途径
class alarminfoModel(models.Model):
    id = UUIDField(auto=True, primary_key=True)
    contact_name = models.CharField(max_length=100, verbose_name="报警组名称")
    connect_address = models.CharField(max_length=100, verbose_name="钉钉地址")

#保存告警开关，是否屏蔽发送告警
class contact_switch(models.Model):
    id = UUIDField(auto=True, primary_key=True)
    topic_id = models.CharField(max_length=100, verbose_name="topic关联的id")
    shield_state = models.CharField(max_length=100, verbose_name="是否屏蔽")


