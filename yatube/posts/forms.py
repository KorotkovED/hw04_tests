from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta():
        model = Post
        fields = ('text', 'group',)
        help_texts = {
            'текст': 'Опишите Ваш пост',
            'группа': 'Если Ваш пост можно отнести к какой-то группе,'
                     'то выбирете соответсвующую группу',
        }
        labels = {
            'text': 'текст',
            'group': 'группа',
            'author': 'автор',
            'pub_date': 'дата публикации',
        }

    def not_empty_text(self):
        data = self.cleaned_data['text']
        if data == '':
            raise forms.ValidationError(
                'Кажется, все-таки нужно что-нибудь написать.')
        return data
