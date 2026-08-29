# راهنمای قالب پروژه کارشناسی دانشگاه بناب

این سند تنها مرجع کار با قالب است. فایل‌های تکراری راهنما حذف شده‌اند. جدول تطبیق با دستورالعمل دانشگاه در `docs/COMPLIANCE.md` است.

قالب با **XeLaTeX** و **Biber** برای گزارش پروژه کارشناسی علوم کامپیوتر دانشگاه بناب تنظیم شده است. دستورالعمل اصلی دانشگاه برای تحصیلات تکمیلی نوشته شده؛ فرم دفاع ارشد و دکتری عمداً در این قالب نیست.

---

## ۱. چه چیزی را ویرایش کنید و چه چیزی را نه

| کار شما | مسیر | دست نزنید مگر... |
|---|---|---|
| نام، عنوان، استاد، کلیدواژه، روشن/خاموش بخش‌ها | `config/metadata.tex` | نام فرمان‌ها و آکولادها |
| متن فصل‌ها | `chapters/` | ساختار `\chapter` و `\label` |
| چکیده، تقدیم، سپاس، علائم | `frontmatter/` | منطق شرطی عنوان‌ها |
| پیوست | `appendices/` | مگر بخواهید پیوست را حذف/اضافه کنید |
| منابع | `references.bib` | سبک BibLaTeX |
| شکل و لوگو | `assets/` | نام `logo.pdf` در صفحات عنوان |
| ترتیب صفحات و فهرست فصل‌ها | `main.tex` | فقط برای افزودن فصل یا پیوست |
| قلم | `config/fonts.tex` | خانوادهٔ جایگزین |
| بسته‌ها | `config/packages.tex` | زی‌پرشین باید آخرین بسته بماند |
| ظاهر | `config/style.tex` | اگر دستورالعمل دانشگاه عوض شود |
| فرمان‌های قالب | `config/commands.tex` | تقریباً هرگز |

متن علمی این مخزن یک پروژهٔ نمونهٔ کامل است. برای پروژهٔ جدید، مشخصات را در `metadata.tex` عوض کنید و فصل‌ها را بازنویسی کنید؛ فایل‌های `config/` را کپی کنید نه بازنویسی از صفر.

---

## ۲. درخت پروژه

```text
main.tex                 نقطهٔ ورود؛ ترتیب صفحات
references.bib           کتاب‌شناسی (سبک IEEE، Biber)
latexmkrc                تنظیم واحد کامپایل
build.sh / build.bat     اجرای همان مسیر در لینوکس/macOS و ویندوز
Makefile                 make  و  make clean
config/
  metadata.tex           مشخصات دانشجو و کلید بخش‌ها
  packages.tex           بسته‌ها
  fonts.tex              قلم فارسی، انگلیسی، ارقام
  style.tex              اندازه، عنوان، جدول، کد، TikZ
  commands.tex           \pcite، شماره‌گذاری، فراداده PDF
frontmatter/
  besmellah.tex          بسم الله (بدون شماره)
  title-fa.tex           صفحه عنوان فارسی
  dedication.tex         تقدیم
  acknowledgements.tex   سپاسگزاری
  abstract-fa.tex        چکیده فارسی
  symbols.tex            علائم و اختصارات
  abstract-en.tex        چکیده انگلیسی (انتهای سند)
  title-en.tex           عنوان انگلیسی (آخرین صفحه)
chapters/                فصل‌های ۱ تا ۵
appendices/
  reproducibility.tex    پیوست الف
  hard-layer.tex         پیوست ب
assets/                  logo.pdf و شکل‌ها
docs/GUIDE.md            همین راهنما
docs/COMPLIANCE.md       تطبیق با دستورالعمل دانشگاه
```

تصویرها را فقط در `assets/` بگذارید. مسیر `figures/` دیگر تعریف نشده است.

---

## ۳. نصب و اجرا

موتور باید **XeLaTeX** باشد. یک بار اجرا کافی نیست: منابع به Biber و فهرست‌ها به دو اجرای بعدی نیاز دارند.

