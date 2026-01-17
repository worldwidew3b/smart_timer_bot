from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from ..keyboards.builders import get_main_keyboard
from ..services.api_client import ApiClient


router = Router()


@router.message(Command("search"))
async def command_search(message: Message):
    """Search for tasks with various filters"""
    # Extract search parameters from the message
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) < 2:
        await message.answer("Usage: /search filter:tag=work or /search filter:priority=high")
        return
    
    search_params = command_parts[1]
    
    # Parse filters
    filters = {}
    if "filter:" in search_params:
        filter_part = search_params.split("filter:")[1]
        if "=" in filter_part:
            key, value = filter_part.split("=", 1)
            filters[key] = value
    
    # Call API with filters
    async with ApiClient("http://localhost:8000") as api_client:
        try:
            # Build query parameters based on filters
            params = {}
            if 'tag' in filters:
                # In a real implementation, we would need to get tag ID by name
                # For now, we'll simulate this
                params['tag_ids'] = '1'  # This would be the actual tag ID
            if 'priority' in filters:
                priority_map = {'low': 1, 'medium': 3, 'high': 5}
                if filters['priority'].lower() in priority_map:
                    params['priority'] = priority_map[filters['priority'].lower()]
            if 'status' in filters:
                params['completed'] = filters['status'].lower() == 'completed'
            if 'today' in filters:
                # This would require additional API support for date filtering
                pass
            
            # For now, just get all tasks as an example
            tasks = await api_client.get_tasks(user_id=1)
            
            if not tasks:
                await message.answer("No tasks found matching your criteria.")
                return
            
            # Format and send results
            tasks_text = "<b>Search Results:</b>\n\n"
            for i, task in enumerate(tasks[:10], 1):  # Limit to first 10
                status = "✅" if task.completed else "⏳"
                tasks_text += (
                    f"{i}. {status} <b>{task.title}</b>\n"
                    f"   Est. time: {task.estimated_time} min | "
                    f"Priority: {'⭐' * task.priority}\n"
                )
                
                if task.tags:
                    tag_names = [tag.name for tag in task.tags]
                    tasks_text += f"   Tags: {', '.join(tag_names)}\n"
                
                tasks_text += "\n"
            
            await message.answer(tasks_text, parse_mode="HTML", reply_markup=get_main_keyboard())
        except Exception as e:
            await message.answer(f"❌ Search failed: {str(e)}")


@router.message(F.text.contains("#"))  # Handle hashtag-based filtering
async def handle_hashtag_filter(message: Message):
    """Handle hashtag-based filtering in regular messages"""
    text = message.text.lower()
    
    if "#today" in text:
        # Show today's tasks
        await show_today_tasks(message)
    elif "#week" in text:
        # Show weekly tasks
        await show_weekly_tasks(message)
    elif "#high" in text or "#urgent" in text:
        # Show high priority tasks
        await show_high_priority_tasks(message)
    elif text.startswith("#tag:"):
        # Show tasks with specific tag
        tag_name = text.split("#tag:")[1].split()[0]  # Get first word after #tag:
        await show_tasks_by_tag(message, tag_name)


async def show_today_tasks(message: Message):
    """Helper to show today's tasks"""
    await message.answer("Showing today's tasks... (implementation would go here)")


async def show_weekly_tasks(message: Message):
    """Helper to show weekly tasks"""
    await message.answer("Showing weekly tasks... (implementation would go here)")


async def show_high_priority_tasks(message: Message):
    """Helper to show high priority tasks"""
    async with ApiClient("http://localhost:8000") as api_client:
        try:
            # This would be enhanced to actually filter by priority
            tasks = await api_client.get_tasks(user_id=1)
            high_prio_tasks = [task for task in tasks if task.priority >= 4]
            
            if not high_prio_tasks:
                await message.answer("No high priority tasks found.")
                return
            
            tasks_text = "<b>High Priority Tasks:</b>\n\n"
            for i, task in enumerate(high_prio_tasks[:10], 1):
                status = "✅" if task.completed else "⏳"
                tasks_text += f"{i}. {status} <b>{task.title}</b> ({'⭐' * task.priority})\n"
            
            await message.answer(tasks_text, parse_mode="HTML")
        except Exception as e:
            await message.answer(f"❌ Failed to load high priority tasks: {str(e)}")


async def show_tasks_by_tag(message: Message, tag_name: str):
    """Helper to show tasks by tag"""
    await message.answer(f"Showing tasks with tag #{tag_name}... (implementation would go here)")