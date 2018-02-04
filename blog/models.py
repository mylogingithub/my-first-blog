from django.db import models
from django.http import Http404
from django.utils import timezone
from django.contrib.auth.models import User


class Post(models.Model):
    author = models.ForeignKey('auth.User')
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(
            default=timezone.now)
    published_date = models.DateTimeField(
            blank=True, null=True)
    views = models.IntegerField(default=0)

    def add_view(self):
        self.views += 1
        self.save()

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def approved_comments(self):
        return self.comments.filter(approved_comment=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey('blog.Post', related_name='comments')
    author = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    approved_comment = models.BooleanField(default=False)

    def approve(self):
        self.approved_comment = True
        self.save()

    def __str__(self):
        return self.text


class Like(models.Model):
    post = models.ForeignKey('blog.Post', related_name='likes')
    author = models.ForeignKey('auth.User')
    created_date = models.DateTimeField(
        default=timezone.now)

    @staticmethod
    def count_of_likes(post):
        return Like.objects.filter(post=post).count()

    @staticmethod
    def is_like(post, current_user):
        like = list(Like.objects.filter(post=post))
        if like:
            author = like.pop().author
            if current_user == author:
                is_like = True
            else:
                is_like = False
        else:
            is_like = False
        return is_like

    @staticmethod
    def create_like_or_404(post, author):
        like = Like.objects.filter(post=post, author=author)
        if not list(like):
            like = Like.create(post, author)
            like.save()
        else:
            raise Http404()

    @staticmethod
    def delete_like_or_404(post, author):
        like = Like.objects.filter(post=post, author=author)
        if list(like):
            like.delete()
        else:
            raise Http404()

    @classmethod
    def create(cls, post, author):
        like = cls(post=post, author=author)
        return like
