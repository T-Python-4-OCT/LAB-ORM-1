from django.db import migrations

def move_content_type(apps, schema_editor):
    ContentType=apps.get_model('contenttypes','ContentType')
    ContentType.objects.using(schema_editor.connection.alias).filter(app_label='media_library',model='postattachment').update(app_label='blog')

class Migration(migrations.Migration):
    dependencies=[('blog','0007_adopt_attachments'),('contenttypes','0002_remove_content_type_name')]
    operations=[migrations.AlterModelTable(name='postattachment',table=None),migrations.RunPython(move_content_type,migrations.RunPython.noop)]
