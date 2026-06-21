from typing import Any

from pydantic import BaseModel, Field


class QueryGenerateRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)


class QueryGenerateResponse(BaseModel):
    sql: str


class VisualizationMetadata(BaseModel):
    chart_type: str
    x_axis: str | None = None
    y_axis: str | None = None


class AnomalyDetectionInsight(BaseModel):
    enabled: bool
    outlier_count: int


class ClusteringInsight(BaseModel):
    enabled: bool
    cluster_count: int | None = None


class ForecastingInsight(BaseModel):
    enabled: bool
    x_axis: str | None = None
    y_axis: str | None = None
    horizon: int
    rows: list[dict[str, Any]]


class MLInsights(BaseModel):
    anomaly_detection: AnomalyDetectionInsight
    clustering: ClusteringInsight
    forecasting: ForecastingInsight


class QueryRunResponse(BaseModel):
    sql: str
    columns: list[str]
    row_count: int
    rows: list[dict[str, Any]]
    visualization: VisualizationMetadata
    ml_insights: MLInsights
    insights: str
