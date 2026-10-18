
import os

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine


@event.listens_for(Engine, "connect")
def enable_sqlite_foreign_keys(connection, _record):
    if connection.__class__.__module__.startswith("sqlite3"):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


db = SQLAlchemy()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "floodguard.db")


def init_db(app, seed=True):
    app.config.setdefault("SQLALCHEMY_DATABASE_URI", f"sqlite:///{DATABASE_PATH}")
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)

    db.init_app(app)

    with app.app_context():
        from models import BroadcastAlert, EvacuationCenter, Region, Sensor, SensorLog

        db.create_all()

        if seed:
            seed_database()


def seed_database():
    from datetime import datetime, timedelta, timezone

    from models import BroadcastAlert, EvacuationCenter, Region, Sensor, SensorLog

    if db.session.query(Region.id).first() is not None:
        return

    regions = [
        Region(name="North District", zone_code="ZONE-01", risk_level="Green"),
        Region(name="Poblacion", zone_code="ZONE-02", risk_level="Yellow"),
        Region(name="Riverside", zone_code="ZONE-03", risk_level="Orange"),
        Region(name="Low-Lying District", zone_code="ZONE-04", risk_level="Red"),
    ]

    db.session.add_all(regions)
    db.session.flush()

    centers = [
        EvacuationCenter(region_id=regions[0].id, name="North District Community Hall", capacity=300, current_status="Open"),
        EvacuationCenter(region_id=regions[0].id, name="North Elementary School Gym", capacity=200, current_status="Open"),
        EvacuationCenter(region_id=regions[1].id, name="Poblacion Municipal Gym", capacity=500, current_status="Open"),
        EvacuationCenter(region_id=regions[1].id, name="Poblacion Covered Court", capacity=250, current_status="Full"),
        EvacuationCenter(region_id=regions[2].id, name="Riverside Evacuation Hall", capacity=400, current_status="Open"),
        EvacuationCenter(region_id=regions[3].id, name="Low-Lying District High School", capacity=600, current_status="Open"),
    ]
    db.session.add_all(centers)

    sensor_specs = [
        (regions[0], "Rainfall", 2.5, "mm/hr"),
        (regions[0], "Water-Level", 0.35, "m"),
        (regions[1], "Rainfall", 12.0, "mm/hr"),
        (regions[1], "Water-Level", 0.90, "m"),
        (regions[2], "Rainfall", 28.0, "mm/hr"),
        (regions[2], "Water-Level", 1.65, "m"),
        (regions[3], "Rainfall", 45.0, "mm/hr"),
        (regions[3], "Water-Level", 2.40, "m"),
    ]

    sensors = [
        Sensor(region_id=region.id, sensor_type=sensor_type, current_value=value, unit=unit)
        for region, sensor_type, value, unit in sensor_specs
    ]
    db.session.add_all(sensors)
    db.session.flush()

    now = datetime.now(timezone.utc)
    logs = [
        SensorLog(sensor_id=sensor.id, reading_value=sensor.current_value, timestamp=now - timedelta(minutes=5 * index))
        for index, sensor in enumerate(sensors)
    ]
    db.session.add_all(logs)

    alerts = [
        BroadcastAlert(region_id=regions[1].id, alert_level="Yellow", message="Mock alert: Monitor local rainfall and follow official advisories.", timestamp=now - timedelta(minutes=20)),
        BroadcastAlert(region_id=regions[2].id, alert_level="Orange", message="Mock alert: Prepare for possible evacuation and monitor official instructions.", timestamp=now - timedelta(minutes=10)),
        BroadcastAlert(region_id=regions[3].id, alert_level="Red", message="Mock critical alert: Follow local authorities' evacuation instructions immediately.", timestamp=now),
    ]
    db.session.add_all(alerts)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
