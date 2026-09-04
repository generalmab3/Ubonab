# کد آزمایش

```bash
python3 -m venv .venv
.venv/bin/pip install -r code/requirements.txt
.venv/bin/python code/prepare_public_data.py
.venv/bin/python code/test_physics.py
.venv/bin/python code/simulate.py
.venv/bin/python code/benchmark_runtime.py
```

خروجی شاخص‌ها: `code/data/metrics.json`  
شکل‌ها: `assets/`
