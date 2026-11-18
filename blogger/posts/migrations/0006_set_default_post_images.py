from django.db import migrations, models


def set_default_images(apps, schema_editor):
    Post = apps.get_model('posts', 'Post')
    Post.objects.using(schema_editor.connection.alias).filter(
        models.Q(image='') | models.Q(image__isnull=True),
    ).update(image='images/default.jpg')


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0005_alter_post_image'),
    ]

    operations = [
        migrations.RunPython(set_default_images, migrations.RunPython.noop),
    ]
