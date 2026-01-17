from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from ..keyboards.builders import get_statistics_keyboard
from ..services.api_client import ApiClient
from ...core.config import settings

router = Router()


@router.message(Command("stats"))
async def command_stats(message: Message, state: FSMContext):
    """Show overall statistics"""
    user_data = await state.get_data()
    if not user_data.get("user_id"):
        await message.answer("Please run /start first to register.")
        return
    await message.answer("📊 Select statistics view:", reply_markup=get_statistics_keyboard())


@router.message(Command("statstoday"))
async def command_stats_today(message: Message, state: FSMContext):
    """Show today's statistics"""
    user_data = await state.get_data()
    user_id = user_data.get("user_id")
    if not user_id:
        await message.answer("Please run /start first to register.")
        return

    async with ApiClient(settings.api_base_url) as api_client:
        try:
            stats = await api_client.get_daily_stats(user_id=user_id)
            if not stats:
                await message.answer("Could not retrieve today's stats.")
                return
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
async def command_stats_week(message: Message, state: FSMContext):
    """Show weekly statistics"""
    user_data = await state.get_data()
    user_id = user_data.get("user_id")
    if not user_id:
        await message.answer("Please run /start first to register.")
        return

    async with ApiClient(settings.api_base_url) as api_client:
        try:
            stats = await api_client.get_weekly_stats(user_id=user_id)
            if not stats:
                await message.answer("Could not retrieve weekly stats.")
                return

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
async def stats_callback(callback: CallbackQuery, state: FSMContext):
    """Handle statistics callbacks"""
    user_data = await state.get_data()
    user_id = user_data.get("user_id")
    if not user_id:
        await callback.message.edit_text("Please run /start first to register.")
        return

    stat_type = callback.data.split('_')[1]
    
    async with ApiClient(settings.api_base_url) as api_client:
        try:
            stats_text = ""
            if stat_type == "today":
                stats = await api_client.get_daily_stats(user_id=user_id)
                if stats:
                    stats_text = (
                        f"📅 <b>Today's Statistics</b>\n\n"
                        f"⏱️ Time spent: {stats.total_time_spent} minutes\n"
                        f"✅ Completed tasks: {stats.completed_tasks}\n"
                        f"📝 Active tasks: {stats.active_tasks}"
                    )
                else:
                    stats_text = "Could not retrieve today's stats."
            elif stat_type == "week":
                stats = await api_client.get_weekly_stats(user_id=user_id)
                if stats:
                    stats_text = (
                        f"📆 <b>Week's Statistics ({stats.week_start} to {stats.week_end})</b>\n\n"
                        f"⏱️ Total time spent: {stats.total_time_spent} minutes\n"
                        f"✅ Completed tasks: {stats.completed_tasks}"
                    )
                else:
                    stats_text = "Could not retrieve weekly stats."
            elif stat_type == "by_tags":
                stats = await api_client.get_tag_stats(user_id=user_id)
                stats_text = "🏷️ <b>Statistics by Tags</b>\n\n"
                if stats:
                    for tag_stat in stats:
                        stats_text += f"  {tag_stat.tag_name}: {tag_stat.total_time_spent} min, {tag_stat.task_count} tasks\n"
                else:
                    stats_text += "No tag statistics available."
            # Trends endpoint is not implemented yet in the API in this branch
            # elif stat_type == "trends":
            #     ...
            else:
                stats_text = "Unknown statistics type."
            
            await callback.message.edit_text(stats_text, parse_mode="HTML")
        except Exception as e:
            await callback.message.edit_text(f"❌ Failed to load statistics: {str(e)}")