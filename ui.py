import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QDialog, QDialogButtonBox, QFormLayout,
                               QHBoxLayout, QVBoxLayout, QWidget, QMainWindow,
                               QMessageBox, QListWidgetItem, QLabel)

from models import Session, TaskManager
from storage import TaskStorage, SessionStorage
from widgets import (WidgetIdentity, ActionButton, LoginEdit, SearchEdit, TitleEdit,
                     DescriptionEdit, TaskTypeCombo, PrioritySpin, StatusCombo,
                     TaskList, CounterLabel, CompletedCheck)


class LoginDialog(WidgetIdentity, QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вход в список задач")
        self.setMinimumWidth(340)
        self.session = None
        self.controls.add("login", LoginEdit())
        self.controls["login"].setMaxLength(30)
        self.controls["login"].setPlaceholderText("Ваш логин")
        self.controls.add("error", QLabel())
        self.controls["error"].setWordWrap(True)
        self.controls["error"].setStyleSheet("color: #a02020;")
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                  QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Войти")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Отмена")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout = QFormLayout(self)
        layout.addRow("Логин:", self.controls["login"])
        layout.addRow(self.controls["error"])
        layout.addRow(buttons)

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value):
        if value is not None and not isinstance(value, Session):
            raise ValueError("Ожидается сеанс пользователя.")
        self._session = value

    def accept(self):
        try:
            self.session = Session(self.controls["login"].text_value)
        except ValueError as error:
            self.controls["error"].setText(str(error))
            self.controls["login"].setFocus()
            return
        super().accept()

    def __eq__(self, other):
        return super().__eq__(other)

    def __repr__(self):
        return super().__repr__()

    def __str__(self):
        return super().__str__()

    def __lt__(self, other):
        return super().__lt__(other)

    def __le__(self, other):
        return super().__le__(other)

    def __gt__(self, other):
        return super().__gt__(other)

    def __ge__(self, other):
        return super().__ge__(other)

    def comparison_key(self):
        return super().comparison_key()


class TaskDialog(WidgetIdentity, QDialog):
    @property
    def storage(self):
        return self._storage

    @storage.setter
    def storage(self, value):
        if not isinstance(value, TaskStorage):
            raise ValueError("Ожидается TaskStorage.")
        self._storage = value

    def __init__(self, storage, task=None, parent=None):
        super().__init__(parent)
        self.storage = storage
        self.task = None
        self.setWindowTitle("Изменить задачу" if task else "Добавить задачу")
        self.setMinimumWidth(460)
        self.controls.add("title", TitleEdit())
        self.controls["title"].setMaxLength(120)
        self.controls.add("description", DescriptionEdit())
        self.controls["description"].setAcceptRichText(False)
        self.controls["description"].setMaximumHeight(140)
        self.controls.add("kind", TaskTypeCombo())
        self.controls["kind"].addItem("Обычная", "regular")
        self.controls["kind"].addItem("Учебная", "study")
        self.controls["kind"].addItem("Рабочая", "work")
        self.controls.add("extra", TitleEdit())
        self.controls["extra"].setMaxLength(120)
        self.controls.add("extra_label", QLabel())
        self.controls.add("priority", PrioritySpin())
        self.controls["priority"].setRange(1, 3)
        self.controls["priority"].number = 2
        self.controls.add("completed", CompletedCheck("Выполнена"))
        self.controls.add("error", QLabel())
        self.controls["error"].setWordWrap(True)
        self.controls["error"].setStyleSheet("color: #a02020;")
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save |
                                  QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("Сохранить")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Отмена")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form = QFormLayout(self)
        form.addRow("Название:", self.controls["title"])
        form.addRow("Описание:", self.controls["description"])
        form.addRow("Тип:", self.controls["kind"])
        form.addRow(self.controls["extra_label"], self.controls["extra"])
        form.addRow("Приоритет:", self.controls["priority"])
        form.addRow(self.controls["completed"])
        form.addRow(self.controls["error"])
        form.addRow(buttons)
        self.controls["kind"].currentIndexChanged.connect(self.update_extra)
        if task:
            self.controls["title"].text_value = task.title
            self.controls["description"].text_value = task.description
            self.controls["kind"].selected_index = self.controls["kind"].findData(task.kind())
            self.controls["extra"].text_value = task.extra()
            self.controls["priority"].number = task.priority
            self.controls["completed"].checked = task.completed
        self.update_extra()

    @property
    def task(self):
        return self._task

    @task.setter
    def task(self, value):
        from models import Task
        if value is not None and not isinstance(value, Task):
            raise ValueError("Ожидается задача.")
        self._task = value

    def update_extra(self):
        kind = self.controls["kind"].currentData()
        self.controls["extra"].setVisible(kind != "regular")
        self.controls["extra_label"].setVisible(kind != "regular")
        self.controls["extra_label"].setText("Предмет:" if kind == "study" else "Проект:")

    def accept(self):
        try:
            self.task = self.storage.create_task(
                self.controls["kind"].currentData(), self.controls["title"].text_value,
                self.controls["description"].text_value, self.controls["priority"].number,
                self.controls["completed"].checked, self.controls["extra"].text_value)
        except (ValueError, KeyError) as error:
            self.controls["error"].setText(str(error))
            return
        super().accept()

    def __eq__(self, other):
        return super().__eq__(other)

    def __repr__(self):
        return super().__repr__()

    def __str__(self):
        return super().__str__()

    def __lt__(self, other):
        return super().__lt__(other)

    def __le__(self, other):
        return super().__le__(other)

    def __gt__(self, other):
        return super().__gt__(other)

    def __ge__(self, other):
        return super().__ge__(other)

    def comparison_key(self):
        return super().comparison_key()


