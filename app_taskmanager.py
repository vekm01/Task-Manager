'''Task manager app.'''

import os
import time
import datetime
import pickle
from pathlib import Path
import taskmanager

def loadTaskManager():
    '''Retrieves task manager from save file. Creates new save file if not found.
    
    Returns:
        Loaded task manager object if found, a fresh one otherwise.
    '''
    try:
        fileName = Path("savefile.pkl")
        fileName.touch(exist_ok=True)
        if os.path.getsize("savefile.pkl") > 0:
            with open(fileName, "rb") as file:
                taskManager = pickle.load(file)
        else:
            taskManager = taskmanager.TaskManager()
            print("\n>> No save file found. Initializing new task manager.")
    except Exception as error:
        print(f"An unexpected error occured when attempting to load or create save file: {error}")
    return taskManager

def saveToFile():
    '''Saves task manager to "savefile.pkl".'''
    with open('savefile.pkl', "wb") as file:
        pickle.dump(tm, file)

def mainMenuHelp():
    '''Lists commands and tips for main menu.'''
    msg = "\nCommands:"
    msg += "\n\t'h' or 'help' for help menu."
    msg += "\n\t'q' or 'quit' to quit program. "
    msg += "Add an exclamation mark to bypass prompt. Changes are saved automatically."
    msg += "\n\t'a' or 'add' to add task to task manager."
    msg += "\n\t'e <task number>' or 'edit <task number>' to edit selected task."
    msg += "\n\t't <task number(s)>' or 'toggle <task number(s)>' "
    msg += "to toggle completion status of task(s)."
    msg += "\n\t'rc' or 'remove completed' to remove completed task(s)."
    msg += "\n\t'r <task(s)>' or 'remove <task(s)>' to remove selected task(s)."
    msg += "\n\t'v' or 'view' to switch between standard view and description view."
    msg += "\n\t's' or 'sort' to switch between date-then-priority "
    msg += "and priority-then-date sorting mode."
    msg += "\n\t'ex' or 'example' to load task manager example preset."
    msg += "\n\t'reset' to reset task manager."
    msg += "\n\nAccepted input for selection:"
    msg += "\n\tTask number(s) separated by spaces."
    msg += "\n\tExamples:"
    msg += "\n\t\t'e 1' selects task 1 for editing if it exists."
    msg += "\n\t\t'r 1 2' deletes task 1 and 2 if they exist."
    msg += "\n\t\t't 3 6' toggles completion status of task 3 and 6 if they exist."

    print(msg)

def acceptedTitleInput():
    '''Generates message about accepted title input.'''
    msg = "\nAccepted title input:"
    msg += f"\n\tAnything under {taskmanager.titleLimit} characters."
    return msg

def acceptedDueDateInput():
    '''Generates message about accepted due date input.'''
    msg = "\nAccepted due date input:"
    msg += "\n\t'DD/MM/YYYY' where YYYY is optional. Current year will be assumed if not specified."
    msg += "\n\t'today' for today's date."
    msg += "\n\t'tomorrow' for tomorrow's date."
    msg += "\n\t'<number>' for the date <number> days from now."
    msg += "\n\tIn [Edit Mode]: '+<number>' or '-<number>' "
    msg += "to add/subtract <number> of days to/from current date."
    return msg

def acceptedPriorityInput():
    '''Generates message about accepted priority input'''
    msg = "\nAccepted priority input:"
    msg += "\n\t'h' or 'high' for high priority."
    msg += "\n\t'm' or 'medium' for medium priority."
    msg += "\n\t'l' or 'low' for low priority."
    return msg

def acceptedDescriptionInput():
    '''Generates message about accepted description input'''
    msg = "\nAccepted description input:"
    msg += f"\n\tAnything under {taskmanager.descriptionLimit} characters."
    return msg

def addOrEditHelp():
    '''Lists commands and tips for add/edit menu'''
    msg = "\nCommands:"
    msg += "\n\t'help' for help menu."
    msg += "\n\t'c' or 'cancel' to cancel action."
    msg += " Add an exclamation mark to bypass prompt."
    msg += "\n\t'q' or 'quit' to quit program. Add an exclamation "
    msg += "mark to bypass prompt. Changes are saved automatically."
    msg += "\n" + acceptedTitleInput()
    msg += "\n" + acceptedDueDateInput()
    msg += "\n" + acceptedPriorityInput()
    msg += "\n" + acceptedDescriptionInput()
    print(msg)

