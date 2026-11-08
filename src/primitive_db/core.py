"""Основная логика работы с таблицами и данными."""

from primitive_db.constants import ID_COLUMN, ID_TYPE, VALID_TYPES
from primitive_db.decorators import (
    confirm_action,
    create_cacher,
    handle_db_errors,
    log_time,
)

select_cache = create_cacher()


@handle_db_errors
def create_table(metadata, table_name, columns):
    """Создаёт таблицу. Возвращает обновлённые метаданные или None при ошибке."""
    if not table_name.isidentifier():
        raise ValueError(table_name)
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return None

    schema = {ID_COLUMN: ID_TYPE}
    for column in columns:
        name, _, column_type = column.partition(":")
        is_valid = (
            name.isidentifier() and column_type in VALID_TYPES and name not in schema
        )
        if not is_valid:
            raise ValueError(column)
        schema[name] = column_type

    metadata[table_name] = schema
    columns_text = format_columns(schema)
    print(f'Таблица "{table_name}" успешно создана со столбцами: {columns_text}')
    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    """Удаляет таблицу. Возвращает обновлённые метаданные."""
    if table_name not in metadata:
        raise KeyError(table_name)

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def list_tables(metadata):
    """Возвращает список имён всех таблиц."""
    return list(metadata)


def format_columns(schema):
    """Форматирует схему таблицы в строку вида ID:int, name:str."""
    return ", ".join(f"{name}:{kind}" for name, kind in schema.items())


def get_schema(metadata, table_name):
    """Возвращает схему таблицы. Если таблицы нет, выбрасывает KeyError."""
    if table_name not in metadata:
        raise KeyError(table_name)
    return metadata[table_name]


def validate_value(column_type, value):
    """Проверяет, что значение соответствует типу столбца."""
    if type(value) is not VALID_TYPES[column_type]:
        raise ValueError(value)


def validate_clause(schema, clause):
    """Проверяет, что столбцы условия существуют, а значения нужного типа."""
    for column, value in clause.items():
        if column not in schema:
            raise ValueError(column)
        validate_value(schema[column], value)


def matches(record, where_clause):
    """Проверяет, подходит ли запись под условие."""
    return all(record.get(column) == value for column, value in where_clause.items())


@handle_db_errors
@log_time
def insert(metadata, table_name, table_data, values):
    """Добавляет запись. Возвращает обновлённые данные таблицы."""
    schema = get_schema(metadata, table_name)
    columns = [column for column in schema if column != ID_COLUMN]
    if len(values) != len(columns):
        raise ValueError(f"ожидалось значений: {len(columns)}, получено: {len(values)}")

    for column, value in zip(columns, values):
        validate_value(schema[column], value)

    new_id = max((record[ID_COLUMN] for record in table_data), default=0) + 1
    record = {ID_COLUMN: new_id, **dict(zip(columns, values))}
    table_data.append(record)
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
    return table_data


@handle_db_errors
@log_time
def select(metadata, table_name, table_data, where_clause=None):
    """Возвращает записи таблицы, подходящие под условие (или все).

    Результаты одинаковых запросов к одинаковым данным берутся из кэша.
    """
    schema = get_schema(metadata, table_name)
    where_clause = where_clause or {}
    validate_clause(schema, where_clause)

    cache_key = repr((table_name, table_data, where_clause))
    return select_cache(
        cache_key,
        lambda: [record for record in table_data if matches(record, where_clause)],
    )


@handle_db_errors
def update(metadata, table_name, table_data, set_clause, where_clause):
    """Обновляет подходящие записи. Возвращает данные или None, если их нет."""
    schema = get_schema(metadata, table_name)
    if ID_COLUMN in set_clause:
        raise ValueError(ID_COLUMN)
    validate_clause(schema, set_clause)
    validate_clause(schema, where_clause)

    found = [record for record in table_data if matches(record, where_clause)]
    if not found:
        print("Записи, подходящие под условие, не найдены.")
        return None

    for record in found:
        record.update(set_clause)
        print(
            f'Запись с ID={record[ID_COLUMN]} в таблице "{table_name}" '
            "успешно обновлена."
        )
    return table_data


@handle_db_errors
@confirm_action("удаление записи")
def delete(metadata, table_name, table_data, where_clause):
    """Удаляет подходящие записи. Возвращает данные или None, если их нет."""
    schema = get_schema(metadata, table_name)
    validate_clause(schema, where_clause)

    found = [record for record in table_data if matches(record, where_clause)]
    if not found:
        print("Записи, подходящие под условие, не найдены.")
        return None

    for record in found:
        print(
            f"Запись с ID={record[ID_COLUMN]} успешно удалена "
            f'из таблицы "{table_name}".'
        )
    return [record for record in table_data if not matches(record, where_clause)]


@handle_db_errors
def table_info(metadata, table_name, table_data):
    """Выводит информацию о таблице."""
    schema = get_schema(metadata, table_name)
    print(f"Таблица: {table_name}")
    print(f"Столбцы: {format_columns(schema)}")
    print(f"Количество записей: {len(table_data)}")
