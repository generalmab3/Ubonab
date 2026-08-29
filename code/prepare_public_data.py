"""Build the hourly hybrid case study.

Intended public sources are the UCI appliances set and NASA POWER.
If those hosts are unreachable, the same calendar and Stambruges location
are filled with a documented residential load shape and a solar-altitude
PV envelope so the experiment remains fully reproducible from this repo.
"""

from __future__ import annotations

import csv
import io
import json
import math
import urllib.request
import zipfile
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import numpy as np

from params import (
    BACKGROUND_LOAD_KW,
    BUY_NORMAL,
    BUY_OFFPEAK,
    BUY_PEAK,
    BUY_WEEKEND,
    CASE_CSV,
    DATA_DIR,
    LATITUDE,
    LONGITUDE,
    METADATA_JSON,
    NASA_POWER_URL,
    OFFPEAK_HOURS,
    PEAK_HOURS,
    PV_NOMINAL_KW,
    PV_PERFORMANCE_RATIO,
    SELL_PRICE,
    TIMEZONE,
    UCI_ZIP_URL,
)

TZ = ZoneInfo(TIMEZONE)
START = datetime(2016, 1, 11, 17)
END = datetime(2016, 5, 27, 17)
UCI_CSV_MIRRORS = (
    UCI_ZIP_URL,
    "https://archive.ics.uci.edu/ml/machine-learning-databases/00374/energydata_complete.csv",
)


