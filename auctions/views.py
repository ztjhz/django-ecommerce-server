from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Watchlist, Bid, Comment
from .forms import ListingForm, BidForm, CommentForm


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all()
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

def listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    comments = listing.comments.all()
    winner = None
    bids = listing.bids.all()
    if bids:
        winner = bids.order_by("-bid")[0]
    watchlist = Watchlist.objects.filter(user_id=request.user.id, listing=listing)
    message = request.session.get("message")
    request.session["message"] = None
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "watchlist": watchlist,
        "bid": BidForm(auto_id=False),
        "message": message,
        "winner": winner,
        "comments": comments,
        "commentForm": CommentForm()
    })

@login_required(login_url="/login")
def create(request):
    if request.method == "GET":
        form = ListingForm()
        return render(request, "auctions/create.html", {
            "form": form
        })
    elif request.method == "POST":
        form = ListingForm(request.POST)

        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            starting_bid = form.cleaned_data["starting_bid"]
            image = None
            try:
                image = request.FILES["image"]
            except:
                pass
            category = form.cleaned_data["category"]
            creator_id = request.user.id
            listing = Listing(title=title, description=description, starting_bid=starting_bid, 
                              image=image, category=category, creator_id=creator_id, highest_bid=starting_bid)
            listing.save()
            return HttpResponseRedirect(reverse("index"))

@login_required(login_url="/login")
def change_watchlist(request):
    listing = Listing.objects.get(id=int(request.POST["listing"]))
    user = User.objects.get(id=request.user.id)
    if request.POST["type"] == "add":
        w = Watchlist(user=user)
        w.save()
        w.listing.add(listing)
    else:
        #temp = Watchlist.objects.get(listing=listing, user=user)
        temp = listing.watchlists.get(user=user)
        temp.delete()
    return HttpResponseRedirect(reverse("index"))

@login_required(login_url="/login")
def bid(request):
    if request.method == "POST":
        listing_id = int(request.POST["listing"])
        bid = float(request.POST["bid"])
        user = User(pk=request.user.id)
        listing = Listing.objects.get(pk=listing_id)
        if bid < listing.starting_bid:
            request.session["message"] = "Error! Bid is less than starting bid!"
            return HttpResponseRedirect(reverse("listing", args=[listing_id]))
        if bid <= listing.highest_bid:
            request.session["message"] = "Error! Bid is less than other bids!"
            return HttpResponseRedirect(reverse("listing", args=[listing_id]))

        listing.highest_bid = bid
        listing.save()
        new_bid = Bid(bid=bid, listing=listing, user=user)
        new_bid.save()
        request.session["message"] = "Success! Bid placed successfully!"
        return HttpResponseRedirect(reverse("listing", args=[listing_id]))  

@login_required(login_url="/login")
def close(request):
    if request.method == "POST":
        listing_id = int(request.POST["listing"])
        listing = Listing.objects.get(pk=listing_id)
        listing.active = False
        listing.save()
        return HttpResponseRedirect(reverse("listing", args=[listing_id]))

@login_required(login_url="/login")
def comment(request):
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            listing_id = request.POST["listing"]
            listing = Listing.objects.get(pk=listing_id)
            comment = form.cleaned_data["comment"]
            new_comment = Comment(listing=listing, comment=comment, user=request.user)
            new_comment.save()
            request.session["message"] = "Commented sucessfully!"
            return HttpResponseRedirect(reverse("listing", args=[listing_id]))

@login_required(login_url="/login")
def watchlist(request):
    query = request.user.watchlists.all()
    watchlists = []
    for i in query:
        listing = i.listing.all()[0]
        watchlists.append(listing)
    return render(request, "auctions/watchlist.html", {
        "watchlist": watchlists
    })

def category(request):
    query = Listing.objects.all().values("category").distinct()
    categories = []
    for i in query:
        if i["category"] != "":
            categories.append(i["category"])
    return render(request, "auctions/category.html", {
        "categories": categories
    })

def category_filter(request, category):
    listings = Listing.objects.filter(category=category)
    return render(request, "auctions/category_filter.html", {
        "listings": listings,
        "category": category
    })