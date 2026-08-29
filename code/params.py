# پارامترهای آزمایش (پیوست الف)

from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
CASE_CSV = DATA_DIR / "public_microgrid_case.csv"
METADATA_JSON = DATA_DIR / "metadata.json"
METRICS_JSON = DATA_DIR / "metrics.json"
ASSETS_DIR = ROOT.parent / "assets"

ETA_C = 0.95
ETA_D = 0.95
E_MAX = 2.0
P_MAX = 1.0
S_MIN = 0.20
S_MAX = 0.90
KAPPA = 0.008
DELTA_T = 1.0
S0 = 0.50

PV_NOMINAL_KW = 1.0
PV_PERFORMANCE_RATIO = 0.82
BACKGROUND_LOAD_KW = 0.20

# Stambruges (خانه Candanedo 2017)
LATITUDE = 50.5083
LONGITUDE = 3.7147
TIMEZONE = "Europe/Brussels"

BUY_OFFPEAK = 0.16
BUY_NORMAL = 0.22
BUY_PEAK = 0.34
BUY_WEEKEND = 0.20
SELL_PRICE = 0.06
PEAK_HOURS = range(17, 22)
OFFPEAK_HOURS = tuple(list(range(0, 7)) + list(range(22, 24)))

SOC_GRID_STEP = 0.01
N_ACTIONS = 41

HIDDEN = 32
BATCH = 64
EPOCHS = 450
PATIENCE = 55
LR = 1.2e-3
SEEDS = (7, 11, 19, 23, 29)
TRAIN_FRAC = 0.60
VAL_FRAC = 0.20

UCI_ZIP_URL = "https://archive.ics.uci.edu/static/public/374/appliances+energy+prediction.zip"
NASA_POWER_URL = (
    "https://power.larc.nasa.gov/api/temporal/daily/point"
    "?parameters=ALLSKY_SFC_SW_DWN&community=RE&format=JSON"
    f"&latitude={LATITUDE}&longitude={LONGITUDE}"
    "&start=20160111&end=20160527"
)
