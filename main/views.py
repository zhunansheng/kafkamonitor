# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import commands
import os

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, render_to_response
import logging
from django.contrib.auth.decorators import login_required
from kafkamonitor.views import is_auth
from django.contrib.auth.models import User
from models import kafkabrokerModel,dbinfoModel,topicinfoModel,alarminfoModel
# Create your views here.
from django.template import RequestContext
import json
#配置日志格式
logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
def run_shell(cmd):
    (status,output) = commands.getstatusoutput(cmd)
    context = {
        'status':status,
        'output':output,
    }
    return context

def test(request):
    logging.info(run_shell('supervisorctl update'))
def login_view(request):
    redirect_to = settings.LOGIN_REDIRECT_URL

    if request.method == "POST":
        redirect_to = request.POST.get('next')
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            login(request, form.get_user())
            return HttpResponseRedirect(redirect_to)

    else:
        if request.GET.has_key('next'):
            redirect_to = request.GET['next']

        if not bool(User.objects.all().count()):
            return HttpResponseRedirect('/superuser/')
            #User.objects.create_superuser('admin','admin@123.com','1234.com')

        form = AuthenticationForm(request)

    context = {
        'form': form,
        'next': redirect_to
    }
    return render_to_response('login.html', context)
@login_required(login_url="/login/")
def index(request):
    topic_info_list = json.load(open(r'%s/data_topic_info_web.json' % settings.MEDIA_DIRS, 'r'))
    return render(request, 'index.html',locals())

@login_required(login_url="/login/")
def gettopicinfo(request):
    topic_info_list = json.load(open(r'%s/data_topic_info_web.json' % settings.MEDIA_DIRS, 'r'))
    content = {
        'result': list(topic_info_list)
    }
    response = JsonResponse(content)
    response['Access-Control-Allow-Origin'] = '*'
    return response

#配置topic信息
@login_required(login_url="/login/")
def topic_manager(request):
    topic_selected = 'true'
    kafka_id_name ={}
    contact_id_name = {}
    kafka_broker_name_list = kafkabrokerModel.objects.all().values()
    topic_list = topicinfoModel.objects.all().values()
    contact_name_list = alarminfoModel.objects.all().values()
    logging.info(topic_list)
    logging.info(contact_name_list)
    logging.info(kafka_broker_name_list)
    logging.info(topic_list)

    logging.info(kafka_broker_name_list)
    if request.method == 'POST':
        logging.info(request.POST)
        logging.info(request.POST.get('switch',''))
        name = request.POST.get('name','')
        groupid = request.POST.get('groupid','')
        lag_threshold = request.POST.get('lag_threshold','')
        kafka_broker_name = request.POST.get('kafka_broker_name','')
        contact_name_name = request.POST.get('contact_name_name', '')
        partention_merge = request.POST.get('partention_merge','')
        state = request.POST.get('switch','off')
        remark = request.POST.get('remark','null')
        try:
            data_save = topicinfoModel.objects.get(name=name)
            return HttpResponse('不允许重复添加<a href="javascript:history.go(-1)">返回</a>')
        except topicinfoModel.DoesNotExist as e:
            data_save = topicinfoModel(name=name,groupid=groupid,lag_threshold=lag_threshold,kafka_broker_name=kafka_broker_name,contact_name_name=contact_name_name,partention_merge=partention_merge,state=state,remark=remark)
            data_save.save()
            logging.info('1')
            logging.info(settings.MEDIA_DIRS)
            if os.path.exists(r'%s/data_topic_info.json' % settings.MEDIA_DIRS):
                os.remove(r'%s/data_topic_info.json' % settings.MEDIA_DIRS)
            with open(r'%s/data_topic_info.json' % settings.MEDIA_DIRS, 'w') as f:
                topic_info = topicinfoModel.objects.filter(state='on').values('name', 'groupid','lag_threshold','kafka_broker_name','contact_name_name','partention_merge')
                f.write(json.dumps(list(topic_info)))
            return HttpResponse('添加成功<a href="javascript:history.go(-1)">返回</a>')
    return render(request, 'topic.html', locals())

