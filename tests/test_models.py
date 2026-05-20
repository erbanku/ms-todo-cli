#!/usr/bin/env python3
"""Unit tests for data models (TodoList and Task)"""

import unittest
from datetime import datetime, timezone
from todocli.models.todolist import TodoList
from todocli.models.todotask import Task, TaskStatus, TaskImportance, TaskBody, Attachment


class TestTodoListModel(unittest.TestCase):
    """Test TodoList model initialization and properties"""

    def test_basic_list_creation(self):
        """Test creating a TodoList from API response"""
        api_response = {
            "id": "list123",
            "displayName": "Personal",
            "isOwner": True,
            "isShared": False,
            "wellknownListName": "none",
        }
        todo_list = TodoList(api_response)

        self.assertEqual(todo_list.id, "list123")
        self.assertEqual(todo_list.display_name, "Personal")
        self.assertTrue(todo_list.is_owner)
        self.assertFalse(todo_list.is_shared)
        self.assertEqual(
            todo_list.well_known_list_name, TodoList.WellKnownListName.none
        )

    def test_default_list(self):
        """Test creating the default 'Tasks' list"""
        api_response = {
            "id": "default123",
            "displayName": "Tasks",
            "isOwner": True,
            "isShared": False,
            "wellknownListName": "defaultList",
        }
        todo_list = TodoList(api_response)

        self.assertEqual(todo_list.display_name, "Tasks")
        self.assertEqual(
            todo_list.well_known_list_name, TodoList.WellKnownListName.DefaultList
        )

    def test_flagged_emails_list(self):
        """Test creating flagged emails list"""
        api_response = {
            "id": "flagged123",
            "displayName": "Flagged Emails",
            "isOwner": True,
            "isShared": False,
            "wellknownListName": "flaggedEmails",
        }
        todo_list = TodoList(api_response)

        self.assertEqual(
            todo_list.well_known_list_name, TodoList.WellKnownListName.FlaggedEmails
        )

    def test_shared_list(self):
        """Test creating a shared list"""
        api_response = {
            "id": "shared123",
            "displayName": "Family",
            "isOwner": True,
            "isShared": True,
            "wellknownListName": "none",
        }
        todo_list = TodoList(api_response)

        self.assertTrue(todo_list.is_shared)
        self.assertTrue(todo_list.is_owner)

    def test_non_owner_list(self):
        """Test list where user is not owner"""
        api_response = {
            "id": "notmine123",
            "displayName": "Shared Work",
            "isOwner": False,
            "isShared": True,
            "wellknownListName": "none",
        }
        todo_list = TodoList(api_response)

        self.assertFalse(todo_list.is_owner)
        self.assertTrue(todo_list.is_shared)


