from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from ..services.state import TimerManagement
from ..keyboards.builders import get_main_keyboard
from ..services.api_client import ApiClient


router = Router()


@router.message(Command("starttimer"))
async def command_start_timer(message: Message, state: FSMContext):
    """Start timer for a task"""
    # For simplicity, we'll assume the user sends the task ID as an argument
    command_parts = message.text.split()
    if len(command_parts) < 2:
        await message.answer("Please specify a task ID: /starttimer <task_id>")
        return
    
    try:
        task_id = int(command_parts[1])
    except ValueError:
        await message.answer("Task ID must be a number.")
        return
    
    async with ApiClient("http://localhost:8000") as api_client:
        try:
            timer_response = await api_client.start_timer(task_id, user_id=1)
            if timer_response:
                await message.answer(f"✅ Timer started for task ID {task_id}!")
            else:
                await message.answer("❌ Failed to start timer. Make sure the task exists and is accessible.")
        except Exception as e:
            await message.answer(f"❌ Failed to start timer: {str(e)}")


@router.message(Command("stoptimer"))
async def command_stop_timer(message: Message):
    """Stop the current timer"""
    # For simplicity, we'll stop the currently active timer
    async with ApiClient("http://localhost:8000") as api_client:
        try:
            active_timer = await api_client.get_active_timer(user_id=1)
            if not active_timer:
                await message.answer("❌ No active timer found.")
                return
            
            timer_response = await api_client.stop_timer(active_timer.id, user_id=1)
            if timer_response:
                await message.answer(f"✅ Timer stopped! Duration: {timer_response.duration} minutes.")
            else:
                await message.answer("❌ Failed to stop timer.")
        except Exception as e:
            await message.answer(f"❌ Failed to stop timer: {str(e)}")


@router.message(Command("current"))
async def command_current_task(message: Message):
    """Show the current task being worked on"""
    async with ApiClient("http://localhost:8000") as api_client:
        try:
            active_timer = await api_client.get_active_timer(user_id=1)
            if not active_timer:
                await message.answer("⏸️ No active task. Use /starttimer to begin working on a task.")
                return
            
            # Get the task details
            task = await api_client.get_task(active_timer.task_id, user_id=1)
            if task:
                # Calculate elapsed time based on start_time and current time if timer is still active
                from datetime import datetime
                if active_timer.end_time:
                    elapsed_time = (active_timer.end_time - active_timer.start_time).total_seconds() // 60
                else:
                    # Convert to naive datetime for comparison
                    start_time_naive = active_timer.start_time.replace(tzinfo=None)
                    elapsed_time = (datetime.now() - start_time_naive).total_seconds() // 60

                await message.answer(
                    f"⏱️ Currently working on:\n\n"
                    f"<b>{task.title}</b>\n"
                    f"Elapsed time: {int(elapsed_time)} minutes\n"
                    f"Estimated time: {task.estimated_time} minutes",
                    parse_mode="HTML"
                )
            else:
                await message.answer(f"⏱️ Working on task ID {active_timer.task_id}")
        except Exception as e:
            await message.answer(f"❌ Failed to get current task: {str(e)}")