### Overleaf

1. ZIP را با New Project → Upload Project بارگذاری کنید.
2. Menu → Compiler → XeLaTeX.
3. Main document: `main.tex`.
4. Recompile from scratch.

### ویندوز

TeX Live یا MiKTeX کامل، سپس `build.bat`. برای پاک‌سازی: `build.bat clean`.

### لینوکس و macOS

```bash
chmod +x build.sh
./build.sh
./build.sh clean    # در صورت نیاز
```

### مسیر واحد در همه سیستم‌ها

```bash
latexmk -xelatex main.tex
latexmk -C          # پاک‌سازی
```

اگر `latexmk` نباشد، اسکریپت‌ها همان چهار مرحله را دستی اجرا می‌کنند: XeLaTeX، Biber، XeLaTeX، XeLaTeX.

خروجی `main.pdf` در ریشه پروژه است. فایل‌های `.aux` و مشابه را در Git نگذارید.

---

## ۴. مشخصات پروژه (`config/metadata.tex`)

فقط متن داخل `{...}` را عوض کنید.

### نهاد

- `\UniversityNameFa` / `\UniversityNameEn`
- `\MinistryNameFa`
- `\FacultyNameFa` / `\FacultyNameEn`
- `\DepartmentNameFa` / `\DepartmentNameEn`
- `\DegreeNameFa` / `\DegreeNameEn` — اینجا کارشناسی / Bachelor of Science
- `\FieldNameFa` / `\FieldNameEn`
- `\OrientationFa` — گرایش؛ اگر ندارید «عمومی» بماند

### افراد و عنوان

- `\ProjectTitleFa` / `\ProjectTitleEn`
- `\StudentNameFa` / `\StudentNameEn`
- `\StudentNumber` — رقم؛ قلم ارقام جدا از B Mitra است
- `\SupervisorNameFa` / `\SupervisorNameEn` — دو استاد را با `\\` جدا کنید
- `\AdvisorNameFa` / `\AdvisorNameEn` — **کاملاً خالی** یعنی بدون استاد مشاور؛ فاصله نگذارید
- `\AcademicYearFa` ، `\DefenseDateFa` ، `\DefenseDateEn`

### برچسب صفحه عنوان

با **یک** استاد راهنما:

```latex
\newcommand{\SupervisorLabelFa}{استاد راهنما}
\newcommand{\SupervisorLabelEn}{Supervisor}
```

با **دو** استاد (وضعیت فعلی):

```latex
\newcommand{\SupervisorLabelFa}{استادان راهنما}
\newcommand{\SupervisorLabelEn}{Supervisors}
```

بقیه برچسب‌ها: `\AdvisorLabelFa`، `\AuthorLabelFa`، `\StudentIdLabelFa`، `\AcademicYearLabelFa` و معادل انگلیسی.

### کلیدواژه

`\KeywordsFa` و `\KeywordsEn` باید ۵ تا ۱۰ مورد و هم‌معنا باشند. همین `\KeywordsEn` وارد فراداده PDF می‌شود.

### کلیدهای اختیاری

در انتهای همان فایل:

| کلید | اثر اگر `false` |
|---|---|
| `\IncludeDedicationfalse` | حذف تقدیم |
| `\IncludeAcknowledgementsfalse` | حذف سپاسگزاری |
| `\IncludeSymbolsfalse` | حذف فهرست علائم |
| `\IncludeListOfFiguresfalse` | حذف فهرست شکل |
| `\IncludeListOfTablesfalse` | حذف فهرست جدول |
| `\IncludeListOfListingsfalse` | حذف فهرست کد |
| `\IncludeAppendixfalse` | حذف همه پیوست‌ها |
| `\IncludeEnglishPagesfalse` | حذف چکیده و عنوان انگلیسی |

اگر فهرست شکل/جدول/کد هیچ مدخلی ندارد، کلید را `false` کنید تا صفحه خالی نسازید.

اگر پیوست را خاموش می‌کنید، هر `\ref` به `app:...` در فصل‌ها را هم حذف کنید؛ وگرنه در PDF علامت سؤال می‌آید.

