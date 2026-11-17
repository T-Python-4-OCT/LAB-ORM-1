# LAB-ORM-1
# Blogger — Django Blogging Website

> **Blogger** is a Django-based blogging website developed as part of the university assignment **LAB-ORM-1**. The project demonstrates the use of Django ORM, Models, Views, URL Routing, HTML Templates, Template Inheritance, Static Files, and database migrations.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Features](#2-features)
3. [Technologies Used](#3-technologies-used)
4. [Project Directory Structure](#4-project-directory-structure)
5. [Installation & Setup](#5-installation--setup)
6. [Database & Migrations](#6-database--migrations)
7. [Running the Application](#7-running-the-application)
8. [Database Model & ORM](#8-database-model--orm)
9. [Website Pages](#9-website-pages)
10. [Course Requirements Compliance](#10-course-requirements-compliance)

---

## 1. Project Overview

Blogger is a simple blogging platform that allows users to create and publish blog posts.

The website provides a homepage to display the latest posts and a dedicated page to add new posts.

The project was developed using Django following the Model-View-Template (MVT) architecture.

---

## 2. Features

- **Homepage:** Displays the latest blog posts.
- **Add New Post:** Allows users to create new posts.
- **Post Title:** Supports titles up to 2048 characters.
- **Post Content:** Uses a text field to store post content.
- **Publication Status:** Users can choose between Published and Unpublished.
- **Publication Date:** Automatically records the date and time when a post is created.
- **Post Status Display:** Displays whether each post is Published or Unpublished.
- **Template Inheritance:** Uses a shared base template for consistent website layout.
- **Dynamic URL Resolving:** Uses Django URL names when navigating between pages.
- **Custom Styling:** Uses CSS static files to design the website.

---

## 3. Technologies Used

- **Python** — Programming Language.
- **Django** — Web Development Framework.
- **SQLite** — Relational Database.
- **HTML5** — Website Structure.
- **CSS3** — Website Styling.
- **Django ORM** — Database Operations.

---

## 4. Project Directory Structure

```text
Blogger/
│
├── Blogger/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── main/
│   ├── migrations/
│   ├── templates/
│   │   └── main/
│   │       ├── base.html
│   │       ├── home.html
│   │       └── add_post.html
│   │
│   ├── static/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── manage.py
├── db.sqlite3
└── README.md
```

---

## 5. Installation & Setup

### 1. Open the Project Directory

Navigate to the project root directory containing `manage.py`.

```powershell
cd Blogger
```

### 2. Create a Virtual Environment

```powershell
python -m venv venv
```

### 3. Activate the Virtual Environment (Windows PowerShell)

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install Django

```powershell
python -m pip install django
```

---

## 6. Database & Migrations

Create and apply database migrations:

```powershell
python manage.py makemigrations main
python manage.py migrate
```

To check migration status:

```powershell
python manage.py showmigrations
```

---

## 7. Running the Application

Start the Django development server:

```powershell
python manage.py runserver
```

Open your browser at:

```text
http://127.0.0.1:8000/
```

---

## 8. Database Model & ORM

### Post Model (`main/models.py`)

The project uses a Django model called `Post` to store blog posts.

```python
from django.db import models

class Post(models.Model):

    title = models.CharField(max_length=2048)

    content = models.TextField()

    is_published = models.BooleanField(default=True)

    published_at = models.DateTimeField(auto_now_add=True)
```

### Model Attributes

| Attribute | Field Type | Description |
|---|---|---|
| title | CharField | Stores the post title (maximum 2048 characters). |
| content | TextField | Stores the post content. |
| is_published | BooleanField | Determines whether the post is published. Default is True. |
| published_at | DateTimeField | Automatically stores the creation date and time. |

### Django ORM Usage

Retrieve all posts ordered by publication date:

```python
posts = Post.objects.all().order_by('-published_at')
```

Create a new post:

```python
Post.objects.create(
    title="My First Post",
    content="This is my first blog post.",
    is_published=True
)
```

---

## 9. Website Pages

### Homepage

The homepage displays blog posts with:

- Post Title
- Post Content
- Publication Date and Time
- Publication Status

Posts are ordered by the latest publication date.

### Add New Post

The Add Post page provides an HTML form that allows users to enter:

- Post Title
- Post Content
- Publication Status

The publication status is selected using a dropdown list:

- Published
- Unpublished

The form data is processed directly in the Django view using `request.POST`, without using a separate `forms.py` file.

---

## 10. Course Requirements Compliance

| Assignment Requirement | Implementation | Status |
|---|---|---|
| Django Project | Blogger | PASS |
| Homepage | `main/home.html` | PASS |
| Add New Posts Page | `main/add_post.html` | PASS |
| Post Model | `main/models.py` | PASS |
| CharField (2048) | title | PASS |
| TextField | content | PASS |
| BooleanField (default=True) | is_published | PASS |
| DateTimeField (auto_now_add=True) | published_at | PASS |
| Templates | HTML Templates | PASS |
| Template Inheritance | base.html | PASS |
| Static Files | CSS | PASS |
| Dynamic URL Resolving | Django URL Names | PASS |
| Django ORM | Database Operations | PASS |
| Database Migrations | Django Migrations | PASS |

---

**Assignment:** LAB-ORM-1  
**Project Name:** Blogger  
**Framework:** Django  
**Database:** SQLite