from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from ..keyboards.builders import get_main_keyboard, get_statistics_keyboard
from ..services.api_client import ApiClient


router = Router()


@router.message(Command("stats"))
async def command_stats(message: Message):
    """Show overall statistics"""
    await message.answer("📊 Select statistics view:", reply_markup=get_statistics_keyboard())


@router.message(Command("statstoday"))
async def command_stats_today(message: Message):
    """Show today's statistics"""
    async with ApiClient("http://localhost:8000") as api_client:
        try:
            stats = await api_client.get_daily_stats(user_id=1)
            stats_text = (
                f"📅 <b>Today's Statistics</b>\n\n"
                f"⏱️ Time spent: {stats.total_time_spent} minutes\n"
                f"✅ Completed tasks: {stats.completed_tasks}\n"
                f"📝 Active tasks: {stats.active_tasks}"
            )
            await message.answer(stats_text, parse_mode="HTML")
        except Exception as e:
            await message.answer(f"❌ Failed to load today's statistics: {str(e)}")


@router.message(Command("statsweek"))
async def command_stats_week(message: Message):
    """Show weekly statistics"""
    async with ApiClient("http://localhost:8000") as api_client:
        try:
            stats = await api_client.get_weekly_stats(user_id=1)
            stats_text = (
                f"📆 <b>Week's Statistics ({stats.week_start} to {stats.week_end})</b>\n\n"
                f"⏱️ Total time spent: {stats.total_time_spent} minutes\n"
                f"✅ Completed tasks: {stats.completed_tasks}\n\n"
                f"<b>Daily breakdown:</b>\n"
            )
            
            for day_stat in stats.daily_breakdown:
                stats_text += f"  {day_stat.date}: {day_stat.total_time_spent} min, {day_stat.completed_tasks} tasks\n"
            
            await message.answer(stats_text, parse_mode="HTML")
        except Exception as e:
            await message.answer(f"❌ Failed to load weekly statistics: {str(e)}")


@router.callback_query(F.data.startswith("stats_"))
async def stats_callback(callback: CallbackQuery):
    """Handle statistics callbacks"""
    stat_type = callback.data.split('_')[1]
    
    async with ApiClient("http://localhost:8000") as api_client:
        try:
            if stat_type == "today":
                stats = await api_client.get_daily_stats(user_id=1)
                stats_text = (
                    f"📅 <b>Today's Statistics</b>\n\n"
                    f"⏱️ Time spent: {stats.total_time_spent} minutes\n"
                    f"✅ Completed tasks: {stats.completed_tasks}\n"
                    f"📝 Active tasks: {stats.active_tasks}"
                )
            elif stat_type == "week":
                stats = await api_client.get_weekly_stats(user_id=1)
                stats_text = (
                    f"📆 <b>Week's Statistics ({stats.week_start} to {stats.week_end})</b>\n\n"
                    f"⏱️ Total time spent: {stats.total_time_spent} minutes\n"
                    f"✅ Completed tasks: {stats.completed_tasks}"
                )
            elif stat_type == "by_tags":
                # For now, get all tag stats
                stats = await api_client.get_tag_stats(user_id=1)
                stats_text = "🏷️ <b>Statistics by Tags</b>\n\n"
                if stats:
                    for tag_stat in stats:
                        stats_text += f"  {tag_stat.tag_name}: {tag_stat.total_time_spent} min, {tag_stat.task_count} tasks\n"
                else:
                    stats_text = "No tag statistics available."
            elif stat_type == "trends":
                trends = await api_client.get_productivity_trends(user_id=1)
                stats_text = "📈 <b>Productivity Trends</b>\n\n"
                for trend in trends[:5]:  # Show first 5 days
                    stats_text += f"  {trend.day}: Planned {trend.planned_time} min, Actual {trend.actual_time} min\n"
            else:
                stats_text = "Unknown statistics type."
            
            await callback.message.edit_text(stats_text, parse_mode="HTML")
        except Exception as e:
            await callback.message.edit_text(f"❌ Failed to load statistics: {str(e)}")