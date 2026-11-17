# LAB-ORM-1

## Run Blogger locally

Requires Python 3.10 or newer.

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

Open http://127.0.0.1:8000/ to view published posts, or
http://127.0.0.1:8000/posts/new/ to add a post. Dates use Asia/Riyadh time.
Posts support an optional image. Use Edit post on a post card to update its
title, content, image, or publication status. Upload a new image to replace
the current image, or select Clear to remove it. Delete opens a confirmation
page; a post is deleted only after confirming. Uploaded images are stored in
`media/` and served by Django during local development.
Uncheck the publish option to save an unpublished post. To manage these posts,
run `manage.py createsuperuser` using the virtual environment's Python and visit
http://127.0.0.1:8000/admin/.

Run checks and tests:

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test
```

The default settings are for local development. For deployment, configure
`DJANGO_SECRET_KEY`, set `DJANGO_DEBUG=False`, and configure `ALLOWED_HOSTS`
for your domain.

## Original lab requirements

## Using what you learned , Create a Blog website called `Blogger` . Has the following pages:
- A homepage : displays the lates posts (Post title, content, date & time published) .
- A page to add new posts.


### To Acheive that, you need to create model `Post` , it should have the following attributes :
- title : char field (max 2048)
- content : text field.
- is_published : boolean field, default is True.
- published_at : datetime field, default is now. (use auto_now_add parameter)

### Design & Layout:
  - Make sure you use Templates & Templates inheritance to unify the look of the website.
  - Make sure to use static files if needed, and dynamic URL resolving when linking to your pages.
  - Generally use best practices (what you learned in previous lessons).
  - It is up to you how you design it. Use whatever means you need (colors, icons, logo, images, fonts, etc.) .
