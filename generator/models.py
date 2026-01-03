from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, Float, Integer, func

class Base(DeclarativeBase):
    pass

class WeatherReading(Base):
    __tablename__ = "weather_readings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[object] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    temperature_c: Mapped[float] = mapped_column(Float, nullable=False)
    humidity_percent: Mapped[float] = mapped_column(Float, nullable=False)
    pressure_hpa: Mapped[float] = mapped_column(Float, nullable=False)
    wind_speed_mps: Mapped[float] = mapped_column(Float, nullable=False)
