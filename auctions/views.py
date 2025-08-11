from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Auction, Bid, Comment


def index(request):
    auctions = Auction.objects.all()
    return render(request, "auctions/index.html", {
        "auctions": auctions,
        "open_auctions": Auction.objects.filter(closed=False)
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def create_listing(request):
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        category = request.POST["category"]
        image_url = request.POST["image_url"]
        starting_bid = request.POST["starting_bid"]
        
        if category.strip() == "":
            category = None

        auction = Auction(
            title=title,
            description=description,
            category=category,
            image_url=image_url,
            starting_bid=starting_bid,
            current_bid=starting_bid,
            creator=request.user
        )
        auction.save()

        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/createAuction.html")
    

def auction_detail(request, auction_id):

    auction = Auction.objects.get(id=auction_id)
    comments = Comment.objects.filter(auction=auction)
    if request.method == "POST":
        
        if 'close_auction' in request.POST:
            auction.closed = True
            auction.winner = auction.highest_bidder
            auction.save()
            return HttpResponseRedirect(reverse("Auction", args=(auction_id,)))
        
        elif 'bid_amount' in request.POST:
            bid_amount = request.POST.get("bid_amount")
            if (float(bid_amount) > auction.current_bid):
                bid = Bid(auction = auction, bidder = request.user, amount = bid_amount)
                bid.save()

                auction.current_bid = bid_amount
                auction.highest_bidder = request.user
                auction.save()
                return HttpResponseRedirect(reverse("Auction", args=(auction_id,)))
            else:
                return render(request, "auctions/Auction.html", {
                    "comments": comments,
                    "auction": auction,
                    "message": "Your bid must be higher than the current bid."
                })
            
        elif 'add_watchlist' in request.POST:
            request.user.watch_list.add(auction)
            return HttpResponseRedirect(reverse("Auction", args=(auction_id,)))
        
        elif 'remove_watchlist' in request.POST:
            request.user.watch_list.remove(auction)
            return HttpResponseRedirect(reverse("Auction", args=(auction_id,)))
        
        elif 'comment' in request.POST:
            comment = Comment(content = request.POST["comment"], owner = request.user, auction = auction)
            comment.save()
            return HttpResponseRedirect(reverse("Auction", args=(auction_id,)))
        
    else:
        return render(request, "auctions/Auction.html", {
            "auction": auction,
            "comments": comments
        })


def watchlist(request):
    return render(request, "auctions/watchlist.html", {
        "watchlist": request.user.watch_list.filter()
    })


def categories(request): 
    categories = Auction.objects.values_list('category', flat=True).distinct()
    categories = [c for c in categories if c and c.strip() != '']
    return render(request, "auctions/categories.html", {
        "categories": categories
    })


def category_auctions(request, category_name):
    
    auctions = Auction.objects.filter(category=category_name, closed=False)
    return render(request, "auctions/index.html", {
        "auctions": auctions,
        "open_auctions": auctions,
        "category": category_name
    })