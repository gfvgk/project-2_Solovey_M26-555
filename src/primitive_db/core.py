"""Основная логика работы с таблицами."""

from primitive_db.constants import ID_COLUMN, ID_TYPE, VALID_TYPES


def create_table(metadata, table_name, columns):
    """Создаёт таблицу. Возвращает обновлённые метаданные или None при ошибке."""
    if not table_name.isidentifier():
        print(f"Некорректное значение: {table_name}. Попробуйте снова.")
        return None
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return None

    schema = {ID_COLUMN: ID_TYPE}
    for column in columns:
        name, _, column_type = column.partition(":")
        is_valid = (
            name.isidentifier()
            and column_type in VALID_TYPES
            and name not in schema
        )
        if not is_valid:
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return None
        schema[name] = column_type

    metadata[table_name] = schema
    columns_text = ", ".join(f"{name}:{kind}" for name, kind in schema.items())
    print(f'Таблица "{table_name}" успешно создана со столбцами: {columns_text}')
    return metadata


def drop_table(metadata, table_name):
    """Удаляет таблицу. Возвращает обновлённые метаданные или None при ошибке."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return None

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def list_tables(metadata):
    """Возвращает список имён всех таблиц."""
    return list(metadata)