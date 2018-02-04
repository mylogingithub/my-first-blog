from django.shortcuts import render, redirect
from .models import Post, Comment, Like
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required

# Create your views here.

# def post_list(request):
#     return render(request, 'blog/post_list.html', {})


def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    return render(request, 'blog/post_list.html', {'posts': posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    is_like = Like.is_like(post, request.user)
    number_of_likes = Like.count_of_likes(post)
    post.add_view()
    number_of_views = post.views
    return render(request, 'blog/post_detail.html', {
        'post': post,
        'is_like': is_like,
        'number_of_likes': number_of_likes,
        'number_of_views': number_of_views
    })


@login_required
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            # post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})


@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            # post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})


@login_required
def post_draft_list(request):
    posts = Post.objects.filter(published_date__isnull=True).order_by('created_date')
    return render(request, 'blog/post_draft_list.html', {'posts': posts})


@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect('post_detail', pk=pk)


@login_required
def post_remove(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    return redirect('post_list')


def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/add_comment_to_post.html', {'form': form})


@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('post_detail', pk=comment.post.pk)


@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()
    return redirect('post_detail', pk=comment.post.pk)


@login_required
def add_like(request, pk):
    post = get_object_or_404(Post, pk=pk)
    Like.create_like_or_404(post, request.user)
    return redirect('post_detail', pk=pk)


@login_required
def add_dislike(request, pk):
    post = get_object_or_404(Post, pk=pk)
    Like.delete_like_or_404(post, request.user)
    return redirect('post_detail', pk=pk)


@login_required
def favorites(request):
    likes = Like.objects.filter(author=request.user)
    posts = []
    for like in likes:
        posts.append(like.post)
    return render(request, 'blog/post_list.html', {'posts': posts})
