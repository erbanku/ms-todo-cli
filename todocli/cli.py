import argparse
import shlex
import sys

import todocli.graphapi.wrapper as wrapper
from todocli.utils.update_checker import check as update_checker
from todocli.utils.datetime_util import (
    parse_datetime,
    TimeExpressionNotRecognized,
    ErrorParsingTime,
)
from todocli.utils.recurrence_util import (
    parse_recurrence,
    InvalidRecurrenceExpression,
)
from todocli.models.todotask import TaskImportance, TaskStatus


class InvalidTaskPath(Exception):
    def __init__(self, path):
        self.message = (
            "Invalid path: '{}', path can only contain one '/'. "
            "Please specify the task in format: '<list>/<task>'".format(path)
        )
        super(InvalidTaskPath, self).__init__(self.message)


def parse_task_path(task_input, list_name=None):
    """Parse task input into list name and task name.

    Args:
        task_input: Task identifier from user, can be 'task_name' or 'list_name/task_name'
        list_name: Optional list name from --list flag. If provided, task_input is
                   treated as task name only, allowing slashes in the task name.

    Returns:
        Tuple of (list_name, task_name)
    """
    if list_name:
        # If list is explicitly provided via --list flag, treat entire input as task name
        return list_name, task_input

    if "/" in task_input:
        elems = task_input.split("/")
        if len(elems) > 2:
            raise InvalidTaskPath(task_input)
        return elems[0], elems[1]
    else:
        return "Tasks", task_input


def print_list(item_list):
    for i, x in enumerate(item_list):
        print(f"[{i}]\t{x}")


def ls(args):
    lists = wrapper.get_lists()
    lists_names = [l.display_name for l in lists]
    print_list(lists_names)


def lst(args):
    tasks = wrapper.get_tasks(list_name=args.list_name)
    tasks_titles = [x.title for x in tasks]
    print_list(tasks_titles)


def new(args):
    task_list, name = parse_task_path(args.task_name, getattr(args, "list", None))

    reminder_date_time_str = args.reminder
    reminder_datetime = None

    if reminder_date_time_str is not None:
        reminder_datetime = parse_datetime(reminder_date_time_str)

    due_date_time_str = args.due
    due_datetime = None
    if due_date_time_str is not None:
        due_datetime = parse_datetime(due_date_time_str)

    recurrence = parse_recurrence(args.recurrence)

    wrapper.create_task(
        name,
        list_name=task_list,
        reminder_datetime=reminder_datetime,
        due_datetime=due_datetime,
        recurrence=recurrence,
    )


def newl(args):
    wrapper.create_list(args.list_name)


def try_parse_as_int(input_str: str):
    try:
        return int(input_str)
    except ValueError:
        return input_str


def complete(args):
    task_list, name = parse_task_path(args.task_name, getattr(args, "list", None))
    wrapper.complete_task(list_name=task_list, task_name=try_parse_as_int(name))


def rm(args):
    task_list, name = parse_task_path(args.task_name, getattr(args, "list", None))
    wrapper.remove_task(task_list, try_parse_as_int(name))


def show(args):
    task_list, name = parse_task_path(args.task_name, getattr(args, "list", None))
    task = wrapper.get_task(list_name=task_list, task_name=try_parse_as_int(name))
    print(task)


def update(args):
    task_list, name = parse_task_path(args.task_name, getattr(args, "list", None))

    reminder_datetime = None
    if args.reminder is not None:
        reminder_datetime = parse_datetime(args.reminder)

    due_datetime = None
    if args.due is not None:
        due_datetime = parse_datetime(args.due)

    wrapper.update_task(
        list_name=task_list,
        task_name=try_parse_as_int(name),
        new_title=args.title,
        body=args.body,
        importance=args.importance,
        reminder_datetime=reminder_datetime,
        due_datetime=due_datetime,
        status=args.status,
    )


def rml(args):
    wrapper.delete_list(args.list_name)


def attach(args):
    task_list, name = parse_task_path(args.task_name, getattr(args, "list", None))
    wrapper.add_attachment(
        list_name=task_list,
        task_name=try_parse_as_int(name),
        file_path=args.file,
    )


def la(args):
    task_list, name = parse_task_path(args.task_name, getattr(args, "list", None))
    attachments = wrapper.list_attachments(
        list_name=task_list,
        task_name=try_parse_as_int(name),
    )
    if not attachments:
        print("No attachments")
    else:
        print_list([str(a) for a in attachments])


helptext_task_name = """
        Specify the task.
        Can be one of the following:
        task_name
        list_name/task_name
        task_number
        list_name/task_number

        Use --list flag to specify the list explicitly, allowing task names with slashes (e.g., URLs).
        """


