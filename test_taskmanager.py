import unittest
from unittest.mock import patch
import datetime
from taskmanager import *
from app_taskmanager import *

def informationExtractor(tasks):
    return {(task.title, datetimeToString(task.dueDate), task.priority, task.description) for task in tasks}


class TestFunctionsFromTaskManagerModule(unittest.TestCase):

    def testShorten(self):
        message = "It's a beautiful day today"
        goodLimits = [30, 20, 10]
        expected = [
            "It's a beautiful day today",
            "It's a beautiful ...",
            "It's a ..."
            ]
        badLimits = [0, -1, -50]
        
        for i, limit in enumerate(goodLimits):
            self.assertEqual(shorten(message, limit), expected[i])

        with self.assertRaises(ValueError):
            for limit in badLimits:
                shorten(message, limit)
    
    def testValidTitle(self):
        goodTitle = "blablablablablab"
        badTitle = "blablalsddddddddddddddddddddddddddddddddddd"

        self.assertEqual(validTitle(goodTitle), goodTitle)

        with self.assertRaises(ValueError):
            validTitle(badTitle)
    
    def testValidDate(self):
        goodInputs = ["tomorrow", "today", "2", "20/05", "20/05/2002", "+1", "-1"]
        now = datetime.datetime.now()
        currYear = datetime.datetime.strftime(now, "%Y")
        task = Task("", "18/02/1930", "high", "")
        expected = [
            now + datetime.timedelta(1),
            now,
            now + datetime.timedelta(2),
            stringToDatetime("20/05/" + currYear),
            stringToDatetime("20/05/2002"),
            task.dueDate + datetime.timedelta(1),
            task.dueDate - datetime.timedelta(1),
        ]
        badInputs = ["no", "yesterday", "never", "maybe in the future", "56/18/3094"]
        
        for i, input in enumerate(goodInputs):
            self.assertEqual(datetimeToString((validDate(input, task))), datetimeToString(expected[i]))
        with self.assertRaises(ValueError):
            for input in badInputs:
                validDate(input)

    def testValidPriority(self):
        goodInputs = ["high", "medium", "low", "h", "m", "l"]
        badInputs = ["very high", "very low", "inbetween", "10", "20"]
        expected = ["high", "medium", "low", "high", "medium", "low"]

        for i, input in enumerate(goodInputs):
            self.assertEqual(validPriority(input), expected[i])
        with self.assertRaises(ValueError):
            for input in badInputs:
                validPriority(input)
    
    def testValidDescription(self):
        goodInput = "This is a description"
        expected = "This is a description"
        badInput = "hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh"

        self.assertEqual(validDescription(goodInput), expected)
        with self.assertRaises(ValueError):
            validDescription(badInput)


class TestTaskClass(unittest.TestCase):
    
    def testTaskInit(self):
        title = "Test"
        dueDate = "today"
        priority = "high"
        description = "Test"

        task = Task(title, dueDate, priority, description)
        # setDefaultAttributes implicitly called
        task1 = Task(title, "bad due date", priority, description)
        
        self.assertEqual(task.title, title)
        self.assertEqual(task.description, description)
        self.assertEqual(datetimeToString(task.dueDate), datetimeToString(validDate(dueDate)))
        self.assertEqual(task.priority, validPriority(priority))
        self.assertFalse(task.completed)
        
        self.assertEqual(task1.title, "Default")
        self.assertEqual(task1.description, "Default")
        self.assertEqual(datetimeToString(task1.dueDate), datetimeToString(datetime.datetime.now()))
        self.assertEqual(task1.priority, "high")


