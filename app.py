from flask import Flask, request
import api
import _thread

app = Flask(__name__)


@app.route('/', methods=["POST"])
def post_data():
    if request.get_json().get('message_type')=='private':		
        uid = request.get_json().get('sender').get('user_id')
        message = request.get_json().get('raw_message')
        api.keyword(message, uid)
        
    if request.get_json().get('message_type')=='group':
        gid = request.get_json().get('group_id')
        uid = request.get_json().get('sender').get('user_id')
        message = request.get_json().get('raw_message')
        api.keyword(message, uid, gid)   	
    return 'OK'


if __name__ == '__main__':
    '''
    try:
        _thread.start_new_thread( api.reminders, "./resources/reminders.json" )
    except:
        print ("Error: unable to start thread")
    '''
    _thread.start_new_thread( api.reminders, ("./resources/reminders.json",) )
    app.run(debug=True, host='127.0.0.1', port=8000)# 此处的 host和 port对应上面 yml文件的设置

