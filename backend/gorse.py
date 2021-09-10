from collections import namedtuple
from datetime import datetime
from typing import List

import requests

Success = namedtuple("Success", ["RowAffected"])


class GorseException(BaseException):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message


class Gorse:
    def __init__(self, entry_point: str, api_key: str):
        self.entry_point = entry_point
        self.api_key = api_key

    def insert_feedback(
        self, feedback_type: str, user_id: str, item_id: str
    ) -> Success:
        r = requests.post(
            self.entry_point + "/api/feedback",
            headers={"X-API-Key": self.api_key},
            json=[
                {
                    "FeedbackType": feedback_type,
                    "UserId": user_id,
                    "ItemId": item_id,
                    "Timestamp": datetime.now().isoformat(),
                }
            ],
        )
        if r.status_code == 200:
            return r.json()
        raise GorseException(r.status_code, r.text)

    def get_recommend(self, user_id: str, n: int = 1) -> List[str]:
        r = requests.get(
            self.entry_point + "/api/recommend/%s?n=%d" % (user_id, n),
            headers={"X-API-Key": self.api_key},
        )
        if r.status_code == 200:
            return r.json()
        raise GorseException(r.status_code, r.text)

    def insert_feedbacks(self, feedbacks) -> Success:
        r = requests.post(
            self.entry_point + "/api/feedback",
            headers={"X-API-Key": self.api_key},
            json=feedbacks,
        )
        if r.status_code == 200:
            return r.json()
        raise GorseException(r.status_code, r.text)

    def insert_item(self, item) -> Success:
        r = requests.post(
            self.entry_point + "/api/item",
            headers={"X-API-Key": self.api_key},
            json=item,
        )
        if r.status_code == 200:
            return r.json()
        raise GorseException(r.status_code, r.text)

    def insert_user(self, user) -> Success:
        r = requests.post(
            self.entry_point + "/api/user",
            headers={"X-API-Key": self.api_key},
            json=user,
        )
        if r.status_code == 200:
            return r.json()
        raise GorseException(r.status_code, r.text)
