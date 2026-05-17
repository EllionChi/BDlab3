import enum
import os
import pandas as pd
from datetime import datetime, time
from sqlalchemy import create_engine, Column, Integer, String, Float, Enum, DateTime, Time, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

csv_path = 'C:/Users/ediks/OneDrive/Документы/GitHub/BDlab3/GlobalWeatherRepository.csv'
cols = ['country', 
        'last_updated', 
        'sunrise', 
        'wind_mph', 
        'wind_kph', 
        'wind_degree', 
        'wind_direction', 
        'gust_mph', 
        'gust_kph']
df = pd.read_csv(csv_path)[cols]
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
    should_go_outside = Column(Boolean, nullable=False)
    measurement = relationship("WeatherMeasurement", back_populates="wind")


if __name__ == "__main__":
    db_url = 'sqlite:///C:/Users/ediks/OneDrive/Документы/GitHub/BDlab3/weather_v2.db'
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    with Session() as session:
        if session.query(WeatherMeasurement).count() == 0:
            print("Порожня база- заповнення")
            
            for _, row in df.iterrows():
                date_obj = datetime.strptime(row['last_updated'], '%Y-%m-%d %H:%M')
                time_obj = datetime.strptime(row['sunrise'], '%I:%M %p').time()
                wind_speed_kph = row['wind_kph']
                is_safe_weather = True
                if pd.notna(wind_speed_kph) and wind_speed_kph > 36.0:
                    is_safe_weather = False
                
                measurement = WeatherMeasurement(
                    country=row['country'],
                    last_updated=date_obj,
                    sunrise=time_obj
                )
                
                wind_info = WindData(
                    wind_mph=row['wind_mph'],
                    wind_kph=wind_speed_kph,
                    wind_degree=int(row['wind_degree']) if pd.notna(row['wind_degree']) else None,
                    wind_direction=WindDirectionEnum[row['wind_direction']] if pd.notna(row['wind_direction']) else None,
                    gust_mph=row['gust_mph'],
                    gust_kph=row['gust_kph'],
                    should_go_outside=is_safe_weather
                )
                measurement.wind = wind_info
                session.add(measurement)
                
            session.commit()
            print("збережен weather_v2.db")
        else:
            print(f"база вже заповнена ({session.query(WeatherMeasurement).count()} записів).")