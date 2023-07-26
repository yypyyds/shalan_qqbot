import requests

def Haskey(dict,key):
    for i,item in enumerate(dict):
        if item["key"] == key:
            return i
    return -1


def SendGroupMsg(gid,msg):
    return requests.get(url='http://127.0.0.1:9692/send_group_msg?group_id={0}&message={1}'.format(gid, msg))


def SendPrivateMsg(uid,msg):
    return requests.get(url='http://127.0.0.1:9692/send_private_msg?user_id={0}&message={1}'.format(uid, msg))