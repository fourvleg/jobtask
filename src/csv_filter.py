import argparse
import csv
from tabulate import tabulate
import operator
from typing import List, Dict, Tuple, Optional, Union


def parse_args() -> argparse.Namespace:
    """Парсит аргументы командной строки.

    Returns:
        argparse.Namespace: Объект с аргументами:
            - file (str): Путь к CSV файлу (обязательный)
            - where (str): Условие фильтрации (опционально)
            - aggregate (str): Условие агрегации (опционально)
    """
    parser = argparse.ArgumentParser(description="CSV фильтрация и агрегация")
    parser.add_argument("-f", "--file", required=True, help="Путь к CSV файлу")
    parser.add_argument(
        "-w", "--where", help="Фильтрация, формат: column>value, column=value и т.п."
    )
    parser.add_argument(
        "-a", "--aggregate", help="Агрегация, формат: column=func (func: avg|min|max)"
    )
    return parser.parse_args()


def read_csv(file_path: str) -> List[Dict[str, str]]:
    """Читает CSV файл и возвращает данные в виде списка словарей.

    Args:
        file_path (str): Путь к CSV файлу

    Returns:
        list: Список словарей, где каждый словарь представляет строку CSV

    """

    with open(file_path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def parse_condition(condition: str) -> Tuple[str, str, str]:
    """Парсит условие фильтрации вида 'column>value'.

    Args:
        condition (str): Условие фильтрации

    Returns:
        tuple: (column, operator, value)

    Raises:
        ValueError: Если формат условия неверный
    """

    for op_symbol in [">=", "<=", ">", "<", "="]:
        if op_symbol in condition:
            parts = condition.split(op_symbol, 1)
            return parts[0].strip(), op_symbol, parts[1].strip()
    raise ValueError("Неверный формат условия")


def apply_filter(
    data: List[Dict[str, str]],
    col: str,
    op_symbol: str,
    value: str,
) -> List[Dict[str, str]]:
    """Фильтрует данные по условию.

    Args:
        data (list): Список словарей с данными
        col (str): Название колонки для фильтрации
        op_symbol (str): Оператор сравнения (>, <, =, >=, <=)
        value (str): Значение для сравнения

    Returns:
        list: Отфильтрованные данные

    Raises:
        ValueError: Если оператор не поддерживается
    """

    ops = {
        "=": operator.eq,
        ">": operator.gt,
        "<": operator.lt,
        ">=": operator.ge,
        "<=": operator.le,
    }
    op_func = ops.get(op_symbol)
    if op_func is None:
        raise ValueError(f"Неподдерживаемый оператор: {op_symbol}")

    filtered_data = []
    for row in data:
        try:
            row_value = float(row[col])
            compare_value = float(value)
        except ValueError:
            row_value = row[col]
            compare_value = value

        if op_func(row_value, compare_value):
            filtered_data.append(row)

    return filtered_data


def parse_aggregate(agg_str: str) -> Tuple[str, str]:
    """Парсит строку агрегации вида 'column=func'.

    Args:
        agg_str (str): Строка агрегации

    Returns:
        tuple: (column, func), где func может быть avg, min или max

    Raises:
        ValueError: Если формат строки неверный
    """

    if "=" not in agg_str:
        raise ValueError("Неверный формат агрегации. Пример: rating=avg")
    parts = agg_str.split("=", 1)
    return parts[0].strip(), parts[1].strip()


def aggregate(
    data: List[Dict[str, str]], col: str, func: str
) -> Optional[Union[float, int]]:
    """Выполняет агрегацию данных по указанной колонке.

    Args:
        data (list): Список словарей с данными
        col (str): Название колонки для агрегации
        func (str): Функция агрегации (avg, min, max)

    Returns:
        float|None: Результат агрегации или None если данные пустые

    Raises:
        ValueError: Если функция агрегации не поддерживается
    """

    values = []
    for row in data:
        try:
            value = float(row[col])
            values.append(value)
        except (ValueError, KeyError):
            continue

    if not values:
        return None

    if func == "avg":
        return round(sum(values) / len(values), 2)
    if func == "min":
        return min(values)
    if func == "max":
        return max(values)

    raise ValueError(f"Агрегация '{func}' не поддерживается")


def main() -> None:
    """Основная функция: читает CSV, применяет фильтрацию и агрегацию, выводит результат."""

    args = parse_args()
    data = read_csv(args.file)

    if args.where:
        col, op, val = parse_condition(args.where)
        data = apply_filter(data, col, op, val)

    if args.aggregate:
        agg_col, agg_func = parse_aggregate(args.aggregate)
        result = aggregate(data, agg_col, agg_func)
        print(tabulate([[agg_func, result]], headers=[agg_func], tablefmt="grid"))
    else:
        print(tabulate(data, headers="keys", tablefmt="grid"))


if __name__ == "__main__":
    main()
