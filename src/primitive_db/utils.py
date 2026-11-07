"""Вспомогательные функции для работы с файлами."""

import json
import os

from primitive_db.constants import DATA_DIR, TABLE_FILE_EXTENSION


def load_json(filepath, default):
    """Загружает данные из JSON-файла. Если файла нет, возвращает default."""
    try:
        with open(filepath, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return default


def save_json(filepath, data):
    """Сохраняет данные в JSON-файл."""
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def load_metadata(filepath):
    """Загружает метаданные. Если файла нет, возвращает {}."""
    return load_json(filepath, {})


def save_metadata(filepath, data):
    """Сохраняет метаданные."""
    save_json(filepath, data)


def get_table_path(table_name):
    """Возвращает путь к файлу с данными таблицы."""
    return os.path.join(DATA_DIR, table_name + TABLE_FILE_EXTENSION)


def load_table_data(table_name):
    """Загружает записи таблицы. Если файла нет, возвращает []."""
    return load_json(get_table_path(table_name), [])


def save_table_data(table_name, data):
    """Сохраняет записи таблицы."""
    os.makedirs(DATA_DIR, exist_ok=True)
    save_json(get_table_path(table_name), data)


def delete_table_data(table_name):
    """Удаляет файл с данными таблицы, если он есть."""
    path = get_table_path(table_name)
    if os.path.exists(path):
        os.remove(path)