from datetime import datetime

class Todo:
    def __init__(self, user_id, task, date, time, completed=False):
        self.user_id = user_id
        self.task = task
        self.date = date  # Expected in YYYY-MM-DD format
        self.time = time  # Expected in HH:MM format
        self.completed = completed

    def to_dict(self):
        """
        Convert the Todo object into a dictionary for storage in MongoDB.
        """
        return {
            "userId": self.user_id,
            "task": self.task,
            "date": self.date,
            "time": self.time,
            "completed": self.completed,
        }

    @staticmethod
    def from_dict(data):
        """
        Create a Todo instance from a dictionary.
        """
        return Todo(
            user_id=data["userId"],
            task=data["task"],
            date=data["date"],
            time=data["time"],
            completed=data.get("completed", False),
        )

    @staticmethod
    def validate_date(date_str):
        """
        Validate the date format (YYYY-MM-DD).
        """
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_time(time_str):
        """
        Validate the time format (HH:MM).
        """
        try:
            datetime.strptime(time_str, "%H:%M")
            return True
        except ValueError:
            return False
