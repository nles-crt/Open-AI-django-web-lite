import time
from datetime import datetime
import requests
import openai
import os
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import logout
from django.shortcuts import redirect
import html
import pymysql
import re
import json
class mysql:
    def __init__(self):
        # 连接数据库
        self.conn = pymysql.connect(host='localhost', user='daojin', password='daojin771', db='daojin')
    def query(self,sql):
        #创建游标
        print(sql)
        cursor = self.conn.cursor()
        try:
            #执行sql
            cursor.execute(sql)
            #提交
            self.conn.commit()
        except:
            #如果发生错误则回滚
            self.conn.rollback()
        #获取结果
        res = cursor.fetchall()
        #关闭游标
        cursor.close()
        return res
        #返回结果
    def sqldump(self, Type, data):
        if Type == 'Login':
            sql = self.query(f"select * from user where username = '{filter_character(data['username'])}' and password = '{filter_character(data['password'])}';")
        elif Type == 'registration':
            print(data, type(data))
            username = self.query(f"select `username` from user where username = '{filter_character(data['username'])}';")
            mail = self.query(f"select `username` from user where mail = '{filter_character(data['mail'])}';")
            if username == () and mail == ():
                sql = self.query(f"INSERT INTO `daojin`.`user` (`username`, `password`, `phone`, `mail`, `time`) VALUES ('{data['username']}', '{data['password']}', '{data['phone']}', '{data['mail']}', '{time.strftime('%Y-%m-%d', time.localtime())}');")
            elif username:
                sql = "用户名已被注册 <br/> <a href='/Register'>返回重新输入</a>"
            else:
                sql = "邮箱已经被注册了 <br/> <a href='/Register'>返回重新输入</a>"
            print(sql)
        return sql




    def uptime(self, username):
        times = time.strftime("%Y-%m-%d", time.localtime())
        sql = self.queue(f"UPDATE `daojin`.`user` SET `time`='{times}' WHERE `username`='{username}' LIMIT 1;")
        return sql

mysql = mysql()
def hello(request):
    return render(request, "test.html")


def logout_view(request):
    logout(request)
    return redirect('/')



def url(request):
    return render(request, "url.html")
def Register(request):
    return render(request, "Register.html")

def processing(request,data):
    if not data:
        return False
    if len(data) >= 1:
        print(data)
        request.session["key"] = data[0][1]
        return True

def filter_character(string):
    string = html.escape(string)
    return string

def dataRegister(request):
    parameters = {"username":request.POST.get('username'), "mail":request.POST.get('mail'), "phone":request.POST.get('phone'),"password":request.POST.get('password')}
    print(len(parameters))
    if len(parameters) == 4:
        print(parameters)
        Register = mysql.sqldump(Type='registration', data=parameters)
        if Register == ():
            return HttpResponse("注册成功<br/> <a href='/url'>返回重新输入</a>")
        return HttpResponse(f'执行结果：{Register}',content_type='text/html;charset=utf-8')
    else:
        print(parameters)
        return HttpResponse('补齐参数', content_type='text/html;charset=utf-8')
    return render(request, "url.html")

def dataurl(request):
    request.encoding = 'utf-8'
    if 'username' in request.GET and request.GET['username']:
        data = {'username':request.GET['username'],'password':request.GET['password']}
        message = processing(request,data=mysql.sqldump(Type='Login', data=data))
        print(message, type(message))
        if message==True:
            return redirect('/')
        else:
            message = "密码错误      <br/> <a href='/url'>返回重新输入</a>"
    else:
        message = "请输入账号密码      <br/>  <a href='/url'>返回重新输入</a>"
    return HttpResponse(message, content_type='text/html;charset=utf-8')


def mesopenai(text):
    openai.api_key = ("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")
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=text['text'],
        temperature=0.7,
        max_tokens=int(text['max_tokens']),
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    print(type(response), text['max_tokens'])
    aidata = (replace(response['choices'][0]['text']))
    return aidata

def replace(str):
    return str.replace('\n', '')



def queryrequest(request):
    data = {}
    if request.session.get("key", None):
        print('当前key: '+request.session["key"])
        if 'text' in request.POST and request.POST['text']:
            if 'max_tokens' in request.POST and not request.POST['max_tokens']:
                max_tokens = 256
            else:
                max_tokens = request.POST['max_tokens']
            text = {'text':request.POST['text'],'max_tokens':max_tokens}
            data = {
                'status': 200,
                'comment': 'Successfully return current time',
                'data': {
                    'username': request.session["key"],
                    'mytext': request.POST['text'],
                    'text': mesopenai(text)
                }
            }
        else:
            data = {
                'status': 201,
                'comment': '请输入内容'
            }
    else:
        print('没有key')
        data = {
            'status': 205,
            'comment': '未登入'
            }
    return JsonResponse(data,json_dumps_params={'ensure_ascii':False, 'indent':4})


def index(request):
    return HttpResponse("Hello world ! ")




