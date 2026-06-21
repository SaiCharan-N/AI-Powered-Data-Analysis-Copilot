import logging
from typing import Any

import pandas as pd
from pandas.api.types import is_numeric_dtype
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import silhouette_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

ANOMALY_MIN_ROWS = 10
CLUSTERING_MIN_ROWS = 20
FORECAST_MIN_ROWS = 6
FORECAST_HORIZON = 6
ANOMALY_CONTAMINATION = 0.05
MIN_CLUSTER_COUNT = 2
MAX_CLUSTER_COUNT = 5
RANDOM_STATE = 42


def enrich_dataframe_with_ml(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    metadata = _default_metadata()

    if dataframe is None or dataframe.empty:
        logger.info("Skipping ML enrichment for empty DataFrame.")
        return dataframe.copy() if dataframe is not None else pd.DataFrame(), metadata

    enriched_dataframe = dataframe.copy()
    numeric_dataframe = _get_numeric_dataframe(enriched_dataframe)

    if numeric_dataframe.empty:
        logger.info("Skipping ML enrichment because no numeric columns were found.")
        return enriched_dataframe, metadata

    enriched_dataframe, anomaly_metadata = _add_anomaly_detection(
        enriched_dataframe=enriched_dataframe,
        numeric_dataframe=numeric_dataframe,
    )
    metadata["anomaly_detection"] = anomaly_metadata

    enriched_dataframe, clustering_metadata = _add_clustering(
        enriched_dataframe=enriched_dataframe,
        numeric_dataframe=numeric_dataframe,
    )
    metadata["clustering"] = clustering_metadata
    metadata["forecasting"] = _build_forecast_metadata(
        dataframe=enriched_dataframe,
        numeric_dataframe=numeric_dataframe,
    )

    return enriched_dataframe, metadata


def _add_anomaly_detection(
    enriched_dataframe: pd.DataFrame,
    numeric_dataframe: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    metadata = {"enabled": False, "outlier_count": 0}

    if len(enriched_dataframe.index) < ANOMALY_MIN_ROWS:
        return enriched_dataframe, metadata

    try:
        features = _prepare_features(numeric_dataframe)
        model = IsolationForest(
            contamination=ANOMALY_CONTAMINATION,
            random_state=RANDOM_STATE,
        )
        predictions = model.fit_predict(features)
        scores = model.decision_function(features)

        enriched_dataframe["anomaly_score"] = scores
        enriched_dataframe["is_outlier"] = predictions == -1

        outlier_count = int((predictions == -1).sum())
        metadata = {"enabled": True, "outlier_count": outlier_count}
        logger.info("Anomaly detection completed. outlier_count=%s", outlier_count)
    except Exception as exc:
        logger.warning("Anomaly detection skipped after failure. error=%s", exc)

    return enriched_dataframe, metadata


def _add_clustering(
    enriched_dataframe: pd.DataFrame,
    numeric_dataframe: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    metadata = {"enabled": False, "cluster_count": None}

    if len(enriched_dataframe.index) < CLUSTERING_MIN_ROWS or len(numeric_dataframe.columns) < 2:
        return enriched_dataframe, metadata

    try:
        features = _prepare_features(numeric_dataframe)
        cluster_count = _select_cluster_count(features, row_count=len(enriched_dataframe.index))

        if cluster_count is None:
            return enriched_dataframe, metadata

        model = KMeans(
            n_clusters=cluster_count,
            random_state=RANDOM_STATE,
            n_init="auto",
        )
        enriched_dataframe["cluster_id"] = model.fit_predict(features)

        metadata = {"enabled": True, "cluster_count": int(cluster_count)}
        logger.info("Clustering completed. cluster_count=%s", cluster_count)
    except Exception as exc:
        logger.warning("Clustering skipped after failure. error=%s", exc)

    return enriched_dataframe, metadata


def _select_cluster_count(features: Any, row_count: int) -> int | None:
    max_clusters = min(MAX_CLUSTER_COUNT, row_count - 1)
    if max_clusters < MIN_CLUSTER_COUNT:
        return None

    best_cluster_count: int | None = None
    best_score: float | None = None

    for cluster_count in range(MIN_CLUSTER_COUNT, max_clusters + 1):
        model = KMeans(
            n_clusters=cluster_count,
            random_state=RANDOM_STATE,
            n_init="auto",
        )
        labels = model.fit_predict(features)

        if len(set(labels)) < 2:
            continue

        score = silhouette_score(features, labels)
        if best_score is None or score > best_score:
            best_score = float(score)
            best_cluster_count = cluster_count

    return best_cluster_count


def _build_forecast_metadata(
    dataframe: pd.DataFrame,
    numeric_dataframe: pd.DataFrame,
) -> dict[str, Any]:
    metadata = {
        "enabled": False,
        "x_axis": None,
        "y_axis": None,
        "horizon": 0,
        "rows": [],
    }

    if len(dataframe.index) < FORECAST_MIN_ROWS or numeric_dataframe.empty:
        return metadata

    datetime_column = _detect_datetime_column(dataframe)
    if datetime_column is None:
        return metadata

    y_axis = str(numeric_dataframe.columns[0])

    try:
        working = dataframe[[datetime_column, y_axis]].dropna().copy()
        working[datetime_column] = pd.to_datetime(working[datetime_column], errors="coerce")
        working[y_axis] = pd.to_numeric(working[y_axis], errors="coerce")
        working = working.dropna().sort_values(datetime_column)

        if len(working.index) < FORECAST_MIN_ROWS:
            return metadata

        start_date = working[datetime_column].min()
        x_values = (working[datetime_column] - start_date).dt.days.to_numpy().reshape(-1, 1)
        y_values = working[y_axis].to_numpy()

        model = LinearRegression()
        model.fit(x_values, y_values)

        interval_days = _infer_interval_days(working[datetime_column])
        last_date = working[datetime_column].max()
        future_dates = [
            last_date + pd.Timedelta(days=interval_days * step)
            for step in range(1, FORECAST_HORIZON + 1)
        ]
        future_x = [(date - start_date).days for date in future_dates]
        predictions = model.predict(pd.DataFrame(future_x).to_numpy().reshape(-1, 1))

        metadata = {
            "enabled": True,
            "x_axis": datetime_column,
            "y_axis": y_axis,
            "horizon": FORECAST_HORIZON,
            "rows": [
                {
                    datetime_column: date.date().isoformat(),
                    y_axis: round(float(prediction), 4),
                }
                for date, prediction in zip(future_dates, predictions)
            ],
        }
        logger.info("Forecasting completed. x_axis=%s y_axis=%s", datetime_column, y_axis)
    except Exception as exc:
        logger.warning("Forecasting skipped after failure. error=%s", exc)

    return metadata


def _detect_datetime_column(dataframe: pd.DataFrame) -> str | None:
    for column in dataframe.columns:
        if is_numeric_dtype(dataframe[column]):
            continue

        parsed = pd.to_datetime(dataframe[column], errors="coerce")
        if parsed.notna().mean() >= 0.8:
            return str(column)

    return None


def _infer_interval_days(series: pd.Series) -> int:
    sorted_dates = series.sort_values()
    diffs = sorted_dates.diff().dropna().dt.days
    median_diff = int(diffs.median()) if not diffs.empty else 1
    return max(median_diff, 1)


def _get_numeric_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    numeric_columns = [
        column
        for column in dataframe.columns
        if is_numeric_dtype(dataframe[column]) and not pd.api.types.is_bool_dtype(dataframe[column])
    ]
    return dataframe[numeric_columns].copy()


def _prepare_features(numeric_dataframe: pd.DataFrame) -> Any:
    pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    return pipeline.fit_transform(numeric_dataframe)


def _default_metadata() -> dict[str, Any]:
    return {
        "anomaly_detection": {
            "enabled": False,
            "outlier_count": 0,
        },
        "clustering": {
            "enabled": False,
            "cluster_count": None,
        },
        "forecasting": {
            "enabled": False,
            "x_axis": None,
            "y_axis": None,
            "horizon": 0,
            "rows": [],
        },
    }
