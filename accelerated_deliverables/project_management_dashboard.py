#!/usr/bin/env python3
"""
项目管理仪表板 v1.0
专业级项目进度跟踪、资源管理、风险监控、团队协作系统
"""

import json
import datetime
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
import hashlib
import statistics
from enum import Enum

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """任务状态枚举"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"

class Priority(Enum):
    """优先级枚举"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class TeamMember:
    """团队成员数据结构"""
    member_id: str
    name: str
    role: str
    email: str
    skills: List[str]
    capacity_hours: float  # 每周可用小时数
    current_load: float = 0.0
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "member_id": self.member_id,
            "name": self.name,
            "role": self.role,
            "email": self.email,
            "skills": self.skills,
            "capacity_hours": self.capacity_hours,
            "current_load": round(self.current_load, 2),
            "utilization_percentage": self.calculate_utilization(),
            "availability": self.calculate_availability()
        }
    
    def calculate_utilization(self) -> float:
        """计算利用率"""
        if self.capacity_hours == 0:
            return 0.0
        return round((self.current_load / self.capacity_hours) * 100, 2)
    
    def calculate_availability(self) -> str:
        """计算可用性状态"""
        utilization = self.calculate_utilization()
        if utilization >= 90:
            return "overloaded"
        elif utilization >= 70:
            return "busy"
        elif utilization >= 40:
            return "optimal"
        else:
            return "available"

@dataclass
class ProjectTask:
    """项目任务数据结构"""
    task_id: str
    title: str
    description: str
    project_id: str
    assignee_id: str
    status: TaskStatus
    priority: Priority
    estimated_hours: float
    actual_hours: float = 0.0
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    dependencies: List[str] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.tags is None:
            self.tags = []
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "project_id": self.project_id,
            "assignee_id": self.assignee_id,
            "status": self.status.value,
            "priority": self.priority.value,
            "estimated_hours": round(self.estimated_hours, 2),
            "actual_hours": round(self.actual_hours, 2),
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completed_date": self.completed_date.isoformat() if self.completed_date else None,
            "dependencies": self.dependencies,
            "tags": self.tags,
            "progress_percentage": self.calculate_progress(),
            "is_overdue": self.is_overdue(),
            "is_blocked": self.is_blocked(),
            "remaining_hours": self.calculate_remaining_hours()
        }
    
    def calculate_progress(self) -> float:
        """计算进度百分比"""
        if self.status == TaskStatus.COMPLETED:
            return 100.0
        elif self.status == TaskStatus.NOT_STARTED:
            return 0.0
        elif self.estimated_hours > 0:
            return round((self.actual_hours / self.estimated_hours) * 100, 2)
        else:
            return 0.0
    
    def is_overdue(self) -> bool:
        """检查是否逾期"""
        if self.due_date and self.status != TaskStatus.COMPLETED:
            return datetime.utcnow() > self.due_date
        return False
    
    def is_blocked(self) -> bool:
        """检查是否被阻塞"""
        return self.status == TaskStatus.BLOCKED
    
    def calculate_remaining_hours(self) -> float:
        """计算剩余工时"""
        return max(0, self.estimated_hours - self.actual_hours)

