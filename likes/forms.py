from django import forms
from .models import Comment

class CommentCreateForm(forms.ModelForm) :
    class Meta :
        model = Comment
        fields = ('comment_text',)
    
    comment_text = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder' : 'Add you comment...',
        'class' : 'w-full py-1 text-sm pl-4 border border-2 border-slate-600 rounded-xl'
    }))
