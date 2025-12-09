
from enum import Enum

# Enum for user roles (static-based)
class UserRole(str, Enum):
    team_lead = "team_lead"
    team_user = "team_user"
    project_owner = "project_owner"


