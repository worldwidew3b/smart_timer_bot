from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from ..services.state import TaskEditing
from ..keyboards.builders import get_main_keyboard, get_task_actions_keyboard, get_priority_keyboard
from ..services.api_client import ApiClient


router = Router()


@router.message(Command("mytasks"))
async def command_list_tasks(message: Message):
    """Show user's tasks with action options"""
    async with ApiClient("http://localhost:8000") as api_client:
        try:
            tasks = await api_client.get_tasks(user_id=1)
            if not tasks:
                await message.answer("You don't have any tasks yet. Use /newtask to create one!")
                return
            
            for i, task in enumerate(tasks[:5], 1):  # Show first 5 tasks
                status = "✅" if task.completed else "⏳"
                task_info = (
                    f"{i}. {status} <b>{task.title}</b>\n"
                    f"   Est. time: {task.estimated_time} min | "
                    f"Actual: {task.actual_time_spent} min\n"
                    f"   Priority: {'⭐' * task.priority}\n"
                )
                
                if task.tags:
                    tag_names = [tag.name for tag in task.tags]
                    task_info += f"   Tags: {', '.join(tag_names)}\n"
                
                await message.answer(task_info, parse_mode="HTML", reply_markup=get_task_actions_keyboard(task.id))
        except Exception as e:
            await message.answer(f"❌ Failed to load tasks: {str(e)}")


@router.callback_query(F.data.startswith("edit_task_"))
async def edit_task_callback(callback: CallbackQuery, state: FSMContext):
    """Handle edit task callback"""
    task_id = int(callback.data.split('_')[2])
    
    async with ApiClient("http://localhost:8000") as api_client:
        try:
            task = await api_client.get_task(task_id, user_id=1)
            if not task:
                await callback.message.edit_text("Task not found.")
                return
            
            await state.update_data(task_id=task_id, current_task=task)
            await callback.message.edit_text(
                f"Editing task: <b>{task.title}</b>\n\n"
                "What would you like to edit?",
                parse_mode="HTML"
            )
            # In a full implementation, we would show options to edit different fields
            await state.set_state(TaskEditing.choosing_field)
        except Exception as e:
            await callback.message.edit_text(f"❌ Failed to load task: {str(e)}")


@router.callback_query(F.data.startswith("delete_task_"))
async def delete_task_callback(callback: CallbackQuery):
    """Handle delete task callback"""
    task_id = int(callback.data.split('_')[2])
    
    async with ApiClient("http://localhost:8000") as api_client:
        try:
            success = await api_client.delete_task(task_id, user_id=1)
            if success:
                await callback.message.edit_text("✅ Task deleted successfully!")
            else:
                await callback.message.edit_text("❌ Failed to delete task.")
        except Exception as e:
            await callback.message.edit_text(f"❌ Failed to delete task: {str(e)}")