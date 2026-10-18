from abc import ABCMeta, abstractmethod

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QPushButton, QLineEdit, QTextEdit, QComboBox,
                               QSpinBox, QListWidget, QLabel, QCheckBox, QWidget)

from models import Entity, PairMap


class QtAbstractMeta(ABCMeta, type(QWidget)):
    def __eq__(cls, other):
        return cls is other

    def __lt__(cls, other):
        if not isinstance(other, type):
            return NotImplemented
        return (cls.__module__, cls.__name__, id(cls)) < (other.__module__, other.__name__, id(other))

    def __le__(cls, other):
        if not isinstance(other, type):
            return NotImplemented
        return cls == other or cls < other

    def __gt__(cls, other):
        if not isinstance(other, type):
            return NotImplemented
        return not cls <= other

    def __ge__(cls, other):
        if not isinstance(other, type):
            return NotImplemented
        return not cls < other

    def __repr__(cls):
        return type.__repr__(cls)

    def __str__(cls):
        return type.__repr__(cls)

    def __hash__(cls):
        return type.__hash__(cls)


class WidgetIdentity(Entity, metaclass=QtAbstractMeta):
    def __init__(self, *arguments):
        # Метакласс Qt сам не блокирует создание абстрактных подклассов.
        if type(self).__abstractmethods__:
            raise TypeError("Нельзя создать абстрактный компонент интерфейса.")
        super().__init__(*arguments)
        self.controls = PairMap()

    @property
    def controls(self):
        return self._controls

    @controls.setter
    def controls(self, value):
        if not isinstance(value, PairMap):
            raise ValueError("Компоненты должны храниться в PairMap.")
        if any(not isinstance(name, str) or not isinstance(widget, QWidget) for name, widget in value):
            raise ValueError("Ожидаются пары: имя компонента и виджет Qt.")
        self._controls = value

    @property
    def object_name(self):
        return self.objectName()

    @object_name.setter
    def object_name(self, value):
        if not isinstance(value, str):
            raise ValueError("Имя компонента должно быть строкой.")
        self.setObjectName(value)

    @abstractmethod
    def comparison_key(self):
        return (type(self).__name__, self.object_name, id(self))

    def __str__(self):
        return f"{type(self).__name__}: {self.objectName() or 'без имени'}"

    def __eq__(self, other):
        return super().__eq__(other)

    def __repr__(self):
        return super().__repr__()

    def __lt__(self, other):
        return super().__lt__(other)

    def __le__(self, other):
        return super().__le__(other)

    def __gt__(self, other):
        return super().__gt__(other)

    def __ge__(self, other):
        return super().__ge__(other)


class ActionButton(WidgetIdentity, QPushButton):
    @property
    def caption(self):
        return self.text()

    @caption.setter
    def caption(self, value):
        if not isinstance(value, str):
            raise ValueError("Недопустимое значение caption.")
        self.setText(value)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.click()
            event.accept()
        else:
            super().keyPressEvent(event)

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


class LoginEdit(WidgetIdentity, QLineEdit):
    @property
    def text_value(self):
        return self.text()

    @text_value.setter
    def text_value(self, value):
        if not isinstance(value, str):
            raise ValueError("Недопустимое значение text_value.")
        self.setText(value)

    def focusOutEvent(self, event):
        self.setText(self.text().strip())
        super().focusOutEvent(event)

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


class SearchEdit(WidgetIdentity, QLineEdit):
    @property
    def text_value(self):
        return self.text()

    @text_value.setter
    def text_value(self, value):
        if not isinstance(value, str):
            raise ValueError("Недопустимое значение text_value.")
        self.setText(value)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.clear()
            event.accept()
        else:
            super().keyPressEvent(event)

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


class TitleEdit(WidgetIdentity, QLineEdit):
    @property
    def text_value(self):
        return self.text()

    @text_value.setter
    def text_value(self, value):
        if not isinstance(value, str):
            raise ValueError("Недопустимое значение text_value.")
        self.setText(value)

    def focusOutEvent(self, event):
        self.setText(self.text().strip())
        super().focusOutEvent(event)

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


class DescriptionEdit(WidgetIdentity, QTextEdit):
    @property
    def text_value(self):
        return self.toPlainText()

    @text_value.setter
    def text_value(self, value):
        if not isinstance(value, str):
            raise ValueError("Недопустимое значение text_value.")
        self.setPlainText(value)

    def insertFromMimeData(self, source):
        self.insertPlainText(source.text())

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


class TaskTypeCombo(WidgetIdentity, QComboBox):
    @property
    def selected_index(self):
        return self.currentIndex()

    @selected_index.setter
    def selected_index(self, value):
        if type(value) is not int or not -1 <= value < self.count():
            raise ValueError("Недопустимое значение selected_index.")
        self.setCurrentIndex(value)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Home:
            self.setCurrentIndex(0)
            event.accept()
        elif event.key() == Qt.Key.Key_End:
            self.setCurrentIndex(self.count() - 1)
            event.accept()
        else:
            super().keyPressEvent(event)

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


class PrioritySpin(WidgetIdentity, QSpinBox):
    @property
    def number(self):
        return self.value()

    @number.setter
    def number(self, value):
        if type(value) is not int or not self.minimum() <= value <= self.maximum():
            raise ValueError("Недопустимое значение number.")
        self.setValue(value)

    def textFromValue(self, value):
        names = ("", "1 — высокий", "2 — средний", "3 — низкий")
        return names[value] if 1 <= value <= 3 else str(value)

    def valueFromText(self, text):
        number = text.split(" — ")[0].strip()
        return int(number) if number in ("1", "2", "3") else self.value()

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


class StatusCombo(WidgetIdentity, QComboBox):
    @property
    def selected_index(self):
        return self.currentIndex()

    @selected_index.setter
    def selected_index(self, value):
        if type(value) is not int or not -1 <= value < self.count():
            raise ValueError("Недопустимое значение selected_index.")
        self.setCurrentIndex(value)

    def wheelEvent(self, event):
        event.ignore()

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


class TaskList(WidgetIdentity, QListWidget):
    @property
    def selected_row(self):
        return self.currentRow()

    @selected_row.setter
    def selected_row(self, value):
        if type(value) is not int or not -1 <= value < self.count():
            raise ValueError("Недопустимое значение selected_row.")
        self.setCurrentRow(value)

    deleteRequested = Signal()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            self.deleteRequested.emit()
            event.accept()
        else:
            super().keyPressEvent(event)

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


class CounterLabel(WidgetIdentity, QLabel):
    @property
    def caption(self):
        return self.text()

    @caption.setter
    def caption(self, value):
        if not isinstance(value, str):
            raise ValueError("Недопустимое значение caption.")
        self.setText(value)

    def setText(self, text):
        super().setText(text)
        self.setAccessibleName(text)

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


class CompletedCheck(WidgetIdentity, QCheckBox):
    @property
    def checked(self):
        return self.isChecked()

    @checked.setter
    def checked(self, value):
        if type(value) is not bool:
            raise ValueError("Недопустимое значение checked.")
        self.setChecked(value)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.toggle()
            event.accept()
        else:
            super().keyPressEvent(event)

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
