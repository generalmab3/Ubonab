# داده

اسکریپت `prepare_public_data.py` سری ساعتی را می‌سازد.

اگر دانلود برقرار باشد:
- بار از UCI (Candanedo 2017، DOI 10.24432/C5VC8G)، میانگین ساعتی وسایل و روشنایی به‌علاوه 0.20 kW
- تابش روزانه NASA POWER برای Stambruges، پخش‌شده با ارتفاع خورشید

اگر دانلود نشود همان بازه با مدل بار و پوش خورشید پر می‌شود. منبع هر اجرا در `metadata.json` است.

- `public_microgrid_case.csv`
- `metadata.json`
- `metrics.json` بعد از `simulate.py`

بازه: 2016-01-11 17:00 تا 2016-05-27 17:00 به وقت Brussels، 3289 ساعت.