class MainWindow(WidgetIdentity, QMainWindow):
    @property
    def manager(self):
        return self._manager

    @manager.setter
    def manager(self, value):
        if not isinstance(value, TaskManager):
            raise ValueError("Ожидается TaskManager.")
        self._manager = value

    @property
    def storage(self):
        return self._storage

    @storage.setter
    def storage(self, value):
        if not isinstance(value, TaskStorage):
            raise ValueError("Ожидается TaskStorage.")
        self._storage = value

    @property
    def session_storage(self):
        return self._session_storage

    @session_storage.setter
    def session_storage(self, value):
        if not isinstance(value, SessionStorage):
            raise ValueError("Ожидается SessionStorage.")
        self._session_storage = value

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value):
        if not isinstance(value, Session):
            raise ValueError("Ожидается Session.")
        self._session = value

    @property
    def report_saved(self):
        return self._report_saved

    @report_saved.setter
    def report_saved(self, value):
        if type(value) is not bool:
            raise ValueError("Флаг отчёта должен быть bool.")
        self._report_saved = value

    def __init__(self, manager, storage, session_storage, session):
        super().__init__()
        self.manager = manager
        self.storage = storage
        self.session_storage = session_storage
        self.session = session
        self.report_saved = False
        self.setWindowTitle(f"Список задач — {session.login}")
        self.resize(960, 650)
        self.setMinimumSize(650, 470)
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        filters = QHBoxLayout()
        self.controls.add("search", SearchEdit())
        self.controls["search"].setPlaceholderText("Поиск по названию (Esc — очистить)")
        self.controls["search"].setClearButtonEnabled(True)
        self.controls.add("state", StatusCombo())
        self.controls["state"].addItems(("Все задачи", "Оставшиеся", "Выполненные"))
        self.controls.add("sort", StatusCombo())
        self.controls["sort"].addItems(("Сначала высокий приоритет", "Сначала низкий приоритет"))
        filters.addWidget(self.controls["search"], 1)
        filters.addWidget(self.controls["state"])
        filters.addWidget(self.controls["sort"])
        layout.addLayout(filters)
        self.controls.add("counts", CounterLabel())
        layout.addWidget(self.controls["counts"])
        self.controls.add("list", TaskList())
        self.controls["list"].setWordWrap(True)
        self.controls["list"].setSpacing(5)
        layout.addWidget(self.controls["list"], 1)
        self.controls.add("details", DescriptionEdit())
        self.controls["details"].setReadOnly(True)
        self.controls["details"].setMaximumHeight(125)
        self.controls["details"].setPlaceholderText("Выберите задачу, чтобы увидеть описание")
        layout.addWidget(self.controls["details"])
        actions = QHBoxLayout()
        self.controls.add("add", ActionButton("Добавить"))
        self.controls.add("edit", ActionButton("Изменить"))
        self.controls.add("delete", ActionButton("Удалить"))
        self.controls.add("toggle", ActionButton("Отметить выполненной"))
        for button in (self.controls["add"], self.controls["edit"], self.controls["delete"], self.controls["toggle"]):
            actions.addWidget(button)
        layout.addLayout(actions)
        self.statusBar().showMessage("Приоритет: 1 — высокий, 2 — средний, 3 — низкий")
        self.controls["search"].textChanged.connect(self.refresh)
        self.controls["state"].currentIndexChanged.connect(self.refresh)
        self.controls["sort"].currentIndexChanged.connect(self.refresh)
        self.controls["list"].currentItemChanged.connect(self.update_selection)
        self.controls["list"].itemDoubleClicked.connect(self.edit_task)
        self.controls["list"].deleteRequested.connect(self.delete_task)
        self.controls["add"].clicked.connect(self.add_task)
        self.controls["edit"].clicked.connect(self.edit_task)
        self.controls["delete"].clicked.connect(self.delete_task)
        self.controls["toggle"].clicked.connect(self.toggle_task)
        self.refresh()

    def selected_index(self):
        item = self.controls["list"].currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def refresh(self):
        selected = self.selected_index()
        self.controls["list"].clear()
        for index, task in self.manager.visible(self.controls["search"].text_value,
                                                 self.controls["state"].selected_index,
                                                 self.controls["sort"].selected_index == 1):
            item = QListWidgetItem(str(task))
            item.setData(Qt.ItemDataRole.UserRole, index)
            item.setToolTip(task.description or "Без описания")
            font = item.font()
            font.setStrikeOut(task.completed)
            item.setFont(font)
            self.controls["list"].addItem(item)
            if index == selected:
                self.controls["list"].setCurrentItem(item)
        total, done, remaining = self.manager.counts()
        self.controls["counts"].caption = f"Всего: {total}    Выполнено: {done}    Осталось: {remaining}"
        self.update_selection()

    def update_selection(self):
        index = self.selected_index()
        for button in (self.controls["edit"], self.controls["delete"], self.controls["toggle"]):
            button.setEnabled(index is not None)
        if index is None:
            self.controls["details"].clear()
            self.controls["toggle"].caption = "Отметить выполненной"
        else:
            task = self.manager.tasks[index]
            self.controls["details"].text_value = f"{task.context()}\n{task.description or 'Без описания'}"
            self.controls["toggle"].caption = "Вернуть в оставшиеся" if task.completed else "Отметить выполненной"

    def persist_change(self, method, *arguments):
        previous = self.manager.tasks
        states = [task.completed for task in previous]
        try:
            method(*arguments)
            self.storage.save(self.manager.tasks)
        except (OSError, ValueError) as error:
            for task, state in zip(previous, states):
                task.completed = state
            self.manager.tasks = previous
            QMessageBox.critical(self, "Не удалось сохранить", str(error))
            return False
        self.refresh()
        self.statusBar().showMessage("Изменения сохранены", 3000)
        return True

    def add_task(self):
        dialog = TaskDialog(self.storage, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.persist_change(self.manager.add, dialog.task)

    def edit_task(self):
        index = self.selected_index()
        if index is None:
            return
        dialog = TaskDialog(self.storage, self.manager.tasks[index], self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.persist_change(self.manager.replace, index, dialog.task)

    def delete_task(self):
        index = self.selected_index()
        if index is None:
            return
        answer = QMessageBox.question(self, "Удаление задачи", "Удалить выбранную задачу?",
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                      QMessageBox.StandardButton.No)
        if answer == QMessageBox.StandardButton.Yes:
            self.persist_change(self.manager.remove, index)

    def toggle_task(self):
        index = self.selected_index()
        if index is not None:
            self.persist_change(self.manager.toggle, index)

    def closeEvent(self, event):
        try:
            self.storage.save(self.manager.tasks)
            if not self.report_saved:
                self.session.finish()
                self.session_storage.save(self.session)
                self.report_saved = True
        except (OSError, ValueError) as error:
            QMessageBox.critical(self, "Не удалось завершить сеанс",
                                 f"{error}\nИсправьте причину и снова закройте окно.")
            event.ignore()
            return
        event.accept()

    @staticmethod
    def run():
        app = QApplication.instance() or QApplication(sys.argv)
        app.setStyle("Fusion")
        login = LoginDialog()
        if login.exec() != QDialog.DialogCode.Accepted:
            return 0
        folder = Path(__file__).resolve().parent / "data"
        storage = TaskStorage(folder / "tasks.csv")
        try:
            if storage.exists():
                tasks = storage.load()
            else:
                tasks = TaskManager.demo()
                storage.save(tasks)
        except (OSError, ValueError) as error:
            QMessageBox.critical(None, "Ошибка чтения задач", str(error))
            return 1
        window = MainWindow(TaskManager(tasks), storage,
                            SessionStorage(folder / "sessions.txt"), login.session)
        window.show()
        return app.exec()

    def __eq__(self, other):
        return super().__eq__(other)

    def __repr__(self):
        return super().__repr__()

    def __str__(self):
        return super().__str__()

    def __lt__(self, other):
        return super().__lt__(other)

    def __le__(self, other):
        return super().__le__(other)

    def __gt__(self, other):
        return super().__gt__(other)

    def __ge__(self, other):
        return super().__ge__(other)

    def comparison_key(self):
        return super().comparison_key()