class TestTaskManagerClass(unittest.TestCase):

    def testTaskManagerInit(self):
        tm = TaskManager()

        self.assertEqual(tm.tasks, [])
        self.assertEqual(tm.descriptionView, False)
        self.assertEqual(tm.sortingMode, "date-then-priority")
    
    def testLoadExamples(self):
        tm = TaskManager()
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

        tm.loadExampleTasks()
                
        self.assertEqual(informationExtractor(tm.tasks), informationExtractor(taskList))

    def testSwichSortingMode(self):
        tm = TaskManager()
        tm.switchSortingMode()
        self.assertEqual(tm.sortingMode, "priority-then-date")
        tm.switchSortingMode()
        self.assertEqual(tm.sortingMode, "date-then-priority")
    
    def testSortTasks(self):
        task1 = Task("1", "today", "h", "1")
        task2 = Task("2", "tomorrow", "h", "2")
        task3 = Task("3", "today", "l", "3")
        task4 = Task("4", "2", "m", "4")
        taskList = [task1, task2, task3, task4]
        expected1 = [task1, task3, task2, task4]
        expected2 = [task1, task2, task4, task3]
        tm = TaskManager()

        tm.addTasks(taskList)
        self.assertEqual(tm.tasks, expected1)
        tm.switchSortingMode()
        self.assertEqual(tm.tasks, expected2)
    
    def testCheckDuplicate(self):
        task1 = Task("1", "today", "h", "1")
        task2 = Task("1", "today", "h", "1")
        tm = TaskManager()

        tm.addTasks(task1)
        
        with self.assertRaises(DuplicateTaskError):
            tm.checkDuplicate(task2)
    
    def testAddTasks(self):
        task1 = Task("1", "today", "h", "1")
        task2 = Task("2", "tomorrow", "h", "2")
        task3 = Task("3", "today", "l", "3")
        task4 = Task("4", "2", "m", "4")
        taskList = [task2, task3, task4]
        tm = TaskManager()

        tm.addTasks(task1)
        self.assertIn(task1, tm.tasks)
        tm.addTasks(taskList)
        taskList.append(task1)
        self.assertEqual(informationExtractor(taskList), informationExtractor(tm.tasks))
    
    def testToggleStatus(self):
        tm = TaskManager()
        task = Task("1", "today", "h", "1")

        tm.toggleStatus(task)
        self.assertEqual(task.completed, True)
        tm.toggleStatus(task)
        self.assertEqual(task.completed, False)
    
    def testRemoveCompleted(self):
        tm = TaskManager()
        task = Task("1", "today", "h", "1")

        tm.toggleStatus(task)
        tm.removeCompleted()
        self.assertEqual(tm.tasks, [])
        tm.removeCompleted()
        self.assertEqual(tm.tasks, [])
    
    def testRemoveTask(self):
        task1 = Task("1", "today", "h", "1")
        task2 = Task("2", "tomorrow", "h", "2")
        task3 = Task("3", "today", "l", "3")
        task4 = Task("4", "2", "m", "4")
        taskList = [task1, task2, task3, task4]
        tm = TaskManager()

        tm.addTasks(taskList)
        tm.removeTasks(task1)
        self.assertEqual(set(taskList[1:]), set(tm.tasks))

    def testReset(self):
        tm = TaskManager()
        tm.loadExampleTasks()
        tm.reset()
        self.assertEqual(tm.tasks, [])
    
    def testSwitchViewMode(self):
        tm = TaskManager()
        tm.switchViewMode()
        self.assertEqual(tm.descriptionView, True)
        tm.switchViewMode()
        self.assertEqual(tm.descriptionView, False)
    
    def testStringRepresentation(self):
        task1 = Task("Test task 1", "23/02/2024", "medium", "One")
        task2 = Task("Test task 2", "23/02/2024", "high", "Two")
        task3 = Task("Test task 3", "22/02/2024", "high", "Three")
        tm = TaskManager()
        tm.addTasks([task1, task2, task3])
        expectedString1 = "\n                      *** Task Manager ***                      "
        expectedString1 += "\n----------------------------------------------------------------"
        expectedString1 += "\n Num |    Title    |  Due date  | Priority | Description | Done "
        expectedString1 += "\n----------------------------------------------------------------"
        expectedString1 += "\n 1   | Test task 3 | 22/02/2024 | high     | Three       | No   "
        expectedString1 += "\n 2   | Test task 2 | 23/02/2024 | high     | Two         | No   "
        expectedString1 += "\n 3   | Test task 1 | 23/02/2024 | medium   | One         | No   "

        expectedString2 =  "\n   *** Task Manager ***   "
        expectedString2 += "\n--------------------------"
        expectedString2 += "\n Num | Description | Done "
        expectedString2 += "\n--------------------------"
        expectedString2 += "\n 1   | Three       | No   "
        expectedString2 += "\n 2   | Two         | No   "
        expectedString2 += "\n 3   | One         | No   "

        self.maxDiff = None
        self.assertEqual(tm.__str__(), expectedString1)
        tm.switchViewMode()
        self.assertEqual(tm.__str__(), expectedString2)