---

## ۵. افزودن یا حذف فصل

1. فایل `chapters/chapter6.tex`:

```latex
\chapter{عنوان فصل}
\label{chap:short-name}

\section{عنوان بخش}
متن.
```

2. در `main.tex` بعد از فصل ۵:

```latex
\include{chapters/chapter6}
```

پیوست جدید: فایل در `appendices/` بسازید و داخل `\ifIncludeAppendix` با `\include{appendices/name}` اضافه کنید. `\appendix` فقط یک بار قبل از اولین پیوست بیاید.

قرارداد برچسب:

| موضوع | پیشوند | نمونه |
|---|---|---|
| فصل | `chap:` | `chap:method` |
| پیوست | `app:` | `app:reproducibility` |
| رابطه | `eq:` | `eq:power-balance` |
| شکل | `fig:` | `fig:first-test-day` |
| جدول | `tab:` | `tab:accuracy` |
| کد | `lst:` | `lst:hard-layer` |

ارجاع در متن فارسی:

```latex
فصل~\ref{chap:method}
رابطه~\eqref{eq:power-balance}
شکل~\ref{fig:first-test-day}
جدول~\ref{tab:accuracy}
```

هر شکل، جدول، رابطهٔ شماره‌دار و قطعه کد باید `\label` داشته باشد و در متن ارجاع شود.

---

## ۶. فارسی، لاتین و مربع خالی

B Mitra و B Titr حرف لاتین ندارند. B Mitra درصد عربی `٪` (U+066A) و جداکننده اعشار `٫` (U+066B) را هم ندارد.

### اصطلاح لاتین در جمله فارسی

```latex
شبکه \lr{PINN} با \lr{PyTorch} پیاده‌سازی شد.
```

### پاراگراف کاملاً انگلیسی

```latex
\begin{latin}
This paragraph is English.
\end{latin}
```

صفحات چکیده و عنوان انگلیسی از قبل داخل `latin` هستند. عنوان «Abstract» را با `\chapter*` نسازید؛ قلم فصل B Titr است و واژه انگلیسی مربع می‌شود.

### ارجاع منبع در فارسی

```latex
\pcite{raissi2019pinns}
\pcite{lu2021hardconstraints,chen2024hardlinear}
```

`\pcite` شماره و براکت را با قلم لاتین می‌چیند. در متن فارسی `\cite` ننویسید.

### درصد و عدد اعشاری

ننویسید: `۷٫۱٪`  
بنویسید: `$7.1$ درصد`

نسخه نرم‌افزار و نام فایل لاتین را داخل `\lr{...}` بگذارید: `\lr{3.11.2}`، `\lr{simulate.py}`.

اسلش ASCII میان واژه‌های فارسی نگذارید. به‌جای `شارژ/دشارژ` بنویسید «شارژ و دشارژ».

### کد و عنوان انگلیسی در فهرست

```latex
\begin{latin}
\begin{lstlisting}[style=bonabcode,caption={\protect\lr{Python example}},label={lst:python}]
print("Hello")
\end{lstlisting}
\end{latin}
```

`\protect\lr` از وارونه‌شدن عنوان در فهرست کدها جلوگیری می‌کند.

---

## ۷. شکل

فایل را در `assets/` بگذارید (مثلاً `assets/plot.png`).

```latex
\begin{figure}[H]
  \centering
  \includegraphics[width=0.75\textwidth]{plot.png}
  \caption{عنوان فارسی شکل}
  \label{fig:plot}
\end{figure}
```

عنوان پایین شکل است، اندازه ۱۰ پوینت، شماره به‌صورت `شکل. ۱-۳`. اگر عنوان شکل اصطلاح لاتین دارد از `\protect\lr{...}` استفاده کنید.

---

## ۸. جدول

عنوان **بالای** جدول:

