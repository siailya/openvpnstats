import datetime
import os

import pymongo
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__, static_folder="/client/dist/assets")
CORS(app)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

client = MongoClient(os.environ["DB_CONN"])
db = client["openvpnstats"]


@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.cache_control.max_age = 0
    return r


@app.get("/")
def index():
    return send_from_directory("client/dist", "index.html")


@app.get("/status")
def status():
    return "Okay"


@app.get("/api/get_stat")
def get_stat():
    online = db["users"].count_documents({"connected": True})
    data = list(db["segments"].aggregate([
        {
            '$match': {
                'time': {
                    '$gt': (datetime.datetime.now() - datetime.timedelta(minutes=60))
                }
            }
        }, {
            '$group': {
                '_id': None,
                'received': {
                    '$sum': '$d_received'
                },
                'send': {
                    '$sum': '$d_send'
                }
            }
        }, {
            "$project": {
                "_id": 0
            }
        }
    ]))

    if not len(data):
        return {"received": 0, "send": 0, "online": 0}

    data = data[0]
    data["received"] = data["received"] / 1024 / 1024
    data["send"] = data["send"] / 1024 / 1024

    data.update({"online": online})

    return jsonify(data)


@app.get("/api/get_users_info")
def get_users_info():
    users = list(db["users"].find({}, {"user_name": 1, "connected": 1, "_id": 0}))

    for u in users:
        last_session = list(db["sessions"]
                            .find({"user_name": u["user_name"]}, {"_id": 0})
                            .sort("connected_since", pymongo.DESCENDING)
                            .limit(1))[0]
        hour_segments = list(db["segments"].aggregate([
            {
                '$match': {
                    'user_name': u["user_name"],
                    'time': {
                        '$gt': (datetime.datetime.now() - datetime.timedelta(minutes=60))
                    }
                }
            }, {
                '$group': {
                    '_id': None,
                    'received': {
                        '$sum': '$d_received'
                    },
                    'send': {
                        '$sum': '$d_send'
                    }
                }
            }, {
                "$project": {
                    "_id": 0
                }
            }
        ]))

        if not len(hour_segments):
            hour_segments = {}
            hour_segments.update({"received": 0})
            hour_segments.update({"send": 0})
        else:
            hour_segments = hour_segments[0]
            hour_segments["received"] = hour_segments["received"] / 1024 / 1024
            hour_segments["send"] = hour_segments["send"] / 1024 / 1024

        u.update(last_session)
        u.update(hour_segments)

    return jsonify(users)


if __name__ == '__main__':
    app.run()
