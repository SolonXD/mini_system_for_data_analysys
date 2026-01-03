import math
import os
import random
import time
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import text

from generator.db import ENGINE, SessionLocal
from generator.models import Base, WeatherReading

Base.metadata.create_all(bind=ENGINE)
def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


@dataclass
class WeatherState:
    temperature_c: float
    humidity_percent: float
    pressure_hpa: float
    wind_speed_mps: float

    @staticmethod
    def initial() -> "WeatherState":
        temp = random.uniform(-2.0, 25.0)
        humidity = random.uniform(35.0, 90.0)
        pressure = random.uniform(990.0, 1030.0)
        wind = random.uniform(0.5, 8.0)
        return WeatherState(temp, humidity, pressure, wind)

    def step(self) -> "WeatherState":
        """
        Генерация следующего состояния: небольшие изменения (random walk)
        + корреляции между показателями:
          - ниже давление -> выше ветер
          - выше температура -> обычно ниже влажность (при прочих равных)
        """
        temp = self.temperature_c + random.gauss(0.0, 0.25)
        temp = clamp(temp, -25.0, 40.0)
        pressure = self.pressure_hpa + random.gauss(0.0, 0.35)
        pressure = clamp(pressure, 970.0, 1045.0)
        low_pressure_factor = clamp((1018.0 - pressure) / 25.0, -1.0, 1.0)
        wind_target = 3.0 + 6.0 * max(0.0, low_pressure_factor)
        wind = self.wind_speed_mps
        wind += 0.25 * (wind_target - wind) + random.gauss(0.0, 0.45)
        wind = clamp(wind, 0.0, 30.0)
        humidity = self.humidity_percent
        humidity_target = 70.0 - 1.2 * (temp - 10.0)
        humidity += 0.18 * (humidity_target - humidity) + random.gauss(0.0, 1.8)
        humidity -= 0.10 * max(0.0, wind - 10.0)
        humidity = clamp(humidity, 15.0, 100.0)
        return WeatherState(
            temperature_c=round(temp, 1),
            humidity_percent=round(humidity, 1),
            pressure_hpa=round(pressure, 1),
            wind_speed_mps=round(wind, 1),
        )


def wait_for_db(max_seconds: int = 60):
    deadline = time.time() + max_seconds
    last_err = None
    while time.time() < deadline:
        try:
            with ENGINE.connect() as conn:
                conn.execute(text("SELECT 1"))
            return
        except Exception as e:
            last_err = e
            time.sleep(1)
    raise RuntimeError(f"DB is not available after {max_seconds}s: {last_err}")


def main():
    interval_seconds = float(os.environ.get("GEN_INTERVAL_SECONDS", "3"))

    wait_for_db(60)
    Base.metadata.create_all(bind=ENGINE)

    state = WeatherState.initial()

    print("Weather generator started. Writing 1 record each", interval_seconds, "seconds.")
    try:
        while True:
            state = state.step()
            reading = WeatherReading(
                temperature_c=state.temperature_c,
                humidity_percent=state.humidity_percent,
                pressure_hpa=state.pressure_hpa,
                wind_speed_mps=state.wind_speed_mps,
            )

            with SessionLocal() as session:
                session.add(reading)
                session.commit()

            ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
            print(
                f"[{ts}] temp={state.temperature_c}°C, "
                f"hum={state.humidity_percent}%, "
                f"press={state.pressure_hpa}hPa, "
                f"wind={state.wind_speed_mps}m/s"
            )

            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("Weather generator stopped.")


if __name__ == "__main__":
    main()
