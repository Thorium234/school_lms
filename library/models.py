from django.db import models
from .models import  models
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.

class Book(models.Model):
    title=models.CharField(max_length=255)
    publishers=models.CharField(max_length=255)
    first_publication=models.PositiveIntegerField()
    ISBN=models.CharField(max_length=255)
    category=models.CharField(max_length=255)
    created=models.DateTimeField(auto_now_add=True)
    available_copies = models.PositiveIntegerField(default=1)
    total_copies = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.title
    
    def is_available(self):
        return self.available_copies > 0


class Student(models.Model):
    first_name=models.CharField(max_length=255)
    last_name=models.CharField(max_length=255)
    admision_number=models.PositiveIntegerField()
    stream=models.CharField(max_length=255)
    created=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.admision_number})"
    
    def get_active_borrows(self):
        return self.borrow_set.filter(returned=False)

class Borrow(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    borrowed_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    returned = models.BooleanField(default=False)
    returned_date = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        status = "Returned" if self.returned else "Borrowed"
        return f"{self.student} - {self.book} ({status})"

    def is_overdue(self):
        return not self.returned and timezone.now() > self.due_date   
    def days_overdue(self):
        if not self.is_overdue():
            return 0
        return (timezone.now() - self.due_date).days      