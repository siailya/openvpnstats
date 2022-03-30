import datetime
import telnetlib
from datetime import datetime as dt
from enum import Enum
from typing import Union, List

import pymongo
from pymongo.database import Database


class OVPNInterfaceState(Enum):
    pending_login = 0
    ready = 1
    pending_output = 2
    unsuccessful_login = 3


class OVPNUser:
    def __init__(self, user_name: str, connected_since: datetime.datetime, received: int, send: int, db: Database,
                 auto_update: bool = True):
        self.user_name = user_name
        self.connected_since = connected_since
        self.received = received
        self.send = send
        self.db = db

        if auto_update:
            self.update()

    def update(self, start: int = None, received: int = None, send: int = None):
        if start is None:
            start = self.connected_since
        if received is None:
            received = self.received
        if send is None:
            send = self.send

        self.connected_since = start
        self.received = received
        self.send = send

        last_segment = list(self.db["segments"]
                            .find({"user_name": self.user_name})
                            .sort("time", pymongo.DESCENDING)
                            .limit(1))
        if len(last_segment) > 0:
            last_segment = last_segment[0]
        else:
            last_segment = {
                "time": dt.now(),
                "received": 0,
                "send": 0
            }

        self.db["segments"].insert_one({
            "user_name": self.user_name,
            "time": dt.now(),
            "connected_since": self.connected_since,
            "received": self.received,
            "send": self.send,
            "d_time": (dt.now() - last_segment["time"]).total_seconds(),
            "d_received": self.received - last_segment["received"],
            "d_send": self.send - last_segment["send"]
        })

        self.db["sessions"].update_one(
            {
                "user_name": self.user_name,
                "connected_since": self.connected_since
            },
            {
                "$set": {
                    "user_name": self.user_name,
                    "connected_since": self.connected_since,
                    "received": self.received,
                    "send": self.send
                }
            }, upsert=True)

        self.db["users"].update_one(
            {
                "user_name": self.user_name
            },
            {
                "$set": {"connected": True}
            }, upsert=True)


class OVPNStatus:
    def __init__(self, raw_status: bytes, db: Database):
        self.raw_status = raw_status
        self.db = db
        self.parsed = {}

    def __get_raw(self) -> bytes:
        return self.__get_raw()

    def _filter_users(self):
        decoded_status = self.raw_status.decode("u8")
        users_data = list(filter(lambda line_data: line_data.startswith("CLIENT_LIST"), decoded_status.split("\n")))

        return users_data

    def parse_users(self) -> List[OVPNUser]:
        users_raw = self._filter_users()
        users = []

        for user in users_raw:
            _, name, common_ip, internal_ip, _, send, received, _, connected_since_iso = user.split(",")[:9]
            ovpn_user = OVPNUser(name, dt.fromtimestamp(int(connected_since_iso)), int(received), int(send), self.db)
            users.append(ovpn_user)

        return users


class OVPNInterface:
    def __init__(self, host="localhost", port=5555, db: Database = None):
        self.db = db
        self.tn = telnetlib.Telnet(host, port)
        self.state = OVPNInterfaceState.pending_login

    def close(self):
        self.tn.close()

    def login(self, password: bytes):
        self.tn.read_until(b"ENTER PASSWORD:")
        self.tn.write(password + b"\n")

        is_successful = self.tn.read_until(b"SUCCESS: password is correct",
                                           timeout=2) == b"SUCCESS: password is correct"

        if is_successful:
            self.__set_state(OVPNInterfaceState.ready)
        else:
            self.__set_state(OVPNInterfaceState.unsuccessful_login)

        return is_successful

    def _execute(self, command: bytes, expected: bytes = b"", timeout: int = 2) -> Union[bytes, bool]:
        if self.__get_state() == OVPNInterfaceState.ready:
            self.tn.write(command.strip(b"\n") + b"\n")
            result = self.tn.read_until(expected, timeout=timeout)
            if "END" in result.decode("u8"):
                return result
        return False

    def __get_state(self) -> OVPNInterfaceState:
        return self.state

    def __set_state(self, state: OVPNInterfaceState):
        self.state = state

    def status(self) -> OVPNStatus:
        return OVPNStatus(self._execute(b"status", b"END"), self.db)