@dataclass
class Project:
    """项目数据结构"""
    project_id: str
    name: str
    description: str
    owner_id: str
    start_date: datetime
    end_date: datetime
    budget: float
    status: str  # 'planning', 'active', 'on_hold', 'completed', 'cancelled'
    tasks: List[ProjectTask] = None
    team_members: List[str] = None
    risks: List[Dict] = None
    
    def __post_init__(self):
        if self.tasks is None:
            self.tasks = []
        if self.team_members is None:
            self.team_members = []
        if self.risks is None:
            self.risks = []
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "project_id": self.project_id,
            "name": self.name,
            "description": self.description,
            "owner_id": self.owner_id,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "budget": round(self.budget, 2),
            "status": self.status,
            "team_members": self.team_members,
            "tasks": [task.to_dict() for task in self.tasks],
            "risks": self.risks,
            "metrics": self.calculate_metrics(),
            "timeline": self.calculate_timeline()
        }
    
    def calculate_metrics(self) -> Dict:
        """计算项目指标"""
        total_tasks = len(self.tasks)
        completed_tasks = sum(1 for t in self.tasks if t.status == TaskStatus.COMPLETED)
        
        total_estimated_hours = sum(t.estimated_hours for t in self.tasks)
        total_actual_hours = sum(t.actual_hours for t in self.tasks)
        
        overdue_tasks = sum(1 for t in self.tasks if t.is_overdue())
        blocked_tasks = sum(1 for t in self.tasks if t.is_blocked())
        
        # 计算进度
        if total_tasks > 0:
            completion_percentage = (completed_tasks / total_tasks) * 100
        else:
            completion_percentage = 0.0
        
        # 计算预算使用率
        if self.budget > 0:
            # 假设每小时成本为$50
            cost_per_hour = 50
            spent_budget = total_actual_hours * cost_per_hour
            budget_utilization = (spent_budget / self.budget) * 100
        else:
            spent_budget = 0
            budget_utilization = 0.0
        
        # 计算时间进度
        total_duration = (self.end_date - self.start_date).days
        elapsed_days = (datetime.utcnow() - self.start_date).days
        
        if total_duration > 0:
            time_progress = (elapsed_days / total_duration) * 100
        else:
            time_progress = 0.0
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": sum(1 for t in self.tasks if t.status == TaskStatus.IN_PROGRESS),
            "overdue_tasks": overdue_tasks,
            "blocked_tasks": blocked_tasks,
            "completion_percentage": round(completion_percentage, 2),
            "total_estimated_hours": round(total_estimated_hours, 2),
            "total_actual_hours": round(total_actual_hours, 2),
            "spent_budget": round(spent_budget, 2),
            "budget_utilization": round(budget_utilization, 2),
            "time_progress": round(time_progress, 2),
            "schedule_variance": round(completion_percentage - time_progress, 2),
            "health_score": self.calculate_health_score(completion_percentage, time_progress, budget_utilization)
        }
    
    def calculate_health_score(self, completion: float, time_progress: float, budget_utilization: float) -> float:
        """计算项目健康分数"""
        # 进度偏差
        schedule_variance = completion - time_progress
        
        # 预算偏差 (假设目标预算利用率为100%)
        budget_variance = 100 - budget_utilization
        
        # 计算分数 (0-100)
        schedule_score = max(0, 100 - abs(schedule_variance) * 2)
        budget_score = max(0, 100 - abs(budget_variance) * 0.5)
        
        # 阻塞任务扣分
        blocked_penalty = sum(1 for t in self.tasks if t.is_blocked()) * 5
        
        # 逾期任务扣分
        overdue_penalty = sum(1 for t in self.tasks if t.is_overdue()) * 10
        
        base_score = (schedule_score * 0.4) + (budget_score * 0.3) + (completion * 0.3)
        final_score = max(0, base_score - blocked_penalty - overdue_penalty)
        
        return round(final_score, 2)
    
    def calculate_timeline(self) -> Dict:
        """计算时间线"""
        today = datetime.utcnow()
        
        # 计算关键日期
        milestones = []
        for task in self.tasks:
            if task.due_date:
                milestones.append({
                    "date": task.due_date.isoformat(),
                    "title": task.title,
                    "type": "task_due",
                    "status": task.status.value
                })
        
        # 添加项目里程碑
        milestones.append({
            "date": self.start_date.isoformat(),
            "title": "项目启动",
            "type": "project_start",
            "status": "completed" if today >= self.start_date else "upcoming"
        })
        
        milestones.append({
            "date": self.end_date.isoformat(),
            "title": "项目结束",
            "type": "project_end",
            "status": "completed" if today >= self.end_date else "upcoming"
        })
        
        # 按日期排序
        milestones.sort(key=lambda x: x["date"])
        
        return {
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "current_date": today.isoformat(),
            "days_remaining": max(0, (self.end_date - today).days),
            "milestones": milestones
        }

