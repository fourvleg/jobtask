import pytest
from src.csv_filter import (
    parse_condition,
    apply_filter,
    parse_aggregate,
    aggregate,
)

sample_data = [
    {"name": "iphone 15 pro", "brand": "apple", "price": "999", "rating": "4.9"},
    {"name": "galaxy s23 ultra", "brand": "samsung", "price": "1199", "rating": "4.8"},
    {"name": "redmi note 12", "brand": "xiaomi", "price": "199", "rating": "4.6"},
    {"name": "poco x5 pro", "brand": "xiaomi", "price": "299", "rating": "4.4"},
    {"name": "c4", "brand": "xiaomi", "price": "1000", "rating": "5.0"},
]


def test_parse_condition_valid():
    assert parse_condition("price>500") == ("price", ">", "500")
    assert parse_condition("brand=xiaomi") == ("brand", "=", "xiaomi")
    assert parse_condition("rating>=4.8") == ("rating", ">=", "4.8")


def test_parse_condition_invalid():
    with pytest.raises(ValueError):
        parse_condition("bad-format")


def test_apply_filter_numeric():
    filtered = apply_filter(sample_data, "price", "<", "500")
    assert len(filtered) == 2
    assert all(float(row["price"]) < 500 for row in filtered)


def test_apply_filter_string():
    filtered = apply_filter(sample_data, "brand", "=", "apple")
    assert len(filtered) == 1
    assert filtered[0]["name"] == "iphone 15 pro"


def test_parse_aggregate_valid():
    assert parse_aggregate("rating=avg") == ("rating", "avg")


def test_parse_aggregate_invalid():
    with pytest.raises(ValueError):
        parse_aggregate("rating")


def test_aggregate_avg():
    result = aggregate(sample_data, "rating", "avg")
    expected = round((4.9 + 4.8 + 4.6 + 4.4 + 5.0) / 5, 2)
    assert result == expected


def test_aggregate_min():
    result = aggregate(sample_data, "price", "min")
    assert result == 199.0


def test_aggregate_max():
    result = aggregate(sample_data, "price", "max")
    assert result == 1199.0


def test_aggregate_unsupported():
    with pytest.raises(ValueError):
        aggregate(sample_data, "price", "sum")
