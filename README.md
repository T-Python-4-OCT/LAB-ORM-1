# LAB-ORM-1

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

---

## How to Run

```bash
pip install django pillow
python manage.py migrate
python manage.py loaddata posts    # loads sample posts with their images
python manage.py runserver
```

Then open http://127.0.0.1:8000

## Features
- **Home page**: the latest 3 published posts (limiting with slicing `[0:3]`) with cover image, category, title, content preview, date & time.
- **All posts page**: filter by category and order by newest / oldest / title, with the results count.
- **Search page**: search posts by title or content (min 3 characters), order the results, and show the results count.
- **Add post**: built with a `ModelForm` (`PostForm`) with validation; optional cover image (a default image is used otherwise).
- **Post detail page**: full post with its image and category.
- **Update post**: same `ModelForm`; edit title, content, category, publish status, and replace the image.
- **Delete post**: with a confirmation dialog (POST request + CSRF protection).
- **Category choices**: `Post.Category` (`TextChoices`): General, Technology, Sports, Lifestyle.
- Templates inheritance (`base.html` + reusable partials), static files (CSS, logo), media files (uploaded images), and dynamic URL resolving with `{% url %}`.

## Run the tests
```bash
python manage.py test main
```
