import re
from unicodedata import category
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watch_list = models.ManyToManyField('Auction', related_name='watchers', blank=True)
    user_bids = models.ManyToManyField('Auction', through='Bid', related_name='bidders')
    pass

class Auction(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100, blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    current_bid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    highest_bidder = models.ForeignKey(User,related_name='highest_bids',null=True,blank=True,on_delete=models.CASCADE)
    winner = models.ForeignKey(User, related_name='won_auctions', null=True, blank=True, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, related_name='auctions', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    closed = models.BooleanField(default=False) 

    def __str__(self):
        return self.title

class Bid(models.Model):
    auction = models.ForeignKey(Auction, related_name='bids', on_delete=models.CASCADE)
    bidder = models.ForeignKey(User, related_name='bids', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

class Comment(models.Model):
    content = models.CharField(max_length=510)
    owner = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    auction = models.ForeignKey(Auction, related_name='comments', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
