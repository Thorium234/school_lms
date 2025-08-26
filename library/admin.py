from django.contrib import admin
from .models import Book, Student, Borrow, Shelf, RevisionPaper, Room

@admin.register(Shelf)
class ShelfAdmin(admin.ModelAdmin):
    list_display = ('shelf_name', 'shelf_code', 'category', 'shelf_count', 'max_borrow_per_student')
    search_fields = ('shelf_name', 'shelf_code', 'category')
    list_filter = ('category',)
    ordering = ('shelf_name',)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'ISBN', 'book_number', 'shelf', 'category', 'publishers',
        'first_publication', 'created'
    )
    search_fields = ('title', 'ISBN', 'book_number', 'publishers', 'category')
    list_filter = ('category', 'shelf')
    list_select_related = ('shelf',)
    ordering = ('title',)

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('form', 'stream', 'class_teacher', 'total_students')
    search_fields = ('form', 'stream', 'class_teacher')
    ordering = ('form', 'stream')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'first_name', 'last_name', 'admission_number', 'room',
        'display_form', 'display_stream', 'created'
    )
    search_fields = (
        'first_name', 'last_name', 'admission_number',
        'room__form', 'room__stream', 'room__class_teacher'
    )
    list_filter = ('room__form', 'room__stream', 'room')
    ordering = ('room', 'admission_number')

    def display_form(self, obj):
        return obj.room.form if obj.room else '-'
    display_form.short_description = 'Form'

    def display_stream(self, obj):
        return obj.room.stream if obj.room else '-'
    display_stream.short_description = 'Stream'

@admin.register(Borrow)
class BorrowAdmin(admin.ModelAdmin):
    list_display = (
        'student_admission_number', 'student_name', 'book_title', 'book_number', 'book_isbn',
        'student_room_form', 'student_room_stream',
        'borrowed_date', 'due_date', 'returned', 'returned_date', 'processed_by'
    )
    search_fields = (
        'book__title', 'book__book_number', 'book__ISBN',
        'student__admission_number', 'student__first_name', 'student__last_name'
    )
    list_filter = (
        'returned', 'borrowed_date', 'due_date', 'student__room__form', 'student__room__stream'
    )
    date_hierarchy = 'borrowed_date'
    raw_id_fields = ('student', 'book', 'processed_by')
    ordering = ('-borrowed_date',)

    @admin.display(description="Book Title")
    def book_title(self, obj):
        return obj.book.title if obj.book else "-"

    @admin.display(description="Book No.")
    def book_number(self, obj):
        return obj.book.book_number if obj.book else "-"

    @admin.display(description="ISBN")
    def book_isbn(self, obj):
        return obj.book.ISBN if obj.book else "-"

    @admin.display(description="Adm. No.")
    def student_admission_number(self, obj):
        return obj.student.admission_number if obj.student else "-"

    @admin.display(description="Student Name")
    def student_name(self, obj):
        if obj.student:
            return f"{obj.student.first_name} {obj.student.last_name}"
        return "-"

    @admin.display(description="Form")
    def student_room_form(self, obj):
        return obj.student.room.form if obj.student and obj.student.room else "-"

    @admin.display(description="Stream")
    def student_room_stream(self, obj):
        return obj.student.room.stream if obj.student and obj.student.room else "-"

@admin.register(RevisionPaper)
class RevisionPaperAdmin(admin.ModelAdmin):
    list_display = ('title', 'room', 'subject', 'uploaded_by', 'uploaded_at')
    search_fields = ('title', 'subject', 'room__form', 'room__stream')
    list_filter = ('room', 'subject')
    ordering = ('-uploaded_at',)


site_header = "Library Management System"
site_title = "Kikai Girls Library Admin"
index_title = "Welcome to Library Management System Admin"    