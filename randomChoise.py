# Import the framework
from flask import Flask
from flask import request, jsonify
from flask_pymongo import PyMongo
import json
from pprint import pprint
import random
import time
from datetime import datetime
from prettyprinter import pprint

app = Flask(__name__)
app.config['DEBUG'] = True


app.config["MONGO_URI"] = "mongodb://localhost:27017/coinFlip"
mongo = PyMongo(app)

@app.route("/reset", methods=['GET'])
def reset():
    cursor = mongo.db.users.find_one_or_404({'name': 'luca'})
    user = cursor['_id']
    result = mongo.db.users.update_one({'_id': user}, {"$set": {'prob': 5}})
    return 'fatto'

@app.route("/user/<name>/firstReq", methods=['GET'])
def firstReq(name):
    user_data = {}
    cursor = mongo.db.users.find_one_or_404({'name': name})
    prob = cursor['probability']
    user_data['probability'] = prob
    user_data['isFirstTry'] = cursor['isFirstTry']
    user_data['itAlreadyFailed'] = cursor['itAlreadyFailed']
    user_data['itAlreadyPay'] = cursor['itAlreadyPay']
    user_data['point'] = cursor['point']
    data = json.dumps(user_data)
    return data

@app.route("/user/<name>", methods=['GET'])
def home(name):
    user_data = {}
    rnd = random.randint(1,1000)
    cursor = mongo.db.users.find_one_or_404({'name': name})
    user = cursor['_id']
    prob = cursor['probability']
    point = cursor['point']
    user_data['probability'] = prob
    user_data['itAlreadyFailed'] = cursor['itAlreadyFailed']
    user_data['itAlreadyPay'] = cursor['itAlreadyPay']
    print(prob)
    if not user_data['itAlreadyPay']:
        if rnd <= int(prob):
            user_data['flipResult'] = 1
            user_data['point'] = point
            result = mongo.db.users.update_one({'_id': user}, {"$set": {'itAlreadyFailed': True}})
            data = json.dumps(user_data)
            return data
        else:
            if int(prob) <= 500:
                new_prob = int(prob) + 1
            else:
                new_prob = int(prob)
            result = mongo.db.users.update_one({'_id': user}, {"$set": {'probability': new_prob, 'point': point + 1 , 'isFirstTry': False}})
            user_data['probability'] = new_prob
            user_data['flipResult'] = 0
            user_data['isFirstTry'] = False
            user_data['point'] = point + 1
            data = json.dumps(user_data)
            return data

@app.route("/user/<name>/ranking", methods=['GET'])
def getRanking(name):
    ranking = {}
    numberOfRank = 10
    elements = mongo.db.users.find().sort('point', -1)
    for index, x in enumerate(elements):
        if index > numberOfRank:
            break
        if str(x['name']) == str(name):
            numberOfRank = 10
        aux = [str((index+1)), x['name'], str(int(x['point'])), x['itAlreadyPay']]
        ranking[index] = aux
    if numberOfRank == 10:
        ranking[9] = ['', '...','', '']
        for index,x in enumerate(elements):
            if str(x['name']) == str(name):
                ranking[10] = [str(index+8), name, str(int(x['point'])), x['itAlreadyPay']]

    ranking_json = json.dumps(ranking)
    return ranking_json
    

@app.route("/user/login", methods=['POST'])
def getDataLogin():
    user_data = {}
    cursor = mongo.db.login.find_one({'email': request.form['email']})
    data = mongo.db.users.find_one({'name': cursor['username']})
    if cursor == None:
        user_data['error'] = 'Wrong Email'
        user_data['request_result'] = False
        returnData = json.dumps(user_data)
        return returnData

    print(cursor['password'])
    print(request.form['password'])
    if(cursor['password'] == request.form['password']):
        user_data['username'] = data['name']
        user_data['point'] = data['point']
        user_data['itAlreadyFailed'] = data['itAlreadyFailed']
        user_data['isFirstTry'] = data['isFirstTry']
        user_data['request_result'] = True
    else:
        user_data['error'] = 'Wrong Password'
        user_data['request_result'] = False
    
    returnData = json.dumps(user_data)
    return returnData

@app.route("/user/registration", methods=['POST'])
def getDataRegistration():
    user_data = {}
    email = mongo.db.login.find_one({'email': request.form['email']})
    username = mongo.db.login.find_one({'username': request.form['username']})
    print(email == None and username == None)
    if email == None and username == None:
        ciao = mongo.db.login.insert({ 'username': request.form['username'], 'email': request.form['email'], 'password': request.form['password']})
        user_data['username'] = request.form['username']
        user_data['email'] = request.form['email']
        user_data['point'] = 0
        user_data['itAlreadyFailed'] = False
        user_data['isFirstTry'] = True
        user_data['request_result'] = True
        insertNewUser(request.form['username'])
    else: 
        if username != None:
            user_data['error'] = 'Username already Registered'
        else:
            user_data['error'] = 'Email already Registered'
        user_data['request_result'] = False
    print(user_data)
    data = json.dumps(user_data)
    return data

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

def insertNewUser(user):
    mongo.db.users.insert({
        "name": user,
        "point": 0,
        "dateOfLastFlip": datetime.timestamp(datetime.now()),
        "isFirstTry": True,
        "itAlreadyFailed": False,
        "itAlreadyPay": False,
        "probability": 5
    })


if __name__ == '__main__':
    app.run()