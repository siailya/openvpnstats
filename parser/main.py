import datetime
import os

import telebot
from apscheduler.schedulers.background import BackgroundScheduler
from pymongo import MongoClient
from pymongo.collection import Collection

from OVPNInterface import OVPNInterface

client = MongoClient(os.environ["DB_CONN"])
db = client["openvpnstats"]
bot = telebot.TeleBot(os.environ["TG_TOKEN"])
TRAFFIC_THRESHOLD = 8
NOTIFY_TG_ID = os.environ["TG_ID"]


def main(ovpn_interface: OVPNInterface):
    connected_users = ovpn_interface.status().parse_users()

    print(f"Parsed {len(connected_users)} users: {[u.user_name for u in connected_users]}")


def set_users_status(stat_coll: Collection, ovpn_interface: OVPNInterface):
    connected_users = [u.user_name for u in ovpn_interface.status().parse_users()]

    stat_coll.update_many({"user_name": {"$nin": connected_users}},
                          {"$set": {"connected": False}})

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
        return

    data = data[0]
    data["received"] = data["received"] / 1024 / 1024
    data["send"] = data["send"] / 1024 / 1024

    if (data["received"] + data["send"]) / 60 / 60 * 8 > TRAFFIC_THRESHOLD:
        bot.send_message(NOTIFY_TG_ID,
                         f'Скорость трафика превышена!'
                         f'\n'
                         f'Скорость за последний час - {(data["received"] + data["send"]) / 60 / 60 * 8}Мбит/с')

    print(f"Change connection status for users who offline")


if __name__ == '__main__':
    ovpn = OVPNInterface(db=db,
                         port=(os.environ["MANAGEMENT_PORT"] or 5555),
                         host=(os.environ["MANAGEMENT_HOST"] or "localhost"))
    ovpn.login(bytes(os.environ["MANAGEMENT_PASSWORD"], "utf-8"))

    print("Logged in to OpenVPN interface")

    print("Starting parser")
    main(ovpn)
    set_users_status(db["users"], ovpn)

    scheduler = BackgroundScheduler(daemon=False)
    scheduler.add_job(main, 'interval', [ovpn], minutes=1)
    scheduler.add_job(set_users_status, "interval", [db["users"], ovpn], minutes=5)
    scheduler.start()
