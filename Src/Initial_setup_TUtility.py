import datetime
import threading


class InitialSetupUtility:

    def __init__(self, app):
        self.canProgress = None
        self.App = app
        self.changeStackToDefault(self.App.TodoContainer)

        self.initializeTodo()
        self.App.Events.registerActiveWindowChangeEvent(self.windowChanged)
        print("Initial Setup Done")

    def initializeTodo(self):

        loaded = self.App.Store.getDatabase()

        for i, data in enumerate(loaded):
            saved = data.get("data")
            progress = data.get("progress")

            todo = self.App.AddRemoveTUtility.addTodoComp(saved.get("title"))
            todo.todoCounter.set_text(str(i + 1))
            todo.state = loaded[i]["state"]
            todo.absoluteProgress = progress
            todo.aId = loaded[i].get("a_id")
            todo.isCompleted = loaded[i]["is_completed"]

            self.App.TodoList.append(todo)
            self.App.Events.addDefaultTodoHandlers(todo, i)
            self.App.ProgressTUtility.setTodoProgress(todo, progress)

            if loaded[i]["state"] == "Playing":
                self.App.PlayPauseTUtility.changeComponentIcons("play", todo)
                self.canProgress = True
                self.App.ProgressTUtility.advanceProgress(loaded[i]["progress"], loaded[i]["data"]["time"], todo,
                                                          datetime.datetime.now(), i,
                                                          loaded)
            elif loaded[i]["state"] == "Paused":
                self.App.PlayPauseTUtility.changeComponentIcons("pause", todo)

            elif loaded[i]["state"] == "Completed":
                self.App.PlayPauseTUtility.changeComponentIcons("complete", todo)
                todo.absoluteProgress = 100
                todo.relativeProgress = 100
                self.App.ProgressTUtility.setTodoProgress(todo, todo.absoluteProgress)

    def changeStackToDefault(self, default):
        self.App.Stack.set_visible_child(default)

    def windowChanged(self, screen, window):
        index = self.App.ActiveTodoIndex
        activeProgram = self.App.ActiveWindow.get("program")
        lastActiveProgram = self.App.LastActiveWindow
        timeSpend = ((datetime.datetime.now() - self.App.LastActiveWindowOn).total_seconds()) / 60

        if index is not None:
            activeTodo = self.App.TodoList[index]

            i = activeTodo.aId
            prvData = self.App.DBStore.getSingleLocalAnalyticalData(i, "p_time")

            def saveData(il, pData, lAP, aP, tS):
                if lAP is not None:

                    if pData.get(lAP.get("program")) is not None:
                        pData[lAP.get("program")] = pData.get(lAP.get("program")) + tS
                    else:
                        pData[lAP.get("program")] = tS
                else:
                    pData.set(aP, tS)

                print(pData)

                self.App.DBStore.updateLocalAnalyticalData(il, "p_time", pData)

            threading.Thread(target=saveData,
                             args=(i, prvData, lastActiveProgram, activeProgram, timeSpend),
                             daemon=True).start()

        self.App.LastActiveWindow = self.App.ActiveWindow
