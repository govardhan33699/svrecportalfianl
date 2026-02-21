Fixed usage of == operator space stripping by switching to {% ifequal %} tags with integer comparison from the view.
This avoids parsing errors and ensures the correct course/section is pre-selected.
Please refresh: http://127.0.0.1:8000/timetable/manage/
