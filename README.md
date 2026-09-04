# قالب پروژه کارشناسی دانشگاه بناب

قالب XeLaTeX برای گزارش پروژه کارشناسی علوم کامپیوتر. راهنمای کامل:

**[docs/GUIDE.md](docs/GUIDE.md)**

تطبیق با دستورالعمل دانشگاه: [docs/COMPLIANCE.md](docs/COMPLIANCE.md)

## شروع سریع

موتور کامپایل باید **XeLaTeX** باشد. منابع با **Biber** ساخته می‌شوند.

### Overleaf

1. ZIP را بارگذاری کنید.
2. Compiler را روی XeLaTeX بگذارید.
3. Main document: `main.tex`
4. Recompile from scratch

### محلی

```bash
./build.sh          # لینوکس و macOS
build.bat           # ویندوز
latexmk -xelatex main.tex
```

پاک‌سازی: `./build.sh clean` یا `latexmk -C`

## ویرایش روزمره

| فایل | کار |
|---|---|
| `config/metadata.tex` | نام، عنوان، استاد، کلید بخش‌ها |
| `chapters/*.tex` | متن فصل |
| `frontmatter/abstract-fa.tex` | چکیده فارسی |
| `frontmatter/abstract-en.tex` | چکیده انگلیسی |
| `references.bib` | منابع |

در متن فارسی: اصطلاح لاتین داخل `\lr{...}` و ارجاع با `\pcite{key}`. جزئیات و خطاهای مربع خالی در راهنما است.
