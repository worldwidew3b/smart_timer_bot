from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from ..keyboards.builders import get_main_keyboard
from ..services.api_client import ApiClient
from ...core.config import settings


router = Router()


@router.message(CommandStart())
async def command_start(message: Message, state: FSMContext):
    """Handle /start command and register user."""
    
    # Instantiate API client with base URL from settings
    async with ApiClient(settings.api_base_url) as api_client:
        user = await api_client.get_or_create_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username
        )

    if user:
        # Save backend user ID to state for future use
        await state.update_data(user_id=user.id)
        
        welcome_text = (
            f"👋 Welcome, {message.from_user.first_name}!\n\n"
            "I'm here to help you manage your tasks and track your time.\n\n"
            "Commands available:\n"
            "/start - Show this message\n"
            "/newtask - Create a new task\n"
            "/mytasks - List your tasks\n"
            "/help - Show help information\n\n"
            "Use the buttons below to navigate:"
        )
        keyboard = get_main_keyboard()
        await message.answer(welcome_text, reply_markup=keyboard)
    else:
        await message.answer(
            "❌ Sorry, there was a problem connecting to the service. "
            "Please try again later."
        )


@router.message(Command("help"))
async def command_help(message: Message):
    """Handle /help command"""
    help_text = (
        "📚 Smart Timer Bot Help\n\n"
        
        "📝 <b>Task Management:</b>\n"
        "• /newtask - Create a new task with title, description, estimated time, priority, and tags\n"
        "• /mytasks - View all your tasks with options to start timer, edit, or delete\n"
        "• /edittask - Modify existing tasks\n"
        "• /deltask - Remove tasks you no longer need\n\n"
        
        "⏱️ <b>Time Tracking:</b>\n"
        "• /starttimer - Begin timing a task\n"
        "• /stoptimer - Finish timing the current task\n"
        "• /current - See what task you're currently working on\n\n"
        
        "📊 <b>Statistics:</b>\n"
        "• /stats - Get overall productivity statistics\n"
        "• /statstoday - View today's statistics\n"
        "• /statsweek - View weekly statistics\n"
        "• /statstag - Get statistics filtered by tag\n\n"
        
        "Use the menu buttons for quick access to common functions!"
    )
    
    await message.answer(help_text, parse_mode="HTML")