def _download(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Ubonab-thesis-repro/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def _try_download(url: str):
    try:
        return _download(url)
    except Exception as exc:
        print(f"download failed: {url}: {exc}")
        return None


def _solar_altitude_rad(lat_deg: float, lon_deg: float, utc: datetime) -> float:
    day = utc.timetuple().tm_yday
    gamma = 2.0 * math.pi / 365.0 * (day - 1)
    decl = (
        0.006918
        - 0.399912 * math.cos(gamma)
        + 0.070257 * math.sin(gamma)
        - 0.006758 * math.cos(2 * gamma)
        + 0.000907 * math.sin(2 * gamma)
        - 0.002697 * math.cos(3 * gamma)
        + 0.00148 * math.sin(3 * gamma)
    )
    eqtime = 229.18 * (
        0.000075
        + 0.001868 * math.cos(gamma)
        - 0.032077 * math.sin(gamma)
        - 0.014615 * math.cos(2 * gamma)
        - 0.040849 * math.sin(2 * gamma)
    )
    minutes = utc.hour * 60 + utc.minute + utc.second / 60.0
    tst = minutes + eqtime + 4.0 * lon_deg
    ha = math.radians(tst / 4.0 - 180.0)
    lat = math.radians(lat_deg)
    sin_alt = math.sin(lat) * math.sin(decl) + math.cos(lat) * math.cos(decl) * math.cos(ha)
    return math.asin(max(-1.0, min(1.0, sin_alt)))


def _buy_price(local: datetime) -> float:
    if local.weekday() >= 5:
        return BUY_WEEKEND
    hour = local.hour
    if hour in PEAK_HOURS:
        return BUY_PEAK
    if hour in OFFPEAK_HOURS:
        return BUY_OFFPEAK
    return BUY_NORMAL


def target_hours() -> list[datetime]:
    hours = []
    t = START
    while t <= END:
        hours.append(t)
        t += timedelta(hours=1)
    return hours


def parse_uci_csv(text: str) -> dict[datetime, float]:
    rows = []
    reader = csv.DictReader(io.StringIO(text))
    for rec in reader:
        stamp = datetime.strptime(rec["date"], "%Y-%m-%d %H:%M:%S")
        kw = (float(rec["Appliances"]) + float(rec["lights"])) * 6.0 / 1000.0
        rows.append((stamp, kw))
    buckets: dict[datetime, list[float]] = {}
    for stamp, kw in rows:
        hour = stamp.replace(minute=0, second=0, microsecond=0)
        buckets.setdefault(hour, []).append(kw)
    return {hour: float(np.mean(vals) + BACKGROUND_LOAD_KW) for hour, vals in buckets.items() if len(vals) == 6}


def load_from_uci() -> dict[datetime, float] | None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = DATA_DIR / "energydata_complete.zip"
    csv_path = DATA_DIR / "energydata_complete.csv"
    blob = _try_download(UCI_ZIP_URL)
    if blob and blob[:2] == b"PK":
        zip_path.write_bytes(blob)
        with zipfile.ZipFile(zip_path) as zf:
            name = next(n for n in zf.namelist() if n.lower().endswith(".csv"))
            text = zf.read(name).decode("utf-8")
        csv_path.write_text(text, encoding="utf-8")
        return parse_uci_csv(text)
    blob = _try_download(UCI_CSV_MIRRORS[1])
    if blob and b"Appliances" in blob[:2000]:
        text = blob.decode("utf-8")
        csv_path.write_text(text, encoding="utf-8")
        return parse_uci_csv(text)
    if csv_path.exists():
        return parse_uci_csv(csv_path.read_text(encoding="utf-8"))
    return None


def nasa_daily() -> dict | None:
    cache = DATA_DIR / "nasa_power_daily.json"
    if cache.exists():
        payload = json.loads(cache.read_text(encoding="utf-8"))
    else:
        blob = _try_download(NASA_POWER_URL)
        if blob is None:
            return None
        payload = json.loads(blob.decode("utf-8"))
        cache.write_text(json.dumps(payload), encoding="utf-8")
    series = payload["properties"]["parameter"]["ALLSKY_SFC_SW_DWN"]
    daily = {}
    for key, value in series.items():
        if float(value) < 0:
            continue
        day = datetime.strptime(key, "%Y%m%d").date()
        daily[day] = float(value)
    return daily


def synthetic_load(hours: list[datetime]) -> dict[datetime, float]:
    """Residential shape at the scale of the UCI house, plus the documented 0.20 kW background."""
    rng = np.random.default_rng(20160111)
    out = {}
    noise = 0.0
    for hour in hours:
        h = hour.hour
        weekend = hour.weekday() >= 5
        morning = math.exp(-0.5 * ((h - 8) / 1.6) ** 2)
        evening = math.exp(-0.5 * ((h - 19) / 2.2) ** 2)
        midday = 0.35 * math.exp(-0.5 * ((h - 13) / 3.0) ** 2)
        night = 0.12 if 0 <= h < 6 else 0.0
        occ = 0.18 * morning + 0.22 * evening + midday + night
        if weekend:
            occ = 0.85 * occ + 0.08
        noise = 0.65 * noise + 0.35 * rng.normal(0.0, 0.05)
        out[hour] = float(max(0.12, BACKGROUND_LOAD_KW + occ + noise))
    return out


def pv_from_daily(hours: list[datetime], daily: dict) -> dict[datetime, float]:
    by_day: dict = {}
    for hour in hours:
        by_day.setdefault(hour.date(), []).append(hour)
    pv = {}
    for day, day_hours in by_day.items():
        total = daily.get(day, 0.0)
        weights = []
        for hour in day_hours:
            utc = hour.replace(tzinfo=TZ).astimezone(timezone.utc)
            alt = _solar_altitude_rad(LATITUDE, LONGITUDE, utc)
            weights.append(max(0.0, math.sin(alt)))
        wsum = sum(weights)
        if wsum <= 0.0 or total <= 0.0:
            for hour in day_hours:
                pv[hour] = 0.0
            continue
        for hour, w in zip(day_hours, weights):
            ghi = total * (w / wsum)
            pv[hour] = float(max(0.0, PV_NOMINAL_KW * PV_PERFORMANCE_RATIO * ghi))
    return pv


def synthetic_pv(hours: list[datetime]) -> dict[datetime, float]:
    """Clear-sky envelope at Stambruges with a slow daily cloud factor."""
    rng = np.random.default_rng(20160117)
    pv = {}
    cloud = 0.75
    last_day = None
    for hour in hours:
        if hour.date() != last_day:
            cloud = float(np.clip(0.55 + 0.35 * rng.random(), 0.25, 1.0))
            last_day = hour.date()
        utc = hour.astimezone(timezone.utc)
        alt = _solar_altitude_rad(LATITUDE, LONGITUDE, utc)
        sin_a = max(0.0, math.sin(alt))
        if sin_a <= 0.0:
            pv[hour] = 0.0
            continue
        ghi = 0.95 * sin_a * math.exp(-0.32 / max(sin_a, 0.08)) * cloud
        pv[hour] = float(max(0.0, PV_NOMINAL_KW * PV_PERFORMANCE_RATIO * ghi))
    return pv


def write_case(hours, load, pv) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with CASE_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["timestamp", "P_L_kW", "P_PV_kW", "c_b", "c_s", "hour", "weekday", "is_workday"])
        for hour in hours:
            writer.writerow(
                [
                    hour.strftime("%Y-%m-%d %H:%M"),
                    f"{load[hour]:.6f}",
                    f"{pv[hour]:.6f}",
                    f"{_buy_price(hour):.4f}",
                    f"{SELL_PRICE:.4f}",
                    hour.hour,
                    hour.weekday(),
                    int(hour.weekday() < 5),
                ]
            )


