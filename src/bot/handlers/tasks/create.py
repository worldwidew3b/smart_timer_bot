from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from ..services.state import TaskCreation
from ..keyboards.builders import get_main_keyboard, get_priority_keyboard, get_confirmation_keyboard
from ..services.api_client import ApiClient
import re


router = Router()


@router.message(Command("newtask"))
async def command_new_task(message: Message, state: FSMContext):
    """Start the task creation process"""
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
    
    # For now, we'll skip the tags selection and go to confirmation
    # In a full implementation, we would allow tag selection here
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
    
    # Create the task via API
    async with ApiClient("http://localhost:8000") as api_client:
        from ..domain.models.task import TaskCreate
        task_create_data = TaskCreate(
            title=data['title'],
            description=data['description'] if data['description'] else None,
            estimated_time=data['estimated_time'],
            priority=data['priority'],
            tags=[]  # No tags for now
        )
        
        try:
            created_task = await api_client.create_task(task_create_data, user_id=1)
            await callback.message.edit_text(f"✅ Task '{created_task.title}' created successfully!")
        except Exception as e:
            await callback.message.edit_text(f"❌ Failed to create task: {str(e)}")
    
    await state.clear()


@router.callback_query(F.data == "cancel")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    """Cancel current action"""
    await callback.message.edit_text("Action cancelled.")
    await state.clear()


@router.message(Command("mytasks"))
async def command_my_tasks(message: Message):
    """Show user's tasks"""
    async with ApiClient("http://localhost:8000") as api_client:
        try:
            tasks = await api_client.get_tasks(user_id=1)
            if not tasks:
                await message.answer("You don't have any tasks yet. Use /newtask to create one!")
                return
            
            tasks_text = "<b>Your Tasks:</b>\n\n"
            for i, task in enumerate(tasks[:10], 1):  # Limit to first 10 tasks
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
            await message.answer(f"❌ Failed to load tasks: {str(e)}")