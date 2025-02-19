from django import forms
from .models import Post, User, Comment


class PostForm(forms.ModelForm):
    # TODO

    class Meta:
        model = Post
        fields = [
            'title',
            'text',
            'pub_date',
            'category',
            'location',
            'is_published',
            'image'
        ]
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'})
        }


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ['text']
