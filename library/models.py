from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver



class Room(models.Model):
    form = models.CharField(max_length=20)
    stream = models.CharField(max_length=20)
    class_teacher = models.CharField(max_length=100, blank=True, null=True)
    total_students = models.PositiveIntegerField(default=0, editable=False)

    class Meta:
        unique_together = ('form', 'stream')

    def __str__(self):
        return f"{self.form} {self.stream}"


class Shelf(models.Model):
    shelf_name = models.CharField(max_length=100, unique=True, null=True, blank=True)
    shelf_code = models.CharField(max_length=10, unique=True, null=True, blank=True)
    category = models.CharField(max_length=50, null=True, blank=True)
    form_class = models.CharField(max_length=50, null=True, blank=True, help_text="Form/class associated with this shelf.")  # New field
    shelf_count = models.PositiveIntegerField(default=0, editable=False)
    max_borrow_per_student = models.PositiveIntegerField(default=1, help_text="Maximum books a student can borrow from this shelf.")

    def __str__(self):
        return f"{self.shelf_name} ({self.category})"

    def save(self, *args, **kwargs):
        old = None
        if self.pk:
            old = Shelf.objects.filter(pk=self.pk).first()
        super().save(*args, **kwargs)
        if old and old.category != self.category:
            self.books.update(category=self.category)


class Book(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    publishers = models.CharField(max_length=255, null=True, blank=True)
    first_publication = models.PositiveIntegerField(null=True, blank=True)
    ISBN = models.CharField(max_length=255, unique=True, null=True, blank=True)
    book_number = models.CharField(max_length=255, unique=True, null=True, blank=True)
    shelf = models.ForeignKey(Shelf, on_delete=models.CASCADE, related_name="books", null=True, blank=True)
    category = models.CharField(max_length=50, editable=False, null=True, blank=True)
    book_picture = models.ImageField(upload_to='book_pictures/', blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.title or 'No Title'} ({self.category})"

    def save(self, *args, **kwargs):
        if self.shelf:
            self.category = self.shelf.category
        super().save(*args, **kwargs)


class Student(models.Model):
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    admission_number = models.PositiveIntegerField(unique=True)
    student_id = models.CharField(max_length=20, unique=True, editable=False, blank=True)
  # New field
    year_of_study = models.PositiveIntegerField(null=True, blank=True)  # New field
    current_class = models.CharField(max_length=50, null=True, blank=True)  # New field
    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name="students", null=True, blank=True)
    student_picture = models.ImageField(upload_to='student_pictures/', blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.student_id and self.first_name and self.last_name:
            year = timezone.now().year % 100  # e.g. 2025 -> 25
            initials = f"{self.first_name[0]}{self.last_name[0]}".upper()
            similar_ids = Student.objects.filter(student_id__startswith=f"{initials}/", created__year=timezone.now().year).count()
            serial = str(similar_ids + 1).zfill(4)  # e.g. 0001
            self.student_id = f"{initials}/{serial}/{year}"
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.admission_number})"

    def get_active_borrows(self):
        return self.borrow_set.filter(returned=False)


@receiver([post_save, post_delete], sender=Book)
def update_shelf_count(sender, instance, **kwargs):
    if instance.shelf:
        shelf = instance.shelf
        shelf.shelf_count = shelf.books.count()
        shelf.save(update_fields=['shelf_count'])


@receiver([post_save, post_delete], sender=Student)
def update_room_count(sender, instance, **kwargs):
    if instance.room:
        room = instance.room
        room.total_students = room.students.count()
        room.save(update_fields=['total_students'])


class Borrow(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    borrowed_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    returned = models.BooleanField(default=False)
    returned_date = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    shelf = models.ForeignKey(Shelf, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        status = "Returned" if self.returned else "Borrowed"
        return f"{self.student} - {self.book} ({status})"

    def is_overdue(self):
        return not self.returned and self.due_date and self.due_date < timezone.now()

    def days_overdue(self):
        if not self.is_overdue():
            return 0
        return (timezone.now() - self.due_date).days


class RevisionPaper(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.CharField(max_length=50, null=True, blank=True)
    file = models.FileField(upload_to='revision_papers/', null=True, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.subject} ({self.room})"