```latex
\begin{table}[H]
  \centering
  \caption{عنوان فارسی جدول}
  \label{tab:sample}
  \begin{tabular}{lcc}
    \toprule
    روش & خطا & هزینه \\
    \midrule
    پیشنهادی & $0.01$ & $12.5$ \\
    \bottomrule
  \end{tabular}
\end{table}
```

اعداد را در حالت ریاضی بنویسید تا از قلم ارقام کامل استفاده شود. برای جدول طولانی `longtable` و برای ادغام سلول `multirow` / `makecell` از قبل بارگذاری شده‌اند.

---

## ۹. رابطه

```latex
\begin{equation}
  E = mc^2
  \label{eq:energy}
\end{equation}
```

رابطه از حاشیه چپ و شماره از راست است. پارامترها را در متن بعد از رابطه توضیح دهید.

---

## ۱۰. کد برنامه‌نویسی

سبک پیش‌فرض `bonabpython` است (رنگ‌آمیزی پایتون). برای شبه‌کد بدون زبان:

```latex
\begin{lstlisting}[style=bonabcode,caption={...},label={lst:...}]
```

سبک‌ها در `config/style.tex` تعریف شده‌اند: `bonabcode` و `bonabpython`.

---

## ۱۱. تعریف، قضیه، مثال

```latex
\begin{definition}[وضعیت شارژ]
متن تعریف.
\end{definition}

\begin{theorem}
حکم.
\end{theorem}
\begin{proof}
برهان.
\end{proof}
```

شماره با شمارندهٔ تعریف و به‌صورت فصل‌محور است.

---

## ۱۲. نمودار TikZ

در `config/style.tex` سه سبک کمکی هست: `block`، `loss`، `flow`. نمونه در فصل روش‌شناسی. متن لاتین داخل گره را با `\lr{...}` بنویسید.

---

## ۱۳. منابع

ورود در `references.bib`:

```bibtex
@article{key2024,
  author  = {First Author and Second Author},
  title   = {Title},
  journal = {Journal Name},
  year    = {2024},
  doi     = {10.0000/example}
}
```

سبک IEEE است، ترتیب ظهور در متن (`sorting=none`). DOI و URL چاپ می‌شوند. فهرست منابع داخل محیط `latin` است تا عنوان انگلیسی مربع نشود.

کلید منبع را در متن فارسی فقط با `\pcite{key2024}` صدا بزنید.

---

## ۱۴. صفحات آغازین و پایانی

ترتیب ثابت `main.tex` مطابق دستورالعمل:

1. بسم الله (بدون شماره)
2. عنوان فارسی (بدون شماره)
3. تقدیم، سپاس، چکیده فارسی، علائم (حروف فارسی)
4. فهرست مطالب، شکل، جدول، کد
5. فصل‌ها از صفحه ۱
6. پیوست
7. منابع
8. چکیده انگلیسی و عنوان انگلیسی (بدون شماره)

چکیده فارسی حداکثر ۵۰۰ واژه. چکیده انگلیسی باید هم‌معنا باشد نه ترجمه واژه‌به‌واژهٔ درهم.

---

## ۱۵. قلم‌ها

ترتیب در `config/fonts.tex`:

| نقش | اولویت |
|---|---|
| متن فارسی | B Mitra → Amiri → FreeSerif |
| عنوان بخش | B Nazanin → Amiri → FreeSerif |
| عنوان فصل | B Titr → Amiri → FreeSerif |
| لاتین | Times New Roman → TeX Gyre Termes |
| ارقام و ریاضی | Amiri → FreeSerif → DejaVu Sans |

B Mitra را `digitfont` نکنید. اگر TeX Live کامل نباشد قالب به قلم آزاد برمی‌گردد؛ مربع‌های لاتین در آن حالت کمتر دیده می‌شوند ولی باید همان `\lr` و `\pcite` را رعایت کنید تا روی سیستم دانشگاه (با B Mitra) خراب نشود.

---

## ۱۶. شماره‌گذاری

پس از `\begin{document}` فرمان `\ApplyBonabNumbering` اجرا می‌شود. خروجی چاپی:

- بخش: `۱-۲` یعنی بخش ۲ از فصل ۱
- شکل، جدول، رابطه، تعریف، کد: همین الگو

