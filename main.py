import uvicorn
from fastapi import FastAPI
from users.routes.routes_v1 import router as users_router
from projects.routes.project_routes_v1 import router as projects_router
from reports.routes.routes_v1 import router as reports_router
from teams.routes.routes_v1 import router as teams_router


from users.models import models_v1
from projects.models import models_v1
from reports.models import models_v1
from teams.models import models_v1


app = FastAPI(title="LLM Task Manager")


app.include_router(users_router, prefix="/users")
app.include_router(projects_router, prefix="/projects")
app.include_router(reports_router, prefix="/reports")
app.include_router(teams_router, prefix="/teams")


# def main():
#     print("Hello from llm-app!")


def main():
    # This runs the server when you type "python main.py"
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()


