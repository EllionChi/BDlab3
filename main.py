import enum
import pandas as pd
from datetime import datetime, time
from sqlalchemy import create_engine, Column, Integer, String, Float, Enum, DateTime, Time
from sqlalchemy.orm import declarative_base

df = pd.read_csv('C:/Users/ediks/OneDrive/Документы/GitHub/BD/GlobalWeatherRepository.csv')


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
    wind_mph = Column(Float, nullable=True)
    wind_kph = Column(Float, nullable=True)                          
    wind_degree = Column(Integer, nullable=True)                     
    wind_direction = Column(Enum(WindDirectionEnum), nullable=True) 
    gust_mph = Column(Float, nullable=True)
    gust_kph = Column(Float, nullable=True)

if __name__ == "__main__":
    for column in WeatherMeasurement.__table__.columns:
        print(f" - {column.name}: {column.type}")