class TestAppFunctions(unittest.TestCase):

    def testFunc1(self):
        return "1"

    def testFunc2(self):
        return "2"

    def testFunc3(self):
        return "3"
    
    def testFunc4(self):
        return "4"
    
    @patch('builtins.input', side_effect=['y', 'n'])
    def testPromptLoopYes(self, mockInput):
        result1 = promptLoop("", self.testFunc1)
        result2 = promptLoop("", self.testFunc1)

        self.assertEqual(result1, "1")
        self.assertEqual(result2, None)
        mockInput.assert_called()

    @patch('builtins.input', side_effect=['something else', 'y'])
    def testPromptLoopLoop(self, mockInput):
        result = promptLoop("", self.testFunc1)

        self.assertEqual(result, "1")
        mockInput.assert_called()

    @patch('builtins.input', side_effect=['y'])
    def testOptions(self, mockInput):
        # No cases hit
        result1 = options("input", self.testFunc1, self.testFunc2, "testMenu", self.testFunc3)
        # Asking for help
        result2 = options("help", self.testFunc1, self.testFunc2, "testMenu", self.testFunc3)
        # Quitting and entering 'y'
        result3 = options("quit", self.testFunc1, self.testFunc2, "testMenu", self.testFunc3)

        self.assertEqual(result1, "input")
        self.assertEqual(result2, None)
        self.assertEqual(result3, None)
        mockInput.assert_called()

    @patch('builtins.input', side_effect=['h', 'very high', 'l', 'today', 'never', '2'])
    def testEnterInfo(self, mockInput):
        # Entering 'h'
        result1 = enterInfoLoop("priority", validPriority, acceptedPriorityInput)
        # Entering invalid priority, looping back and then 'l'
        result2 = enterInfoLoop("priority", validPriority, acceptedPriorityInput)
        # Entering 'today'
        result3 = enterInfoLoop("due date", validDate, acceptedDueDateInput)
        # Entering 'never', looping back and then '2'
        result4 = enterInfoLoop("due date", validDate, acceptedDueDateInput)
        now = datetime.datetime.now()
        nowPlusTwo = datetime.datetime.now() + datetime.timedelta(2)

        self.assertEqual(result1, "high")
        self.assertEqual(result2, "low")
        self.assertEqual(datetimeToString(result3), datetimeToString(now))
        self.assertEqual(datetimeToString(result4), datetimeToString(nowPlusTwo))
        mockInput.assert_called()

    @patch('builtins.input', side_effect=['new title', '', 'high', 'what?'])
    def testEdit(self, mockInput):
        task = Task("ok", "20/12/2012", "low", "wow")
        edit(task)

        self.assertEqual(task.title, "new title")
        print(task.dueDate)
        self.assertEqual(datetimeToString(task.dueDate), "20/12/2012")
        self.assertEqual(task.priority, "high")
        self.assertEqual(task.description, "what?")
        mockInput.assert_called()
    
if __name__ == "__main__":
    unittest.main(buffer=True)
