import uuid
from datetime import datetime, timedelta

from flask import Flask
from flask import jsonify, request

from utildb import utildb
from managedb import managedb
from tempClass import Temperature
from humidClass import Humidity
from tokenClass import Token

AUTH_HEADER = 'Authorization'
USER_TYPE_SERVICE = 'service'
USER_TYPE_USER = 'user'
TOKEN_LIFESPAN = timedelta(hours= 3)

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "Welcome."

@app.route('/data/all/temperature', methods=['GET'])
def get_All_Temp():
    auth_result = assert_token(request, USER_TYPE_USER)
    if auth_result != None:
        return auth_result
    if not request.args:
        db = managedb()
        resulttemp = db.query(utildb.select_all('temperature_table'))
        db.die()
        return jsonify(resulttemp)

@app.route('/data/all/humidity', methods=['GET'])
def get_All_Humid():
    auth_result = assert_token(request, USER_TYPE_USER)
    if auth_result != None:
        return auth_result
    if not request.args:
        db = managedb()
        resulthumid = db.query(utildb.select_all('humidity_table'))
        db.die()
        return jsonify(resulthumid)


@app.route('/data/last/temperature', methods=['GET'])
def get_Last_Temp():
    auth_result = assert_token(request, USER_TYPE_USER)
    if auth_result != None:
        return auth_result
    if not request.args:
        db = managedb()
        resulttemp = db.query(utildb.select_last('temperature_table'))
        db.die()
        return jsonify(resulttemp)

@app.route('/data/last/humidity', methods=['GET'])
def get_Last_Humid():
    auth_result = assert_token(request, USER_TYPE_USER)
    if auth_result != None:
        return auth_result
    if not request.args:
        db = managedb()
        resulthumid = db.query(utildb.select_last('humidity_table'))
        db.die()
        return jsonify(resulthumid)


@app.route('/data/timerange/temperature/<string:range>', methods=['GET'])
def get_In_Range_Temp(range):
    auth_result = assert_token(request, USER_TYPE_USER)
    if auth_result != None:
        return auth_result
    if not request.args:
        db = managedb()
        resulttemp = db.query(utildb.select_between('temperature_table',range))
        db.die()
        return jsonify(resulttemp)


@app.route('/data/timerange/humidity/<string:range>', methods=['GET'])
def get_In_Range_Humid(range):
    auth_result = assert_token(request, USER_TYPE_USER)
    if auth_result != None:
        return auth_result
    if not request.args:
        db = managedb()
        resulthumid = db.query(utildb.select_between('humidity_table',range))
        db.die()
        return jsonify(resulthumid)

@app.route('/token', methods=['POST'])
def issue_token():
    username = request.json['username']
    password = request.json['password']

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
        temp = Temperature()
        humid = Humidity()
        temp.date_time = request.json['date_time']
        humid.date_time = request.json['date_time']
        temp.temperature = request.json['temperature']
        humid.humidity = request.json['humidity']
        temp.pi_id = request.json['pi_id']
        humid.pi_id = request.json['pi_id']

        try:
            db = managedb()
            db.execute(utildb.insert('temperature_table', temp))
            db.execute(utildb.insert('humidity_table', humid))
        except Exception as e:
            return flask.Response(response=str(e),status=500)
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
#     "date_time":"2030-01-01 20:59:59",
#     "temperature":100.0,
#     "humidity":200.0,
#     "pi_id":1
# }

#
# auth_result = assert_token(request, USER_TYPE_USER)
# if auth_result != None:
#     return auth_result

# {
#     "username":"testuser",
#     "password":"9f735e0df9a1ddc702bf0a1a7b83033f9f7153a00c29de82cedadc9957289b05"
# }