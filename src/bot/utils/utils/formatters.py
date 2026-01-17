from datetime import datetime
from typing import List
from ..domain.models.task import TaskResponse
from ..domain.models.timer import TimerResponse
from ..domain.models.statistics import DailyStats, WeeklyStats, TagStats


def format_task(task: TaskResponse) -> str:
    """Format a task for display in the bot"""
    status = "✅" if task.completed else "⏳"
    priority_stars = "⭐" * task.priority
    
    task_str = (
        f"{status} <b>{task.title}</b>\n"
        f"ID: {task.id}\n"
        f"Estimated: {task.estimated_time} min | Actual: {task.actual_time_spent} min\n"
        f"Priority: {priority_stars}\n"
        f"Created: {task.created_at.strftime('%Y-%m-%d %H:%M') if task.created_at else 'N/A'}\n"
    )
    
    if task.description:
        task_str += f"Description: {task.description}\n"
    
    if task.tags:
        tag_names = [tag.name for tag in task.tags]
        task_str += f"Tags: {', '.join(tag_names)}\n"
    
    if task.completed_at:
        task_str += f"Completed: {task.completed_at.strftime('%Y-%m-%d %H:%M')}\n"
    
    return task_str.rstrip()


def format_timer(timer: TimerResponse) -> str:
    """Format a timer session for display in the bot"""
    status = "🟢 Active" if timer.active else "⏹️ Stopped"
    
    timer_str = (
        f"Timer Session #{timer.id}\n"
        f"Status: {status}\n"
        f"Task ID: {timer.task_id}\n"
        f"Start: {timer.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    )
    
    if timer.end_time:
        timer_str += f"End: {timer.end_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    
    if timer.duration:
        timer_str += f"Duration: {timer.duration} minutes\n"
    
    return timer_str.rstrip()


def format_daily_stats(stats: DailyStats) -> str:
    """Format daily statistics for display in the bot"""
    return (
        f"📅 <b>Statistics for {stats.date}</b>\n\n"
        f"⏱️ Time spent: {stats.total_time_spent} minutes\n"
        f"✅ Completed tasks: {stats.completed_tasks}\n"
        f"📝 Active tasks: {stats.active_tasks}"
    )


def format_weekly_stats(stats: WeeklyStats) -> str:
    """Format weekly statistics for display in the bot"""
    stats_str = (
        f"📆 <b>Week's Statistics ({stats.week_start} to {stats.week_end})</b>\n\n"
        f"⏱️ Total time spent: {stats.total_time_spent} minutes\n"
        f"✅ Completed tasks: {stats.completed_tasks}\n\n"
        f"<b>Daily breakdown:</b>\n"
    )
    
    for day_stat in stats.daily_breakdown:
        stats_str += f"  {day_stat.date}: {day_stat.total_time_spent} min, {day_stat.completed_tasks} tasks\n"
    
    return stats_str


def format_tag_stats(tag_stats: List[TagStats]) -> str:
    """Format tag statistics for display in the bot"""
    if not tag_stats:
        return "No tag statistics available."
    
    stats_str = "🏷️ <b>Statistics by Tags</b>\n\n"
    for tag_stat in tag_stats:
        stats_str += (
            f"  <b>{tag_stat.tag_name}</b>: "
            f"{tag_stat.total_time_spent} min, "
            f"{tag_stat.task_count} tasks\n"
        )
    
    return stats_str.rstrip()


def format_time_duration(minutes: int) -> str:
    """Format time duration in minutes to human-readable format"""
    if minutes < 60:
        return f"{minutes} min"
    
    hours = minutes // 60
    remaining_minutes = minutes % 60
    if remaining_minutes == 0:
        return f"{hours}h"
    else:
        return f"{hours}h {remaining_minutes}min"


def format_tasks_list(tasks: List[TaskResponse], title: str = "Tasks") -> str:
    """Format a list of tasks for display"""
    if not tasks:
        return f"No {title.lower()} found."
    
    tasks_str = f"<b>{title}:</b>\n\n"
    for i, task in enumerate(tasks, 1):
        status = "✅" if task.completed else "⏳"
        tasks_str += f"{i}. {status} <b>{task.title}</b> ({'⭐' * task.priority})\n"
        tasks_str += f"   ID: {task.id} | Est: {task.estimated_time} min\n"
        
        if task.tags:
            tag_names = [tag.name for tag in task.tags]
            tasks_str += f"   Tags: {', '.join(tag_names)}\n"
        
        tasks_str += "\n"
    
    return tasks_str.rstrip()


def format_progress_bar(current: int, total: int, width: int = 20) -> str:
    """Format a progress bar for displaying completion percentages"""
    if total == 0:
        return "[" + " " * width + "] 0%"
    
    percentage = (current / total) * 100
    filled_width = int((current / total) * width)
    bar = "█" * filled_width + "░" * (width - filled_width)
    return f"[{bar}] {percentage:.1f}%"