def quitApp():
    '''Saves task manager and exits program.'''
    try:
        print("\n>> Saving task manager data ... ")
        time.sleep(0.4)
        saveToFile()
        print("\n>> Data saved.")
        time.sleep(0.25)
        print("\n>> Quitting ...")
        time.sleep(0.25)
        exit(0)
    except Exception as error:
        print(error)
        exit(1)


def promptLoop(actionMessage, actionFunc):
    '''Asks for action confirmation from user until valid answer given.
    
    Param:
        actionMessage: String describing action.
        actionFunc: Function that will be called if user says yes.
    Returns:
        If yes, return value of actionFunc, and None otherwise.
    '''
    while True:
        userInput = input(f"\nAre you sure you want to {actionMessage}? ('y' or 'n'): ").strip()
        if userInput in ["1", "y"]:
            return actionFunc()
        elif userInput in ["0", "n"]:
            return None

def options(userInput, helpFunc, returnFunc, currentMenuName, quitFunc=quitApp):
    '''Checks if input matches standard commands.
    
    Param:
        userInput: User input string.
        helpFunc: Appropriate help function.
        returnFunc: Function to return to previous menu if applicable.
        currentMenuName: Name of caller menu. Determines available options.
        quitFunc: Function to exit program.
    Returns:
        User input if no cases are hit, None otherwise.
    '''
    match userInput:
        case h1 if h1 in ["help", "h"] and currentMenuName != "enterInfo":
            helpFunc()
        case "help":
            helpFunc()
        case c if c in ["cancel", "cancel!", "c", "c!"] and currentMenuName != "main":
            if "!" in c:
                returnFunc()
            else:
                promptLoop("cancel action", returnFunc)
        case q if q in ["quit", "quit!", "q", "q!"]:
            if "!" in q:
                quitFunc()
            else:
                promptLoop("quit program", quitFunc)
        case _:
            return userInput


def translator(keyword, task, dateStr=False):
    '''Translates keyword string to corresponding task attribute.'''
    match keyword:
        case "title":
            return task.title
        case "due date":
            if dateStr:
                return datetime.datetime.strftime(task.dueDate, taskmanager.dateFormat)
            return task.dueDate
        case "priority":
            return task.priority
        case "description":
            return task.description


def enterInfoLoop(keyword, validityCheckFunc, acceptedInputFunc, task=None):
    '''Looping function for gathering and validating specific user input.
    
    Param:
        keyword: Type of information being gathered.
        validEntryFunc: Appropriate function for validating user input.
        acceptedInputFunc: Appropriate function for generating format tip.
        task: Task object used when editing.
    Returns:
        Valid task data.
    '''
    showTip = True
    while True:
        try:
            if showTip:
                print(acceptedInputFunc())
            showTip = True
            msg = f"\nEnter {keyword}"
            if task:
                msg += f" (leave blank to keep '{translator(keyword, task, dateStr=True)}')"
            msg += ": "
            entry = input(msg).strip()
            if options(entry, addOrEditHelp, mainMenu, currentMenuName="enterInfo") is None:
                # Skip the tip for one loop because help menu was activated
                showTip = False
                continue
            if task and entry == "":
                return translator(keyword, task, dateStr=False)
            if keyword == "due date":
                result = validityCheckFunc(entry, task)
            else:
                result = validityCheckFunc(entry)
            return result
        except ValueError as error:
            print(f"\nError: {error}")


def getTaskInfo(task=None):
    '''Compiles necessary task information from user.
    
    Param:
        task: Task object used when editing.
    Returns:
        A 4-tuple of valid task data.
    '''
    if task:
        msg = f"Update information about task '{task.title}'."
    else:
        msg = "Provide information about your task."
    print(msg)

    title = enterInfoLoop("title", taskmanager.validTitle, acceptedTitleInput, task)
    if isinstance(task, taskmanager.Task) and task.completed:
        print("\n>> Skipping due date field current task is already completed.")
        dueDate = task.dueDate
    else:
        dueDate = enterInfoLoop("due date", taskmanager.validDate, acceptedDueDateInput, task)
    priority = enterInfoLoop("priority", taskmanager.validPriority, acceptedPriorityInput, task)
    # Renaming to shorten line
    validDescription = taskmanager.validDescription
    goodDescription = acceptedDescriptionInput
    description = enterInfoLoop("description", validDescription, goodDescription, task)

    return (title, dueDate, priority, description)

