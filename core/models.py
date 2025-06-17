from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

def post_image_path(instance, filename):
    # Generate path: media/posts/user_id/filename
    return f'posts/{instance.author.id}/{filename}'

class Post(models.Model):
    image = models.ImageField(upload_to=post_image_path, default='posts/default.jpg')
    caption = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.author.username}'s post - {self.created_at}"

    def total_likes(self):
        return self.likes.count()

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"

    def save(self, *args, **kwargs):
        if self.follower == self.following:
            raise ValueError("Users cannot follow themselves")
        super().save(*args, **kwargs)
