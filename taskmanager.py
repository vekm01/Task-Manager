'''Task manager library.'''

import datetime

dateFormat = "%d/%m/%Y"
priorityTable = {"low":3, "medium":2, "high":1}
completionTable = {True:"Yes", False:"No"}
titleLimit = 20
descriptionLimit = 90

def shorten(message, limit):
    '''Shortens given string and adds three dots to end.
    
    Param:
        message: String to be shortened.
        limit: Desired total string length.
    Returns:
        The shortened string.
    Raises:
        ValueError: If limit is less than 3.
    '''
    result = message
    if limit < 3:
        raise ValueError("Limit may not be less than 3.")
    if len(message) > limit:
        result = f"{message[0:limit-3]}"
        result += "..."
    return result

def stringToDatetime(date):
    '''Converts date string to datetime object.'''
    return datetime.datetime.strptime(date, dateFormat)

def datetimeToString(obj):
    '''Converts datetime object to date string.'''
    return datetime.datetime.strftime(obj, dateFormat)

def validTitle(title):
    '''Checks if title is valid. If not, raises ValueError.'''
    if len(title) > titleLimit:
        raise ValueError(f"Title can be no longer than {titleLimit} characters.")
    return title

def validDate(date, task=None):
    '''Checks if date input is valid.
    
    Param:
        date: Can be a datetime object or a string.
        task: Optional task object for editing.
    Returns:
        A valid datetime object.
    Raises:
        ValueError: If input was a string but not convertible to datetime object.
        TypeError: If input was neither a string or a datetime object.
    '''
    if isinstance(date, datetime.datetime):
        return date
    if isinstance(date, str):
        today = datetime.datetime.now()
        match date:
            case "today":
                return today
            case "tomorrow":
                return today + datetime.timedelta(1)
            # Days from today
            case days if days.isdigit() and int(days) >= 0:
                return today + datetime.timedelta(int(days))
            # Add or subtract days if editing task
            case offset if (
                task and offset[0] in ["+", "-"]
                and len(offset) > 1 and offset[1:].isdigit()
            ):
                result = None
                days = int(offset[1:])
                if offset[0] == "+":
                    result = task.dueDate + datetime.timedelta(days)
                else:
                    result = task.dueDate - datetime.timedelta(days)
                return result
        # Add year if only date and month given
        if len(date.split("/")) == 2:
            currentYear = today.strftime("%Y")
            date = date + "/" + currentYear
        try:
            return stringToDatetime(date)
        except ValueError as error:
            raise ValueError("Invalid due date. Make sure to match accepted format.") from error
    raise TypeError("Due date should be either a string or a datetime object.")

def validPriority(priority):
    '''Checks if priority is valid.

    Param:
        priority: Unchecked priority input.
    Returns:
        A valid priority tag.
    Raises:
        ValueError if priority input doesn't match shorthands or accepted format.
    '''
    match priority:
        case "h":
            return "high"
        case "m":
            return "medium"
        case "l":
            return "low"
        case x if x in ["high", "medium", "low"]:
            return x
        case _:
            raise ValueError("Invalid priority tag. Make sure to match accepted format.")

def validDescription(description):
    '''Checks if description input is valid. If not, raises ValueError.'''
    if len(description) > descriptionLimit:
        raise ValueError(f"Description can be no longer than {descriptionLimit} characters.")
    return description


class DuplicateTaskError(Exception):
    '''Custom exception for duplicate tasks.'''


class Task:
    '''Class for representing a task.'''

    def __init__(self, title, dueDate, priority, description):
        '''Instantiates a task object. If invalid arguments, assigns default values.

        Parameters:
            title: Title string.
            description: Description string.
            dueDate: Either a datetime object or a date string.
            priority: Priority string.
            completed: Boolean for representing completion status.
        '''
        try:
            self.title = validTitle(title)
            self.dueDate = validDate(dueDate)
            self.priority = validPriority(priority)
            self.description = validDescription(description)
            self.completed = False

        except Exception as error:
            print(f"\nInternal error: {error}")
            self.setDefaultAttributes(title)

    def setDefaultAttributes(self, initTitle):
        '''Sets default attribute values for the task.

        Param:
            initTitle: Title that should correspond to task title before resetting.
        '''
        self.title = "Default"
        self.dueDate = datetime.datetime.now()
        self.priority = "high"
        self.description = "Default"
        self.completed = False
        title = shorten(initTitle, titleLimit)
        print(f"\n>> Attention! Default attributes have been set for task '{title}'.")


