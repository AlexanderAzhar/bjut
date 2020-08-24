
import os
import sys
import time
import uuid
import traceback

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import request
from docxtpl import DocxTemplate
from common import get_doc_url
from config import ROOT_DIR, SERVICE_HOST, SERVICE_PORT



# models
from models import Role,LeaveBeijing
# schema
from schema import leave_beijing_add_schema,leave_beijing_list_schema
# common
from common import success_out, error_out, validation_error


app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app, use_native_unicode='utf8')





@app.route('/')
def hello_flask():
    return 'Hello Flask!'


@app.route('/leave_beijing', methods=['POST'])
def leave_beijing_add():
    '''用户登录'''
    data = request.get_json()
    save_path = ''
    doc_url = ''
    print(data)
    if not data:
        return error_out(msg="请求参数不能为空")
    try:
        data = leave_beijing_add_schema.load(data)
    except  Exception as e:
        return validation_error(e)
    try:
        LeaveBeijing.add(**data)
    except Exception as e:
        return error_out(msg=str(e))
    # 生成word
    try:
        current_day = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        save_dir = '{}/{}'.format(ROOT_DIR,current_day)
        print('save_dir:{}'.format(save_dir))
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        doc_path = os.path.abspath("leave-beijing.docx")
        doc = DocxTemplate(doc_path)
        doc.render(data)
        current_day = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        save_path = '{}/{}.docx'.format(save_dir, uuid.uuid1())
        print('save_path%s' %save_path)
        doc.save(save_path)
        doc_url = get_doc_url(save_path)
    except Exception as e:
        error_message = '生成docx fail：{}'.format(traceback.format_exc())
        return error_out(msg=error_message)
    res = {
        "doc_url": doc_url,
        "save_path": save_path
    }
    return success_out(res)



@app.route('/leave_beijing', methods=['GET'])
def leave_beijing_list():
    '''用户登录'''
    page = request.args.get('page', 1)
    pagesize = request.args.get('pagesize', 10)
    data = {}
    try:
        query_res =LeaveBeijing.query.paginate(page=page,per_page=pagesize)
        items = leave_beijing_list_schema.dump(query_res.items)
        data['items'] = items
        data['total'] = query_res.total
        data['has_next'] = query_res.has_next
    except Exception as e:
        print(e)
        return error_out(msg=str(e))

    return success_out(data)



if __name__ == '__main__':
    app.debug = app.config['DEBUG'] # 配置为Debug模式，这样修改文件后，会自动重启服务
    app.run(host='0.0.0.0', port=SERVICE_PORT) # 这里配置为可在局域网中访问，默认为127.0.0.1，只能在本机访问