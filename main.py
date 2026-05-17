import enum
import pandas as pd
from datetime import datetime, time
from sqlalchemy import create_engine, Column, Integer, String, Float, Enum, DateTime, Time, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

df = pd.read_csv('C:/Users/ediks/OneDrive/Документы/GitHub/BDlab3/GlobalWeatherRepository.csv')

selected_columns = [
    'country',          
    'last_updated',     
    'sunrise',          
    'wind_mph',         
    'wind_kph',        
    'wind_degree',      
    'wind_direction',   
    'gust_mph',         
    'gust_kph'          
]

filtered_df = df[selected_columns]
filtered_df.to_csv('filtered_weather_orm.csv', index=False)
print(f"Розмірність: {filtered_df.shape}")
Base = declarative_base()

class WindDirectionEnum(enum.Enum):
    NNW = "NNW"
    NW = "NW"
    W = "W"
    SW = "SW"
    SSE = "SSE"
    E = "E"
    N = "N"
    SE = "SE"
    ESE = "ESE"
    NNE = "NNE"
    S = "S"
    WSW = "WSW"
    SSW = "SSW"
    ENE = "ENE"
    NE = "NE"
    WNW = "WNW"

class WeatherMeasurement(Base):
    __tablename__ = 'weather_measurements'
    id = Column(Integer, primary_key=True, autoincrement=True)
    country = Column(String(100), nullable=False)
    last_updated = Column(DateTime, nullable=False)
    sunrise = Column(Time, nullable=False)
    wind = relationship("WindData", back_populates="measurement", uselist=False)

class WindData(Base):
    __tablename__ = 'wind_data'
    id = Column(Integer, primary_key=True, autoincrement=True)
    measurement_id = Column(Integer, ForeignKey('weather_measurements.id'), nullable=False, unique=True)
    wind_mph = Column(Float, nullable=True)
    wind_kph = Column(Float, nullable=True)                                          
    wind_degree = Column(Integer, nullable=True)                     
    wind_direction = Column(Enum(WindDirectionEnum), nullable=True) 
    gust_mph = Column(Float, nullable=True)
    gust_kph = Column(Float, nullable=True)
    measurement = relationship("WeatherMeasurement", back_populates="wind")

if __name__ == "__main__":
    db_url = 'sqlite:///C:/Users/ediks/OneDrive/Документы/GitHub/BDlab3/weather.db'
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    for model in [WeatherMeasurement, WindData]:
        print(f"\nТаблиця: '{model.__tablename__}'")
        for column in model.__table__.columns:
            print(f" - {column.name}: {column.type}")