"""Модуль сортировки данных с реализацией сортировки слиянием."""

from __future__ import annotations

import argparse
import random
from functools import cmp_to_key
from pathlib import Path
from typing import Any, Callable, Optional


def _build_key(
    key: Optional[Callable[[Any], Any]] = None,
    cmp: Optional[Callable[[Any, Any], int]] = None,
) -> Callable[[Any], Any]:
    """Построить функцию-ключ для сравнения элементов.

    Args:
        key: Функция извлечения значения для сравнения.
        cmp: Функция сравнения двух элементов.

    Returns:
        Функция-ключ, подходящая для стандартного сравнения Python.
    """
    if cmp is not None:
        base_cmp = cmp

        if key is not None:
            def combined(left: Any, right: Any) -> int:
                return base_cmp(key(left), key(right))

            return cmp_to_key(combined)

        return cmp_to_key(base_cmp)

    if key is not None:
        return key

    return lambda value: value


def _merge(
    left: list[Any],
    right: list[Any],
    key_func: Callable[[Any], Any],
    reverse: bool,
) -> list[Any]:
    """Слить два отсортированных списка в один.

    Args:
        left: Левый отсортированный список.
        right: Правый отсортированный список.
        key_func: Функция-ключ для сравнения.
        reverse: Флаг сортировки по невозрастанию.

    Returns:
        Новый отсортированный список.
    """
    result: list[Any] = []
    i = 0
    j = 0
    while i < len(left) and j < len(right):
        left_key = key_func(left[i])
        right_key = key_func(right[j])
        take_left = left_key > right_key if reverse else left_key <= right_key
        if take_left:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    if i < len(left):
        result.extend(left[i:])
    if j < len(right):
        result.extend(right[j:])
    return result


def merge_sort(
    array: list[Any],
    reverse: bool = False,
    key: Optional[Callable[[Any], Any]] = None,
    cmp: Optional[Callable[[Any, Any], int]] = None,
) -> list[Any]:
    """Отсортировать список сортировкой слиянием.

    Args:
        array: Исходный список.
        reverse: Флаг сортировки по невозрастанию.
        key: Функция, возвращающая значение для сравнения.
        cmp: Функция сравнения двух элементов.

    Returns:
        Новый отсортированный список.
    """
    if len(array) <= 1:
        return list(array)

    key_func = _build_key(key=key, cmp=cmp)
    middle = len(array) // 2
    left_sorted = merge_sort(array[:middle], reverse=reverse, key=key, cmp=cmp)
    right_sorted = merge_sort(array[middle:], reverse=reverse, key=key, cmp=cmp)
    return _merge(left_sorted, right_sorted, key_func, reverse)


def my_sort(
    array: list[Any],
    reverse: bool = False,
    key: Optional[Callable[[Any], Any]] = None,
    cmp: Optional[Callable[[Any, Any], int]] = None,
) -> list[Any]:
    """Отсортировать список и вернуть новый отсортированный список.

    Args:
        array: Сортируемый список.
        reverse: Флаг определяющий вариант сортировки.
        key: Функция, вычисляющая значение для сравнения.
        cmp: Функция сравнения двух элементов.

    Returns:
        Новый список с отсортированными элементами.
    """
    return merge_sort(array, reverse=reverse, key=key, cmp=cmp)


def _merge_step(
    values: list[int],
    left: int,
    middle: int,
    right: int,
    reverse: bool,
    on_step: Callable[[list[int], tuple[int, int] | None], None],
) -> None:
    """Слить два подмассива на месте с вызовом шага визуализации.

    Args:
        values: Сортируемый список.
        left: Левая граница.
        middle: Индекс середины.
        right: Правая граница (не включительно).
        reverse: Флаг сортировки по невозрастанию.
        on_step: Обработчик шага визуализации.
    """
    left_part = values[left:middle]
    right_part = values[middle:right]
    i = 0
    j = 0
    k = left
    while i < len(left_part) and j < len(right_part):
        take_left = (
            left_part[i] > right_part[j] if reverse else left_part[i] <= right_part[j]
        )
        if take_left:
            values[k] = left_part[i]
            i += 1
        else:
            values[k] = right_part[j]
            j += 1
        on_step(list(values), (k, right - 1))
        k += 1
    while i < len(left_part):
        values[k] = left_part[i]
        on_step(list(values), (k, right - 1))
        i += 1
        k += 1
    while j < len(right_part):
        values[k] = right_part[j]
        on_step(list(values), (k, right - 1))
        j += 1
        k += 1


