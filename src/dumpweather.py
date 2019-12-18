"""
Simple script to query a weather API and get historical data

TODO:
- create tool for hourly history? so i can look at windspeed, direction and rainfall intensity in more detail?
"""

import sys
import datetime
from typing import Any, Generator, List, Tuple

from darksky.api import DarkSky, DarkSkyAsync
from darksky.types import languages, units, weather

API_KEY = open('darksky_api_key.txt').read().strip()
darksky = DarkSky(API_KEY)


def str_to_date(s: str) -> datetime.datetime:
    return datetime.datetime.strptime(s, "%Y-%m-%d")


def dates_by_day(start_date: datetime.datetime, end_date: datetime.datetime) -> Generator[datetime.datetime, None, None]:
    """Generator that returns datetimes, one for each day between the two given datetimes

    Note: For consistency with "range", this is inclusive on start_date and exclusive on end_date.
    Reference: https://stackoverflow.com/a/1060330
    """
    for day_offset in range((end_date - start_date).days):
        yield start_date + datetime.timedelta(day_offset)


def get_hist(latitude: float, longitude: float, query_time: datetime.datetime) -> Tuple[Any, ...]:
    try:
        forecast = darksky.get_time_machine_forecast(
            latitude, longitude,
            time=query_time,
            exclude=[weather.MINUTELY, weather.HOURLY, weather.ALERTS]
        )
        d = forecast.daily.data[0]
        return (
            query_time,
            query_time.year,
            query_time.month,
            query_time.day,
            d.apparent_temperature_low,
            d.apparent_temperature_high,
            d.precip_type if hasattr(d, "precip_type") else "???",
            d.precip_intensity,
            d.precip_intensity * 24  # daily-ized rainfall total
        )
    except Exception as e:
        print(f"ERROR: latitude:{latitude} longitude:{longitude} query_time:{query_time}")
        raise


def get_daily(latitude: float, longitude: float, start_date: datetime.datetime, end_date: datetime.datetime) -> List[Tuple[Any, ...]]:
    """Query weather API to get daily, historical data"""
    results = []
    for d in dates_by_day(start_date, end_date):
        row = get_hist(latitude, longitude, d)
        results.append(row)
    return results


def print_daily(latitude: float, longitude: float, start_date: datetime.datetime, end_date: datetime.datetime) -> None:
    """Print results of historical weather query"""
    table = get_daily(latitude, longitude, start_date, end_date)
    print("date,year,month,day,low,high,precip_type,precip_intensity,precip_accumulation")
    for r in table:
        print(f"{r[0]},{r[1]},{r[2]},{r[3]},{r[4]:.2f},{r[5]:.2f},{r[6]},{r[7]:.4f},{r[8]:.4f}")


def print_daily_cli() -> None:
    """Provide CLI interface to daily historical weather query"""
    if len(sys.argv) != 5:
        msg = """Requires 4 arguments: LATITUDE, LONGITUDE, START_DATE, END_DATE
Ex: python dumpweather.py 41.9773 -87.8369 2019-09-23 2019-10-05"""
        raise Exception(msg)
    latitude = float(sys.argv[1])
    longitude = float(sys.argv[2])
    start_date = str_to_date(sys.argv[3])
    end_date = str_to_date(sys.argv[4])
    print_daily(latitude, longitude, start_date, end_date)


#####################################################33
def get_hist_hourly(latitude: float, longitude: float, query_time: datetime.datetime) -> List[Tuple[Any, ...]]:
    try:
        forecast = darksky.get_time_machine_forecast(
            latitude, longitude,
            time=query_time,
            exclude=[weather.MINUTELY, weather.ALERTS]
        )
        results = []
        daily_precip_accum = 0.0
        for hour_row in forecast.hourly.data:
            daily_precip_accum += hour_row.precip_intensity
            t = hour_row.time
            year = t.year
            month = t.month
            day = t.day
            results.append((
                t,
                year,
                month,
                day,
                hour_row.temperature,
                hour_row.precip_type if hasattr(hour_row, "precip_type") else "???",
                hour_row.precip_intensity,
                daily_precip_accum,
                hour_row.wind_bearing,
                hour_row.wind_speed,
                hour_row.wind_gust,
            ))
        return results
    except Exception as e:
        print(f"ERROR: latitude:{latitude} longitude:{longitude} query_time:{query_time}")
        raise


def print_hist_hourly(latitude: float, longitude: float, start_date: datetime.datetime, end_date: datetime.datetime) -> None:
    """Print results of historical weather query"""
    results = []
    for d in dates_by_day(start_date, end_date):
        row = get_hist_hourly(latitude, longitude, d)
        results.extend(row)

    print("date,year,month,day,temp,precip_type,precip_intensity,daily_precip_accumulation,wind_bearing,wind_speed,wind_gust")
    for row in results:
        print(','.join([str(x) for x in row]))


def print_hist_hourly_cli() -> None:
    """Provide CLI interface to hourly historical weather query"""
    latitude = float(sys.argv[1])
    longitude = float(sys.argv[2])
    start_date = str_to_date(sys.argv[3])
    end_date = str_to_date(sys.argv[4])
    print_hist_hourly(latitude, longitude, start_date, end_date)


if __name__ == '__main__':
    if len(sys.argv) != 6:
        msg = f"""Requires 5 arguments: daily/monthly, LATITUDE, LONGITUDE, START_DATE, END_DATE
Example usage:
  {sys.argv[0]} daily 41.984542 -87.904535 2019-09-01 2019-10-01
  {sys.argv[0]} hourly 41.984542 -87.904535 2019-09-01 2019-10-01
"""
        raise Exception(msg)

    cmd = sys.argv.pop(1)
    if cmd.lower().strip() == "daily":
        print_daily_cli()
    else:
        print_hist_hourly_cli()
