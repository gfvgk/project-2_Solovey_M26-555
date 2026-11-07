"""Основной цикл программы и разбор команд."""

import prompt
from prettytable import PrettyTable

from primitive_db.constants import META_FILE, PROMPT_TEXT
from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    insert,
    list_tables,
    select,
    table_info,
    update,
)
from primitive_db.parser import parse_set, parse_values, parse_where, tokenize
from primitive_db.utils import (
    delete_table_data,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def print_help():
    """Выводит справку по командам."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\n***Операции с данными***")
    print("Функции:")
    print(
        "<command> insert into <имя_таблицы> values "
        "(<значение1>, <значение2>, ...) - создать запись."
    )
    print(
        "<command> select from <имя_таблицы> where <столбец> = <значение> "
        "- прочитать записи по условию."
    )
    print("<command> select from <имя_таблицы> - прочитать все записи.")
    print(
        "<command> update <имя_таблицы> set <столбец1> = <новое_значение1> "
        "where <столбец_условия> = <значение_условия> - обновить запись."
    )
    print(
        "<command> delete from <имя_таблицы> where <столбец> = <значение> "
        "- удалить запись."
    )
    print("<command> info <имя_таблицы> - вывести информацию о таблице.")

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


def print_records(columns, records):
    """Выводит записи в виде таблицы PrettyTable."""
    table = PrettyTable()
    table.field_names = columns
    for record in records:
        table.add_row([record.get(column) for column in columns])
    print(table)


def is_keyword(token, keyword):
    """Проверяет, что токен — ключевое слово (без учёта регистра)."""
    return token.lower() == keyword


def find_keyword(tokens, keyword):
    """Возвращает индекс ключевого слова в токенах или -1."""
    for index, token in enumerate(tokens):
        if is_keyword(token, keyword):
            return index
    return -1


def handle_create_table(metadata, params):
    """create_table <таблица> <столбец:тип> ..."""
    if len(params) < 2:
        raise ValueError(" ".join(params) or "create_table")
    new_metadata = create_table(metadata, params[0], params[1:])
    if new_metadata is not None:
        save_metadata(META_FILE, new_metadata)


def handle_drop_table(metadata, params):
    """drop_table <таблица>"""
    if len(params) != 1:
        raise ValueError(" ".join(params) or "drop_table")
    new_metadata = drop_table(metadata, params[0])
    if new_metadata is not None:
        save_metadata(META_FILE, new_metadata)
        delete_table_data(params[0])


def handle_insert(metadata, params):
    """insert into <таблица> values (<значение1>, ...)"""
    if (
        len(params) < 4
        or not is_keyword(params[0], "into")
        or not is_keyword(params[2], "values")
    ):
        raise ValueError(" ".join(params) or "insert")
    table_name = params[1]
    values = parse_values(params[3:])
    new_data = insert(metadata, table_name, load_table_data(table_name), values)
    if new_data is not None:
        save_table_data(table_name, new_data)


def handle_select(metadata, params):
    """select from <таблица> [where <столбец> = <значение>]"""
    if len(params) < 2 or not is_keyword(params[0], "from"):
        raise ValueError(" ".join(params) or "select")
    table_name = params[1]
    where_clause = None
    if len(params) > 2:
        if not is_keyword(params[2], "where"):
            raise ValueError(params[2])
        where_clause = parse_where(params[3:])

    records = select(metadata, table_name, load_table_data(table_name), where_clause)
    if records is not None:
        print_records(list(metadata[table_name]), records)


def handle_update(metadata, params):
    """update <таблица> set <столбец> = <значение> where <столбец> = <значение>"""
    where_index = find_keyword(params, "where")
    if len(params) < 3 or not is_keyword(params[1], "set") or where_index == -1:
        raise ValueError(" ".join(params) or "update")
    table_name = params[0]
    set_clause = parse_set(params[2:where_index])
    where_clause = parse_where(params[where_index + 1 :])
    new_data = update(
        metadata, table_name, load_table_data(table_name), set_clause, where_clause
    )
    if new_data is not None:
        save_table_data(table_name, new_data)


def handle_delete(metadata, params):
    """delete from <таблица> where <столбец> = <значение>"""
    if (
        len(params) < 3
        or not is_keyword(params[0], "from")
        or not is_keyword(params[2], "where")
    ):
        raise ValueError(" ".join(params) or "delete")
    table_name = params[1]
    where_clause = parse_where(params[3:])
    new_data = delete(metadata, table_name, load_table_data(table_name), where_clause)
    if new_data is not None:
        save_table_data(table_name, new_data)


def handle_info(metadata, params):
    """info <таблица>"""
    if len(params) != 1:
        raise ValueError(" ".join(params) or "info")
    table_info(metadata, params[0], load_table_data(params[0]))


def process_command(metadata, user_input):
    """Выполняет одну команду. Возвращает False, если нужно выйти."""
    tokens = tokenize(user_input)
    if not tokens:
        return True

    command, params = tokens[0], tokens[1:]
    match command:
        case "create_table":
            handle_create_table(metadata, params)
        case "drop_table":
            handle_drop_table(metadata, params)
        case "list_tables":
            print_tables(metadata)
        case "insert":
            handle_insert(metadata, params)
        case "select":
            handle_select(metadata, params)
        case "update":
            handle_update(metadata, params)
        case "delete":
            handle_delete(metadata, params)
        case "info":
            handle_info(metadata, params)
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

        try:
            should_continue = process_command(metadata, user_input)
        except KeyError as error:
            print(f'Ошибка: Таблица "{error.args[0]}" не существует.')
            should_continue = True
        except ValueError as error:
            print_invalid_value(error)
            should_continue = True

        if not should_continue:
            break
        print()