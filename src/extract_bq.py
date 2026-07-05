"""Extract a bounded slice of London trips from BigQuery.

Joins the trip table to station metadata to attach lat/lon, which the feature
step needs. The date window (see config) keeps bytes-billed inside the free tier;
widen it in the notebook if you have quota to spare — more rows = a bigger GPU win.
"""
from __future__ import annotations

from . import config


def query_sql(start_date: str = config.BQ_START_DATE, end_date: str = config.BQ_END_DATE) -> str:
    return f"""
    WITH s AS (
      SELECT id, name, latitude AS lat, longitude AS lon
      FROM `{config.BQ_STATIONS_TABLE}`
    )
    SELECT
      h.start_station_id,
      h.start_station_name,
      ss.lat  AS start_lat,
      ss.lon  AS start_lon,
      h.end_station_id,
      h.end_station_name,
      es.lat  AS end_lat,
      es.lon  AS end_lon,
      h.start_date,
      h.end_date
    FROM `{config.BQ_TRIPS_TABLE}` h
    LEFT JOIN s ss ON h.start_station_id = ss.id
    LEFT JOIN s es ON h.end_station_id = es.id
    WHERE h.start_date >= TIMESTAMP('{start_date}')
      AND h.start_date <  TIMESTAMP('{end_date}')
      AND h.start_station_id IS NOT NULL
      AND h.end_station_id IS NOT NULL
    """


def extract(project: str | None = None, save_path=config.RAW_TRIPS_PATH):
    """Run the query with the pandas BigQuery client and cache to parquet.

    In the Colab notebook you can instead read directly into cuDF for the GPU path.
    """
    from google.cloud import bigquery

    client = bigquery.Client(project=project)
    df = client.query(query_sql()).result().to_dataframe(create_bqstorage_client=True)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(save_path, index=False)
    print(f"Extracted {len(df):,} trips -> {save_path}")
    return df


if __name__ == "__main__":
    extract()
