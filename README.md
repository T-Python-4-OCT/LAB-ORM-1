# SIYAQ | سِياق

## 1. Project Overview

SIYAQ is an Arabic-only Django article publishing application based on LAB-ORM-1. It uses server-rendered templates, SQLite and Django storage. `FREEZE_REPORT.md` contains the audit evidence and compliance matrix.

## 2. Original LAB-ORM-1 Requirements

The required Post fields retain their exact definitions:

```python
title = models.CharField(max_length=2048)
content = models.TextField()
is_published = models.BooleanField(default=True)
published_at = models.DateTimeField(auto_now_add=True)
```

The homepage retrieves published articles through the ORM and displays publisher, title, excerpt, publication date/time and detail links, newest first. Creation handles GET/POST, CSRF, validation, SQLite persistence and a success redirect. Publication time is automatic and cannot be changed through editing.

## 3. Additional SIYAQ Features

Publisher validation, editing/deletion, a separate article archive, search/sorting, multiple attachments, uploaded-image covers, attachment removal, persistent dark/light themes, responsive layouts and reduced-motion support extend the assignment.

## 4. Technology Stack

Verified environment: Windows, Python 3.14.8, Django 6.1.3, Pillow 12.3.0 and SQLite. Runtime dependencies are pinned; no frontend framework or external authentication package is required.

## 5. Project Structure

```text
LAB-ORM-1/
  blog/
    models.py, forms.py, views.py, urls.py, admin.py
    upload_forms.py, upload_validators.py, attachment_services.py, signals.py
    migrations/, templates/, static/, templatetags/, test_*.py, tests.py
  blogger_project/
    settings.py, urls.py, asgi.py, wsgi.py
  media/
    images/, pdf/, documents/
  manage.py
  requirements.txt
  README.md
  FREEZE_REPORT.md
```

Attachment management is intentionally integrated into `blog`. The former `media_library` application was merged at the owner's request. There is one active application for articles and their attachments, and one upload storage directory. Historical migration replacement metadata is retained.

## 6. Installation

Open PowerShell in the single folder containing `manage.py`. Use Python 3.14 for the verified environment. Do not create a nested project copy.

## 7. Virtual Environment Setup

For a fresh checkout only:

```powershell
py -3.14 -m venv .venv
```

Reuse an existing working `.venv`. Commands below call its interpreter directly without requiring activation.

## 8. Requirements Installation

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
```

Pinned packages: Django, asgiref, sqlparse, tzdata and Pillow. `polib` is no longer needed after removing obsolete translation catalogs. Installed dependency resolution and compatibility were verified; a separate clean-machine installation was not performed.

## 9. Database Configuration

SQLite uses `BASE_DIR / "db.sqlite3"`. Existing local data is preserved. SQLite and user uploads are ignored by Git to avoid publishing account records or private files. A fresh checkout starts empty after migration; create demonstration articles at `/add/`. Review local demonstration data before submitting it separately.

`TIME_ZONE = "Asia/Riyadh"` and `USE_TZ = True`. UTC storage is converted to Riyadh for display. `published_at` is the sole article timestamp and is generated automatically.

## 10. Models and Relationships

`Post` adds `publisher_name` and a nullable Django User foreign key to the required fields. No ownership is guessed for legacy records. `PostAttachment` belongs to Post with CASCADE and stores a file reference, safe display filename, validated MIME type, upload timestamp and featured flag. A database constraint allows one featured attachment per article. File bytes are stored on disk, not in SQLite.

## 11. Django ORM Implementation

`views.py` uses `filter`, `Q`, `order_by`, `prefetch_related` and object lookup. ModelForms and `attachment_services.py` create/update records in transactions. Published-only filtering happens server-side; attachment retrieval uses `select_related` for its parent.

## 12. Migrations

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py showmigrations
.\.venv\Scripts\python.exe manage.py migrate --plan
.\.venv\Scripts\python.exe manage.py makemigrations
.\.venv\Scripts\python.exe manage.py sqlmigrate blog 0009
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
```

`makemigrations` records legitimate changes; no changes is valid. `migrate` applies changes, `showmigrations` lists their state, and `sqlmigrate` previews SQL. Back up SQLite first. Never reset the database, fake migrations or delete migration history.

Migration 0004 preserved distinct Arabic translation text before removing the translation model. Migrations 0005/0006 record the previous date implementation. Migration 0007 adopts the historical media migration through replacement metadata; 0008 transfers its existing table into `blog`. Migration 0009 restores the assignment's automatic timestamp without changing existing values.

## 13. Apps and Views

`blog` owns public pages, articles and attachments; `blogger_project` owns settings and root routing. Django's admin, authentication, sessions, contenttypes, messages and staticfiles remain registered. No separate media application is currently installed.

## 14. MVT Architecture

Models define records and relationships; views process requests through the ORM; templates render HTML. Forms validate articles, upload validators inspect content, and the attachment service coordinates storage and database transactions.

## 15. Templates and Inheritance

Public pages extend `blog/base.html` for a shared Arabic RTL document, header, footer, theme control and messages. `actions.html` is reused inside details. Django escaping remains enabled. CSS preserves article paragraphs; user input is not rendered as executable HTML.

## 16. Static Files

Templates use Django's `static` tag for CSS/JavaScript. Fallback covers remain in `blog/static/blog/img/posts/`. The neutral default is an application-owned SVG; user SVG uploads are prohibited. Google Fonts supplies Alexandria, Cairo and IBM Plex Sans Arabic with system fallbacks.

