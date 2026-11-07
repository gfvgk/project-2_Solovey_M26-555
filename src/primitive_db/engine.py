"""Основной цикл программы и разбор команд."""

import shlex

import prompt

from primitive_db.constants import META_FILE, PROMPT_TEXT
from primitive_db.core import create_table, drop_table, list_tables
from primitive_db.utils import load_metadata, save_metadata


def print_help():
    """Выводит справку по командам."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def print_invalid_value(value):
    """Выводит сообщение о некорректном значении."""
    print(f"Некорректное значение: {value}. Попробуйте снова.")


def print_tables(metadata):
    """Выводит список таблиц."""
    tables = list_tables(metadata)
    if not tables:
        print("Таблиц пока нет.")
    for table_name in tables:
        print(f"- {table_name}")


def process_command(metadata, user_input):
    """Выполняет одну команду. Возвращает False, если нужно выйти."""
    try:
        args = shlex.split(user_input)
    except ValueError:
        print_invalid_value(user_input)
        return True
    if not args:
        return True

    command, params = args[0], args[1:]
    match command:
        case "create_table":
            if len(params) < 2:
                print_invalid_value(user_input)
                return True
            new_metadata = create_table(metadata, params[0], params[1:])
            if new_metadata is not None:
                save_metadata(META_FILE, new_metadata)
        case "drop_table":
            if len(params) != 1:
                print_invalid_value(user_input)
                return True
            new_metadata = drop_table(metadata, params[0])
            if new_metadata is not None:
                save_metadata(META_FILE, new_metadata)
        case "list_tables":
            print_tables(metadata)
        case "help":
            print_help()
        case "exit":
            return False
        case _:
            print(f"Функции {command} нет. Попробуйте снова.")
    return True


def run():
    """Запускает основной цикл программы."""
    print_help()

    while True:
        metadata = load_metadata(META_FILE)
        try:
            user_input = prompt.string(PROMPT_TEXT).strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not process_command(metadata, user_input):
            break
        print()