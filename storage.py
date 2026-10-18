import csv
from pathlib import Path

from models import Entity, PairMap, RegularTask, StudyTask, WorkTask, Session, Task


class TaskStorage(Entity):
    HEADER = ("type", "title", "description", "priority", "completed", "extra")

    def __init__(self, path):
        self.path = path
        self.task_types = PairMap((("regular", RegularTask), ("study", StudyTask), ("work", WorkTask)))

    @property
    def task_types(self):
        return self._types

    @task_types.setter
    def task_types(self, value):
        if not isinstance(value, PairMap):
            raise ValueError("Типы задач должны храниться в PairMap.")
        for name, task_class in value:
            if not isinstance(name, str) or not isinstance(task_class, type) or not issubclass(task_class, Task):
                raise ValueError("Сопоставление должно связывать строки с классами задач.")
        self._types = value

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = Path(value)

    def comparison_key(self):
        return (type(self).__name__, str(self.path))

    def exists(self):
        return self.path.exists()

    def create_task(self, kind, title, description, priority, completed, extra=""):
        task_class = self.task_types.get(kind)
        if kind == "regular":
            return task_class(title, description, priority, completed)
        return task_class(title, description, priority, completed, extra)

    def load(self):
        tasks = []
        with self.path.open("r", encoding="utf-8-sig", newline="") as stream:
            rows = csv.reader(stream)
            if tuple(next(rows, ())) != self.HEADER:
                raise ValueError("Неверный заголовок CSV. Исходный файл сохранён.")
            for number, row in enumerate(rows, 2):
                try:
                    if len(row) != 6 or row[4] not in ("0", "1"):
                        raise ValueError("Неверный формат строки")
                    if row[0] == "regular" and row[5]:
                        raise ValueError("У обычной задачи нет дополнительного поля")
                    tasks.append(self.create_task(row[0], row[1], row[2], int(row[3]),
                                                  row[4] == "1", row[5]))
                except (ValueError, KeyError) as error:
                    raise ValueError(f"Строка CSV {number}: {error}") from error
        return tasks

    def save(self, tasks):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        try:
            with temporary.open("w", encoding="utf-8-sig", newline="") as stream:
                writer = csv.writer(stream)
                writer.writerow(self.HEADER)
                for task in tasks:
                    if not isinstance(task, Task):
                        raise ValueError("Можно сохранять только задачи.")
                    writer.writerow((task.kind(), task.title, task.description, task.priority,
                                     int(task.completed), task.extra()))
            temporary.replace(self.path)
        finally:
            if temporary.exists():
                temporary.unlink()

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


class SessionStorage(Entity):
    def __init__(self, path):
        self.path = path

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = Path(value)

    def comparison_key(self):
        return (type(self).__name__, str(self.path))

    def save(self, session):
        if not isinstance(session, Session) or session.time_out is None:
            raise ValueError("Сеанс должен быть завершён.")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        border = "+" + "-" * 76 + "+\n"
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(border)
            stream.write(f"| {'login':<30} | {'time_in':<19} | {'time_out':<19} |\n")
            stream.write("|" + "-" * 32 + "|" + "-" * 21 + "|" + "-" * 21 + "|\n")
            start = session.time_in.strftime("%d.%m.%Y %H:%M:%S")
            end = session.time_out.strftime("%d.%m.%Y %H:%M:%S")
            stream.write(f"| {session.login:<30} | {start} | {end} |\n")
            stream.write(border + "\n")

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
