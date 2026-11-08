"""Декораторы и замыкание для кэширования."""

import time

from primitive_db.constants import CONFIRM_ANSWER


def handle_db_errors(func):
    """Перехватывает ошибки работы с БД и выводит понятное сообщение."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "Ошибка: Файл данных не найден. "
                "Возможно, база данных не инициализирована."
            )
        except KeyError as error:
            print(f'Ошибка: Таблица "{error.args[0]}" не существует.')
        except ValueError as error:
            print(f"Некорректное значение: {error}. Попробуйте снова.")
        except Exception as error:
            print(f"Произошла непредвиденная ошибка: {error}")
        return None

    return wrapper


def confirm_action(action_name):
    """Запрашивает подтверждение перед выполнением опасной операции."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            answer = input(f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: ')
            if answer.strip().lower() != CONFIRM_ANSWER:
                print("Операция отменена.")
                return None
            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    """Замеряет и выводит время выполнения функции."""

    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        elapsed = time.monotonic() - start
        print(f"Функция {func.__name__} выполнилась за {elapsed:.3f} секунд.")
        return result

    return wrapper


def create_cacher():
    """Создаёт функцию кэширования, которая хранит кэш в замыкании."""
    cache = {}

    def cache_result(key, value_func):
        """Возвращает результат из кэша или вычисляет и сохраняет его."""
        if key not in cache:
            cache[key] = value_func()
        return cache[key]

    return cache_result
