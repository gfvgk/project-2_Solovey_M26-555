"""Константы проекта."""

META_FILE = "db_meta.json"
DATA_DIR = "data"
TABLE_FILE_EXTENSION = ".json"

ID_COLUMN = "ID"
ID_TYPE = "int"

VALID_TYPES = {
    "int": int,
    "str": str,
    "bool": bool,
}

BOOL_VALUES = {
    "true": True,
    "false": False,
}

QUOTE_CHARS = "\"'"
PUNCTUATION_CHARS = "=,()"

PROMPT_TEXT = ">>>Введите команду: "
CONFIRM_ANSWER = "y"