class TestTaskModel(unittest.TestCase):
    """Test Task model initialization and properties"""

    def test_basic_task_creation(self):
        """Test creating a basic task from API response"""
        api_response = {
            "id": "task123",
            "title": "Buy milk",
            "importance": "normal",
            "status": "notStarted",
            "createdDateTime": "2024-01-25T10:00:00.0000000Z",
            "lastModifiedDateTime": "2024-01-25T10:00:00.0000000Z",
            "isReminderOn": False,
        }
        task = Task(api_response)

        self.assertEqual(task.id, "task123")
        self.assertEqual(task.title, "Buy milk")
        self.assertEqual(task.importance, TaskImportance.NORMAL)
        self.assertEqual(task.status, TaskStatus.NOT_STARTED)
        self.assertFalse(task.is_reminder_on)
        self.assertIsNotNone(task.created_datetime)
        self.assertIsNone(task.completed_datetime)
        self.assertIsNone(task.due_datetime)
        self.assertIsNone(task.reminder_datetime)

    def test_task_with_reminder(self):
        """Test task with reminder set"""
        api_response = {
            "id": "task123",
            "title": "Meeting",
            "importance": "high",
            "status": "notStarted",
            "createdDateTime": "2024-01-25T10:00:00.0000000Z",
            "lastModifiedDateTime": "2024-01-25T10:00:00.0000000Z",
            "isReminderOn": True,
            "reminderDateTime": {
                "dateTime": "2024-01-26T09:00:00.0000000Z",
                "timeZone": "UTC",
            },
        }
        task = Task(api_response)

        self.assertEqual(task.title, "Meeting")
        self.assertTrue(task.is_reminder_on)
        self.assertIsNotNone(task.reminder_datetime)
        self.assertEqual(task.importance, TaskImportance.HIGH)

    def test_completed_task(self):
        """Test completed task"""
        api_response = {
            "id": "task123",
            "title": "Done task",
            "importance": "normal",
            "status": "completed",
            "createdDateTime": "2024-01-25T10:00:00.0000000Z",
            "lastModifiedDateTime": "2024-01-25T11:00:00.0000000Z",
            "completedDateTime": {
                "dateTime": "2024-01-25T11:00:00.0000000Z",
                "timeZone": "UTC",
            },
            "isReminderOn": False,
        }
        task = Task(api_response)

        self.assertEqual(task.status, TaskStatus.COMPLETED)
        self.assertIsNotNone(task.completed_datetime)

    def test_task_with_due_date(self):
        """Test task with due date"""
        api_response = {
            "id": "task123",
            "title": "Project deadline",
            "importance": "high",
            "status": "inProgress",
            "createdDateTime": "2024-01-25T10:00:00.0000000Z",
            "lastModifiedDateTime": "2024-01-25T10:00:00.0000000Z",
            "dueDateTime": {
                "dateTime": "2024-01-31T23:59:00.0000000Z",
                "timeZone": "UTC",
            },
            "isReminderOn": False,
        }
        task = Task(api_response)

        self.assertEqual(task.status, TaskStatus.IN_PROGRESS)
        self.assertIsNotNone(task.due_datetime)

    def test_task_importance_levels(self):
        """Test all task importance levels"""
        for importance in ["low", "normal", "high"]:
            api_response = {
                "id": "task123",
                "title": "Task",
                "importance": importance,
                "status": "notStarted",
                "createdDateTime": "2024-01-25T10:00:00.0000000Z",
                "lastModifiedDateTime": "2024-01-25T10:00:00.0000000Z",
                "isReminderOn": False,
            }
            task = Task(api_response)
            self.assertEqual(task.importance.value, importance)

    def test_task_status_values(self):
        """Test all task status values"""
        statuses = [
            "notStarted",
            "inProgress",
            "completed",
            "waitingOnOthers",
            "deferred",
        ]
        for status in statuses:
            api_response = {
                "id": "task123",
                "title": "Task",
                "importance": "normal",
                "status": status,
                "createdDateTime": "2024-01-25T10:00:00.0000000Z",
                "lastModifiedDateTime": "2024-01-25T10:00:00.0000000Z",
                "isReminderOn": False,
            }
            task = Task(api_response)
            self.assertEqual(task.status.value, status)

    def test_task_with_body_modification(self):
        """Test task with body last modified datetime"""
        api_response = {
            "id": "task123",
            "title": "Task with notes",
            "importance": "normal",
            "status": "notStarted",
            "createdDateTime": "2024-01-25T10:00:00.0000000Z",
            "lastModifiedDateTime": "2024-01-25T11:00:00.0000000Z",
            "bodyLastModifiedDateTime": "2024-01-25T10:30:00.0000000Z",
            "isReminderOn": False,
        }
        task = Task(api_response)

        self.assertIsNotNone(task.body_last_modified_datetime)

    def test_task_with_body_content(self):
        """Test task with body content"""
        api_response = {
            "id": "task123",
            "title": "Task with notes",
            "importance": "normal",
            "status": "notStarted",
            "createdDateTime": "2024-01-25T10:00:00.0000000Z",
            "lastModifiedDateTime": "2024-01-25T11:00:00.0000000Z",
            "isReminderOn": False,
            "body": {
                "content": "These are my task notes",
                "contentType": "text",
            },
        }
        task = Task(api_response)

        self.assertIsNotNone(task.body)
        self.assertEqual(task.body.content, "These are my task notes")
        self.assertEqual(task.body.content_type, "text")
        self.assertEqual(str(task.body), "These are my task notes")

    def test_task_without_body(self):
        """Test task without body"""
        api_response = {
            "id": "task123",
            "title": "Simple task",
            "importance": "normal",
            "status": "notStarted",
            "createdDateTime": "2024-01-25T10:00:00.0000000Z",
            "lastModifiedDateTime": "2024-01-25T10:00:00.0000000Z",
            "isReminderOn": False,
        }
        task = Task(api_response)
        self.assertIsNone(task.body)

    def test_task_str_basic(self):
        """Test task __str__ with minimal fields"""
        api_response = {
            "id": "task123",
            "title": "Buy milk",
            "importance": "normal",
            "status": "notStarted",
            "createdDateTime": "2024-01-25T10:00:00.0000000Z",
            "lastModifiedDateTime": "2024-01-25T10:00:00.0000000Z",
            "isReminderOn": False,
        }
        task = Task(api_response)
        output = str(task)

        self.assertIn("Buy milk", output)
        self.assertIn("notStarted", output)
        self.assertIn("normal", output)

    def test_task_str_with_body(self):
        """Test task __str__ includes body notes"""
        api_response = {
            "id": "task123",
            "title": "Buy milk",
            "importance": "high",
            "status": "inProgress",
            "createdDateTime": "2024-01-25T10:00:00.0000000Z",
            "lastModifiedDateTime": "2024-01-25T10:00:00.0000000Z",
            "isReminderOn": False,
            "body": {
                "content": "From the store",
                "contentType": "text",
            },
        }
        task = Task(api_response)
        output = str(task)

        self.assertIn("From the store", output)
        self.assertIn("Notes:", output)