class ProjectManagementDashboard:
    """项目管理仪表板核心类"""
    
    def __init__(self, config_path: str = None):
        """
        初始化项目管理仪表板
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.projects = {}
        self.team_members = {}
        self.notifications = []
        
        logger.info("项目管理仪表板初始化完成")
    
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        default_config = {
            "dashboard": {
                "refresh_interval_seconds": 60,
                "auto_save": True,
                "save_interval_minutes": 5
            },
            "notifications": {
                "enabled": True,
                "email_alerts": True,
                "slack_alerts": True,
                "browser_notifications": True
            },
            "reporting": {
                "daily_report": True,
                "weekly_report": True,
                "monthly_report": True,
                "generate_pdf": True
            },
            "integrations": {
                "jira": False,
                "asana": False,
                "trello": False,
                "github": True,
                "gitlab": False
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    self._merge_dicts(default_config, user_config)
            except Exception as e:
                logger.warning(f"加载配置文件失败: {e}, 使用默认配置")
        
        return default_config
    
    def _merge_dicts(self, base: Dict, update: Dict):
        """递归合并字典"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_dicts(base[key], value)
            else:
                base[key] = value
    
    def add_team_member(self, member: TeamMember) -> bool:
        """
        添加团队成员
        
        Args:
            member: 团队成员
            
        Returns:
            添加是否成功
        """
        try:
            self.team_members[member.member_id] = member
            logger.info(f"团队成员添加成功: {member.name}")
            return True
        except Exception as e:
            logger.error(f"添加团队成员失败: {e}")
            return False
    
    def create_project(self, project: Project) -> bool:
        """
        创建项目
        
        Args:
            project: 项目
            
        Returns:
            创建是否成功
        """
        try:
            self.projects[project.project_id] = project
            logger.info(f"项目创建成功: {project.name}")
            return True
        except Exception as e:
            logger.error(f"创建项目失败: {e}")
            return False
    
    def add_task_to_project(self, project_id: str, task: ProjectTask) -> bool:
        """
        添加任务到项目
        
        Args:
            project_id: 项目ID
            task: 任务
            
        Returns:
            添加是否成功
        """
        if project_id not in self.projects:
            logger.error(f"项目不存在: {project_id}")
            return False
        
        try:
            self.projects[project_id].tasks.append(task)
            
            # 更新团队成员负载
            if task.assignee_id in self.team_members:
                member = self.team_members[task.assignee_id]
                member.current_load += task.estimated_hours
            
            logger.info(f"任务添加成功: {task.title}")
            return True
        except Exception as e:
            logger.error(f"添加任务失败: {e}")
            return False
    
    def update_task_status(self, project_id: str, task_id: str, status: TaskStatus, actual_hours: float = None) -> bool:
        """
        更新任务状态
        
        Args:
            project_id: 项目ID
            task_id: 任务ID
            status: 新状态
            actual_hours: 实际工时
            
        Returns:
            更新是否成功
        """
        if project_id not in self.projects:
            logger.error(f"项目不存在: {project_id}")
            return False
        
        project = self.projects[project_id]
        task = next((t for t in project.tasks if t.task_id == task_id), None)
        
        if not task:
            logger.error(f"任务不存在: {task_id}")
            return False
        
        try:
            old_status = task.status
            task.status = status
            
            if status == TaskStatus.COMPLETED:
                task.completed_date = datetime.utcnow()
            
            if actual_hours is not None:
                task.actual_hours = actual_hours
            
            # 发送通知
            if old_status != status:
                self._send_notification(
                    f"任务状态更新: {task.title}",
                    f"状态从 {old_status.value} 变更为 {status.value}",
                    "task_update"
                )
            
            logger.info(f"任务状态更新成功: {task.title} -> {status.value}")
            return True
        except Exception as e:
            logger.error(f"更新任务状态失败: {e}")
            return False
    
    def get_project_dashboard(self, project_id: str) -> Dict:
        """
        获取项目仪表板数据
        
        Args:
            project_id: 项目ID
            
        Returns:
            仪表板数据
        """
        if project_id not in self.projects:
            logger.error(f"项目不存在: {project_id}")
            return {}
        
        project = self.projects[project_id]
        
        # 计算团队负载
        team_load = {}
        for member_id in project.team_members:
            if member_id in self.team_members:
                member = self.team_members[member_id]
                team_load[member_id] = {
                    "name": member.name,
                    "role": member.role,
                    "utilization": member.calculate_utilization(),
                    "availability": member.calculate_availability()
                }
        
        # 计算任务分布
        task_distribution = {
            "not_started": 0,
            "in_progress": 0,
            "review": 0,
            "completed": 0,
            "blocked": 0,
            "cancelled": 0
        }
        
        for task in project.tasks:
            task_distribution[task.status.value] += 1
        
        # 计算优先级分布
        priority_distribution = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }