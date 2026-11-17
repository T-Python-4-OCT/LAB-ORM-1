from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
import zipfile
from unittest.mock import patch
from PIL import Image
from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from blog.models import Post
from blog.test_crud import DATA
from .upload_validators import validate_upload
from .models import PostAttachment

def image_file(name='image.png'):
    data=BytesIO();Image.new('RGB',(12,12)).save(data,format='PNG')
    return SimpleUploadedFile(name,data.getvalue(),content_type='image/png')
def office(ext):
    data=BytesIO()
    with zipfile.ZipFile(data,'w') as z:
        part={'docx':'word/document.xml','xlsx':'xl/workbook.xml','pptx':'ppt/presentation.xml'}[ext]
        kind={'docx':'wordprocessingml.document','xlsx':'spreadsheetml.sheet','pptx':'presentationml.presentation'}[ext]
        z.writestr('[Content_Types].xml',f'<Types><Override PartName="/{part}" ContentType="application/vnd.openxmlformats-officedocument.{kind}.main+xml"/></Types>')
        z.writestr({'docx':'word/document.xml','xlsx':'xl/workbook.xml','pptx':'ppt/presentation.xml'}[ext],'<document/>')
    return SimpleUploadedFile('file.'+ext,data.getvalue())

class MediaTests(TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory()
        self.override=override_settings(MEDIA_ROOT=self.temp.name)
        self.override.enable()
        self.addCleanup(self.temp.cleanup);self.addCleanup(self.override.disable)
        self.user=get_user_model().objects.create_user('owner')
        self.other=get_user_model().objects.create_user('other')
        self.post=Post.objects.create(**DATA,owner=self.user)
        self.client.force_login(self.user)
    def test_supported_types(self):
        uploads=[image_file(),SimpleUploadedFile('a.pdf',b'%PDF-1.4\n%%EOF'),SimpleUploadedFile('a.txt','نص عربي'.encode())]+[office(ext) for ext in ['docx','xlsx','pptx']]
        for file in uploads:self.assertTrue(validate_upload(file))
        for ext,fmt in [('jpg','JPEG'),('webp','WEBP'),('gif','GIF')]:
            stream=BytesIO();Image.new('RGB',(2,2)).save(stream,fmt)
            self.assertTrue(validate_upload(SimpleUploadedFile('a.'+ext,stream.getvalue())))
    def test_unsafe_and_mismatch(self):
        for name,data in [('a.exe',b'MZ'),('a.js',b'alert(1)'),('a.html',b'<html>'),('a.svg',b'<svg/>'),('a.cmd',b'echo'),('a.jpg',b'not image'),('a.pdf',b'not pdf'),('a.txt',b'\x00binary')]:
            with self.assertRaises(ValidationError):validate_upload(SimpleUploadedFile(name,data))
    @override_settings(MAX_ATTACHMENT_SIZE=10)
    def test_oversize(self):
        with self.assertRaises(ValidationError):validate_upload(SimpleUploadedFile('a.txt',b'x'*11))
    def test_multiple_and_featured(self):
        response=self.client.post('/add/',{**DATA,'attachments':[image_file(),SimpleUploadedFile('a.txt',b'text')],'feature_new':'on'})
        self.assertEqual(response.status_code,302)
        post=Post.objects.latest('pk')
        self.assertEqual(post.attachments.count(),2)
        item=post.attachments.get(is_featured=True)
        self.assertTrue(post.get_image_url().startswith('/media/'))
        response=self.client.get(post.get_image_url())
        self.assertEqual(response.status_code,200);response.close()
        self.assertNotIn('image.png',item.file.name)
    def test_invalid_upload_does_not_create_post(self):
        response=self.client.post('/add/',{**DATA,'attachments':[SimpleUploadedFile('bad.exe',b'MZ')]})
        self.assertEqual(response.status_code,200)
        self.assertEqual(Post.objects.count(),1)
    def test_count_limit(self):
        response=self.client.post('/add/',{**DATA,'attachments':[SimpleUploadedFile(f'{i}.txt',b'text') for i in range(6)]})
        self.assertEqual(response.status_code,200)
        self.assertEqual(Post.objects.count(),1)
    def attach(self,post=None):
        return PostAttachment.objects.create(post=post or self.post,file=image_file(),original_filename='image.png',file_type='image/png')
    def test_removal_commit_and_unrelated_files(self):
        item=self.attach();other=self.attach()
        path=Path(item.file.path);other_path=Path(other.file.path)
        with self.captureOnCommitCallbacks(execute=True):
            response=self.client.post(f'/post/{self.post.pk}/edit/',{**DATA,'remove_attachments':[item.pk]})
        self.assertEqual(response.status_code,302)
        self.assertFalse(path.exists());self.assertTrue(other_path.exists())
        self.assertTrue(Post.objects.filter(pk=self.post.pk).exists())
    def test_cannot_remove_other_article_attachment(self):
        other=Post.objects.create(**DATA,owner=self.other)
        item=self.attach(other)
        response=self.client.post(f'/post/{self.post.pk}/edit/',{**DATA,'remove_attachments':[item.pk]})
        self.assertEqual(response.status_code,200)
        self.assertTrue(PostAttachment.objects.filter(pk=item.pk).exists())
        self.assertEqual(self.client.post(f'/post/{other.pk}/edit/',{**DATA,'remove_attachments':[item.pk]}).status_code,302)
    def test_draft_media_and_safe_headers(self):
        item=self.attach()
        response=self.client.get(f'/media/{item.pk}/')
        self.assertEqual(response['X-Content-Type-Options'],'nosniff');response.close()
        self.post.is_published=False;self.post.save()
        self.client.logout()
        self.assertEqual(self.client.get(f'/media/{item.pk}/').status_code,404)
    def test_delete_post_cleanup(self):
        item=self.attach();path=Path(item.file.path)
        with self.captureOnCommitCallbacks(execute=True):self.client.post(f'/post/{self.post.pk}/delete/')
        self.assertFalse(path.exists())
    def test_storage_failure_rolls_back(self):
        with patch('django.core.files.storage.FileSystemStorage._save',side_effect=OSError('disk failure')):
            response=self.client.post('/add/',{**DATA,'attachments':[image_file()]})
        self.assertEqual(response.status_code,200)
        self.assertEqual(Post.objects.count(),1)
        self.assertEqual(PostAttachment.objects.count(),0)
    def test_partial_write_cleanup(self):
        from django.core.files.storage import FileSystemStorage
        original=FileSystemStorage._save
        counter=[0]
        def fail_second(storage,name,content):
            counter[0]+=1
            if counter[0] == 2:raise OSError('second write failed')
            return original(storage,name,content)
        with patch.object(FileSystemStorage,'_save',fail_second):
            response=self.client.post('/add/',{**DATA,'attachments':[image_file(),SimpleUploadedFile('a.txt',b'different text')]})
        self.assertEqual(response.status_code,200)
        self.assertEqual(Post.objects.count(),1)
        self.assertFalse(any(p.is_file() for p in Path(self.temp.name).rglob('*')))
    def test_rollback_keeps_deleted_files(self):
        from django.db import transaction
        item=self.attach();path=Path(item.file.path)
        with self.captureOnCommitCallbacks(execute=True):
            try:
                with transaction.atomic():
                    item.delete()
                    raise RuntimeError('rollback')
            except RuntimeError:pass
        self.assertTrue(path.exists())
        self.assertTrue(PostAttachment.objects.exists())
    def test_duplicate_selection(self):
        response=self.client.post('/add/',{**DATA,'attachments':[image_file('a.png'),image_file('b.png')]})
        self.assertEqual(response.status_code,200)
        self.assertEqual(Post.objects.count(),1)
    def test_office_unsafe_archive(self):
        stream=BytesIO()
        with zipfile.ZipFile(stream,'w') as z:z.writestr('../escape.txt','text')
        with self.assertRaises(ValidationError):validate_upload(SimpleUploadedFile('a.docx',stream.getvalue()))
    def test_total_count_on_edit(self):
        for _ in range(5):self.attach()
        response=self.client.post(f'/post/{self.post.pk}/edit/',{**DATA,'attachments':[SimpleUploadedFile('a.txt',b'text')]})
        self.assertEqual(response.status_code,200)
        self.assertEqual(self.post.attachments.count(),5)

    def test_storage_folders(self):
        from .models import upload_path
        for filename,folder in [('a.png','images/'),('a.pdf','pdf/'),('a.docx','documents/')]:
            self.assertTrue(upload_path(None,filename).startswith(folder))

    def test_image_automatically_used_as_cover(self):
        response=self.client.post('/add/',{**DATA,'attachments':[image_file()]})
        self.assertEqual(response.status_code,302)
        post=Post.objects.latest('pk')
        item=post.attachments.get()
        self.assertEqual(post.get_image_url(),f'/media/{item.pk}/')
        self.assertTrue(item.is_featured)
    def test_replace_cover_and_remove_old(self):
        old=self.attach();old.is_featured=True;old.save()
        response=self.client.get(f'/post/{self.post.pk}/edit/')
        self.assertContains(response,'name="remove_attachments"')
        with self.captureOnCommitCallbacks(execute=True):
            response=self.client.post(f'/post/{self.post.pk}/edit/',{**DATA,'remove_attachments':[old.pk],'attachments':[image_file('replacement.png')]})
        self.assertEqual(response.status_code,302)
        self.assertFalse(PostAttachment.objects.filter(pk=old.pk).exists())
        remaining=self.post.attachments.get()
        self.assertTrue(remaining.is_featured)
        self.assertEqual(self.post.get_image_url(),f'/media/{remaining.pk}/')
