from abc import ABC, abstractmethod
from datetime import datetime


class Comparable(ABC):
    @abstractmethod
    def comparison_key(self):
        pass

    def __eq__(self, other):
        if not isinstance(other, Comparable):
            return NotImplemented
        return self.comparison_key() == other.comparison_key()

    def __lt__(self, other):
        if not isinstance(other, Comparable):
            return NotImplemented
        return self.comparison_key() < other.comparison_key()

    def __le__(self, other):
        if not isinstance(other, Comparable):
            return NotImplemented
        return self.comparison_key() <= other.comparison_key()

    def __gt__(self, other):
        if not isinstance(other, Comparable):
            return NotImplemented
        return self.comparison_key() > other.comparison_key()

    def __ge__(self, other):
        if not isinstance(other, Comparable):
            return NotImplemented
        return self.comparison_key() >= other.comparison_key()

    def __repr__(self):
        return f"{type(self).__name__}({self.comparison_key()!r})"

    def __str__(self):
        return f"{type(self).__name__}: {self.comparison_key()}"


class Entity(Comparable, ABC):
    @abstractmethod
    def comparison_key(self):
        pass

    @staticmethod
    def required_text(value, label, limit=120):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{label}: введите непустой текст.")
        value = value.strip()
        if len(value) > limit or any(ord(char) < 32 for char in value):
            raise ValueError(f"{label}: максимум {limit} символов, без переносов и табуляции.")
        return value

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


class PairMap(Entity):
    def __init__(self, pairs=()):
        self.pairs = pairs

    @property
    def pairs(self):
        return list(self._pairs)

    @pairs.setter
    def pairs(self, value):
        candidate = []
        for key, item in value:
            if any(old_key == key for old_key, _ in candidate):
                raise ValueError("Ключи не должны повторяться.")
            candidate.append((key, item))
        self._pairs = candidate

    def get(self, key):
        for old_key, value in self._pairs:
            if old_key == key:
                return value
        raise KeyError(key)

    def add(self, key, value):
        if any(old_key == key for old_key, _ in self._pairs):
            raise KeyError(key)
        self._pairs.append((key, value))

    def update(self, key, value):
        for index, (old_key, _) in enumerate(self._pairs):
            if old_key == key:
                self._pairs[index] = (key, value)
                return
        raise KeyError(key)

    def remove(self, key):
        for index, (old_key, _) in enumerate(self._pairs):
            if old_key == key:
                return self._pairs.pop(index)[1]
        raise KeyError(key)

    def comparison_key(self):
        return (type(self).__name__, tuple((repr(key), repr(value)) for key, value in self._pairs))

    def __eq__(self, other):
        if not isinstance(other, PairMap):
            return NotImplemented
        return self._pairs == other._pairs

    def __len__(self):
        return len(self._pairs)

    def __iter__(self):
        return iter(self.pairs)

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self.update(key, value)

    def __delitem__(self, key):
        self.remove(key)

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


class Task(Entity):
    def __init__(self, title, description="", priority=2, completed=False):
        self.title = title
        self.description = description
        self.priority = priority
        self.completed = completed

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = self.required_text(value, "Название")

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        if not isinstance(value, str) or len(value) > 3000:
            raise ValueError("Описание: максимум 3000 символов.")
        self._description = value.strip()

    @property
    def priority(self):
        return self._priority

    @priority.setter
    def priority(self, value):
        if type(value) is not int or value not in (1, 2, 3):
            raise ValueError("Приоритет должен быть числом от 1 до 3.")
        self._priority = value

    @property
    def completed(self):
        return self._completed

    @completed.setter
    def completed(self, value):
        if type(value) is not bool:
            raise ValueError("Состояние выполнения должно быть bool.")
        self._completed = value

    @abstractmethod
    def kind(self):
        pass

    @abstractmethod
    def extra(self):
        pass

    @abstractmethod
    def context(self):
        pass

    def toggle(self):
        self.completed = not self.completed

    def comparison_key(self):
        return ("Task", self.priority, self.title.casefold(), self.kind(),
                self.title, self.description, self.completed, self.extra())

    def __str__(self):
        state = "Выполнена" if self.completed else "Осталась"
        return f"{self.title} · {self.context()} · приоритет {self.priority} · {state}"

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