class TaskManager:
    '''Class for representing task manager.'''

    def __init__(self):
        '''Instantiates a task manager object.'''
        self.tasks = []
        self.sortingMode = "date-then-priority"
        self.descriptionView = False

    def loadExampleTasks(self):
        '''Resets task manager and loads pre-defined tasks.'''
        taskList = [
            Task("Cook dinner", "today", "h", "It's gonna be pasta with tomato sauce"),
            Task("Read", "today", "l", "Read until you fall asleep"),
            Task("Bicycle maintenance", "tomorrow", "m", "Tighten the brakes and lubricate chain"),
            Task("Dentist appointment", "2", "m", "Brush teeth well before going"),
            Task("Clean mirror", "today", "l", "The mirror will need cleaning at some point"),
            Task("Send letter", "4", "m", "Send letter when it's done"),
            Task("Matt's birthday", "7", "h", "It's Matt's birthday! Give him a call!"),
            Task("Yoga class", "2", "l", "I could check out this yoga class"),
        ]
        self.reset()
        self.addTasks(taskList)
        print("\n>> Example tasks loaded.")

    def switchSortingMode(self):
        '''Switches sorting mode for tasks in task manager.'''
        try:
            if self.sortingMode == "date-then-priority":
                print("\n>> Now sorting tasks by priority and then date.")
                self.sortingMode = "priority-then-date"
            else:
                print("\n>> Now sorting tasks by date and then priority.")
                self.sortingMode = "date-then-priority"
            self.sortTasks()
        except ValueError as error:
            print(error)

    def sortTasks(self):
        '''Sorts task in task manager.

        Raises:
            ValueError: If sorting mode is not recognized.
        '''
        if self.sortingMode == "date-then-priority":
            self.tasks.sort(
                key=lambda task: (task.dueDate, priorityTable[task.priority])
            )
        elif self.sortingMode == "priority-then-date":
            self.tasks.sort(
                key=lambda task: (priorityTable[task.priority], task.dueDate)
            )
        else:
            raise ValueError("\nInvalid task sorting mode.")

    def checkDuplicate(self, task):
        '''Checks if a task is identical to a pre-existing one.

        Parameters:
            task: Task to check.
        Raises:
            DuplicateTaskError: If duplicate found.
        '''
        currentTaskAttributes = (task.title, task.dueDate, task.priority, task.description)
        allTaskAttributes = [
            (task.title, task.dueDate, task.priority, task.description)
            for task in self.tasks
        ]

        if currentTaskAttributes in allTaskAttributes:
            raise DuplicateTaskError("\nDuplicate tasks not allowed.")

    def addTasks(self, tasks):
        '''Adds task(s) to task manager and sorts the collection.'''
        try:
            if not isinstance(tasks, list):
                tasks = [tasks]
            for task in tasks:
                self.checkDuplicate(task)
                self.tasks.append(task)
            self.sortTasks()
        except DuplicateTaskError as error:
            print(f"Error: {error}")
        except Exception as error:
            print(f"Unexpected error: {error}")

    def toggleStatus(self, tasks):
        '''Toggles completion status of given task(s).'''
        if not isinstance(tasks, list):
            tasks = [tasks]
        for task in tasks:
            if not task.completed:
                task.completed = True
            else:
                task.completed = False
        print(f"\n>> Toggled completion status of {len(tasks)} task(s).")

    def removeCompleted(self):
        '''Removes completed tasks from task manager.'''
        removedTasks = [task for task in self.tasks if task.completed]
        self.tasks = [task for task in self.tasks if not task.completed]
        print(f"\n>> Removed {len(removedTasks)} task(s).")

    def removeTasks(self, tasks):
        '''Removes task(s) from task manager.'''
        try:
            if not isinstance(tasks, list):
                tasks = [tasks]
            for task in tasks:
                self.tasks.remove(task)
            print(f"\n>> Removed {len(tasks)} task(s).")
        except ValueError:
            print("\nError: One or more tasks do not exist in task manager.")

    def reset(self):
        '''Resets task manager by removing all tasks from task list.'''
        self.tasks = []
        print("\n>> Task manager reset.")

    def switchViewMode(self):
        '''Switches between standard and description view'''
        if self.descriptionView:
            self.descriptionView = False
        else:
            self.descriptionView = True

    def __str__(self):
        '''Returns printable string representation in either standard or description view mode.'''
        if self.tasks == []:
            return "\nTask manager is empty. Go ahead and add a task!"
        if self.descriptionView:
            viewableDescriptionLimit = descriptionLimit
            fieldAmount = 3
        else:
            viewableDescriptionLimit = 30
            fieldAmount = 6

        separator = " | "
        space = " "

        longestDescription = max(len(task.description) for task in self.tasks)
        descriptionWidth = min(longestDescription, viewableDescriptionLimit)
        titleWidth = min(max(len(task.title) for task in self.tasks), titleLimit)
        spaceWidth = len(space)
        separatorWidth = len(separator)

        numFieldWidth = len("Num")
        titleFieldWidth = max(titleWidth, len("Title"))
        dueDateFieldWidth = len("DD/MM/YYYY")
        priorityFieldWidth = len("Priority")
        descriptionFieldWidth = max(descriptionWidth, len("Description"))
        completionFieldWidth = len("Done")

        totalWidth = numFieldWidth + descriptionFieldWidth + completionFieldWidth
        if not self.descriptionView:
            totalWidth += titleFieldWidth + dueDateFieldWidth + priorityFieldWidth
        totalWidth += 2*spaceWidth + (fieldAmount-1)*separatorWidth

        # Adding header
        result = ""
        result += f"\n{"*** Task Manager ***":^{totalWidth}}"
        result += "\n" + totalWidth*"-"

        # Adding column names
        result += f"\n{space}{"Num":^{numFieldWidth}}{separator}"
        if not self.descriptionView:
            result += f"{"Title":^{titleFieldWidth}}{separator}"
            result += f"{"Due date":^{dueDateFieldWidth}}{separator}"
            result += f"{"Priority":^{priorityFieldWidth}}{separator}"
        result += f"{"Description":^{descriptionFieldWidth}}{separator}"
        result += f"{"Done":^{completionFieldWidth}}{space}"
        result += "\n" + totalWidth*"-"

        # Adding a line for each task
        for i, task in enumerate(self.tasks):
            result += f"\n{space}{i+1:<3}{separator}"
            if not self.descriptionView:
                result += f"{task.title:{titleFieldWidth}}{separator}"
                result += f"{datetimeToString(task.dueDate):{dueDateFieldWidth}}{separator}"
                result += f"{task.priority:{priorityFieldWidth}}{separator}"
            description = shorten(task.description, viewableDescriptionLimit)
            result += f"{description:{descriptionFieldWidth}}{separator}"
            completion = completionTable[task.completed]
            result += f"{completion:{completionFieldWidth}}{space}"

        return result

def main():
    '''For testing purposes.'''

if __name__ == "__main__":
    main()
