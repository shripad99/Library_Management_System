from django import forms
from .models import Book, Member, Transaction


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = '__all__'


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = '__all__'


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['book', 'member', 'returned_date']
