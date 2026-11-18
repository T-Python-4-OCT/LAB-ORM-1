from django import forms


class PostSearchForm(forms.Form):
    q = forms.CharField(
        label="Search posts", max_length=200, required=False,
        widget=forms.TextInput(attrs={"type": "search", "placeholder": "Search games, reviews, or stories…"}),
    )


class PostFilterForm(forms.Form):
    rating = forms.ChoiceField(label="Minimum rating", choices=[("", "All ratings")] + [(str(n), f"{n} and up") for n in range(1, 6)], required=False)
    order = forms.ChoiceField(label="Order", choices=[("newest", "Newest first"), ("oldest", "Oldest first"), ("rating", "Highest rated")], required=False)
    limit = forms.ChoiceField(label="Show", choices=[("", "All posts"), ("5", "5 posts"), ("10", "10 posts"), ("20", "20 posts")], required=False)
