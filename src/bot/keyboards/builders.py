from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_main_keyboard():
    """Main keyboard with primary commands"""
    keyboard = [
        [
            types.KeyboardButton(text="📝 My Tasks"),
            types.KeyboardButton(text="⏱️ Current Task"),
        ],
        [
            types.KeyboardButton(text="📊 Statistics"),
            types.KeyboardButton(text="➕ New Task"),
        ],
        [
            types.KeyboardButton(text="⚙️ Settings"),
        ]
    ]
    return types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_task_actions_keyboard(task_id: int):
    """Inline keyboard with actions for a specific task"""
    builder = InlineKeyboardBuilder()
    builder.button(text="▶️ Start Timer", callback_data=f"start_timer_{task_id}")
    builder.button(text="✏️ Edit", callback_data=f"edit_task_{task_id}")
    builder.button(text="❌ Delete", callback_data=f"delete_task_{task_id}")
    builder.adjust(1)
    return builder.as_markup()


def get_priority_keyboard():
    """Inline keyboard for selecting task priority"""
    builder = InlineKeyboardBuilder()
    for priority in range(1, 6):
        builder.button(text=f"{'⭐' * priority}", callback_data=f"priority_{priority}")
    builder.adjust(5)
    return builder.as_markup()


def get_confirmation_keyboard(action: str, item_id: int = None):
    """Generic confirmation keyboard"""
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Yes", callback_data=f"confirm_{action}_{item_id}" if item_id else f"confirm_{action}")
    builder.button(text="❌ No", callback_data="cancel")
    builder.adjust(2)
    return builder.as_markup()


def get_navigation_keyboard(current_page: int, total_pages: int):
    """Pagination keyboard"""
    builder = InlineKeyboardBuilder()
    
    if current_page > 1:
        builder.button(text="⬅️ Previous", callback_data=f"page_{current_page-1}")
    
    builder.button(text=f"{current_page}/{total_pages}", callback_data="noop")
    
    if current_page < total_pages:
        builder.button(text="➡️ Next", callback_data=f"page_{current_page+1}")
    
    builder.adjust(3)
    return builder.as_markup()


def get_statistics_keyboard():
    """Keyboard for selecting statistics view"""
    builder = InlineKeyboardBuilder()
    builder.button(text="📅 Today", callback_data="stats_today")
    builder.button(text="📆 Week", callback_data="stats_week")
    builder.button(text="🏷️ By Tags", callback_data="stats_by_tags")
    builder.button(text="📈 Trends", callback_data="stats_trends")
    builder.adjust(2)
    return builder.as_markup()