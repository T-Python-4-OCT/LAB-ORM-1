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


## How to run

```bash
pip install -r requirements.txt
cd Blogger
python manage.py migrate
python manage.py loaddata sample_posts
python manage.py runserver
```

Then open http://127.0.0.1:8000

`loaddata sample_posts` adds the sample posts with their images (stored in `Blogger/media/posts/images/`), so the homepage shows real content right away.

### Features
- Homepage with the latest post as the cover story and the rest as cards.
- Add a post with an optional cover image (media upload with `ImageField`).
- Edit a post: change its text, replace or remove its image.
- Delete a post from a confirmation page (its image file is deleted too).
