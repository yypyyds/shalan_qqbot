import json
import requests
import re
import random
import datetime
import time
from utils import *


rmdlock = 0

def keyword(message, uid, gid = None):
    replyfunc(message,gid,uid)
    if message[0:4] == 'test':
        test(gid,message)
    if message[0:5] == 'reply':
        reply(message,gid)
    if message == "SED":
        SEDforward(uid,gid)
    if message[0:4] == "info":
        reminderconsole(gid,uid,message)
    if message[0:5] == "image":
        randomimage(gid,uid,message)


def SEDforward(uid, gid=None):
    req = requests.get("http://192.168.31.20:5000/RealtimeData/1")
    res = json.loads(req.text)
    a = res['current_result']

    sorted_items = sorted(a.items(), key=lambda x: x[1], reverse=True)
    msg = ""
    for type,val in sorted_items:
        msg += f'{type}: {val}\n'
    
    print("uid={0},gid={1}".format(uid,gid))
    if gid!=None:
        SendGroupMsg(gid,msg)
    else:    
        SendPrivateMsg(uid,msg)


def test(gid,message):
    SendGroupMsg(gid,'connection success')
    msg = 'get' + message
    SendGroupMsg(gid,msg)


def replyfunc(message,gid,uid):
    with open("./resources/reply.json","r") as f:
        rpl = json.load(f)
     

    for item in rpl:
        if message == item["key"]:
            msg = random.choice(item["msg"])
            SendGroupMsg(gid,msg)
            break
    


def reply(message, gid):

    with open("./resources/reply.json","r") as f:
        rpl = json.load(f)

    if 'help' in message:
        msg='''
        用法：
        添加关键词回复：
        reply add 关键词 回复
        列出关键词的所有回复：
        reply list 关键词
        删除指定关键词指定序号的回复:
        reply del 关键词 序号
        '''
        requests.get(url='http://127.0.0.1:9692/send_group_msg?group_id={0}&message={1}'.format(gid, msg))

    if 'add' in message:
        # 添加reply
        token = message.split()
        keyword = token[2]
        val = token[3]
        ret = Haskey(rpl,keyword)
        if ret != -1:   # 存在关键词，直接加在msg列表中
            rpl[ret]["msg"].append(val)
        else:           # 不存在关键词，新建一个词条，加入msg
            rpl.append({"key":keyword,"msg":[val]})
    
        with open("./resources/reply.json","w") as f:
            json_data = json.dumps(rpl, indent=4)
            f.write(json_data)
        SendGroupMsg(gid,"添加成功")
    
    if 'list' in message:
        #列出对应关键词所有的reply
        token = message.split()
        keyword = token[2]
        ret = Haskey(rpl,keyword)
        if ret != -1:   # 存在关键词，按序输出所有的msg
            sendmsg = ""
            for i,msg in enumerate(rpl[ret]["msg"]):
                sendmsg = sendmsg + str(i) + msg + "\n"
            SendGroupMsg(gid,sendmsg)

        else:           # 不存在关键词
            SendGroupMsg(gid,"不存在该关键词")
    
    if "del" in message:
        token = message.split()
        keyword = token[2]
        seq = int(token[3])
        ret = Haskey(rpl,keyword)
        if ret != -1:   # 存在关键词
            length = len(rpl[ret]["msg"])
            if seq > length-1:
                SendGroupMsg(gid,'序号超出回复消息列表范围')
            else:
                delmsg = rpl[ret]["msg"][seq]
                del(rpl[ret]["msg"][seq])
                SendGroupMsg(gid,"已删除："+delmsg)

        else:           # 不存在关键词
            SendGroupMsg(gid,"不存在该关键词")

        with open("./resources/reply.json","w") as f:
            json_data = json.dumps(rpl, indent=4)
            f.write(json_data)
    

def reminders(remdpath):
    change = 0
    while(True):
        with open(remdpath, "r") as f:
            things = json.load(f)
        nt = datetime.datetime.now()

        year, month, day, hour, miniute = nt.year, nt.month, nt.day, nt.hour, nt.minute
        for seq,item in enumerate(things):
            if (str(year) == item["year"] and str(month) == item["month"] and str(day) == item["day"] and str(hour) == item["hour"] and str(miniute) == item["miniute"]):
                SendGroupMsg(item["gid"],item["thing"])
                del things[seq]     #提醒一次自动删除
                change = 1

        if(change == 1):
            change = 0
            with open(remdpath,"w") as f:
                json_data = json.dumps(things, indent = 4)
                f.write(json_data)
        time.sleep(59)


def reminderconsole(gid,uid,msg):
    token = msg.split()
    with open("./resources/reminders.json", "r") as f:
        things = json.load(f)
    change = 0

    if "help" in msg:
        send_msg = '''提醒事项功能：\n[info help]获取帮助信息\n[info add 年.月.日.小时.分钟.提醒信息]添加一条提醒信息\n[info list]获取所有登记的提醒\n[info del 序号]删除指定序号的提醒'''
        SendGroupMsg(gid,send_msg)
        return
    if "add" in msg:
        items = token[2].split(".")
        if len(items) < 6:
            SendGroupMsg(gid,"提醒事项参数太少，请检查后重新提交")
            return
        a = {
            "gid":str(gid),
            "uid":str(uid),
            "year":items[0],
            "month":items[1],
            "day":items[2],
            "hour":items[3],
            "miniute":items[4],
            "thing":items[5]
        }
        things.append(a)
        change = 1
        send_msg = "添加提醒成功\n"
        send_msg = send_msg + "将于{}年{}月{}日{}时{}分提醒您：\n{}".format(a["year"],a['month'],a['day'],a['hour'],a['miniute'],a['thing'])
        SendGroupMsg(gid,send_msg)
        pass
    if "list" in msg:
        send_msg = ""
        for seq,th in enumerate(things):
            temp = str(seq) + ": " + "{}.{}.{}.{}.{}.{}".format(th["year"], th["month"], th["day"], th["hour"], th["miniute"], th["thing"]) + "\n"
            send_msg = send_msg + temp
        
        SendGroupMsg(gid,send_msg)
        pass
    if "del" in msg:
        seqstr = token[2]
        if seqstr.isdigit():
            seq = int(seqstr)
        if seq >= len(things):
            SendGroupMsg(gid,"sequence out of range")
            pass
        else:
            delmsg = things[seq]['thing']
            del things[seq]
            SendGroupMsg(gid,"delete msg: " + delmsg)

        change = 1
        pass

    if change == 1:
        with open("./resources/reminders.json", "w") as f: 
            json_data = json.dumps(things, indent = 4)
            f.write(json_data)


def randomimage(gid,uid,message):
    url = "https://api.likepoems.com/img/pixiv/?type=json"
    resp = requests.get(url)
    json_resp = resp.json()
    url = json_resp['url']
    msg = r'[CQ:image,' r'file=' + str(url) + r']'
    SendGroupMsg(gid,msg)
        
            
        

    



    