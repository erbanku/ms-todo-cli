help_msg = """
NAME
    todocli - Command line client for Microsoft ToDo 

SYNOPSIS
    todocli [options] COMMAND ...  

    'COMMAND' can be one of the following values:
        ls                  Display all lists  

        lst <list_name>     Display all tasks from list
            list_name       Name of the list

        new <task> [-r time] [-d time] [-R recurrence]
                            Create a new task
            task            Task to create. See 'Specifying a task' for details.
            -r time         Set a reminder. See 'Specifying time' for details.              
            -d time         Set a due date. See 'Specifying time' for details.
            -R recurrence   Set recurrence (daily, weekly, monthly, yearly).

        newl <list_name>    Create a new list
            list_name       Name of the list

        complete <task>     Set task status to completed
            task            Task to complete. See 'Specifying a task' for details.

        rm <task>           Remove a task
            task            Task to remove. See 'Specifying a task' for details.

        show <task>         Show task details (title, body, importance, dates)
            task            Task to show. See 'Specifying a task' for details.

        update <task> [-t title] [-b body] [-I importance] [-r time] [-d time] [-s status]
                            Update a task's properties
            task            Task to update. See 'Specifying a task' for details.
            -t title        Set new title
            -b body         Set description/notes
            -I importance   Set importance (low, normal, high)
            -r time         Set a reminder. See 'Specifying time' for details.
            -d time         Set a due date. See 'Specifying time' for details.
            -s status       Set status (notStarted, inProgress, completed,
                            waitingOnOthers, deferred)

        rml <list_name>     Remove a list
            list_name       Name of the list to remove

        attach <task> <file>
                            Attach a file to a task (max 3 MB)
            task            Task to attach file to. See 'Specifying a task' for details.
            file            Path to the file to attach

        la <task>           List attachments on a task
            task            Task to list attachments for.

OPTIONS
    -h, --help
        Display a usage message.

Specifying a task:
    For commands which take 'task' as a parameter, 'task' can be one of the following:

    task_name
    list_name/task_name
    task_number
    list_name/task_number

    If 'list_name' is omitted, the default task list will be used. 
    'task_number' is the position displayed when specifying option '-n'. 

    Use --list (-l) flag to specify the list explicitly, allowing task names with slashes.

Specifying time:
    For options which take 'time' as a parameter, 'time' can be one of the following:

    {n}h
        Current time + n hours. 
        e.g. 1h, 12h. 
        Max: 99h

    morning
        Today at 07:00 AM if current time < 07:00 AM, otherwise tomorrow

    evening
        Today at 06:00 PM if current time < 06:00 PM, otherwise tomorrow

    tomorrow
        Tomorrow at 07:00 AM

    {hour}:{minute}
        Today at {hour}:{minute} if current time < {hour}:{minute}, otherwise tomorrow 
        e.g. 9:30, 09:30, 17:15

    {hour}:{minute} am|pm 
        Today at {hour}:{minute} am|pm  if current time < {hour}:{minute} am|pm, otherwise tomorrow
        e.g. 9:30 am, 12:00 am, 10:15 pm

    {day}.{month}. {hour}:{minute}
        The given day at {hour}:{minute}
        e.g. 24.12. 12:00
        e.g. 7.4.   9:15

    {day}.{month}.{year}
        The given day at 7:00 am
        e.g. 22.12.2020
        e.g. 01.01.21
        """
