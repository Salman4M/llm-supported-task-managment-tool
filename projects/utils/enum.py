
from enum import Enum


class ProjectStatus(str, Enum):
    to_do = "to_do"
    in_progress = "in_progress"
    review = "review"
    done = "done"
