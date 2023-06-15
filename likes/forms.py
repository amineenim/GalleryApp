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

class CommentEditForm(forms.ModelForm) :
    class Meta :
        model = Comment 
        fields = ('comment_text',)
    
    comment_text = forms.CharField(max_length=400, label='Your Comment Text :', widget=forms.TextInput(attrs={
        'class' : "w-full border-2 border-slate-800 rounded-xl py-2 pl-3"
    }))