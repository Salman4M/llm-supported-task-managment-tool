# Team App

## Overview
The **Team App** is responsible for managing teams and team members inside the project management system. It controls who can create teams, who can manage members, and how users are connected to teams.

This app works closely with **Users**, **Projects**, and **Tasks** apps.

---

## Roles and Permissions

### Product Owner (PO / Admin)
- Create teams
- Update team information
- View all teams

### Team Lead (Subadmin)
- Add members to a team
- Remove members from a team
- Manage team composition

### Member
- Can belong to multiple teams
- Has no permission to manage teams or members

---

## Team Model

### Fields (Example)
- `id` – Unique team ID
- `name` – Team name
- `description` – Short team description
- `project` – Related project
- `team_lead` – User who manages the team
- `members` – List of users in the team
- `created_at` – Creation time
- `updated_at` – Last update time

---

## Core Features

### Team Creation
- Only **PO (Admin)** can create a team
- A team must belong to a project
- A team has exactly one team lead

### Team Update
- Only **PO (Admin)** can update team details (name, description, project)

### Add / Remove Members
- Only **Team Lead** can:
  - Add members to the team
  - Remove members from the team
- A member can belong to multiple teams at the same time

---

## Business Rules
- One team has one team lead
- Members can be part of many teams
- Team lead must be a valid project member
- Team actions are protected by role-based permissions

---

## API Endpoints (Example)

### Create Team
`POST /teams/`
- Permission: Admin (PO)

### Update Team
`PUT /teams/{id}/`
- Permission: Admin (PO)

### Add Member
`POST /teams/{id}/add-member/`
- Permission: Team Lead

### Remove Member
`POST /teams/{id}/remove-member/`
- Permission: Team Lead

### List My Teams
`GET /teams/my/`
- Permission: Authenticated user

---

## Permissions Summary

| Action | Admin (PO) | Team Lead | Member |
|------|-----------|-----------|--------|
| Create team | ✅ | ❌ | ❌ |
| Update team | ✅ | ❌ | ❌ |
| Add member | ❌ | ✅ | ❌ |
| Remove member | ❌ | ✅ | ❌ |
| View own teams | ✅ | ✅ | ✅ |

---

## Notes
- Team App does **not** manage tasks or reports directly
- It only defines team structure and member relations
- Other apps use this data for authorization and filtering

---

## Future Improvements
- Team activity logs
- Multiple team leads (optional)
- Team performance statistics

