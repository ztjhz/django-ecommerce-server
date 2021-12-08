from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    starting_bid = models.DecimalField(decimal_places=2, max_digits=10)
    highest_bid = models.DecimalField(decimal_places=2, max_digits=10, default = 0)
    image = models.ImageField(blank=True, null=True, upload_to="images/")
    category = models.CharField(max_length=64, blank=True)
    creator_id = models.IntegerField(default=2)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"[Listing] {self.title}"

class Bid(models.Model):
    bid = models.DecimalField(decimal_places=2, max_digits=10)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")

    def __str__(self):
        return f"[Bid] {self.bid} ({self.listing}, {self.user})"

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlists")
    listing = models.ManyToManyField(Listing, related_name="watchlists", blank=True)

    def __str__(self):
        return f"{self.user}: {self.listing.all()}"


class Comment(models.Model):
    comment = models.TextField()
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")

    def __str__(self):
        return f"{self.listing}: {self.comment}"
