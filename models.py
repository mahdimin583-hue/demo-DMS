
from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, Index

from database import db


def utc_now():
    return datetime.now(timezone.utc)


class Region(db.Model):
    __tablename__ = "regions"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    zone_code = db.Column(db.String(20), unique=True, nullable=False)
    risk_level = db.Column(db.String(10), nullable=False, default="Green")

    __table_args__ = (
        CheckConstraint("risk_level IN ('Green', 'Yellow', 'Orange', 'Red')", name="ck_region_risk_level"),
    )

    evacuation_centers = db.relationship("EvacuationCenter", back_populates="region", lazy="select")
    sensors = db.relationship("Sensor", back_populates="region", lazy="select")
    broadcast_alerts = db.relationship("BroadcastAlert", back_populates="region", lazy="select")

    def __repr__(self):
        return f"<Region {self.zone_code}: {self.name}>"


class EvacuationCenter(db.Model):
    __tablename__ = "evacuation_centers"

    id = db.Column(db.Integer, primary_key=True)
    region_id = db.Column(db.Integer, db.ForeignKey("regions.id", ondelete="RESTRICT"), nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    current_status = db.Column(db.String(10), nullable=False, default="Open")

    __table_args__ = (
        CheckConstraint("capacity > 0", name="ck_evacuation_capacity_positive"),
        CheckConstraint("current_status IN ('Open', 'Full')", name="ck_evacuation_status"),
    )

    region = db.relationship("Region", back_populates="evacuation_centers")

    def __repr__(self):
        return f"<EvacuationCenter {self.name}>"


class Sensor(db.Model):
    __tablename__ = "sensors"

    id = db.Column(db.Integer, primary_key=True)
    region_id = db.Column(db.Integer, db.ForeignKey("regions.id", ondelete="RESTRICT"), nullable=False, index=True)
    sensor_type = db.Column(db.String(20), nullable=False)
    current_value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(10), nullable=False)

    __table_args__ = (
        CheckConstraint("sensor_type IN ('Rainfall', 'Water-Level')", name="ck_sensor_type"),
        CheckConstraint("current_value >= 0", name="ck_sensor_value_nonnegative"),
    )

    region = db.relationship("Region", back_populates="sensors")
    logs = db.relationship("SensorLog", back_populates="sensor", cascade="all, delete-orphan", passive_deletes=True, lazy="select")

    def __repr__(self):
        return f"<Sensor {self.sensor_type} #{self.id}>"


class SensorLog(db.Model):
    __tablename__ = "sensor_logs"

    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey("sensors.id", ondelete="CASCADE"), nullable=False, index=True)
    reading_value = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now)

    __table_args__ = (
        CheckConstraint("reading_value >= 0", name="ck_sensor_log_value_nonnegative"),
        Index("ix_sensor_logs_sensor_timestamp", "sensor_id", "timestamp"),
    )

    sensor = db.relationship("Sensor", back_populates="logs")

    def __repr__(self):
        return f"<SensorLog sensor={self.sensor_id} value={self.reading_value}>"


class BroadcastAlert(db.Model):
    __tablename__ = "broadcast_alerts"

    id = db.Column(db.Integer, primary_key=True)
    region_id = db.Column(db.Integer, db.ForeignKey("regions.id", ondelete="RESTRICT"), nullable=False, index=True)
    alert_level = db.Column(db.String(10), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now)

    __table_args__ = (
        CheckConstraint("alert_level IN ('Green', 'Yellow', 'Orange', 'Red')", name="ck_broadcast_alert_level"),
        CheckConstraint("length(trim(message)) > 0", name="ck_broadcast_message_nonempty"),
    )

    region = db.relationship("Region", back_populates="broadcast_alerts")

    def __repr__(self):
        return f"<BroadcastAlert {self.alert_level} region={self.region_id}>"
