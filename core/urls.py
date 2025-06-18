from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("post/new/", views.PostCreateView.as_view(), name="post-create"),
    path("post/<int:pk>/", views.PostDetailView.as_view(), name="post-detail"),
    path("post/<int:pk>/update/", views.PostUpdateView.as_view(), name="post-update"),
    path("post/<int:pk>/delete/", views.PostDeleteView.as_view(), name="post-delete"),
    path("post/<int:pk>/like/", views.like_post, name="like-post"),
    path("user/<str:username>/", views.profile, name="profile"),
    path("user/<str:username>/follow/", views.follow_toggle, name="follow-toggle"),
    path("user/<str:username>/followers/", views.followers, name="followers"),
    path("user/<str:username>/following/", views.following, name="following"),
    path("suggestions/", views.suggestions, name="suggestions"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="core/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("signup/", views.signup, name="signup"),
]
