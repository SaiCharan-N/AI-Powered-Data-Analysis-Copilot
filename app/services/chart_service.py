import logging
import warnings
from dataclasses import dataclass

import pandas as pd
from pandas.api.types import is_datetime64_any_dtype, is_numeric_dtype

logger = logging.getLogger(__name__)

SMALL_CATEGORY_MAX_CARDINALITY = 8
DATETIME_PARSE_SUCCESS_RATIO = 0.8
NUMERIC_PARSE_SUCCESS_RATIO = 0.9


@dataclass(frozen=True)
class ColumnProfile:
    numeric_columns: list[str]
    categorical_columns: list[str]
    datetime_columns: list[str]
    cardinality: dict[str, int]
    row_count: int


def recommend_visualization(dataframe: pd.DataFrame) -> dict[str, str | None]:
    try:
        profile = profile_dataframe(dataframe)
        recommendation = _recommend_from_profile(profile)
        logger.info(
            "Recommended visualization. chart_type=%s rows=%s",
            recommendation["chart_type"],
            profile.row_count,
        )
        return recommendation
    except Exception as exc:
        logger.warning("Chart recommendation failed; falling back to table. error=%s", exc)
        return _table()


def profile_dataframe(dataframe: pd.DataFrame) -> ColumnProfile:
    if dataframe is None or dataframe.empty:
        return ColumnProfile(
            numeric_columns=[],
            categorical_columns=[],
            datetime_columns=[],
            cardinality={},
            row_count=0,
        )

    numeric_columns: list[str] = []
    categorical_columns: list[str] = []
    datetime_columns: list[str] = []
    cardinality: dict[str, int] = {}

    for column in dataframe.columns:
        column_name = str(column)
        series = dataframe[column]
        non_null_series = series.dropna()
        cardinality[column_name] = int(non_null_series.nunique(dropna=True))

        if non_null_series.empty:
            categorical_columns.append(column_name)
            continue

        if _is_datetime_column(non_null_series):
            datetime_columns.append(column_name)
            continue

        if _is_numeric_column(non_null_series):
            numeric_columns.append(column_name)
            continue

        categorical_columns.append(column_name)

    return ColumnProfile(
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
        datetime_columns=datetime_columns,
        cardinality=cardinality,
        row_count=len(dataframe.index),
    )


def _recommend_from_profile(profile: ColumnProfile) -> dict[str, str | None]:
    if profile.row_count == 0:
        return _table()

    if profile.datetime_columns and profile.numeric_columns:
        return {
            "chart_type": "line",
            "x_axis": profile.datetime_columns[0],
            "y_axis": profile.numeric_columns[0],
        }

    if profile.categorical_columns and profile.numeric_columns:
        category = _lowest_cardinality_column(profile.categorical_columns, profile.cardinality)
        numeric = profile.numeric_columns[0]

        if _is_small_category(category, profile.cardinality):
            return {
                "chart_type": "pie",
                "x_axis": category,
                "y_axis": numeric,
            }

        return {
            "chart_type": "bar",
            "x_axis": category,
            "y_axis": numeric,
        }

    if len(profile.numeric_columns) >= 2:
        return {
            "chart_type": "scatter",
            "x_axis": profile.numeric_columns[0],
            "y_axis": profile.numeric_columns[1],
        }

    return _table()


def _is_datetime_column(series: pd.Series) -> bool:
    if is_datetime64_any_dtype(series):
        return True

    if is_numeric_dtype(series):
        return False

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        parsed = pd.to_datetime(series, errors="coerce")
    return parsed.notna().mean() >= DATETIME_PARSE_SUCCESS_RATIO


def _is_numeric_column(series: pd.Series) -> bool:
    if is_numeric_dtype(series):
        return True

    parsed = pd.to_numeric(series, errors="coerce")
    return parsed.notna().mean() >= NUMERIC_PARSE_SUCCESS_RATIO


def _lowest_cardinality_column(columns: list[str], cardinality: dict[str, int]) -> str:
    return min(columns, key=lambda column: cardinality.get(column, 0))


def _is_small_category(column: str, cardinality: dict[str, int]) -> bool:
    value_count = cardinality.get(column, 0)
    return 1 < value_count <= SMALL_CATEGORY_MAX_CARDINALITY


def _table() -> dict[str, str | None]:
    return {
        "chart_type": "table",
        "x_axis": None,
        "y_axis": None,
    }
