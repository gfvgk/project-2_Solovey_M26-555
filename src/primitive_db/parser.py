"""Разбор команд: токены, значения, условия where и set."""

import shlex

from primitive_db.constants import BOOL_VALUES, PUNCTUATION_CHARS, QUOTE_CHARS


def tokenize(text):
    """Разбивает строку на токены. Кавычки у строк сохраняются."""
    lexer = shlex.shlex(text, posix=False, punctuation_chars=PUNCTUATION_CHARS)
    lexer.whitespace_split = True
    try:
        return list(lexer)
    except ValueError:
        raise ValueError(text) from None


def is_punctuation(token):
    """Проверяет, состоит ли токен только из знаков препинания команды."""
    return all(char in PUNCTUATION_CHARS for char in token)


def parse_value(token):
    """Превращает токен в значение: "текст" -> str, true -> bool, 28 -> int."""
    is_quoted = len(token) >= 2 and token[0] == token[-1] and token[0] in QUOTE_CHARS
    if is_quoted:
        return token[1:-1]
    if token.lower() in BOOL_VALUES:
        return BOOL_VALUES[token.lower()]
    try:
        return int(token)
    except ValueError:
        return token


def parse_values(tokens):
    """Разбирает список значений вида ( v1 , v2 , ... )."""
    if len(tokens) < 2 or tokens[0] != "(" or tokens[-1] != ")":
        raise ValueError(" ".join(tokens))

    values = []
    expect_value = True
    for token in tokens[1:-1]:
        if expect_value:
            if is_punctuation(token):
                raise ValueError(token)
            values.append(parse_value(token))
        elif token != ",":
            raise ValueError(token)
        expect_value = not expect_value

    if expect_value and values:
        raise ValueError(",")
    return values


def parse_clause(tokens, separator):
    """Разбирает условия вида col = val [separator col = val ...] в словарь."""
    clause = {}
    groups = []
    current = []
    for token in tokens:
        if token.lower() == separator:
            groups.append(current)
            current = []
        else:
            current.append(token)
    groups.append(current)

    for group in groups:
        if len(group) != 3 or group[1] != "=" or not group[0].isidentifier():
            raise ValueError(" ".join(group) or separator)
        clause[group[0]] = parse_value(group[2])
    return clause


def parse_where(tokens):
    """Разбирает условие where: age = 28 and name = "Bob" -> словарь."""
    return parse_clause(tokens, "and")


def parse_set(tokens):
    """Разбирает часть set: age = 29, name = "Bob" -> словарь."""
    return parse_clause(tokens, ",")