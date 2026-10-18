
import math
from datetime import datetime, timezone

from flask import Flask, abort, flash, redirect, render_template, request, url_for

from database import DATABASE_PATH, db, init_db
from models import BroadcastAlert, EvacuationCenter, Region, Sensor, SensorLog

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-this-development-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + DATABASE_PATH.replace("\\", "/")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

init_db(app, seed=True)

RISK_ORDER = {
    "Green": 0,
    "Yellow": 1,
    "Orange": 2,
    "Red": 3,
}


def classify_reading(sensor_type, value):
    if sensor_type == "Rainfall":
        if value >= 40:
            return "Red"
        if value >= 25:
            return "Orange"
        if value >= 10:
            return "Yellow"
        return "Green"

    if sensor_type == "Water-Level":
        if value >= 2.2:
            return "Red"
        if value >= 1.5:
            return "Orange"
        if value >= 0.8:
            return "Yellow"
        return "Green"

    raise ValueError("Unsupported sensor type.")


def recalculate_region_risk(region):
    sensors = Sensor.query.filter_by(region_id=region.id).all()

    if not sensors:
        return region.risk_level

    levels = [classify_reading(sensor.sensor_type, sensor.current_value) for sensor in sensors]
    region.risk_level = max(levels, key=lambda level: RISK_ORDER[level])
    return region.risk_level


@app.route("/")
def index():
    return redirect(url_for("user_dashboard"))


@app.route("/user")
def user_dashboard():
    regions = Region.query.order_by(Region.zone_code).all()

    if not regions:
        return render_template(
            "user_dashboard.html",
            regions=[],
            selected_region=None,
            sensors=[],
            centers=[],
            alerts=[],
        )

    region_id = request.args.get("region_id", type=int)
    selected_region = next((r for r in regions if r.id == region_id), regions[0])

    sensors = Sensor.query.filter_by(region_id=selected_region.id).order_by(Sensor.id).all()
    centers = EvacuationCenter.query.filter_by(region_id=selected_region.id).order_by(EvacuationCenter.name).all()
    alerts = BroadcastAlert.query.filter_by(region_id=selected_region.id).order_by(BroadcastAlert.timestamp.desc()).limit(5).all()

    return render_template(
        "user_dashboard.html",
        regions=regions,
        selected_region=selected_region,
        sensors=sensors,
        centers=centers,
        alerts=alerts,
    )


@app.route("/admin", methods=["GET"])
def admin_dashboard():
    regions = Region.query.order_by(Region.zone_code).all()
    sensors = Sensor.query.order_by(Sensor.region_id, Sensor.id).all()

    non_green_alert_count = BroadcastAlert.query.filter(
        BroadcastAlert.alert_level.in_(["Yellow", "Orange", "Red"])
    ).count()

    risk_counts = {
        level: Region.query.filter_by(risk_level=level).count()
        for level in ("Green", "Yellow", "Orange", "Red")
    }

    recent_alerts = BroadcastAlert.query.order_by(BroadcastAlert.timestamp.desc()).limit(10).all()
    recent_logs = SensorLog.query.order_by(SensorLog.timestamp.desc(), SensorLog.id.desc()).limit(10).all()

    return render_template(
        "admin_dashboard.html",
        regions=regions,
        sensors=sensors,
        region_count=len(regions),
        sensor_count=Sensor.query.count(),
        alert_count=BroadcastAlert.query.count(),
        non_green_alert_count=non_green_alert_count,
        risk_counts=risk_counts,
        recent_alerts=recent_alerts,
        recent_logs=recent_logs,
    )


@app.route("/admin/simulate-sensor", methods=["POST"])
def simulate_sensor():
    region_id = request.form.get("region_id", type=int)
    sensor_id = request.form.get("sensor_id", type=int)
    raw_value = request.form.get("reading_value", "").strip()

    if not region_id or not sensor_id or not raw_value:
        flash("Select a region and sensor, then enter a reading.", "danger")
        return redirect(url_for("admin_dashboard"))

    try:
        value = float(raw_value)
        if not math.isfinite(value) or value < 0:
            raise ValueError
    except ValueError:
        flash("Reading must be a finite, nonnegative number.", "danger")
        return redirect(url_for("admin_dashboard"))

    region = db.session.get(Region, region_id)
    sensor = db.session.get(Sensor, sensor_id)

    if region is None or sensor is None or sensor.region_id != region.id:
        abort(400, description="Sensor does not belong to the selected region.")

    try:
        sensor.current_value = value

        log = SensorLog(
            sensor_id=sensor.id,
            reading_value=value,
            timestamp=datetime.now(timezone.utc),
        )
        db.session.add(log)

        new_risk = recalculate_region_risk(region)
        db.session.commit()

        flash(f"Sensor updated successfully. {region.name} risk is now {new_risk}.", "success")
    except Exception:
        db.session.rollback()
        app.logger.exception("Failed to save simulated sensor reading.")
        flash("Unable to save the sensor reading. No changes were committed.", "danger")

    return redirect(url_for("admin_dashboard"))


@app.route("/admin/broadcast-alert", methods=["POST"])
def broadcast_alert():
    region_id = request.form.get("region_id", type=int)
    alert_level = request.form.get("alert_level", "").strip()
    message = request.form.get("message", "").strip()

    allowed_levels = {"Green", "Yellow", "Orange", "Red"}
    region = db.session.get(Region, region_id) if region_id else None

    if region is None:
        flash("Select a valid region.", "danger")
        return redirect(url_for("admin_dashboard"))

    if alert_level not in allowed_levels:
        flash("Select a valid alert level.", "danger")
        return redirect(url_for("admin_dashboard"))

    if not message or len(message) > 2000:
        flash("Message is required and must be at most 2,000 characters.", "danger")
        return redirect(url_for("admin_dashboard"))

    try:
        alert = BroadcastAlert(
            region_id=region.id,
            alert_level=alert_level,
            message=message,
            timestamp=datetime.now(timezone.utc),
        )
        db.session.add(alert)
        db.session.commit()

        flash(f"{alert_level} alert saved for {region.name}. This records an alert in the application; it does not send SMS.", "success")
    except Exception:
        db.session.rollback()
        app.logger.exception("Failed to save broadcast alert.")
        flash("Unable to save the alert. No changes were committed.", "danger")

    return redirect(url_for("admin_dashboard"))


if __name__ == "__main__":
    app.run(debug=True)
