from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from ..services.state import TaskEditing
from ..keyboards.builders import get_task_actions_keyboard
from ..services.api_client import ApiClient
from ...core.config import settings


router = Router()


@router.message(Command("mytasks"))
async def command_list_tasks(message: Message, state: FSMContext):
    """Show user's tasks with action options"""
    user_data = await state.get_data()
    user_id = user_data.get("user_id")

    if not user_id:
        await message.answer("Please run /start first to register.")
        return

    async with ApiClient(settings.api_base_url) as api_client:
        try:
            tasks = await api_client.get_tasks(user_id=user_id)
            if not tasks:
                await message.answer("You don't have any tasks yet. Use /newtask to create one!")
                return
            
            await message.answer("Here are your latest tasks:")
            for i, task in enumerate(tasks[:5], 1):  # Show first 5 tasks
                status = "✅" if task.completed else "⏳"
                task_info = (
                    f"{i}. {status} <b>{task.title}</b>\n"
                    f"   Est. time: {task.estimated_time} min\n"
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
    user_data = await state.get_data()
    user_id = user_data.get("user_id")

    if not user_id:
        await callback.message.edit_text("Error: User not identified. Please run /start again.")
        return
        
    task_id = int(callback.data.split('_')[2])
    
    # In a full implementation, this would transition to an editing state machine.
    # For now, we just acknowledge.
    await callback.message.edit_text(
        f"Editing for task {task_id} is not yet implemented.",
    )


@router.callback_query(F.data.startswith("delete_task_"))
async def delete_task_callback(callback: CallbackQuery, state: FSMContext):
    """Handle delete task callback"""
    user_data = await state.get_data()
    user_id = user_data.get("user_id")

    if not user_id:
        await callback.message.edit_text("Error: User not identified. Please run /start again.")
        return
        
    task_id = int(callback.data.split('_')[2])
    
    async with ApiClient(settings.api_base_url) as api_client:
        try:
            success = await api_client.delete_task(user_id=user_id, task_id=task_id)
            if success:
                await callback.message.edit_text("✅ Task deleted successfully!")
            else:
                await callback.message.edit_text("❌ Failed to delete task. It might have been already deleted.")
        except Exception as e:
            await callback.message.edit_text(f"❌ An error occurred while deleting the task: {str(e)}")
    
    # Remove the original message with the buttons
    await callback.message.delete()