#配置kafka集群信息
@login_required(login_url="/login/")
def kafka_manager(request):
    kafka_selected = 'true'
    kafka_info_list = kafkabrokerModel.objects.all().values()
    logging.info(kafka_info_list)
    if request.method == 'POST':
        logging.info(request.POST)
        broker_address = request.POST.get('broker_address')
        broker_name = request.POST.get('broker_name')
        remark = request.POST.get('remark','null')
        logging.info(request.POST)
        try:
            data_save = kafkabrokerModel.objects.get(broker_address=broker_address)
            return HttpResponse('不允许重复添加<a href="javascript:history.go(-1)">返回</a>')
        except kafkabrokerModel.DoesNotExist as e:
            data_save = kafkabrokerModel(broker_address=broker_address,broker_name=broker_name,remark=remark)
            data_save.save()
            kafka_dict = {}
            if os.path.exists(r'%s/data_kafka_info.json' % settings.MEDIA_DIRS):
                os.remove(r'%s/data_kafka_info.json' % settings.MEDIA_DIRS)
            with open(r'%s/data_kafka_info.json' % settings.MEDIA_DIRS, 'w') as f:
                data_info = kafkabrokerModel.objects.all().values('broker_name','broker_address')
                for data in data_info:
                    kafka_dict[data['broker_name']] = data['broker_address']
                f.write(json.dumps(kafka_dict))
            return HttpResponse('添加成功<a href="javascript:history.go(-1)">返回</a>')
    return render(request, 'kafka.html', locals())

#报警联系方式
@login_required(login_url="/login/")
def contact_manager(request):
    contact_selected = 'true'
    if request.method == 'POST':
        contact_name = request.POST.get('contact_name','').strip().replace(' ','')
        connect_address = request.POST.get('connect_address','').strip().replace(' ','')
        if contact_name and connect_address:
            try:
                data_save = alarminfoModel.objects.get(contact_name=contact_name)
                return HttpResponse('不允许重复添加<a href="javascript:history.go(-1)">返回</a>')
            except alarminfoModel.DoesNotExist as e:
                data_save = alarminfoModel(contact_name=contact_name, connect_address=connect_address)
                data_save.save()
                contact_dict = {}
                if os.path.exists(r'%s/data_contact_info.json' % settings.MEDIA_DIRS):
                    os.remove(r'%s/data_contact_info.json' % settings.MEDIA_DIRS)
                with open(r'%s/data_contact_info.json' % settings.MEDIA_DIRS, 'w') as f:
                    data_info = alarminfoModel.objects.all().values('contact_name', 'connect_address')
                    for data in data_info:
                        contact_dict[data['contact_name']] = data['connect_address']
                    f.write(json.dumps(contact_dict))
                return HttpResponse('添加成功<a href="javascript:history.go(-1)">返回</a>')
        else:
            return HttpResponse('不允许名称或者地址为空,请重新输入<a href="javascript:history.go(-1)">返回</a>')

    return render(request, 'contact.html', locals())

#数据库配置
@login_required(login_url="/login/")
def db_manager(request):
    db_selected = 'true'
    if request.method == 'POST':
        connect_name = request.POST.get('connect_name','')
        connect_address = request.POST.get('connect_address','')
        username = request.POST.get('username','')
        dbname = request.POST.get('dbname','')
        passwd = request.POST.get('passwd','')
        port = request.POST.get('port','')
        dbtype = request.POST.get('dbtype','')
        try:
            data_save = dbinfoModel.objects.get(connect_name=connect_name)
            return HttpResponse('不允许重复添加<a href="javascript:history.go(-1)">返回</a>')
        except dbinfoModel.DoesNotExist as e:
            data_save = dbinfoModel(connect_name=connect_name,connect_address=connect_address,username=username,dbname=dbname,passwd=passwd,port=port,dbtype=dbtype)
            data_save.save()
            contact_dict = {}
            if os.path.exists(r'%s/data_db_info.json' % settings.MEDIA_DIRS):
                os.remove(r'%s/data_db_info.json' % settings.MEDIA_DIRS)
            with open(r'%s/data_db_info.json' % settings.MEDIA_DIRS, 'w') as f:
                data_info = dbinfoModel.objects.all().values('connect_name','connect_address','username','passwd','port','dbname','dbtype')
                f.write(json.dumps(list(data_info)))
            return HttpResponse('添加成功<a href="javascript:history.go(-1)">返回</a>')
        logging.info(request.POST)
    return render(request, 'dbconfig.html', locals())

#增加用户配置
def useradd_manager(request):
    useradd_selected = 'true'
    return render_to_response('dbconfig.html', locals())

#删除用户配置
def userdel_manager(request):
    userdel_selected = 'true'
    return render_to_response('dbconfig.html', locals())

#修改密码配置
def changepass_manager(request):
    changepass_selected = 'true'
    return render_to_response('dbconfig.html', locals())