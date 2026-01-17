import asyncio
from datetime import datetime, timedelta
from aiogram import Bot
from ..services.api_client import ApiClient


class NotificationService:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.running = False

    async def start_reminders(self, user_id: str):
        """Start sending periodic reminders to the user"""
        self.running = True
        while self.running:
            try:
                # Every 30 minutes, check if user has active tasks
                await asyncio.sleep(30 * 60)  # 30 minutes
                
                if not self.running:
                    break
                    
                async with ApiClient("http://localhost:8000") as api_client:
                    active_timer = await api_client.get_active_timer(user_id=1)
                    
                    if active_timer:
                        # Get the task details
                        task = await api_client.get_task(active_timer.task_id, user_id=1)
                        
                        if task:
                            # Calculate elapsed time
                            from datetime import datetime
                            start_time_naive = active_timer.start_time.replace(tzinfo=None)
                            elapsed_minutes = int((datetime.now() - start_time_naive).total_seconds() // 60)
                            
                            message = (
                                f"⏰ Reminder: You've been working on '{task.title}' "
                                f"for {elapsed_minutes} minutes.\n"
                                f"Estimated time was {task.estimated_time} minutes."
                            )
                            
                            await self.bot.send_message(chat_id=user_id, text=message)
                            
            except Exception as e:
                print(f"Error in reminder service: {e}")

    async def send_completion_notification(self, user_id: str, task_title: str):
        """Send notification when a task is completed"""
        message = f"🎉 Great job! You've completed the task: '{task_title}'"
        await self.bot.send_message(chat_id=user_id, text=message)

    async def send_time_up_notification(self, user_id: str, task_title: str):
        """Send notification when estimated time is up"""
        message = f"⏱️ Time's up! You've reached the estimated time for: '{task_title}'"
        await self.bot.send_message(chat_id=user_id, text=message)

    def stop(self):
        """Stop the notification service"""
        self.running = False