class RegularTask(Task):
    def kind(self):
        return "regular"

    def extra(self):
        return ""

    def context(self):
        return "Обычная"

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


class StudyTask(Task):
    def __init__(self, title, description="", priority=2, completed=False, subject=""):
        super().__init__(title, description, priority, completed)
        self.subject = subject

    @property
    def subject(self):
        return self._subject

    @subject.setter
    def subject(self, value):
        self._subject = self.required_text(value, "Предмет")

    def kind(self):
        return "study"

    def extra(self):
        return self.subject

    def context(self):
        return f"Учебная: {self.subject}"

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


class WorkTask(Task):
    def __init__(self, title, description="", priority=2, completed=False, project=""):
        super().__init__(title, description, priority, completed)
        self.project = project

    @property
    def project(self):
        return self._project

    @project.setter
    def project(self, value):
        self._project = self.required_text(value, "Проект")

    def kind(self):
        return "work"

    def extra(self):
        return self.project

    def context(self):
        return f"Рабочая: {self.project}"

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


class TaskManager(Entity):
    def __init__(self, tasks=()):
        self.tasks = tasks

    @property
    def tasks(self):
        return list(self._tasks)

    @tasks.setter
    def tasks(self, value):
        candidate = list(value)
        if any(not isinstance(task, Task) for task in candidate):
            raise ValueError("Список может содержать только задачи.")
        self._tasks = candidate

    def add(self, task):
        self.tasks = self._tasks + [task]

    def replace(self, index, task):
        candidate = self.tasks
        candidate[index] = task
        self.tasks = candidate

    def remove(self, index):
        return self._tasks.pop(index)

    def toggle(self, index):
        self._tasks[index].toggle()

    def visible(self, query="", state=0, descending=False):
        items = [(index, task) for index, task in enumerate(self._tasks)
                 if query.casefold() in task.title.casefold()
                 and (state == 0 or task.completed == (state == 2))]
        return sorted(items, key=self.sort_key, reverse=descending)

    @staticmethod
    def sort_key(item):
        return item[1]

    def counts(self):
        done = sum(task.completed for task in self._tasks)
        return len(self._tasks), done, len(self._tasks) - done

    def comparison_key(self):
        return (type(self).__name__, tuple(self._tasks))

    @staticmethod
    def demo():
        return [
            RegularTask("Купить продукты", "Молоко, хлеб, яблоки", 2),
            StudyTask("Подготовиться к зачёту", "Повторить принципы ООП", 1, False, "ООП"),
            WorkTask("Исправить интерфейс", "Проверить отступы", 1, False, "Список задач"),
            RegularTask("Полить растения", "", 3, True),
            StudyTask("Решить примеры", "Упражнения 1–5", 2, False, "Математика"),
            WorkTask("Написать отчёт", "Результаты недели", 2, False, "Практика"),
            RegularTask("Прогуляться", "30 минут", 3),
            StudyTask("Прочитать главу", "Глава о наследовании", 2, True, "Программирование"),
            WorkTask("Проверить приложение", "Добавление и удаление", 1, True, "Список задач"),
            RegularTask("Убрать рабочий стол", "", 3),
        ]

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


class Session(Entity):
    def __init__(self, login):
        self.login = login
        self.time_in = datetime.now()
        self.time_out = None

    @property
    def login(self):
        return self._login

    @login.setter
    def login(self, value):
        value = self.required_text(value, "Логин", 30)
        if "|" in value:
            raise ValueError("Логин не должен содержать символ |.")
        self._login = value

    @property
    def time_in(self):
        return self._time_in

    @time_in.setter
    def time_in(self, value):
        if not isinstance(value, datetime):
            raise ValueError("Время входа должно быть datetime.")
        self._time_in = value

    @property
    def time_out(self):
        return self._time_out

    @time_out.setter
    def time_out(self, value):
        if value is not None and not isinstance(value, datetime):
            raise ValueError("Время выхода должно быть datetime или None.")
        self._time_out = value

    def finish(self):
        self.time_out = datetime.now()

    def comparison_key(self):
        end = self.time_out.isoformat() if self.time_out else ""
        return (type(self).__name__, self.login, self.time_in.isoformat(), end)

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
