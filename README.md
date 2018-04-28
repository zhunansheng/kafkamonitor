# kafkamonitor


项目起源于需要监控kafka积压，然而发现很多开源工具只能看，不能智能告警，所以项目诞生！非专业开发，代码凑合看吧。

> * 项目基于 [Django](https://www.djangoproject.com/) + [AdminLTE](https://www.almsaeedstudio.com/) 构建，在 centos7.2 上测试通过；为了保证良好的兼容性，请使用 Chrome 浏览器。
> * 为了后续扩展方便，请大家使用 [Tengine](http://tengine.taobao.org/) 替代 Nginx 服务

## 项目地址
- GITHUB - https://github.com/zhunansheng/kafkamonitor


## 更新
* 发布初版kafka监控系统

## 功能
* kafka各个topic监控积压，告警
## python版本
* python2.7

## 运行
* 克隆代码
```
mkdir -p /app  
git clone https://github.com/zhunansheng/kafkamonitor.git
cd /app

* 安装 tengine
```

cd resource/nginx/tengine
yum install -y build-essential libssl-dev libpcre3 libpcre3-dev zlib1g-dev pcre pcre-devel openssl openssl-devel
groupadd www-data
useradd -g www-data www-data
./configure --user=www-data --group=www-data --prefix=/etc/nginx --sbin-path=/usr/sbin --error-log-path=/var/log/nginx/error.log --conf-path=/etc/nginx/nginx.conf --pid-path=/run/nginx.pid
make
make install
mkdir -p /etc/nginx/conf.d
echo "daemon off;" >> /etc/nginx/nginx.conf  
```
* 安装 supervisor
```
pip install supervisor
mkdir -p /etc/supervisor
#创建supervisor默认配置文件
echo_supervisord_conf > /etc/supervisor/supervisord.conf
修改supervisor配置文件


systemctl enable supervisord
```
* 配置 supervisor
```
cp -rf service/* /etc/supervisor/
```
* 安装依赖
```
yum install -y python-devel
pip install -r requirements.txt  
```
* 初始化数据库
```
python manage.py makemigrations  
python manage.py migrate  
```
* 启动服务
```
service supervisor start
```
* 登录系统
```
http://[IP]:8000/  
```
> 首次登陆会要求创建管理员用户，如需修改，可在系统配置中重置管理员用户



## 授权
本项目由 [南风](http://nf1.cc) 维护，采用 [GPLv3](http://www.gnu.org/licenses/gpl-3.0.html) 开源协议。欢迎反馈！欢迎贡献代码！
