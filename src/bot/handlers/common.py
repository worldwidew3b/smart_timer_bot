from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from ..keyboards.builders import get_main_keyboard
from ..services.api_client import ApiClient
from ...core.config import settings

router = Router()


@router.message(Command("search"))
async def command_search(message: Message, state: FSMContext):
    """Search for tasks with various filters"""
    user_data = await state.get_data()
    user_id = user_data.get("user_id")
    if not user_id:
        await message.answer("Please run /start first to register.")
        return

    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) < 2:
        await message.answer("Usage: /search <query> or /search filter:priority=high etc.")
        return
    
    # This is a stub and doesn't use the filters yet.
    # It just demonstrates the auth flow.
    async with ApiClient(settings.api_base_url) as api_client:
        try:
            tasks = await api_client.get_tasks(user_id=user_id)
            if not tasks:
                await message.answer("No tasks found matching your criteria.")
                return
            
            tasks_text = "<b>Your Tasks (search not fully implemented):</b>\n\n"
            for i, task in enumerate(tasks[:10], 1):
                status = "✅" if task.completed else "⏳"
                tasks_text += f"{i}. {status} <b>{task.title}</b>\n"
            
            await message.answer(tasks_text, parse_mode="HTML", reply_markup=get_main_keyboard())
        except Exception as e:
            await message.answer(f"❌ Search failed: {str(e)}")


@router.message(F.text.contains("#"))
async def handle_hashtag_filter(message: Message, state: FSMContext):
    """Handle hashtag-based filtering in regular messages"""
    user_data = await state.get_data()
    if not user_data.get("user_id"):
        await message.answer("Please run /start first to register.")
        return
        
    text = message.text.lower()
    
    if "#today" in text:
        await show_today_tasks(message)
    elif "#week" in text:
        await show_weekly_tasks(message)
    elif "#high" in text or "#urgent" in text:
        await show_high_priority_tasks(message, state)
    elif text.startswith("#tag:"):
        tag_name = text.split("#tag:")[1].split()[0]
        await show_tasks_by_tag(message, tag_name)


async def show_today_tasks(message: Message):
    """Helper to show today's tasks"""
    await message.answer("Showing today's tasks... (implementation would go here)")


async def show_weekly_tasks(message: Message):
    """Helper to show weekly tasks"""
    await message.answer("Showing weekly tasks... (implementation would go here)")


async def show_high_priority_tasks(message: Message, state: FSMContext):
    """Helper to show high priority tasks"""
    user_data = await state.get_data()
    user_id = user_data.get("user_id")
    # No need to check for user_id again, parent handler did it.

    async with ApiClient(settings.api_base_url) as api_client:
        try:
            # The get_tasks endpoint doesn't support priority filtering yet,
            # so we filter client-side.
            tasks = await api_client.get_tasks(user_id=user_id)
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