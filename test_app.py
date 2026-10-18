import ast
import inspect
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from PySide6.QtCore import Qt, QTimer, QMimeData
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox

from models import Task, RegularTask, StudyTask, WorkTask, PairMap, TaskManager, Session
from storage import TaskStorage, SessionStorage
from ui import MainWindow, TaskDialog, LoginDialog
from widgets import DescriptionEdit, SearchEdit, PrioritySpin


class AppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self._temporary = tempfile.TemporaryDirectory()
        self._folder = Path(self._temporary.name)
        self._storage = TaskStorage(self._folder / "tasks.csv")
        self._reports = SessionStorage(self._folder / "sessions.txt")

    def tearDown(self):
        for widget in self.app.topLevelWidgets():
            widget.hide()
            widget.deleteLater()
        self.app.processEvents()
        self._temporary.cleanup()

    def test_abstract_class(self):
        with self.assertRaises(TypeError):
            Task("Недоступно")

    def test_validation_and_properties(self):
        task = RegularTask("  Название  ")
        self.assertEqual(task.title, "Название")
        for value in ("", "\n", "a" * 121, "с\tтабуляцией"):
            with self.assertRaises(ValueError):
                task.title = value
        for value in (0, 4, "1", True):
            with self.assertRaises(ValueError):
                task.priority = value
        with self.assertRaises(ValueError):
            task.completed = 1
        with self.assertRaises(ValueError):
            task.description = "a" * 3001
        with self.assertRaises(ValueError):
            StudyTask("Задача", subject="")
        with self.assertRaises(ValueError):
            WorkTask("Задача", project="")
        with self.assertRaises(ValueError):
            Session("x|y")

    def test_polymorphism_and_comparison(self):
        tasks = [RegularTask("A", priority=3), StudyTask("B", priority=1, subject="ООП"),
                 WorkTask("C", priority=2, project="Практика")]
        self.assertEqual([task.kind() for task in tasks], ["regular", "study", "work"])
        self.assertIn("ООП", str(tasks[1]))
        self.assertIn("Практика", str(tasks[2]))
        self.assertEqual([task.priority for task in sorted(tasks)], [1, 2, 3])
        self.assertEqual(tasks[0], RegularTask("A", priority=3))
        self.assertTrue(tasks[1] < tasks[0])
        self.assertTrue(tasks[1] <= tasks[0])
        self.assertTrue(tasks[0] > tasks[1])
        self.assertTrue(tasks[0] >= tasks[1])
        self.assertIn("RegularTask", repr(tasks[0]))

    def test_pair_map(self):
        mapping = PairMap((("a", 1),))
        mapping.add("b", 2)
        self.assertEqual(mapping.get("b"), 2)
        mapping["b"] = 3
        self.assertEqual(mapping["b"], 3)
        self.assertEqual(len(mapping), 2)
        self.assertEqual(list(mapping), [("a", 1), ("b", 3)])
        with self.assertRaises(KeyError):
            mapping.add("a", 9)
        with self.assertRaises(KeyError):
            mapping.update("missing", 9)
        del mapping["a"]
        self.assertEqual(mapping.remove("b"), 3)
        self.assertEqual(len(mapping), 0)
        with self.assertRaises(KeyError):
            mapping.get("missing")
        with self.assertRaises(ValueError):
            mapping.pairs = (("a", 1), ("a", 2))
        self.assertEqual(PairMap((("a", 1),)), PairMap((("a", 1),)))
        self.assertTrue(PairMap((("a", 1),)) < PairMap((("b", 1),)))

    def test_csv_round_trip(self):
        tasks = TaskManager.demo()
        tasks[0].description = 'Текст, с запятой\nи "кавычками"'
        self.assertEqual(len(tasks), 10)
        self._storage.save(tasks)
        loaded = self._storage.load()
        self.assertEqual(loaded, tasks)
        self.assertIsInstance(loaded[1], StudyTask)
        self.assertIsInstance(loaded[2], WorkTask)
        self._storage.save([])
        self.assertTrue(self._storage.exists())
        self.assertEqual(self._storage.load(), [])

    def test_invalid_csv_does_not_overwrite(self):
        self._storage.path.write_text("ошибка", encoding="utf-8")
        before = self._storage.path.read_bytes()
        with self.assertRaises(ValueError):
            self._storage.load()
        self.assertEqual(self._storage.path.read_bytes(), before)

    def test_atomic_save_failure(self):
        self._storage.save(TaskManager.demo())
        before = self._storage.path.read_bytes()
        with self.assertRaises(ValueError):
            self._storage.save(["Не задача"])
        self.assertEqual(self._storage.path.read_bytes(), before)
        self.assertFalse(self._storage.path.with_suffix(".tmp").exists())

    def test_manager(self):
        manager = TaskManager(TaskManager.demo())
        self.assertEqual(manager.counts(), (10, 3, 7))
        self.assertEqual(len(manager.visible("ЗАЧЁТ")), 1)
        self.assertEqual(len(manager.visible(state=1)), 7)
        self.assertEqual(len(manager.visible(state=2)), 3)
        self.assertEqual(manager.visible()[0][1].priority, 1)
        self.assertEqual(manager.visible(descending=True)[0][1].priority, 3)
        manager.toggle(0)
        self.assertTrue(manager.tasks[0].completed)
        manager.replace(0, WorkTask("Изменено", project="Проект"))
        self.assertIsInstance(manager.tasks[0], WorkTask)
        manager.remove(0)
        manager.add(RegularTask("Добавлено"))
        self.assertEqual(len(manager.tasks), 10)

    def test_login_dialog(self):
        dialog = LoginDialog()
        dialog.accept()
        self.assertIsNone(dialog.session)
        self.assertTrue(dialog.controls["error"].text())
        dialog.controls["login"].setText("  Студент  ")
        dialog.accept()
        self.assertEqual(dialog.session.login, "Студент")
        self.assertEqual(dialog.result(), QDialog.DialogCode.Accepted)

    def test_task_dialog_validation_and_types(self):
        dialog = TaskDialog(self._storage)
        dialog.accept()
        self.assertIsNone(dialog.task)
        dialog.controls["title"].setText("Учебная задача")
        dialog.controls["kind"].setCurrentIndex(1)
        self.assertFalse(dialog.controls["extra"].isHidden())
        dialog.accept()
        self.assertIsNone(dialog.task)
        dialog.controls["extra"].setText("ООП")
        dialog.accept()
        self.assertIsInstance(dialog.task, StudyTask)
        edit = TaskDialog(self._storage, dialog.task)
        edit.controls["kind"].setCurrentIndex(2)
        edit.controls["extra"].setText("Практика")
        edit.accept()
        self.assertIsInstance(edit.task, WorkTask)
        self.assertEqual(edit.task.project, "Практика")

    def fill_add_dialog(self):
        dialog = self.app.activeModalWidget()
        self.assertIsInstance(dialog, TaskDialog)
        dialog.controls["title"].setText("Новая учебная")
        dialog.controls["kind"].setCurrentIndex(1)
        dialog.controls["extra"].setText("ООП")
        dialog.controls["priority"].setValue(1)
        dialog.accept()

    def fill_edit_dialog(self):
        dialog = self.app.activeModalWidget()
        dialog.controls["title"].setText("Изменённая учебная")
        dialog.controls["description"].setPlainText("Описание после редактирования")
        dialog.accept()

    def test_window_user_flow_and_report(self):
        manager = TaskManager([RegularTask("Начальная")])
        self._storage.save(manager.tasks)
        window = MainWindow(manager, self._storage, self._reports, Session("Студент"))
        window.show()
        self.app.processEvents()
        self.assertFalse(window.controls["edit"].isEnabled())
        QTimer.singleShot(0, self.fill_add_dialog)
        QTest.mouseClick(window.controls["add"], Qt.MouseButton.LeftButton)
        self.assertEqual(len(manager.tasks), 2)
        self.assertEqual(self._storage.load(), manager.tasks)
        window.controls["list"].setCurrentRow(0)
        self.assertEqual(window.selected_index(), 1)
        QTimer.singleShot(0, self.fill_edit_dialog)
        QTest.mouseClick(window.controls["edit"], Qt.MouseButton.LeftButton)
        self.assertEqual(manager.tasks[1].title, "Изменённая учебная")
        QTest.mouseClick(window.controls["toggle"], Qt.MouseButton.LeftButton)
        self.assertTrue(manager.tasks[1].completed)
        window.controls["search"].setText("изменённая")
        self.assertEqual(window.controls["list"].count(), 1)
        window.controls["state"].setCurrentIndex(1)
        self.assertEqual(window.controls["list"].count(), 0)
        window.controls["state"].setCurrentIndex(2)
        self.assertEqual(window.controls["list"].count(), 1)
        window.controls["list"].setCurrentRow(0)
        with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Yes):
            QTest.keyClick(window.controls["list"], Qt.Key.Key_Delete)
        self.assertEqual(len(manager.tasks), 1)
        self.assertEqual(self._storage.load(), manager.tasks)
        self.assertTrue(window.close())
        report = self._reports.path.read_text(encoding="utf-8")
        self.assertIn("Студент", report)
        self.assertIn("| login", report)
        self.assertEqual(report.count("Студент"), 1)
        self.assertTrue(window.close())
        self.assertEqual(self._reports.path.read_text(encoding="utf-8").count("Студент"), 1)

    def test_rollback_and_close_failure(self):
        manager = TaskManager([RegularTask("Задача")])
        window = MainWindow(manager, self._storage, self._reports, Session("Тест"))
        window.show()
        self.app.processEvents()
        with patch.object(TaskStorage, "save", side_effect=OSError("Нет доступа")):
            with patch.object(QMessageBox, "critical", return_value=QMessageBox.StandardButton.Ok):
                self.assertFalse(window.persist_change(manager.toggle, 0))
                self.assertFalse(manager.tasks[0].completed)
                self.assertFalse(window.close())
        self.assertFalse(self._reports.path.exists())
        self.assertTrue(window.close())
        self.assertTrue(self._reports.path.exists())

    def test_session_append_and_format(self):
        for login in ("Первый", "Второй"):
            session = Session(login)
            session.finish()
            self._reports.save(session)
        text = self._reports.path.read_text(encoding="utf-8")
        self.assertIn("Первый", text)
        self.assertIn("Второй", text)
        rows = [line for line in text.splitlines() if "Первый" in line or "Второй" in line]
        for row in rows:
            values = row.split("|")
            datetime.strptime(values[2].strip(), "%d.%m.%Y %H:%M:%S")
            datetime.strptime(values[3].strip(), "%d.%m.%Y %H:%M:%S")

    def test_widget_overrides(self):
        search = SearchEdit()
        search.setText("Запрос")
        QTest.keyClick(search, Qt.Key.Key_Escape)
        self.assertEqual(search.text(), "")
        description = DescriptionEdit()
        mime = QMimeData()
        mime.setText("Обычный текст")
        mime.setHtml("<b>Обычный текст</b>")
        description.insertFromMimeData(mime)
        self.assertEqual(description.toPlainText(), "Обычный текст")
        priority = PrioritySpin()
        priority.setRange(1, 3)
        self.assertEqual(priority.valueFromText("2 — средний"), 2)
        self.assertIn("высокий", priority.textFromValue(1))
        self.assertTrue(search == search)
        self.assertTrue(search <= search)
        self.assertIn("SearchEdit", repr(search))

    def test_no_dict_in_application_sources(self):
        folder = Path(__file__).resolve().parent
        for name in ("models.py", "storage.py", "widgets.py", "ui.py", "main.py"):
            tree = ast.parse((folder / name).read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                self.assertNotIsInstance(node, (ast.Dict, ast.DictComp))
                if isinstance(node, ast.Name):
                    self.assertNotIn(node.id, ("dict", "DictReader", "DictWriter"))

    def enter_login(self):
        dialog = self.app.activeModalWidget()
        dialog.controls["login"].setText("Запуск")
        dialog.accept()
        QTimer.singleShot(0, self.close_main)

    def close_main(self):
        for widget in self.app.topLevelWidgets():
            if isinstance(widget, MainWindow) and widget.isVisible():
                widget.close()

    def test_full_startup_first_and_empty_second_run(self):
        import ui
        with patch.object(ui, "__file__", str(self._folder / "ui.py")):
            QTimer.singleShot(0, self.enter_login)
            self.assertEqual(MainWindow.run(), 0)
            store = TaskStorage(self._folder / "data" / "tasks.csv")
            self.assertEqual(len(store.load()), 10)
            store.save([])
            QTimer.singleShot(0, self.enter_login)
            self.assertEqual(MainWindow.run(), 0)
            self.assertEqual(store.load(), [])
        report = (self._folder / "data" / "sessions.txt").read_text(encoding="utf-8")
        self.assertEqual(report.count("Запуск"), 2)

    @staticmethod
    def application_classes():
        import models
        import storage
        import widgets
        import ui
        return [value for module in (models, storage, widgets, ui)
                for _, value in inspect.getmembers(module, inspect.isclass)
                if value.__module__ == module.__name__]

    def test_explicit_special_methods_in_every_class(self):
        required = ("__eq__", "__repr__", "__str__", "__lt__", "__le__", "__gt__", "__ge__")
        for cls in self.application_classes():
            for name in required:
                self.assertIn(name, vars(cls), f"{cls.__name__}: нет явного {name}")

    def test_abstract_ancestry_and_qt_enforcement(self):
        from abc import ABCMeta
        from PySide6.QtWidgets import QPushButton
        from models import Comparable, Entity
        from widgets import QtAbstractMeta, WidgetIdentity
        for cls in self.application_classes():
            if cls is QtAbstractMeta:
                self.assertTrue(issubclass(cls, ABCMeta))
            else:
                self.assertTrue(issubclass(cls, Comparable))
        for cls in (Comparable, Entity, Task, WidgetIdentity):
            self.assertTrue(inspect.isabstract(cls))
            with self.assertRaises(TypeError):
                cls()

        class MissingWidget(WidgetIdentity, QPushButton):
            pass

        self.assertTrue(inspect.isabstract(MissingWidget))
        with self.assertRaises(TypeError):
            MissingWidget()
        concrete = SearchEdit()
        self.assertFalse(inspect.isabstract(type(concrete)))

    def test_every_private_field_has_getter_and_setter(self):
        for cls in self.application_classes():
            tree = ast.parse(inspect.getsource(cls))
            private_fields = [node.attr for node in ast.walk(tree)
                              if isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Store)
                              and isinstance(node.value, ast.Name) and node.value.id == "self"
                              and node.attr.startswith("_")]
            properties = [value for _, value in inspect.getmembers(cls)
                          if isinstance(value, property) and value.fget and value.fset]
            for field in private_fields:
                self.assertTrue(any(field in prop.fget.__code__.co_names and
                                    field in prop.fset.__code__.co_names for prop in properties),
                                f"{cls.__name__}.{field}: нет геттера и сеттера")

    def test_widget_properties_and_validation(self):
        from widgets import (ActionButton, LoginEdit, TitleEdit, TaskTypeCombo,
                             StatusCombo, TaskList, CounterLabel, CompletedCheck)
        for cls, name in ((ActionButton, "caption"), (LoginEdit, "text_value"),
                          (SearchEdit, "text_value"), (TitleEdit, "text_value"),
                          (DescriptionEdit, "text_value"), (CounterLabel, "caption")):
            widget = cls()
            setattr(widget, name, "Текст")
            self.assertEqual(getattr(widget, name), "Текст")
            with self.assertRaises(ValueError):
                setattr(widget, name, 123)
        for cls in (TaskTypeCombo, StatusCombo):
            combo = cls()
            combo.addItems(("Первый", "Второй"))
            combo.selected_index = 1
            self.assertEqual(combo.selected_index, 1)
            with self.assertRaises(ValueError):
                combo.selected_index = 3
        priority = PrioritySpin()
        priority.setRange(1, 3)
        priority.number = 2
        self.assertEqual(priority.number, 2)
        with self.assertRaises(ValueError):
            priority.number = True
        listing = TaskList()
        listing.addItem("Строка")
        listing.selected_row = 0
        self.assertEqual(listing.selected_row, 0)
        with self.assertRaises(ValueError):
            listing.selected_row = 9
        check = CompletedCheck()
        check.checked = True
        self.assertTrue(check.checked)
        with self.assertRaises(ValueError):
            check.checked = 1

    def test_window_properties_and_component_mapping(self):
        manager = TaskManager([RegularTask("Задача")])
        session = Session("Проверка")
        window = MainWindow(manager, self._storage, self._reports, session)
        self.assertIs(window.manager, manager)
        self.assertIs(window.storage, self._storage)
        self.assertIs(window.session_storage, self._reports)
        self.assertIs(window.session, session)
        self.assertIsInstance(window.controls, PairMap)
        self.assertIsInstance(window.controls["search"], SearchEdit)
        self.assertFalse(window.report_saved)
        for name in ("manager", "storage", "session_storage", "session", "report_saved", "controls"):
            with self.assertRaises(ValueError):
                setattr(window, name, "Недопустимо")
        with self.assertRaises(ValueError):
            window.controls = PairMap((("name", "Не виджет"),))
        with self.assertRaises(ValueError):
            self._storage.task_types = [("regular", RegularTask)]
        with self.assertRaises(ValueError):
            self._storage.task_types = PairMap((("regular", str),))
        self.assertTrue(window.close())

    def test_class_metadata_identity_and_hash(self):
        from widgets import ActionButton
        self.assertEqual(ActionButton, ActionButton)
        self.assertNotEqual(ActionButton, SearchEdit)
        self.assertTrue(ActionButton < SearchEdit)
        self.assertTrue(ActionButton <= SearchEdit)
        self.assertTrue(SearchEdit > ActionButton)
        self.assertTrue(SearchEdit >= ActionButton)
        self.assertIsInstance(hash(ActionButton), int)
        self.assertIn("ActionButton", str(ActionButton))
        self.assertIn("ActionButton", repr(ActionButton))


if __name__ == "__main__":
    unittest.main()
