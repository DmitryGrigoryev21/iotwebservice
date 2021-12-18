import decimal
import uuid
from datetime import datetime, timedelta

import flask
from flask import jsonify, request
import json
from utildb import utildb
from managedb import managedb
from dataClass import Data
from tokenClass import Token

from flask.json import JSONEncoder
#put it in /usr/local/bin and chmod 777 the file
class JsonEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return JSONEncoder.default(self, obj)


AUTH_HEADER = 'Authorization'
USER_TYPE_SERVICE = 'service'
USER_TYPE_USER = 'user'
TOKEN_LIFESPAN = timedelta(hours= 3)

app = flask.Flask(__name__)

app.json_encoder = JsonEncoder


@app.route('/', methods=['GET'])
def home():
    return "Welcome."

@app.route('/data/all', methods=['GET'])
def get_All():
    auth_result = assert_token(request, USER_TYPE_USER)
    if auth_result != None:
        return auth_result
    if not request.args:
        db = managedb()
        result = db.query(utildb.select_all('data_table'))
        db.die()
        return jsonify(result)

@app.route('/data/last', methods=['GET'])
def get_Last():
    auth_result = assert_token(request, USER_TYPE_USER)
    if auth_result != None:
        return auth_result
    if not request.args:
        db = managedb()
        result = db.query(utildb.select_last('data_table'))
        db.die()
        return jsonify(result)

@app.route('/data/timerange/<string:range>', methods=['GET'])
def get_In_Range(range):
    auth_result = assert_token(request, USER_TYPE_USER)
    if auth_result != None:
        return auth_result
    if not request.args:
        db = managedb()
        result = db.query(utildb.select_between('data_table',range))
        db.die()
        return jsonify(result)

@app.route('/token', methods=['POST'])
def issue_token():
    try:
            username = request.json['username']
            password = request.json['password']
    except:
            r = request.get_json()
            if not isinstance(r,list):
                r = json.loads(r)
            username = r['username']
            password = r['password']

    if username == None or len(username) == 0:
        return flask.Response(response="missing mandatory username", status=400)
    if password == None or len(password) == 0:
        return flask.Response(response="missing mandatory password", status=400)

    try:
        db = managedb()
        user_result = db.query(utildb.select_all_where('user_table', 'user_name', username))
    except Exception as e:
        return flask.Response(response=str(e), status=500)
    finally:
        if db != None:
            db.die()

    if not user_result: #bad practice,simplifes dict attack
        return flask.Response(response="unknown user", status=403)

    if user_result[0]['password'] != password:
        return flask.Response(response="invalid password", status=403)

    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    expire_time = (now + TOKEN_LIFESPAN)

    token = Token()
    token.token = str(uuid.uuid4())
    token.issued_at = current_time
    token.expires_at = expire_time
    token.user_id = username
    token.user_type = user_result[0]['user_type']
    try:
        db = managedb()
        db.execute(utildb.delete_expired('token_table'))
        db.execute(utildb.insert('token_table', token))
    except Exception as e:
        return flask.Response(response=str(e), status=500)
    finally:
        if db != None:
            db.die()
    return jsonify(token=token.token, expires_at=expire_time)

@app.route('/data/send', methods=['POST'])
def add_Data():
    auth_result=assert_token(request, USER_TYPE_SERVICE)
    if auth_result != None:
        return auth_result

    if not request.args:
        r = request.get_json()
        if not isinstance(r,list):
            r = json.loads(r)
        print(r)
        print(isinstance(r,list))
        print(type(r))
        for x in r:
            data = Data()
            data.pi_id = x['pi_id']
            data.data = x['data']
            data.data_type = x['data_type']
            data.date_time = x['date_time']


            try:
                db = managedb()
                db.execute(utildb.insert('data_table', data))
            except Exception as e:
                return flask.Response(response=str(e),status=500)
            finally:
                if db != None:
                    db.die()

        return flask.Response(response="success", status=200)

@app.route('/token/revoke', methods=['POST'])
def token_revoke():
    auth_result=assert_token(request, USER_TYPE_USER)
    if auth_result != None:
        return auth_result

    if not request.args:
        token = request.headers[AUTH_HEADER]
        try:
            db = managedb()
            db.execute(utildb.delete_by_token('token_table',token))
        except Exception as e:
            return flask.Response(response=str(e), status=500)
        finally:
            if db != None:
                db.die()

        return flask.Response(response="success", status=200)


def assert_token(request, user_type):
    if not AUTH_HEADER in request.headers.keys():
        return flask.Response(response="missing authorization token", status=401)
    token = request.headers[AUTH_HEADER]
    try:
        db = managedb()
        token_result = db.query(utildb.select_all_where('token_table', 'token', token))
    except Exception as e:
        return flask.Response(response=str(e), status=500)
    finally:
        if db != None:
            db.die()

    if not token_result:
        return flask.Response(response="unknown token", status=403)

    now = datetime.now()
    if token_result[0]['expires_at'] < now:
        return flask.Response(response="expired token", status=403)

    if token_result[0]['user_type'] != user_type:
        return flask.Response(response="user type does not match", status=403)


    return None

app.run()

# {
#   "version": "2.0",
#   "type": "temperature+humidity",
#   "items": [
#   { temp1...},
#   { temp2....},
#   ]}

# [{
#     "date_time":"2030-01-01 20:59:59",
#     "data":100.0,
#     "data_type":"temperature",
#     "pi_id":1
# }]

#
# auth_result = assert_token(request, USER_TYPE_USER)
# if auth_result != None:
#     return auth_result

# {
#     "username":"testuser",
#     "password":"9f735e0df9a1ddc702bf0a1a7b83033f9f7153a00c29de82cedadc9957289b05"
# }