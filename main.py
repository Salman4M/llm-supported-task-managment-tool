import uvicorn
from fastapi import FastAPI
from users.routes.routes_v1 import router as users_router
from projects.routes.routes_v1 import router as projects_router
from reports.routes.routes_v1 import router as reports_router


app = FastAPI(title="LLM Task Manager")


app.include_router(users_router, prefix = "/users")
app.include_router(projects_router, prefix = "/projects")
app.include_router(reports_router,prefix = "/reports")

# def main():
#     print("Hello from llm-app!")

def main():
    # This runs the server when you type "python main.py"
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
