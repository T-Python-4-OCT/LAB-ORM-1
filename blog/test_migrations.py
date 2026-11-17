from django.test import TransactionTestCase
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

class ArabicPreservationMigrationTests(TransactionTestCase):
    def test_original_and_unique_arabic_translation_preserved(self):
        executor=MigrationExecutor(connection)
        executor.migrate([('blog','0003_posttranslation')])
        old=executor.loader.project_state([('blog','0003_posttranslation')]).apps
        Post=old.get_model('blog','Post')
        Translation=old.get_model('blog','PostTranslation')
        post=Post.objects.create(title='Original English article',content='Original body stays intact.',publisher_name='John Smith')
        timestamp=post.published_at
        Translation.objects.create(post=post,language_code='ar',title='نص عربي فريد',content='محتوى عربي فريد محفوظ')
        Translation.objects.create(post=post,language_code='en',title='English translation',content='Translation')
        try:
            executor=MigrationExecutor(connection)
            executor.migrate(executor.loader.graph.leaf_nodes())
            apps=executor.loader.project_state(executor.loader.graph.leaf_nodes()).apps
            Current=apps.get_model('blog','Post')
            original=Current.objects.get(pk=post.pk)
            self.assertEqual(original.title,post.title)
            self.assertEqual(original.content,post.content)
            self.assertEqual(original.published_at,timestamp)
            self.assertIsNone(original.owner_id)
            copy=Current.objects.get(title='نص عربي فريد')
            self.assertEqual(copy.publisher_name,'John Smith')
            self.assertEqual(copy.published_at,timestamp)
            self.assertEqual(Current.objects.count(),2)
        finally:
            executor=MigrationExecutor(connection)
            executor.migrate(executor.loader.graph.leaf_nodes())
