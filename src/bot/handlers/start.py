from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from ..keyboards.builders import get_main_keyboard


router = Router()


@router.message(CommandStart())
async def command_start(message: Message):
    """Handle /start command"""
    welcome_text = (
        "👋 Welcome to Smart Timer Bot!\n\n"
        "I'm here to help you manage your tasks and track your time.\n\n"
        "Commands available:\n"
        "/start - Show this message\n"
        "/newtask - Create a new task\n"
        "/mytasks - List your tasks\n"
        "/current - Show current task\n"
        "/stats - View statistics\n"
        "/help - Show help information\n\n"
        "Use the buttons below to navigate:"
    )
    
    keyboard = get_main_keyboard()
    await message.answer(welcome_text, reply_markup=keyboard)


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