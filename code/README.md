# آزمایش گزارش

پیاده‌سازی همان مدل، افراز و شاخص‌های فصل روش‌شناسی.

```bash
python3 -m venv .venv
.venv/bin/pip install -r code/requirements.txt
.venv/bin/python code/prepare_public_data.py
.venv/bin/python code/test_physics.py
.venv/bin/python code/simulate.py
.venv/bin/python code/benchmark_runtime.py
```

`simulate.py` مرجع برنامه‌ریزی پویا، دو شبکه، سیاست حریصانه، آزمایش حذفی نگاه‌به‌جلو، `code/data/metrics.json` و شکل‌ها را می‌نویسد.
