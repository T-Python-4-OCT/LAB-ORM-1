from django.db import models


class Post(models.Model):

    class Rating(models.IntegerChoices):
        UNRATED = 0, "Not Rated"
        ONE = 1, "Poor"
        TWO = 2, "Fair"
        THREE = 3, "Good"
        FOUR = 4, "Very Good"
        FIVE = 5, "Excellent"

    title = models.CharField(max_length=2048)

    content = models.TextField()

    is_published = models.BooleanField(default=True)

    published_at = models.DateTimeField(auto_now_add=True)

    poster = models.ImageField(
        upload_to="images/",
        default="images/default.jpg"
    )

    rating = models.IntegerField(
        choices=Rating.choices,
        default=Rating.UNRATED
    )

    def __str__(self):
        return self.title

class Review(models.Model):

    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    name = models.CharField(max_length=1024)

    rating = models.SmallIntegerField()

    comment = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)