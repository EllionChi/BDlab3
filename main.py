import enum
import os
import pandas as pd
from datetime import datetime, time
import sqlalchemy as sa
from sqlalchemy import create_engine, Column, Integer, String, Float, Enum, Date, Time, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

CSV_PATH = 'C:/Users/ediks/OneDrive/Документы/GitHub/BDlab3/GlobalWeatherRepository.csv'
# Оновлено назву до версії v3 для створення нової структури з розділеною датою і часом
SQLITE_URL = 'sqlite:///C:/Users/ediks/OneDrive/Документы/GitHub/BDlab3/weather_v3.db'

POSTGRES_URL = 'postgresql+psycopg2://postgres:password@localhost:5432/weather_db'
MYSQL_URL = 'mysql+pymysql://root:password@localhost:3306/weather_db'

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
    last_updated_date = Column(Date, nullable=False) 
    last_updated_time = Column(Time, nullable=False) 
    
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


def initialize_and_fill_sqlite():
    engine = create_engine(SQLITE_URL)
    Base.metadata.create_all(engine)
    
    cols = ['country', 
            'last_updated', 
            'sunrise', 
            'wind_mph', 
            'wind_kph', 
            'wind_degree', 
            'wind_direction', 
            'gust_mph', 
            'gust_kph']
        
    df = pd.read_csv(CSV_PATH)[cols]
    Session = sessionmaker(bind=engine)
    
    with Session() as session:
        if session.query(WeatherMeasurement).count() == 0:
            print("База порожня")
            for _, row in df.iterrows():
                full_datetime = datetime.strptime(row['last_updated'], '%Y-%m-%d %H:%M')
                time_obj = datetime.strptime(row['sunrise'], '%I:%M %p').time()
                
                wind_speed_kph = row['wind_kph']
                is_safe_weather = True

                if pd.notna(wind_speed_kph) and wind_speed_kph > 36.0:
                    is_safe_weather = False
                
                measurement = WeatherMeasurement(
                    country=row['country'],
                    last_updated_date=full_datetime.date(),
                    last_updated_time=full_datetime.time(), 
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
            print("Дані в weather_v3.db!")
        else:
            print(f"База заповнена ({session.query(WeatherMeasurement).count()} записів).")


def search_weather_interface():
    engine = create_engine(SQLITE_URL)
    Session = sessionmaker(bind=engine)

    country = input("Країна: ").strip()
    date_str = input("Дата РРРР-ММ-ДД (наприклад 2024-05-16): ").strip()

    try:
        search_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        print("Помилка: треба використати формат РРРР-ММ-ДД.")
        return

    with Session() as session:
        query = session.query(WeatherMeasurement).join(WindData)
        query = query.filter(WeatherMeasurement.country.ilike(f"%{country}%"))
        query = query.filter(WeatherMeasurement.last_updated_date == search_date)

        results = query.all()
        print(f"\nЗнайдено записів: {len(results)}")
        print("-" * 60)
        
        for res in results:
            print(f"Країна: {res.country} | Дата: {res.last_updated_date} | Час оновлення: {res.last_updated_time} | Схід: {res.sunrise}")
            if res.wind:
                print(f"  Вітер: {res.wind.wind_kph} км/г ({res.wind.wind_direction.value if res.wind.wind_direction else 'N/A'})")
                print(f"  Пориви: {res.wind.gust_kph} км/г | Градус: {res.wind.wind_degree}°")
                
                if res.wind.should_go_outside:
                    status_message = "Так"
                else:
                    status_message = "Ні"
                    
                print(f"  Чи можна йти на прогулянку: {status_message}")
            print("-" * 90)


def migrate_and_sync_databases():
    try:
        pg_engine = create_engine(POSTGRES_URL)
        mysql_engine = create_engine(MYSQL_URL)
        Base.metadata.create_all(pg_engine)
        Base.metadata.create_all(mysql_engine)
        PgSession = sessionmaker(bind=pg_engine)
        MysqlSession = sessionmaker(bind=mysql_engine)
        with PgSession() as pg_session, MysqlSession() as mysql_session:
            if pg_session.query(WeatherMeasurement).count() > 0 and mysql_session.query(WeatherMeasurement).count() == 0:
                print("Перенесення даних з PostgreSQL до MySQL...")
                for pg_res in pg_session.query(WeatherMeasurement).all():
                    new_meas = WeatherMeasurement(
                        country=pg_res.country, 
                        last_updated_date=pg_res.last_updated_date, 
                        last_updated_time=pg_res.last_updated_time, 
                        sunrise=pg_res.sunrise
                    )
                    if pg_res.wind:
                        new_meas.wind = WindData(
                            wind_mph=pg_res.wind.wind_mph, wind_kph=pg_res.wind.wind_kph,
                            wind_degree=pg_res.wind.wind_degree, wind_direction=pg_res.wind.wind_direction,
                            gust_mph=pg_res.wind.gust_mph, gust_kph=pg_res.wind.gust_kph,
                            should_go_outside=pg_res.wind.should_go_outside
                        )
                    mysql_session.add(new_meas)
                mysql_session.commit()
    except Exception as e:
        print(f"Помилка міграції. Перевірка СУБД")

if __name__ == "__main__":
    initialize_and_fill_sqlite()
    
    while True:
        print("\n1. Знайти погоду")
        print("2. Міграція(PostgreSQL to MySQL)")
        print("3. Вихід")
        
        choice = input("Дія (1-3): ").strip()
        
        if choice == '1':
            search_weather_interface()
        elif choice == '2':
            migrate_and_sync_databases()
        elif choice == '3':
            print("Вихід")
            break
        else:
            print("Від 1 до 3")