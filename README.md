# Primitive DB

Консольная имитация базы данных на Python. Таблицы и данные хранятся в JSON-файлах.

## Установка

```bash
uv sync
```

Установка как отдельной команды:

```bash
uv build
uv tool install dist/primitive_db-<версия>-py3-none-any.whl
```

## Запуск

```bash
uv run database
```

или, после установки пакета:

```bash
database
```

## Управление таблицами

| Команда | Описание |
|---|---|
| `create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> ...` | создать таблицу |
| `list_tables` | показать список всех таблиц |
| `drop_table <имя_таблицы>` | удалить таблицу |
| `help` | справочная информация |
| `exit` | выход из программы |

Поддерживаемые типы: `int`, `str`, `bool`. Столбец `ID:int` добавляется автоматически.

Пример:

```
>>>Введите команду: create_table users name:str age:int is_active:bool
Таблица "users" успешно создана со столбцами: ID:int, name:str, age:int, is_active:bool

>>>Введите команду: list_tables
- users

>>>Введите команду: drop_table users
Таблица "users" успешно удалена.
```