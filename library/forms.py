from django import forms
from .models import Book, Student, Borrow
from django.utils import timezone
from datetime import timedelta


class BookForm(forms.ModelForm):
    class Meta:
        model=Book
        exclude=['created',]

class StudentForm(forms.ModelForm):
    class Meta:
        model=Student
        exclude=['created',]

class BorrowForm(forms.ModelForm):
    class Meta:
        model = Borrow
        fields = ['book', 'student', 'due_date']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show available books
        self.fields['book'].queryset = Book.objects.filter(available_copies__gt=0)
        # Set default due date (2 weeks from now)
        self.fields['due_date'].initial = timezone.now() + timedelta(days=14)

class ReturnForm(forms.ModelForm):
    class Meta:
        model = Borrow
        fields = []  # No fields needed, just confirmatio