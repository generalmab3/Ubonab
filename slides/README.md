# اسلاید دفاع و درسنامه

دو فایل جدا:

| فایل | کار |
|---|---|
| [`defense.html`](defense.html) | **جلسه دفاع** — ۳۰ اسلاید اصلی + ۳ پشتیبان |
| [`index.html`](index.html) | درسنامه کامل مخزن، مثال عددی، کد، ۱۵ پرسش‌پاسخ |

فرمول‌ها با KaTeX و راست‌به‌چپ‌اند.

## اجرا

از ریشهٔ مخزن:

```bash
python3 -m http.server 8787 --bind 0.0.0.0
```

سپس برای جلسه `slides/defense.html` را باز کنید.

## کلیدها

| کلید | کار |
|---|---|
| فاصله / چپ / پایین | اسلاید بعد (در RTL) |
| راست / بالا / Backspace | اسلاید قبل |
| N | یادداشت گوینده |
| F | تمام‌صفحه |
| Home / End | اول / آخر |
| ? | راهنما |
| P | چاپ همهٔ اسلایدها با یادداشت |

در صفحه، نوار راست اسلاید بعد است و نوار چپ اسلاید قبل.

در جلسه، از عنوان تا «پرسش‌ها» را بگویید (حدود ۲۵ دقیقه). سه اسلاید پشتیبان را نشان ندهید مگر بپرسند.

PDF جلسه: [`defense.pdf`](defense.pdf)  
PDF درسنامه: [`defense-handbook.pdf`](defense-handbook.pdf)

```bash
.venv/bin/python slides/make_pdf.py slides/defense.html slides/defense.pdf
.venv/bin/python slides/make_pdf.py slides/index.html slides/defense-handbook.pdf
```

اعداد باید با `code/data/metrics.json` یکی باشند. استاد راهنما فقط دکتر بابک آذرنوید است.
