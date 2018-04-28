"""kafkamonitor URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from main import views
from .views import login_view,logout_view,create_superuser
urlpatterns = [
    url(r'^login/$', login_view),
    url(r'^logout/$', logout_view),
    url(r'^superuser/$', create_superuser),
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.index, name='index'),
    url(r'^topic_manager',views.topic_manager),
    url(r'^db_manager',views.db_manager),
    url(r'^kafka_manager',views.kafka_manager),
    url(r'^contact_manager',views.contact_manager),
    url(r'^useradd_manager',views.useradd_manager),
    url(r'^userdel_manager',views.userdel_manager),
    url(r'^gettopicinfo', views.gettopicinfo),
    url(r'^changepass_manager',views.changepass_manager),
    url(r'^test', views.test)
]
