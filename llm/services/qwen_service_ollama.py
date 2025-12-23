import httpx
import os
from typing import List, Dict, Any
from fastapi import HTTPException
import json
from core.config import settings

class QwenService:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        self.api_key = settings.OLLAMA_API_KEY
        self.timeout = settings.OLLAMA_TIMEOUT

    
    async def calculate_project_status(
            self,
            project_data:Dict[str, Any]
        ) -> Dict[str, Any]:
        """
        Use Qwen via Ollama to analyze project tasks and determine overall project status
        
        Args:
            project_data: Dictionary containing project info with tasks and subtasks
            
        Returns:
            Dictionary with recommended status and reasoning
        """

        prompt = self._build_status_prompt(project_data)
        try:
            async with httpx.AsyncClient() as client:
                response=await client.post(
                    self.base_url,
                    headers={
                        "Content-Type":"application/json"
                    },
                    json={
                        "model":self.model,
                        "messages": [
                            {
                            "role":"system",
                            "content":"You are aproject management expert. Analyze task statuses and provide status recommendations in JSON format only.Always respond with valid JSON"
                            },
                            {
                                "role":"user",
                                "content":prompt
                            }
                        ],
                        "temperature":0.3,
                        "stream":False
                    },
                    timeout=self.timeout
                )
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Ollama api error :{response.text}"
                    )
                result = response.json()
                analysis=self._parse_ollama_response(result)
                return analysis
            
        except httpx.TimeoutException:
            print("Ollama timeout, using fallback calculation")
            return self._fallback_status_calculation_project(project_data)
        except httpx.RequestError as e:
            print(f"Ollama connection error {e}, using fallback ")
            return self._fallback_status_calculation_project(project_data)
    
    async def calculate_task_status_from_subtask(
            self,
            task_data: Dict[str,Any]
    ) -> Dict[str,Any]:
        """
        Calculate task status based on subtask statuses using Qwen via Ollama
        
        Args:
            task_data: Dictionary with task info including subtasks
            
        Returns:
            Dictionary with recommended task status
        """
        prompt = f"""
        Analyze this task and its subtasks to determine the appropriate status.

        Task: {task_data.get('title')}
        Current Status: {task_data.get('status')}
        Total Subtasks: {len(task_data.get('subtasks', []))}

        Subtask Statuses:
        {self._format_subtasks(task_data.get('subtasks', []))}

        Rules:
        - If all subtasks are "done", task should be "done"
        - If majority are "in_progress", task should be "in_progress"
        - If most are "to_do", task should be "to_do"
        - If any are "in_progress" and some "done", task should be "in_progress"
        - Consider "review" status for completed but unverified work

        Respond with JSON only (no markdown, no explanation):
        {{
            "recommended_status": "to_do|in_progress|review|done",
            "confidence": 0.0-1.0,
            "reasoning": "brief explanation",
            "completion_percentage": 0-100
        }}
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    headers={
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "Respond only with valid JSON. No markdown formatting."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.3,
                        "stream": False
                    },
                    timeout=self.timeout
                )
                
                result = response.json()
                return self._parse_ollama_response(result)
                
        except Exception as e:
            print(f"⚠️  Ollama error: {e}, using fallback")
            return self._fallback_status_calculation(task_data)
        
    def _build_status_prompt(self, project_data: Dict[str,Any])->str:
        """Build a detailed prompt for Qwen to analyze project status"""

        tasks = project_data.get("tasks",[])
        task_summary = self._summarize_tasks(tasks)
        
        prompt = f"""
        Analyze this project and recommend an overall status.

        Project: {project_data.get('name')}
        Current Status: {project_data.get('status')}
        Deadline: {project_data.get('deadline')}
        Total Tasks: {len(tasks)}

        Task Status Summary:
        {task_summary}

        Detailed Task Information:
        {self._format_tasks_detail(tasks)}

        Please analyze and respond with JSON only (no markdown, no code blocks):
        {{
            "recommended_status": "to_do|in_progress|review|done",
            "confidence": 0.0-1.0,
            "reasoning": "detailed explanation",
            "risk_level": "low|medium|high",
            "completion_percentage": 0-100,
            "recommendations": ["action item 1", "action item 2"]
        }}
        """
        return prompt
    
    def _summarize_tasks(self,tasks: List[Dict])-> str:
        "Create a summary of task statuses"
        status_counts = {
            "to_do":0,
            "in_progress":0,
            "review":0,
            "done":0
        }

        for task in tasks:
            status=task.get('status','to_do')
            status_counts[status]=status_counts.get(status,0)+1
        
        total = len(tasks)
        summary=[]
        for status,count in status_counts.items():
            percentage = (count/ total*100) if total>0 else 0
            summary.append(f"-{status}:{count} ({percentage:.1f}%)")

        return "\n".join(summary)

    
    def _format_tasks_detail(self,tasks:List[Dict])->str:
        """Format tasks for prompt"""
        details=[]
        for i,task in enumerate(tasks[:15],1):
            subtasks=task.get('subtasks',[])
            details.append(
                f"{i}.{task.get('title')} -Status: {task.get('status')}"
                f"(Subtasks:{len(subtasks)})"
            )
        if len(subtasks)>15:
            details.append(f".. and {len(tasks)-15} more tasks ")

        return "\n".join(details)
            
    def _format_subtasks(self,subtasks:List[Dict])->str:
        """Format subtaks for the prompt"""
        if not subtasks:
            return "no subtasks"

        formatted=[]
        for i,subtask in enumerate(subtasks,1):
            formatted.append(
                f"{i}. {subtask.get('title')}-{subtask.get('status')}"
            )
        return "\n".join(formatted)
    

    def _parse_ollama_response(self, response_data: Dict) -> Dict[str, Any]:
        """Parse Ollama API response and extract JSON"""
        try:
            # Ollama uses OpenAI-compatible format
            choices = response_data.get('choices', [])
            
            if not choices:
                raise ValueError("No choices in response")
            
            message = choices[0].get('message', {})
            content = message.get('content', '')
            
            content = content.strip()
            
            # when you tell llm to give response in json format it gives response like: ```json
            # to remove that markdowns
            if content.startswith('```json'):
                content = content[7:]
            elif content.startswith('```'):
                content = content[3:]
            
            if content.endswith('```'):
                content = content[:-3]
            
            content = content.strip()
            
            # Parse JSON
            result = json.loads(content)
            
            if 'recommended_status' not in result:
                raise ValueError("Missing recommended_status in response")
            
            # confidence has to be between 0 and 1 to make it consistent
            if 'confidence' in result:
                result['confidence'] = float(result['confidence'])
                result['confidence'] = max(0.0, min(1.0, result['confidence']))
            else:
                result['confidence'] = 0.7  # Default confidence
            
            return result
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Failed to parse Ollama response: {e}")
            print(f"Raw content: {content[:200] if 'content' in locals() else 'N/A'}")
            
            return {
                "recommended_status": "in_progress",
                "confidence": 0.5,
                "reasoning": f"Unable to parse LLM response: {str(e)[:100]}",
                "error": str(e)
            }

    def _fallback_status_calculation(self, task_data: Dict) -> Dict[str, Any]:
        """Rule-based fallback if Ollama is unavailable"""
        subtasks = task_data.get('subtasks', [])
        
        if not subtasks:
            return {
                "recommended_status": task_data.get('status', 'to_do'),
                "confidence": 1.0,
                "reasoning": "No subtasks, keeping current status",
                "completion_percentage": 0,
                "fallback": True
            }
        
        status_counts = {}
        for subtask in subtasks:
            status = subtask.get('status', 'to_do')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        total = len(subtasks)
        done_count = status_counts.get('done', 0)
        in_progress_count = status_counts.get('in_progress', 0)
        review_count = status_counts.get('review', 0)
        
        completion_pct = (done_count / total * 100) if total > 0 else 0
        
        if done_count == total:
            recommended = "done"
            reasoning = "All subtasks completed"
        elif (done_count + review_count) == total:
            recommended = "review"
            reasoning = f"{done_count} done, {review_count} in review"
        elif in_progress_count > 0 or done_count > 0:
            recommended = "in_progress"
            reasoning = f"{done_count}/{total} subtasks done, {in_progress_count} in progress"
        else:
            recommended = "to_do"
            reasoning = "No subtasks started"
        
        return {
            "recommended_status": recommended,
            "confidence": 0.9,
            "reasoning": reasoning,
            "completion_percentage": int(completion_pct),
            "fallback": True
        }
    
    def _fallback_status_calculation_project(self, project_data: Dict) -> Dict[str, Any]:
        """Rule-based fallback for project status"""
        tasks = project_data.get('tasks', [])
        
        if not tasks:
            return {
                "recommended_status": project_data.get('status', 'to_do'),
                "confidence": 1.0,
                "reasoning": "No tasks in project",
                "completion_percentage": 0,
                "fallback": True
            }
        
        status_counts = {
            'to_do': 0,
            'in_progress': 0,
            'review': 0,
            'done': 0
        }
        
        for task in tasks:
            status = task.get('status', 'to_do')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        total = len(tasks)
        done = status_counts['done']
        in_progress = status_counts['in_progress']
        review = status_counts['review']
        
        completion_pct = (done / total * 100) if total > 0 else 0
        
        if done == total:
            recommended = "done"
            reasoning = "All tasks completed"
        elif (done + review) == total:
            recommended = "review"
            reasoning = f"{done} done, {review} in review"
        elif in_progress > 0 or done > 0:
            recommended = "in_progress"
            reasoning = f"{completion_pct:.0f}% complete, {in_progress} tasks in progress"
        else:
            recommended = "to_do"
            reasoning = "No tasks started"
        
        return {
            "recommended_status": recommended,
            "confidence": 0.85,
            "reasoning": reasoning,
            "completion_percentage": int(completion_pct),
            "risk_level": "low" if completion_pct > 50 else "medium",
            "recommendations": [],
            "fallback": True
        }


qwen_service = QwenService()