class TestTaskBodyModel(unittest.TestCase):
    """Test TaskBody model"""

    def test_task_body_creation(self):
        """Test creating TaskBody from dict"""
        body = TaskBody({"content": "Hello", "contentType": "text"})
        self.assertEqual(body.content, "Hello")
        self.assertEqual(body.content_type, "text")

    def test_task_body_defaults(self):
        """Test TaskBody with missing fields"""
        body = TaskBody({})
        self.assertEqual(body.content, "")
        self.assertEqual(body.content_type, "text")

    def test_task_body_str(self):
        """Test TaskBody string representation"""
        body = TaskBody({"content": "My notes", "contentType": "text"})
        self.assertEqual(str(body), "My notes")


class TestAttachmentModel(unittest.TestCase):
    """Test Attachment model"""

    def test_attachment_creation(self):
        """Test creating Attachment from API response"""
        api_response = {
            "id": "att123",
            "name": "document.pdf",
            "size": 2048,
            "contentType": "application/pdf",
        }
        att = Attachment(api_response)

        self.assertEqual(att.id, "att123")
        self.assertEqual(att.name, "document.pdf")
        self.assertEqual(att.size, 2048)
        self.assertEqual(att.content_type, "application/pdf")

    def test_attachment_str(self):
        """Test attachment string representation"""
        api_response = {
            "id": "att123",
            "name": "photo.jpg",
            "size": 1024,
            "contentType": "image/jpeg",
        }
        att = Attachment(api_response)
        output = str(att)

        self.assertIn("photo.jpg", output)
        self.assertIn("1.0 KB", output)

    def test_attachment_defaults(self):
        """Test attachment with minimal fields"""
        api_response = {"id": "att123"}
        att = Attachment(api_response)

        self.assertEqual(att.name, "")
        self.assertEqual(att.size, 0)
        self.assertEqual(att.content_type, "")


if __name__ == "__main__":
    unittest.main()
