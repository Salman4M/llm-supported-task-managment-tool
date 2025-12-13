from enum import Enum


class Status(str, Enum):
    to_do = "to_do"
    in_progress = "in_progress"
    review = "review"
    done = "done"
