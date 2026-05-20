from enum import Enum
from todocli.utils.datetime_util import api_timestamp_to_datetime


class TaskStatus(str, Enum):
    COMPLETED = "completed"
    NOT_STARTED = "notStarted"
    IN_PROGRESS = "inProgress"
    WAITING_ON_OTHERS = "waitingOnOthers"
    DEFERRED = "deferred"


class TaskImportance(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class RecurrencePatternType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    ABSOLUTE_MONTHLY = "absoluteMonthly"
    RELATIVE_MONTHLY = "relativeMonthly"
    ABSOLUTE_YEARLY = "absoluteYearly"
    RELATIVE_YEARLY = "relativeYearly"


class DayOfWeek(str, Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class TaskBody:
    def __init__(self, body_dict):
        self.content = body_dict.get("content", "")
        self.content_type = body_dict.get("contentType", "text")

    def __str__(self):
        return self.content


class Task:
    def __init__(self, query_result):
        self.title = query_result["title"]
        self.id = query_result["id"]
        self.importance = TaskImportance(query_result["importance"])
        self.status = TaskStatus(query_result["status"])
        self.created_datetime = api_timestamp_to_datetime(
            query_result["createdDateTime"]
        )

        if "completedDateTime" in query_result:
            self.completed_datetime = api_timestamp_to_datetime(
                query_result["completedDateTime"]
            )
        else:
            self.completed_datetime = None

        self.is_reminder_on: bool = bool(query_result["isReminderOn"])

        if "dueDateTime" in query_result:
            self.due_datetime = api_timestamp_to_datetime(query_result["dueDateTime"])
        else:
            self.due_datetime = None

        if "reminderDateTime" in query_result:
            self.reminder_datetime = api_timestamp_to_datetime(
                query_result["reminderDateTime"]
            )
        else:
            self.reminder_datetime = None

        self.last_modified_datetime = api_timestamp_to_datetime(
            query_result["lastModifiedDateTime"]
        )

        if "bodyLastModifiedDateTime" in query_result:
            self.body_last_modified_datetime = api_timestamp_to_datetime(
                query_result["bodyLastModifiedDateTime"]
            )
        else:
            self.body_last_modified_datetime = None

        body = query_result.get("body")
        self.body = TaskBody(body) if body else None

    def __str__(self):
        lines = [f"Title:      {self.title}"]
        lines.append(f"Status:     {self.status.value}")
        lines.append(f"Importance: {self.importance.value}")
        if self.body and self.body.content:
            lines.append(f"Notes:      {self.body.content}")
        if self.due_datetime:
            lines.append(f"Due:        {self.due_datetime.strftime('%Y-%m-%d %H:%M')}")
        if self.reminder_datetime:
            lines.append(
                f"Reminder:   {self.reminder_datetime.strftime('%Y-%m-%d %H:%M')}"
            )
        lines.append(
            f"Created:    {self.created_datetime.strftime('%Y-%m-%d %H:%M')}"
        )
        lines.append(
            f"Modified:   {self.last_modified_datetime.strftime('%Y-%m-%d %H:%M')}"
        )
        if self.completed_datetime:
            lines.append(
                f"Completed:  {self.completed_datetime.strftime('%Y-%m-%d %H:%M')}"
            )
        return "\n".join(lines)


class Attachment:
    def __init__(self, query_result):
        self.id = query_result["id"]
        self.name = query_result.get("name", "")
        self.size = query_result.get("size", 0)
        self.content_type = query_result.get("contentType", "")

    def __str__(self):
        size_kb = self.size / 1024
        return f"{self.name} ({size_kb:.1f} KB)"
