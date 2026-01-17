from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from ..services.api_client import ApiClient
from ...core.config import settings
from datetime import datetime

router = Router()


@router.message(Command("starttimer"))
async def command_start_timer(message: Message, state: FSMContext):
    """Start timer for a task"""
    user_data = await state.get_data()
    user_id = user_data.get("user_id")

    if not user_id:
        await message.answer("Please run /start first to register.")
        return
        
    command_parts = message.text.split()
    if len(command_parts) < 2:
        await message.answer("Please specify a task ID: /starttimer <task_id>")
        return
    
    try:
        task_id = int(command_parts[1])
    except ValueError:
        await message.answer("Task ID must be a number.")
        return
    
    async with ApiClient(settings.api_base_url) as api_client:
        try:
            timer_response = await api_client.start_timer(user_id=user_id, task_id=task_id)
            if timer_response:
                await message.answer(f"✅ Timer started for task ID {task_id}!")
            else:
                await message.answer("❌ Failed to start timer. Make sure the task exists and is accessible.")
        except Exception as e:
            await message.answer(f"❌ Failed to start timer: {str(e)}")


@router.message(Command("stoptimer"))
async def command_stop_timer(message: Message, state: FSMContext):
    """Stop the current timer"""
    user_data = await state.get_data()
    user_id = user_data.get("user_id")

    if not user_id:
        await message.answer("Please run /start first to register.")
        return

    async with ApiClient(settings.api_base_url) as api_client:
        try:
            active_timer = await api_client.get_active_timer(user_id=user_id)
            if not active_timer:
                await message.answer("❌ No active timer found.")
                return
            
            timer_response = await api_client.stop_timer(user_id=user_id, timer_id=active_timer.id)
            if timer_response:
                # Assuming the API returns a duration, but the model doesn't have it.
                # Let's calculate it manually for now if end_time is present.
                duration = "N/A"
                if timer_response.end_time:
                    duration_secs = (timer_response.end_time - timer_response.start_time).total_seconds()
                    duration = f"{int(duration_secs // 60)} minutes"

                await message.answer(f"✅ Timer stopped! Duration: {duration}.")
            else:
                await message.answer("❌ Failed to stop timer.")
        except Exception as e:
            await message.answer(f"❌ Failed to stop timer: {str(e)}")


@router.message(Command("current"))
async def command_current_task(message: Message, state: FSMContext):
    """Show the current task being worked on"""
    user_data = await state.get_data()
    user_id = user_data.get("user_id")

    if not user_id:
        await message.answer("Please run /start first to register.")
        return

    async with ApiClient(settings.api_base_url) as api_client:
        try:
            active_timer = await api_client.get_active_timer(user_id=user_id)
            if not active_timer:
                await message.answer("⏸️ No active task. Use /starttimer to begin working on a task.")
                return
            
            # Get the task details
            task = await api_client.get_task(user_id=user_id, task_id=active_timer.task_id)
            if task:
                # Calculate elapsed time
                start_time_naive = active_timer.start_time.replace(tzinfo=None)
                elapsed_time = (datetime.utcnow() - start_time_naive).total_seconds() // 60

                await message.answer(
                    f"⏱️ Currently working on:\n\n"
                    f"<b>{task.title}</b>\n"
                    f"Elapsed time: {int(elapsed_time)} minutes\n"
                    f"Estimated time: {task.estimated_time} minutes",
                    parse_mode="HTML"
                )
            else:
                await message.answer(f"⏱️ Working on task ID {active_timer.task_id}, but could not fetch task details.")
        except Exception as e:
            await message.answer(f"❌ Failed to get current task: {str(e)}")