def setup_parser():
    parser = argparse.ArgumentParser(
        description="Command line interface for Microsoft ToDo"
    )
    parser.add_argument(
        "-i", "--interactive", action="store_true", help="Interactive mode"
    )
    parser.set_defaults(func=None)
    subparsers = parser.add_subparsers(help="Command to execute")

    # create parser for 'ls' command
    subparser = subparsers.add_parser("ls", help="Display all lists")
    subparser.set_defaults(func=ls)

    # create parser for 'lst' command
    subparser = subparsers.add_parser("lst", help="Display tasks from a list")
    subparser.add_argument(
        "list_name",
        nargs="?",
        default="Tasks",
        help="This optional argument specifies the list from which the tasks are displayed."
        "If this parameter is omitted, \
                                all tasks from the default task list will be displayed",
    )
    subparser.set_defaults(func=lst)

    # create parser for 'new' command
    subparser = subparsers.add_parser("new", help="Add a new task")
    subparser.add_argument("task_name", help=helptext_task_name)
    subparser.add_argument("-r", "--reminder")
    subparser.add_argument("-d", "--due")
    subparser.add_argument("-R", "--recurrence")
    subparser.add_argument(
        "-l",
        "--list",
        help="Specify the list name explicitly (allows task names with slashes)",
    )
    subparser.set_defaults(func=new)

    # create parser for 'newl' command
    subparser = subparsers.add_parser("newl", help="Add a new list")
    subparser.add_argument("list_name", help="Name of the list to create")
    subparser.set_defaults(func=newl)

    # create parser for 'complete' command
    subparser = subparsers.add_parser("complete", help="Complete a Task")
    subparser.add_argument("task_name", help=helptext_task_name)
    subparser.add_argument(
        "-l",
        "--list",
        help="Specify the list name explicitly (allows task names with slashes)",
    )
    subparser.set_defaults(func=complete)

    # create parser for 'rm' command
    subparser = subparsers.add_parser("rm", help="Remove a Task")
    subparser.add_argument("task_name", help=helptext_task_name)
    subparser.add_argument(
        "-l",
        "--list",
        help="Specify the list name explicitly (allows task names with slashes)",
    )
    subparser.set_defaults(func=rm)

    # create parser for 'show' command
    subparser = subparsers.add_parser("show", help="Show task details")
    subparser.add_argument("task_name", help=helptext_task_name)
    subparser.add_argument(
        "-l",
        "--list",
        help="Specify the list name explicitly (allows task names with slashes)",
    )
    subparser.set_defaults(func=show)

    # create parser for 'update' command
    subparser = subparsers.add_parser("update", help="Update a task")
    subparser.add_argument("task_name", help=helptext_task_name)
    subparser.add_argument(
        "-l",
        "--list",
        help="Specify the list name explicitly (allows task names with slashes)",
    )
    subparser.add_argument(
        "-t",
        "--title",
        help="New title for the task",
    )
    subparser.add_argument(
        "-b",
        "--body",
        help="Set the task description/notes",
    )
    subparser.add_argument(
        "-I",
        "--importance",
        choices=[e.value for e in TaskImportance],
        help="Set the task importance (low, normal, high)",
    )
    subparser.add_argument("-r", "--reminder", help="Set a reminder time")
    subparser.add_argument("-d", "--due", help="Set a due date/time")
    subparser.add_argument(
        "-s",
        "--status",
        choices=[e.value for e in TaskStatus],
        help="Set the task status",
    )
    subparser.set_defaults(func=update)

    # create parser for 'rml' command
    subparser = subparsers.add_parser("rml", help="Remove a list")
    subparser.add_argument("list_name", help="Name of the list to remove")
    subparser.set_defaults(func=rml)

    # create parser for 'attach' command
    subparser = subparsers.add_parser(
        "attach", help="Add a file attachment to a task (max 3 MB)"
    )
    subparser.add_argument("task_name", help=helptext_task_name)
    subparser.add_argument("file", help="Path to the file to attach")
    subparser.add_argument(
        "-l",
        "--list",
        help="Specify the list name explicitly (allows task names with slashes)",
    )
    subparser.set_defaults(func=attach)

    # create parser for 'la' command (list attachments)
    subparser = subparsers.add_parser(
        "la", help="List attachments on a task"
    )
    subparser.add_argument("task_name", help=helptext_task_name)
    subparser.add_argument(
        "-l",
        "--list",
        help="Specify the list name explicitly (allows task names with slashes)",
    )
    subparser.set_defaults(func=la)

    return parser


def main():
    try:
        parser = setup_parser()
        first_run = True
        interactive = False
        error_occurred = False

        while True:
            try:
                namespace, args = parser.parse_known_args()
                parser.parse_args(args, namespace)

                if namespace.func is not None:
                    namespace.func(namespace)
                else:
                    # No argument was provided
                    parser.print_usage()

                if namespace.interactive and first_run:
                    interactive = True
                    first_run = False

            except argparse.ArgumentError:
                pass
            except wrapper.TaskNotFoundByName as e:
                print(e.message)
                error_occurred = True
            except wrapper.ListNotFound as e:
                print(e.message)
                error_occurred = True
            except wrapper.TaskNotFoundByIndex as e:
                print(e.message)
                error_occurred = True
            except InvalidTaskPath as e:
                print(e.message)
                error_occurred = True
            except TimeExpressionNotRecognized as e:
                print(e.message)
                error_occurred = True
            except ErrorParsingTime as e:
                print(e.message)
                error_occurred = True
            except InvalidRecurrenceExpression as e:
                print(e.message)
                error_occurred = True
            except ValueError as e:
                print(str(e))
                error_occurred = True
            except FileNotFoundError as e:
                print(str(e))
                error_occurred = True
            finally:
                sys.stdout.flush()
                sys.stderr.flush()

            if not interactive:
                break

            arg = input("\nInput command: ")
            args = shlex.split(arg)
            sys.argv = sys.argv[:1]
            sys.argv += args

        # Exit with non-zero code if an error occurred in non-interactive mode
        if error_occurred and not interactive:
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n")
        exit(0)


if __name__ == "__main__":
    update_checker()
    main()
