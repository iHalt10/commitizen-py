from datetime import datetime


class User:
    def __init__(self, name: str, email: str, unix_time: int):
        self.name = name
        self.email = email
        self.datetime = datetime.fromtimestamp(unix_time)
