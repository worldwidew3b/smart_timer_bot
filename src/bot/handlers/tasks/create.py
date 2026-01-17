from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from ..services.state import TaskCreation
from ..keyboards.builders import get_main_keyboard, get_priority_keyboard, get_confirmation_keyboard
from ..services.api_client import ApiClient
from ...core.config import settings
# Use the bot-specific model for creating tasks
from ..models.api import TaskCreate


router = Router()


@router.message(Command("newtask"))
async def command_new_task(message: Message, state: FSMContext):
    """Start the task creation process"""
    user_data = await state.get_data()
    if not user_data.get("user_id"):
        await message.answer("Please run /start first to register.")
        return
        
    await message.answer("📝 Please enter the task title:")
    await state.set_state(TaskCreation.waiting_for_title)


@router.message(TaskCreation.waiting_for_title)
async def process_title(message: Message, state: FSMContext):
    """Process the entered title"""
    title = message.text.strip()
    if len(title) < 1:
        await message.answer("Title cannot be empty. Please enter a valid title:")
        return
    
    await state.update_data(title=title)
    await message.answer("Enter task description (optional, send '-' to skip):")
    await state.set_state(TaskCreation.waiting_for_description)


@router.message(TaskCreation.waiting_for_description)
async def process_description(message: Message, state: FSMContext):
    """Process the entered description"""
    description = message.text.strip()
    if description == '-':
        description = ""
    
    await state.update_data(description=description)
    await message.answer("Enter estimated time in minutes (e.g., 30, 60, 120):")
    await state.set_state(TaskCreation.waiting_for_estimated_time)


@router.message(TaskCreation.waiting_for_estimated_time)
async def process_estimated_time(message: Message, state: FSMContext):
    """Process the entered estimated time"""
    try:
        estimated_time = int(message.text.strip())
        if estimated_time <= 0:
            raise ValueError("Time must be positive")
    except ValueError:
        await message.answer("Please enter a valid number of minutes (e.g., 30, 60, 120):")
        return
    
    await state.update_data(estimated_time=estimated_time)
    await message.answer("Select task priority (1-5 stars):", reply_markup=get_priority_keyboard())
    await state.set_state(TaskCreation.waiting_for_priority)


@router.callback_query(F.data.startswith("priority_"), TaskCreation.waiting_for_priority)
async def process_priority(callback: CallbackQuery, state: FSMContext):
    """Process the selected priority"""
    priority = int(callback.data.split('_')[1])
    await state.update_data(priority=priority)
    
    data = await state.get_data()
    
    preview_text = (
        f"📋 <b>New Task Preview:</b>\n\n"
        f"<b>Title:</b> {data['title']}\n"
        f"<b>Description:</b> {data['description'] or 'Not provided'}\n"
        f"<b>Estimated Time:</b> {data['estimated_time']} minutes\n"
        f"<b>Priority:</b> {'⭐' * data['priority']}\n"
        f"<b>Tags:</b> None"
    )
    
    await callback.message.edit_text(preview_text, parse_mode="HTML")
    await callback.message.answer(
        "Ready to create this task?", 
        reply_markup=get_confirmation_keyboard("create_task")
    )
    await state.set_state(TaskCreation.confirming_creation)


@router.callback_query(F.data.startswith("confirm_create_task"), TaskCreation.confirming_creation)
async def confirm_create_task(callback: CallbackQuery, state: FSMContext):
    """Confirm task creation"""
    data = await state.get_data()
    user_id = data.get("user_id")
    
    if not user_id:
        await callback.message.edit_text("❌ Error: User not identified. Please run /start again.")
        await state.clear()
        return

    # Create the task via API
    async with ApiClient(settings.api_base_url) as api_client:
        task_create_data = TaskCreate(
            title=data['title'],
            description=data['description'] if data['description'] else None,
            estimated_time=data['estimated_time'],
            priority=data['priority'],
            tags=[]  # No tags for now
        )
        
        try:
            created_task = await api_client.create_task(user_id=user_id, task_data=task_create_data)
            await callback.message.edit_text(f"✅ Task '{created_task.title}' created successfully!")
        except Exception as e:
            await callback.message.edit_text(f"❌ Failed to create task: {str(e)}")
    
    await state.clear()


@router.callback_query(F.data == "cancel")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    """Cancel current action"""
    await callback.message.edit_text("Action cancelled.")
    await state.clear()