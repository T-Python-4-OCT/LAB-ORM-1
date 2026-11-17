from pathlib import Path
from zipfile import BadZipFile, ZipFile

from django import forms
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from PIL import Image, UnidentifiedImageError

from .models import Post, PostMedia

ALLOWED_EXTENSIONS = {
    PostMedia.MediaType.IMAGE: {
        ".jpg", ".jpeg", ".png", ".webp", ".gif"
    },
    PostMedia.MediaType.VIDEO: {
        ".mp4", ".webm"
    },
    PostMedia.MediaType.DOCUMENT: {
        ".pdf", ".docx", ".txt"
    },
}

MAX_FILE_SIZE = {
    PostMedia.MediaType.IMAGE: 10 * 1024 * 1024,
    PostMedia.MediaType.VIDEO: 100 * 1024 * 1024,
    PostMedia.MediaType.DOCUMENT: 15 * 1024 * 1024,
}

MAX_ATTACHMENTS_PER_POST = 30


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        if not data:
            return []

        if not isinstance(data, (list, tuple)):
            data = [data]

        parent_clean = super().clean

        return [
            parent_clean(item, initial)
            for item in data
        ]


def detect_media_type(uploaded_file):
    extension = Path(uploaded_file.name).suffix.lower()

    for media_type, extensions in ALLOWED_EXTENSIONS.items():
        if extension in extensions:
            return media_type

    raise forms.ValidationError(
        f"{uploaded_file.name}: Unsupported file type. "
        "Use images (JPG, PNG, WEBP, GIF), "
        "videos (MP4, WEBM), or documents (PDF, DOCX, TXT)."
    )


def validate_media_file(uploaded_file):
    media_type = detect_media_type(uploaded_file)

    if uploaded_file.size > MAX_FILE_SIZE[media_type]:
        limit_mb = MAX_FILE_SIZE[media_type] // (1024 * 1024)

        raise forms.ValidationError(
            f"{uploaded_file.name}: File exceeds "
            f"the {limit_mb} MB limit."
        )

    try:
        uploaded_file.seek(0)

        if media_type == PostMedia.MediaType.IMAGE:
            with Image.open(uploaded_file) as image:
                image.verify()

        else:
            header = uploaded_file.read(16)
            extension = Path(uploaded_file.name).suffix.lower()

            if extension == ".pdf":
                if not header.startswith(b"%PDF-"):
                    raise forms.ValidationError(
                        f"{uploaded_file.name}: Invalid PDF file."
                    )

            if extension == ".mp4":
                if header[4:8] != b"ftyp":
                    raise forms.ValidationError(
                        f"{uploaded_file.name}: Invalid MP4 file."
                    )

            if extension == ".webm":
                if not header.startswith(b"\x1a\x45\xdf\xa3"):
                    raise forms.ValidationError(
                        f"{uploaded_file.name}: Invalid WEBM file."
                    )

            if extension == ".docx":
                uploaded_file.seek(0)

                with ZipFile(uploaded_file) as docx:
                    if "word/document.xml" not in docx.namelist():
                        raise forms.ValidationError(
                            f"{uploaded_file.name}: Invalid DOCX file."
                        )

    except (
        UnidentifiedImageError,
        OSError,
        ValueError,
        BadZipFile
    ) as error:
        raise forms.ValidationError(
            f"{uploaded_file.name}: This file appears damaged "
            "or does not match its extension."
        ) from error

    finally:
        uploaded_file.seek(0)

    return media_type