def add():
    '''Adds task with given data to task manager.'''
    print("\n[Add Mode]", end=" ")
    title, dueDate, priority, description = getTaskInfo()
    task = taskmanager.Task(title, dueDate, priority, description)
    tm.addTasks(task)

def validSelection(stringNumberList, single=False):
    '''Checks if selection is valid.
    
    Param:
        stringNumberList: List of numbers as strings.
        single: Whether or not only one selection is allowed.
    Returns:
        List of valid task numbers as integers, duplicates removed.
    Raises:
        ValueError: If selection(s) invalid.
    '''
    if tm.tasks == []:
        raise ValueError("There are no tasks to select from.")
    if stringNumberList == []:
        msg = "No task selected. Select task by passing task number(s) "
        msg += "after the action keyword."
        msg += "For instance, 'r 1 2' will remove task 1 and 2."
        raise ValueError(msg)
    if single and len(stringNumberList) > 1:
        raise ValueError("Only one selection allowed for this kind of action.")
    if not all(num.isdigit() for num in stringNumberList):
        raise TypeError("Only numbers can be used to select task(s).")
    # Convert to int and remove duplicates
    taskNumbers = {int(num) for num in stringNumberList}
    existingTaskNumbers = set(range(1, len(tm.tasks)+1))
    if not taskNumbers.issubset(existingTaskNumbers):
        raise ValueError("Invalid selection(s). Make sure to match existing task number(s).")
    selectedTasks = [task for i, task in enumerate(tm.tasks) if i+1 in taskNumbers]
    return selectedTasks

def edit(task):
    '''Edits task through user input.'''
    print("\n[Edit Mode]", end=" ")
    if isinstance(task, list):
        task = task[0]
    newTitle, newDueDate, newPriority, newDescription = getTaskInfo(task)
    task.title = newTitle
    task.dueDate = newDueDate
    task.priority = newPriority
    task.description = newDescription

def actionOnSelected(inputTaskNumbers, actionFunc, single=False):
    '''Applies an action on a selection of tasks.
    
    Param:
        inputTaskNumbers: List of task numbers as strings yet to be validated.
        actionFunc: The action to be executed.
        single: Whether only a single task may be selected for action.
    '''
    try:
        tasks = validSelection(inputTaskNumbers, single)
        if tasks is not None:
            actionFunc(tasks)
    except ValueError as error:
        print(f"\nError: {error}")
    except TypeError as error:
        print(f"\nError: {error}")
    except Exception as error:
        print(f"\nAn unexpected error occured: {error}")

def mainMenu():
    '''Main menu loop.'''
    hideTable = False
    while True:
        if not hideTable:
            print(tm)
        hideTable = False

        userInput = input("\nSelect action (or enter 'help'): ").strip()
        args = userInput.split(" ")

        if options(userInput, mainMenuHelp, None, currentMenuName="main") is None:
            # Hide task manager once as to not block help menu.
            hideTable = True
            continue

        match args[0]:
            case a if a in ["add", "a"]:
                add()
            case t if t in ["toggle", "t"]:
                actionOnSelected(args[1:], tm.toggleStatus)
            case e if e in ["edit", "e"]:
                actionOnSelected(args[1:], edit, single=True)
            case rc if rc == "remove" and len(args) > 1 and args[1] == "completed" or rc == "rc":
                tm.removeCompleted()
            case v if v in ["view", "v"]:
                tm.switchViewMode()
            case s if s in ["sort", "s"]:
                tm.switchSortingMode()
            case r if r in ["remove", "r"]:
                actionOnSelected(args[1:], tm.removeTasks)
            case "reset":
                tm.reset()
            case ex if ex in ["example", "ex"]:
                tm.loadExampleTasks()
            case _:
                print(f"\n>> Sorry, command '{args[0]}' not recognized.")

def main():
    '''Main executable code.'''
    global tm
    tm = loadTaskManager()
    print("\nWelcome to Valdemar's task manager application.")
    mainMenu()

if __name__ == "__main__":
    main()