def write_metadata(n, start, end, load_src, pv_src) -> None:
    meta = {
        "description": "Hybrid public-data microgrid case study for the Bonab bachelor report.",
        "n_hours": n,
        "start_local": start.strftime("%Y-%m-%d %H:%M"),
        "end_local": end.strftime("%Y-%m-%d %H:%M"),
        "timezone": TIMEZONE,
        "load": {
            "source": load_src,
            "doi": "10.24432/C5VC8G",
            "background_kW": BACKGROUND_LOAD_KW,
        },
        "pv": {
            "source": pv_src,
            "location": {"latitude": LATITUDE, "longitude": LONGITUDE, "site": "Stambruges, Belgium"},
            "nominal_kW": PV_NOMINAL_KW,
            "performance_ratio": PV_PERFORMANCE_RATIO,
        },
        "tariff": {
            "weekday_offpeak": BUY_OFFPEAK,
            "weekday_normal": BUY_NORMAL,
            "weekday_peak": BUY_PEAK,
            "weekend": BUY_WEEKEND,
            "sell": SELL_PRICE,
            "peak_hours_local": list(PEAK_HOURS),
            "offpeak_hours_local": list(OFFPEAK_HOURS),
            "note": "Engineering assumption, not a utility bill.",
        },
        "battery": {"E_max_kWh": 2.0, "P_max_kW": 1.0, "eta_c": 0.95, "eta_d": 0.95},
    }
    METADATA_JSON.write_text(json.dumps(meta, indent=2), encoding="utf-8")


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    hours = target_hours()
    if len(hours) != 3289:
        raise SystemExit(f"calendar error: {len(hours)} hours")

    uci = load_from_uci()
    if uci is not None and all(h in uci for h in hours):
        load = {h: uci[h] for h in hours}
        load_src = "UCI Appliances Energy Prediction, hourly mean of Appliances+lights plus 0.20 kW"
    else:
        print("UCI file not reachable; using documented residential load shape on the same calendar.")
        load = synthetic_load(hours)
        load_src = "Documented residential shape on the Candanedo 2017 calendar; UCI host was unreachable"

    daily = nasa_daily()
    if daily is not None:
        pv = pv_from_daily(hours, daily)
        pv_src = "NASA POWER ALLSKY_SFC_SW_DWN daily, shaped by solar altitude"
    else:
        print("NASA POWER not reachable; using solar-altitude envelope at Stambruges.")
        pv = synthetic_pv(hours)
        pv_src = "Solar-altitude PV envelope at Stambruges; NASA host was unreachable"

    write_case(hours, load, pv)
    write_metadata(len(hours), hours[0], hours[-1], load_src, pv_src)
    print(f"wrote {CASE_CSV} with {len(hours)} hours")


if __name__ == "__main__":
    main()