class PostForm(forms.ModelForm):

    media_files = MultipleFileField(
        required=False,
        label="Images, videos and documents",
        help_text=(
            "Select multiple files. Images up to 10 MB, "
            "videos 100 MB, documents 15 MB each; "
            "maximum 30 attachments per post."
        ),
        widget=MultipleFileInput(
            attrs={
                "accept": (
                    ".jpg,.jpeg,.png,.webp,.gif,"
                    ".mp4,.webm,.pdf,.docx,.txt"
                )
            }
        ),
    )

    class Meta:
        model = Post

        fields = [
            "title",
            "content",
            "cover_image",
        ]

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "placeholder": "Enter post title"
                }
            ),

            "content": forms.Textarea(
                attrs={
                    "placeholder": "Write your post...",
                    "rows": 8
                }
            ),

            "cover_image": forms.ClearableFileInput(
                attrs={
                    "accept": (
                        ".jpg,.jpeg,.png,.webp,.gif"
                    )
                }
            ),
        }

    def clean_cover_image(self):
        cover = self.cleaned_data.get("cover_image")

        if cover and hasattr(cover, "size"):
            max_size = 10 * 1024 * 1024

            if cover.size > max_size:
                raise forms.ValidationError(
                    "Cover image must be 10 MB or smaller."
                )

        return cover

    def clean_media_files(self):
        uploaded_files = self.cleaned_data.get(
            "media_files", []
        )

        if len(uploaded_files) > MAX_ATTACHMENTS_PER_POST:
            raise forms.ValidationError(
                "You can upload at most 30 files at once."
            )

        for uploaded_file in uploaded_files:
            validate_media_file(uploaded_file)

        return uploaded_files


def save_attachments(post, uploaded_files):

    for uploaded_file in uploaded_files:
        PostMedia.objects.create(
            post=post,
            file=uploaded_file,
            media_type=detect_media_type(uploaded_file),
            original_name=Path(uploaded_file.name).name[:255],
        )


def home(request):

    posts = Post.objects.filter(
        is_published=True
    ).order_by("-published_at", "-id")

    return render(
        request,
        "blog/home.html",
        {"posts": posts}
    )


def create_post(request):

    if request.method == "POST":
        form = PostForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            with transaction.atomic():

                post = form.save()

                save_attachments(
                    post,
                    form.cleaned_data["media_files"]
                )

            return redirect(
                "post_detail",
                pk=post.pk
            )

    else:
        form = PostForm()

    return render(
        request,
        "blog/create_post.html",
        {"form": form}
    )


def post_detail(request, pk):

    post = get_object_or_404(
        Post,
        pk=pk
    )

    attachments = list(post.media.all())

    images = [
        item for item in attachments
        if item.media_type == PostMedia.MediaType.IMAGE
    ]

    videos = [
        item for item in attachments
        if item.media_type == PostMedia.MediaType.VIDEO
    ]

    documents = [
        item for item in attachments
        if item.media_type == PostMedia.MediaType.DOCUMENT
    ]

    return render(
        request,
        "blog/post_detail.html",
        {
            "post": post,
            "images": images,
            "videos": videos,
            "documents": documents,
        }
    )


def update_post(request, pk):

    post = get_object_or_404(
        Post,
        pk=pk
    )

    if request.method == "POST":

        form = PostForm(
            request.POST,
            request.FILES,
            instance=post
        )

        if form.is_valid():

            selected_ids = request.POST.getlist("remove_media")

            try:
                remove_ids = {
                    int(value)
                    for value in selected_ids
                }

                if any(value <= 0 for value in remove_ids):
                    raise ValueError

            except (ValueError, TypeError):
                remove_ids = set()

                form.add_error(
                    None,
                    "Invalid attachment selection."
                )

            existing_ids = set(
                post.media.values_list(
                    "pk",
                    flat=True
                )
            )

            if not remove_ids.issubset(existing_ids):
                form.add_error(
                    None,
                    "One or more selected attachments "
                    "do not belong to this post."
                )

            new_files = form.cleaned_data["media_files"]

            final_count = (
                len(existing_ids)
                - len(remove_ids)
                + len(new_files)
            )

            if final_count > MAX_ATTACHMENTS_PER_POST:
                form.add_error(
                    "media_files",
                    f"A post may have at most "
                    f"{MAX_ATTACHMENTS_PER_POST} attachments."
                )

            if not form.errors:

                with transaction.atomic():

                    form.save()

                    if remove_ids:
                        post.media.filter(
                            pk__in=remove_ids
                        ).delete()

                    save_attachments(
                        post,
                        new_files
                    )

                return redirect(
                    "post_detail",
                    pk=post.pk
                )

    else:
        form = PostForm(instance=post)

    return render(
        request,
        "blog/update_post.html",
        {
            "form": form,
            "post": post,
            "attachments": post.media.all(),
        }
    )

@require_POST
def delete_post(request, pk):

    post = get_object_or_404(
        Post,
        pk=pk
    )

    post.delete()

    return redirect("home")
