# Список задач

Приложение для Windows для ведения обычных, учебных и рабочих задач. Поддерживает добавление, редактирование, удаление, отметку выполнения, поиск и сортировку по приоритету. У учебных задач есть предмет, у рабочих — проект.

Python 3.13.5, PySide6 6.12.0. Интерфейс на русском языке.

## Готовая версия

Распакуйте архив `TaskList-v1.0.0-windows-x64.zip` и запустите `TaskList.exe` внутри папки `TaskList`. Python устанавливать не требуется. Все файлы из папки должны оставаться рядом с приложением.

## Запуск из исходников

Команды PowerShell из папки проекта:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

## Сборка

Сборка выполняется на Windows с помощью [PyInstaller](https://pyinstaller.org/en/stable/usage.html):

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
.\build.ps1
```

Результат: `dist/TaskList/TaskList.exe`. Для распространения упакуйте всю папку `dist/TaskList` в ZIP.

## Данные

При первом запуске создаются 10 демонстрационных задач. Изменения сохраняются в `data/tasks.csv`, отчёты о сеансах — в `data/sessions.txt`. При запуске готовой версии папка `data` создаётся рядом с исполняемым файлом.

Логин используется для отчёта. Список задач общий для всех логинов. Приоритет: 1 — высокий, 2 — средний, 3 — низкий.

## Проверка

```powershell
.\.venv\Scripts\python.exe -m unittest -v test_app
```
