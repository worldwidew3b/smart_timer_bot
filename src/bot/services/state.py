from aiogram.fsm.state import State, StatesGroup


class TaskCreation(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_estimated_time = State()
    waiting_for_priority = State()
    waiting_for_tags = State()
    confirming_creation = State()


class TaskEditing(StatesGroup):
    selecting_task = State()
    choosing_field = State()
    editing_title = State()
    editing_description = State()
    editing_estimated_time = State()
    editing_priority = State()
    editing_tags = State()


class TimerManagement(StatesGroup):
    selecting_task_to_start = State()
    confirming_stop = State()