صفحات مقدماتی حرفی فارسی‌اند (`الف`، `ب`، ...). متن اصلی از ۱. دو صفحه نخست و صفحات انگلیسی پایانی شماره ندارند.

---

## ۱۷. شروع پروژهٔ جدید از این قالب

1. پوشه را کپی کنید؛ تاریخچه Git را لازم ندارید مگر بخواهید.
2. `config/metadata.tex` را پر کنید.
3. `frontmatter/abstract-fa.tex` و `abstract-en.tex` را بنویسید.
4. `frontmatter/dedication.tex` و `acknowledgements.tex` را شخصی کنید.
5. `frontmatter/symbols.tex` را با نمادهای خودتان عوض کنید.
6. فصل‌ها را بازنویسی کنید؛ برچسب‌ها را یکتا نگه دارید.
7. پیوست‌های نامربوط را حذف یا `\IncludeAppendixfalse` کنید.
8. `references.bib` را خالی و دوباره پر کنید.
9. شکل‌های قبلی را از `assets/` بردارید؛ `logo.pdf` بماند.
10. از نو `./build.sh` یا Recompile from scratch.

---

## ۱۸. خطاهای رایج

| پدیده | علت | کار |
|---|---|---|
| مربع به‌جای واژه انگلیسی | لاتین بیرون از `\lr` یا عنوان انگلیسی با B Titr | `\lr` یا محیط `latin` |
| مربع به‌جای ارجاع | `\cite` در فارسی یا اجرا نشدن Biber | `\pcite` و اسکریپت build |
| مربع به‌جای درصد/اعشار | `٪` و `٫` عربی | `$7.1$ درصد` |
| `؟؟` در ارجاع | برچسب نیست یا یک‌بار کامپایل | برچسب را چک کنید؛ کامل build کنید |
| فهرست خالی | یک‌بار XeLaTeX | Biber + دو بار XeLaTeX |
| صفحه خالی فهرست شکل | هیچ شکلی نیست و کلید true است | `\IncludeListOfFiguresfalse` |
| استاد مشاور خالی ولی خط خالی | فاصله داخل آکولاد | `\newcommand{\AdvisorNameFa}{}` |
| پیوست خاموش و `؟؟` | `\ref{app:...}` در فصل مانده | ارجاع را حذف کنید |
| خطای B Mitra و U+066A | `digitfont` اشتباه یا فایل قدیمی | همین `config/fonts.tex` |
| کامپایلر pdfLaTeX | موتور غلط | XeLaTeX |

---

## ۱۹. کنترل پیش از تحویل

- PDF از ابتدا با XeLaTeX و Biber ساخته شده باشد.
- هیچ مربع، `؟؟` یا کلید خام منبع نباشد.
- فهرست‌ها با متن یکی باشند.
- هر شکل و جدول در متن ارجاع شده باشد.
- اعداد و نمودارها واقعی باشند.
- چکیده فارسی و انگلیسی هم‌معنا باشند.
- کلیدواژه ۵ تا ۱۰ مورد باشد.
- اگر فهرست کد خالی است کلیدش خاموش باشد.
- نسخه چاپی (رنگ جلد، صحافی، صفحه سفید پس از جلد) با گروه آموزشی هماهنگ شود. این موارد در PDF نیستند.

---

## ۲۰. تصمیم‌های فنی قالب (برای تغییر ندادن بی‌دلیل)

- کلاس `report` با `oneside` و `fleqn`.
- زی‌پرشین آخرین بسته است؛ `hyperref` قبل از آن.
- منابع BibLaTeX/Biber با سبک IEEE.
- به‌جای `fancyhdr` از سبک `plain` استفاده می‌شود تا با bidi تداخل نکند.
- `\pcite` برابر `\lr{\cite{...}}` است.
- شمارندهٔ کد هم فصل‌محور است، مثل شکل و جدول.
- فراداده PDF از عنوان انگلیسی، نام دانشجو، مدرک و `\KeywordsEn` پر می‌شود.
