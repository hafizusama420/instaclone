from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from .models import Post, Follow
from django.db.models import Q
from django.views.decorators.http import require_POST

# Create your views here.


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! Please log in.")
            return redirect("login")
    else:
        form = UserCreationForm()
    return render(request, "core/signup.html", {"form": form})


class PostListView(ListView):
    model = Post
    template_name = "core/home.html"
    context_object_name = "posts"
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Home"
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = "core/post_detail.html"
    context_object_name = "post"


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = "core/post_form.html"
    fields = ["image", "caption"]
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Post created successfully!")
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    template_name = "core/post_form.html"
    fields = ["image", "caption"]
    success_url = reverse_lazy("home")

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def form_valid(self, form):
        messages.success(self.request, "Post updated successfully!")
        return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = "core/post_confirm_delete.html"
    success_url = reverse_lazy("home")

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Post deleted successfully!")
        return super().delete(request, *args, **kwargs)


@login_required
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    return JsonResponse({"likes": post.total_likes(), "liked": liked})


@login_required
def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user).order_by("-created_at")

    # Get follow stats
    followers_count = user.followers.count()
    following_count = user.following.count()

    # Check if current user is following this user
    is_following = False
    if request.user != user:
        is_following = Follow.objects.filter(
            follower=request.user, following=user
        ).exists()

    context = {
        "profile_user": user,
        "posts": posts,
        "followers_count": followers_count,
        "following_count": following_count,
        "is_following": is_following,
    }
    return render(request, "core/profile.html", context)


@login_required
@require_POST
def follow_toggle(request, username):
    user_to_follow = get_object_or_404(User, username=username)

    if request.user == user_to_follow:
        return JsonResponse({"error": "You cannot follow yourself"}, status=400)

    follow_obj, created = Follow.objects.get_or_create(
        follower=request.user, following=user_to_follow
    )

    if not created:
        follow_obj.delete()
        is_following = False
    else:
        is_following = True

    return JsonResponse(
        {
            "is_following": is_following,
            "followers_count": user_to_follow.followers.count(),
        }
    )


@login_required
def home(request):
    # Get posts from users that the current user follows and their own posts
    following_users = User.objects.filter(followers__follower=request.user)
    posts = Post.objects.filter(
        Q(author__in=following_users) | Q(author=request.user)
    ).order_by("-created_at")

    context = {"posts": posts, "title": "Home"}
    return render(request, "core/home.html", context)


@login_required
def suggestions(request):
    # Get users that current user is already following
    following_users = User.objects.filter(followers__follower=request.user)

    # Get all users except current user and those already being followed
    suggested_users = User.objects.exclude(
        Q(id=request.user.id) | Q(id__in=following_users)
    ).order_by("username")

    # Add follow status for each user
    for user in suggested_users:
        user.followers_count = user.followers.count()
        user.posts_count = user.post_set.count()

    context = {"suggested_users": suggested_users, "title": "Suggestions"}
    return render(request, "core/suggestions.html", context)


@login_required
def followers(request, username):
    user = get_object_or_404(User, username=username)
    followers_list = Follow.objects.filter(following=user).select_related("follower")

    context = {
        "profile_user": user,
        "followers": followers_list,
        "title": f"{user.username}'s Followers",
    }
    return render(request, "core/followers.html", context)


@login_required
def following(request, username):
    user = get_object_or_404(User, username=username)
    following_list = Follow.objects.filter(follower=user).select_related("following")

    context = {
        "profile_user": user,
        "following": following_list,
        "title": f"{user.username}'s Following",
    }
    return render(request, "core/following.html", context)
