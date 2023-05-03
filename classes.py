from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    user_id: int
    money: int
    reward_datetime: datetime