## 17. Media Uploads

`MEDIA_ROOT = BASE_DIR / "media"` and `MEDIA_URL = "/media/"`. UUID filenames are stored under `images/`, `pdf/` or `documents/`. Approved types: JPG/JPEG, PNG, WEBP, GIF, PDF, UTF-8 TXT, DOCX, XLSX and PPTX. Defaults: 10 MiB per file and five total attachments per article, configurable in settings.

Multipart forms read `request.FILES`. Pillow verifies images and dimensions. Validators inspect PDF header/end markers, UTF-8 text and Office ZIP structure, content types, expansion limits, compression ratios and XML. Executables, scripts, HTML, SVG, macro-enabled formats and extension/content mismatches are rejected. These checks are not antivirus scanning or full document sanitization.

The first newly uploaded image becomes the cover. Existing files can be removed during editing. Failed transactions clean new files; deleted records schedule storage cleanup after commit. Cleanup failures are logged and may require manual attention. Tests use temporary storage.

## 18. Article CRUD

Creation/editing redirect to `/home/`. Consecutive duplicate create requests from the same session are detected using normalized form/file fingerprints. This is local retry protection, not distributed exactly-once processing. Editing preserves article identity and publication time. Deletion uses a confirmation dialog and CSRF-protected POST; GET never deletes.

## 19. Authentication and Permissions

**During the final audit, the owner explicitly selected public management:** any visitor may edit/delete any published article without login. This supersedes the earlier owner-only checklist. Publisher names do not prove ownership. Existing account/owner metadata is retained for data preservation and administration, not as a public editing restriction. Anonymous publishing remains supported. Public draft routes return 404. Django Admin requires authentication and standard permissions.

This policy intentionally permits shared editing/deletion. It is not an owner-private production service. There are no public login/logout/signup routes.

## 20. Form Validation

Publisher, title and content are required on the server and in HTML. Names support Unicode letters and normal separators, reject digits, and require 2–150 characters. Titles require written text, at least five characters and at most 2048. Content requires letters and at least 30 non-whitespace characters. Django form fields trim surrounding whitespace. Attachments are optional. Errors are Arabic and invalid submissions create no records.

## 21. Cookies and Theme Preferences

POST `/theme/light/` or `/theme/dark/` stores a validated 30-day `theme` cookie with SameSite=Lax. Redirect targets must match the current host. The context processor validates cookie values; both themes cover forms, dialogs, media and footer.

## 22. Path Parameters

Detail/edit/delete routes use integer `post_id`; media uses integer `attachment_id`. Missing records return 404. Removal choices are scoped to the article being edited, preventing removal of unrelated attachments through that form.

## 23. Query Parameters

`search` filters title/content and `sort=latest|oldest` controls order. They combine on `/home/` and `/articles/`. GET forms encode parameters safely. Default ordering uses newest publication timestamp and ID.

## 24. URL Mapping and Resolving

| Route | Behavior |
| --- | --- |
| `/` | Redirect to `/home/` |
| `/home/` | Two-column homepage |
| `/articles/` | Separate archive with excerpts |
| `/about/` | About SIYAQ |
| `/add/` | Create article |
| `/post/<post_id>/` | Article details |
| `/post/<post_id>/edit/` | Edit published article |
| `/post/<post_id>/delete/` | GET redirects to details; POST deletes |
| `/media/<attachment_id>/` | Validated file response |
| `/theme/<mode>/` | POST theme preference |
| `/admin/` | Django Admin |

Named routes use the `blog` namespace. Historical `/ar/` and `/en/` public links redirect safely; no language-switching endpoint remains.

## 25. Arabic-Only Interface

Public pages use `lang="ar" dir="rtl"`. Middleware activates Arabic independently of old language cookies and clears those cookies. Django's Arabic catalog remains enabled. English date formatting is an explicit display preference. User-authored English articles are preserved.

## 26. Django Admin

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser
```

Post Admin provides search, filters and owner metadata. Attachment Admin lists records and supports deletion; file metadata is read-only, and uploads use the validated article workflow. Credentials are not included in source or documentation.

## 27. Testing

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe -m pip check
```

The suite contains 61 tests covering fields, CRUD, automatic timestamps, public management policy, drafts, CSRF, validation, duplicate retries, URL resolution, RTL templates, search/sort, themes, uploads, file rejection, covers, attachment scoping, transaction cleanup and migration preservation. Tests never use the real upload directory.

## 28. Running the Server

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

Open `http://127.0.0.1:8000/home/`. DEBUG and the development server are for local coursework. Internet deployment requires production hosting, allowed hosts, HTTPS, secure cookies and an appropriate authorization policy. Supply `DJANGO_SECRET_KEY` through the environment; local development generates an ignored `.local_secret` file.

## 29. Assignment Compliance

The required Post fields, automatic timestamp, published-only listing, excerpts/detail links, validated creation, CSRF, SQLite and redirects are implemented and tested. Apps/views, templates, staticfiles, MVT, routes, inheritance, cookies, parameters, ORM, relationships, migrations and forms map to exact files in `FREEZE_REPORT.md`.

## 30. Submission and Freeze Scope

The freeze covers the local university project with the latest explicit public-management policy and integrated attachment architecture. It does not certify unrestricted internet hosting. No commit or push is performed. Uncommitted work is preserved and verified SQLite/source backups remain outside the tracked project. See `FREEZE_REPORT.md` for executed checks, cleanup, limitations and status.