def _merge_sort_visual(
    values: list[int],
    left: int,
    right: int,
    reverse: bool,
    on_step: Callable[[list[int], tuple[int, int] | None], None],
) -> None:
    """Рекурсивная сортировка слиянием с визуализацией шагов.

    Args:
        values: Сортируемый список.
        left: Левая граница.
        right: Правая граница (не включительно).
        reverse: Флаг сортировки по невозрастанию.
        on_step: Обработчик шага визуализации.
    """
    if right - left <= 1:
        return
    middle = (left + right) // 2
    _merge_sort_visual(values, left, middle, reverse, on_step)
    _merge_sort_visual(values, middle, right, reverse, on_step)
    _merge_step(values, left, middle, right, reverse, on_step)


def visualize_merge_sort(size: int, reverse: bool = False) -> None:
    """Визуализировать пошаговую сортировку слиянием случайного списка.

    Args:
        size: Размер случайного списка.
        reverse: Флаг сортировки по невозрастанию.
    """
    if size <= 0:
        raise ValueError("Размер списка должен быть положительным числом")

    values = [random.randint(1, max(10, size * 2)) for _ in range(size)]

    try:
        import matplotlib.pyplot as plt  # type: ignore

        plt.ion()
        fig, axis = plt.subplots()
        bars = axis.bar(range(len(values)), values)
        axis.set_title("Сортировка слиянием")

        def on_step(state: list[int], highlight: tuple[int, int] | None) -> None:
            for index, bar in enumerate(bars):
                bar.set_height(state[index])
                bar.set_color("steelblue")
            if highlight is not None:
                for index in range(highlight[0], highlight[1] + 1):
                    if 0 <= index < len(bars):
                        bars[index].set_color("orange")
            axis.set_ylim(0, max(state) * 1.1 if state else 1)
            fig.canvas.draw()
            fig.canvas.flush_events()
            plt.pause(0.05)

        on_step(list(values), None)
        _merge_sort_visual(values, 0, len(values), reverse, on_step)
        on_step(list(values), None)
        plt.ioff()
        plt.show()
    except Exception:  # pylint: disable=broad-exception-caught
        print("Matplotlib недоступен, текстовая визуализация шагов:")
        print("Начало:", values)

        step = 0

        def on_step(state: list[int], highlight: tuple[int, int] | None) -> None:
            nonlocal step
            step += 1
            marker = f" {highlight}" if highlight is not None else ""
            print(f"Шаг {step}: {state}{marker}")

        _merge_sort_visual(values, 0, len(values), reverse, on_step)
        print("Результат:", values)


def _parse_value(value: str, data_type: str) -> Any:
    """Преобразовать строку в значение заданного типа.

    Args:
        value: Исходная строка.
        data_type: Тип данных: number или text.

    Returns:
        Преобразованное значение.
    """
    if data_type == "number":
        try:
            if any(symbol in value for symbol in ".eE"):
                return float(value)
            return int(value)
        except ValueError as exc:
            raise ValueError(f"Некорректное числовое значение: {value}") from exc
    return value


def read_data(path: str, data_type: str) -> list[Any]:
    """Прочитать данные для сортировки из файла.

    Args:
        path: Путь к файлу.
        data_type: Тип данных: number или text.

    Returns:
        Список значений.
    """
    content = Path(path).read_text(encoding="utf-8")
    tokens = [token for token in content.replace("\n", " ").split(" ") if token != ""]
    return [_parse_value(token, data_type) for token in tokens]


def write_data(path: str, data: list[Any]) -> None:
    """Записать отсортированные данные в файл.

    Args:
        path: Путь к файлу.
        data: Данные для записи.
    """
    Path(path).write_text(" ".join(str(item) for item in data), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    """Создать парсер аргументов командной строки.

    Returns:
        Настроенный парсер аргументов.
    """
    parser = argparse.ArgumentParser(
        description="Консольная утилита сортировки (сортировка слиянием)."
    )
    parser.add_argument("-i", "--input", help="Путь к входному файлу")
    parser.add_argument("-o", "--output", help="Путь к выходному файлу")
    parser.add_argument(
        "-t",
        "--type",
        choices=["number", "text"],
        default="number",
        help="Тип данных во входном файле",
    )
    parser.add_argument(
        "-r",
        "--reverse",
        action="store_true",
        help="Сортировать по невозрастанию",
    )
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="Показать пошаговую визуализацию сортировки",
    )
    parser.add_argument(
        "--size",
        type=int,
        default=20,
        help="Размер случайного списка для визуализации",
    )
    return parser


def main() -> None:
    """Точка входа консольной утилиты."""
    parser = build_parser()
    args = parser.parse_args()

    if args.visualize:
        visualize_merge_sort(args.size, reverse=args.reverse)
        return

    if not args.input or not args.output:
        parser.error("Для сортировки файла укажите --input и --output")

    data = read_data(args.input, args.type)
    sorted_data = my_sort(data, reverse=args.reverse)
    write_data(args.output, sorted_data)
    print(f"Отсортировано элементов: {len(sorted_data)}")


if __name__ == "__main__":
    main()
