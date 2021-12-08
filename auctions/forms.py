from django import forms
from django.forms.widgets import Textarea

class ListingForm(forms.Form):
    title = forms.CharField(max_length=64)
    description = forms.CharField(widget=forms.Textarea)
    starting_bid = forms.DecimalField(decimal_places=2, max_digits=10)
    image = forms.ImageField(required=False)
    category = forms.CharField(max_length=64, required=False)

class BidForm(forms.Form):
    bid = forms.DecimalField(decimal_places=2, max_digits=10, label="")

class CommentForm(forms.Form):
    comment = forms.CharField(widget=Textarea, label="")