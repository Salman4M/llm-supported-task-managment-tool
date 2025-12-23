from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import Dict, Any
from uuid import UUID

from fastapi_mcp import MCPRouter
from core.database import get_db
from core.authentication import get_current_user
from users.models.models_v1 import User
from projects.models.models_v1 import Project, Task

from llm.services.qwen_service_ollama import qwen_service

mcp_router = MCPRouter(
    name="project-status-analyzer",
    version="1.0.0"
)


router = APIRouter(
    prefix="/api/mcp",
    tags=["MCP Status Analysis"]
)


@mcp_router.tool()
async def analyze_project_status(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Analyze project status using AI based on all tasks and subtasks.
    
    This tool fetches a project with all its tasks and subtasks,
    then uses Qwen LLM to intelligently determine the overall
    project status based on task completion.
    
    Args:
        project_id: UUID of the project to analyze
        
    Returns:
        Dictionary with analysis results including:
        - recommended_status: Suggested project status
        - confidence: Confidence score (0-1)
        - reasoning: Explanation of the recommendation
        - completion_percentage: Overall completion percentage
        - task_summary: Summary of task statuses
    """
    try:
        project_uuid = UUID(project_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid project UUID")
    
    # Fetch project with all tasks and subtasks
    project = (
        db.query(Project)
        .options(
            joinedload(Project.tasks)
            .joinedload(Task.subtasks)
        )
        .filter(Project.id == project_uuid)
        .first()
    )
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Convert to dictionary for Qwen
    project_data = {
        "id": str(project.id),
        "name": project.name,
        "description": project.description,
        "status": project.status.value,
        "deadline": str(project.deadline),
        "tasks": [
            {
                "id": task.id,
                "title": task.title,
                "status": task.status.value,
                "deadline": str(task.deadline) if task.deadline else None,
                "subtasks": [
                    {
                        "id": subtask.id,
                        "title": subtask.title,
                        "status": subtask.status.value
                    }
                    for subtask in task.subtasks
                ]
            }
            for task in project.tasks
        ]
    }
    
    analysis = await qwen_service.calculate_project_status(project_data)
    
    analysis["current_status"] = project.status.value
    analysis["project_name"] = project.name
    analysis["total_tasks"] = len(project.tasks)
    
    return analysis

@mcp_router.tool()
async def analyze_task_status(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Analyze task status based on subtasks using AI.
    
    Fetches a task with all subtasks and uses Qwen to determine
    the appropriate task status based on subtask completion.
    
    Args:
        task_id: ID of the task to analyze
        
    Returns:
        Dictionary with:
        - recommended_status: Suggested task status
        - confidence: Confidence score
        - reasoning: Explanation
        - completion_percentage: Percentage of subtasks done
    """
    task = (
        db.query(Task)
        .options(joinedload(Task.subtasks))
        .filter(Task.id == task_id)
        .first()
    )
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_data = {
        "id": task.id,
        "title": task.title,
        "status": task.status.value,
        "deadline": str(task.deadline) if task.deadline else None,
        "subtasks": [
            {
                "id": subtask.id,
                "title": subtask.title,
                "status": subtask.status.value
            }
            for subtask in task.subtasks
        ]
    }
    
    analysis = await qwen_service.calculate_task_status_from_subtasks(task_data)
    
    analysis["current_status"] = task.status.value
    analysis["task_title"] = task.title
    analysis["subtask_count"] = len(task.subtasks)
    
    return analysis

@mcp_router.tool()
async def calculate_project_completion(
    project_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Calculate detailed completion statistics for a project.
    
    Args:
        project_id: UUID of the project
        
    Returns:
        Detailed completion metrics including task breakdown
    """
    try:
        project_uuid = UUID(project_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid project UUID")
    
    project = (
        db.query(Project)
        .options(joinedload(Project.tasks))
        .filter(Project.id == project_uuid)
        .first()
    )
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    tasks = project.tasks
    total_tasks = len(tasks)
    
    if total_tasks == 0:
        return {
            "project_id": str(project.id),
            "project_name": project.name,
            "completion_percentage": 0,
            "tasks_by_status": {},
            "message": "No tasks in project"
        }
    
    # Count tasks by status
    status_counts = {
        "to_do": 0,
        "in_progress": 0,
        "review": 0,
        "done": 0
    }
    
    for task in tasks:
        status = task.status.value
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Calculate completion
    done_count = status_counts["done"]
    completion_pct = (done_count / total_tasks) * 100
    
    return {
        "project_id": str(project.id),
        "project_name": project.name,
        "total_tasks": total_tasks,
        "completion_percentage": round(completion_pct, 2),
        "tasks_by_status": status_counts,
        "done_tasks": done_count,
        "remaining_tasks": total_tasks - done_count
    }


@mcp_router.tool()
async def update_project_status_intelligent(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Automatically update project status based on AI analysis.
    
    This tool analyzes the project and updates its status
    to the recommended status if confidence is high enough.
    
    Args:
        project_id: UUID of the project
        
    Returns:
        Update result with old and new status
    """
    analysis = await analyze_project_status(project_id, db, current_user)
    
    recommended = analysis.get("recommended_status")
    confidence = analysis.get("confidence", 0)
    
    # Only update if confidence is high
    if confidence < 0.7:
        return {
            "updated": False,
            "reason": f"Confidence too low ({confidence:.2f})",
            "recommendation": recommended,
            "current_status": analysis["current_status"]
        }
    
    try:
        project_uuid = UUID(project_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid project UUID")
    
    project = db.query(Project).filter(Project.id == project_uuid).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    old_status = project.status.value
    
    from projects.utils.enum import Status
    
    # Update status
    project.status = Status[recommended]
    db.commit()
    
    return {
        "updated": True,
        "old_status": old_status,
        "new_status": recommended,
        "confidence": confidence,
        "reasoning": analysis.get("reasoning"),
        "project_name": project.name
    }


# HTTP endpoints for testing
@router.post("/analyze-project/{project_id}")
async def http_analyze_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """HTTP endpoint wrapper for project analysis"""
    return await analyze_project_status(project_id, db, current_user)


@router.post("/analyze-task/{task_id}")
async def http_analyze_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """HTTP endpoint wrapper for task analysis"""
    return await analyze_task_status(task_id, db, current_user)


@router.get("/project-completion/{project_id}")
async def http_project_completion(
    project_id: str,
    db: Session = Depends(get_db)
):
    """HTTP endpoint for completion statistics"""
    return await calculate_project_completion(project_id, db)


@router.post("/update-project-status/{project_id}")
async def http_update_project_status(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """HTTP endpoint for intelligent status update"""
    return await update_project_status_intelligent(project_id, db, current_user)


