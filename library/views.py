from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count, F, Value, CharField
from django.db.models.functions import Concat
from django.urls import reverse
from django import forms
from dal import autocomplete

from .models import Book, Student, Borrow, Shelf, RevisionPaper, Room
from .forms import (
    BookForm, StudentForm, BorrowForm, ReturnForm,
    RevisionPaperForm, ShelfForm, RoomForm
)

# ==== Permissions ====

def is_librarian(user):
    return user.is_authenticated and user.is_staff

# ==== Dashboard (with room+form+stream grouping and charts support) ====

@login_required
def dashboard(request):
    total_books = Book.objects.count()
    total_students = Student.objects.count()
    overdue_borrows = Borrow.objects.filter(returned=False, due_date__lt=timezone.now()).count()

    # Room stats (by individual room)
    room_qs = Room.objects.annotate(
        student_count=Count('students', distinct=True),
        borrow_count=Count('students__borrow', filter=Q(students__borrow__returned=False), distinct=True)
    ).values('id', 'form', 'stream', 'class_teacher', 'student_count', 'borrow_count')
    room_stats = list(room_qs)
    borrows_per_room = [room['borrow_count'] for room in room_stats]
    room_labels = [f"{room['form']} {room['stream']}" for room in room_stats]

    # Grouped by form (all Form 2 rooms together, etc.)
    form_stats = (
        Room.objects
        .values('form')
        .annotate(
            total_students=Count('students', distinct=True),
            total_borrows=Count('students__borrow', filter=Q(students__borrow__returned=False), distinct=True)
        )
        .order_by('form')
    )
    forms_list = list(form_stats)

    # Grouped by stream (across all forms)
    stream_stats = (
        Room.objects
        .values('stream')
        .annotate(
            total_students=Count('students', distinct=True),
            total_borrows=Count('students__borrow', filter=Q(students__borrow__returned=False), distinct=True)
        )
        .order_by('stream')
    )
    streams_list = list(stream_stats)

    # Grouped by teacher (across all forms/streams)
    teacher_stats = (
        Room.objects
        .values('class_teacher')
        .annotate(
            total_students=Count('students', distinct=True),
            total_borrows=Count('students__borrow', filter=Q(students__borrow__returned=False), distinct=True)
        )
        .order_by('class_teacher')
    )
    teachers_list = list(teacher_stats)

    latest_book = Book.objects.order_by('-created').first()
    most_borrowed_book = (
        Borrow.objects.values('book__title', 'book__created')
        .annotate(borrow_count=Count('id'))
        .order_by('-borrow_count')
        .first()
    )

    # Recent Activity: Show recent books borrowed
    recent_borrows = (
        Borrow.objects
        .filter(returned=False)
        .select_related('student', 'book')
        .order_by('-borrowed_date')[:5]
    )
    recent_activity = []
    for b in recent_borrows:
        recent_activity.append({
            'user': str(b.student),
            'action': f'borrowed book "{b.book.title}"',
            'timestamp': b.borrowed_date,
            'book': b.book,
            'student': b.student,
        })

    context = {
        'total_books': total_books,
        'total_students': total_students,
        'overdue_borrows': overdue_borrows,
        'room_stats': room_stats,
        'room_labels': room_labels,
        'latest_book': latest_book,
        'most_borrowed_book': most_borrowed_book,
        'recent_activity': recent_activity,
        'recent_borrows': recent_borrows,
        'borrows_per_room': borrows_per_room,
        'forms_list': forms_list,
        'streams_list': streams_list,
        'teachers_list': teachers_list,
    }
    return render(request, 'dashboards/dashboard.html', context)

# ==== Books ====

@login_required
def book_available_list(request):
    # Exclude books currently borrowed
    borrowed_books = Borrow.objects.filter(returned=False).values_list('book_id', flat=True)
    available_books = Book.objects.exclude(id__in=borrowed_books).select_related('shelf')
    
    query = request.GET.get('q')
    if query:
        available_books = available_books.filter(
            Q(title__icontains=query) |
            Q(ISBN__icontains=query) |
            Q(book_number__icontains=query) |
            Q(category__icontains=query)
        )
    
    return render(request, 'books/book_available.html', {'book': available_books})


@login_required
def book_list(request):
    books = Book.objects.select_related('shelf').all()
    query = request.GET.get('q')
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(ISBN__icontains=query) |
            Q(book_number__icontains=query) |
            Q(category__icontains=query)
        )
    return render(request, 'books/book_list.html', {'book': books})

@login_required
def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'books/book_detail.html', {'book': book})

@login_required
def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            if book.shelf:
                book.category = book.shelf.category
            book.save()
            messages.success(request, f'Book "{book.title}" added.')
            return render(request, 'registration/loading.html', {"redirect_url": reverse("book_list")})
    else:
        form = BookForm()
    return render(request, 'books/book_form.html', {'form': form, 'instance': form.instance})

@login_required
def book_edit(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            book = form.save(commit=False)
            if book.shelf:
                book.category = book.shelf.category
            book.save()
            messages.success(request, f'Book "{book.title}" updated.')
            return render(request, 'registration/loading.html', {"redirect_url": reverse("book_list")})
    else:
        form = BookForm(instance=book)
    return render(request, 'books/book_form.html', {'form': form, 'instance': book})

@login_required
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Book deleted.')
        return render(request, 'registration/loading.html', {"redirect_url": reverse("book_list")})
    return render(request, 'books/book_delete_confirm.html', {'book': book})

# ==== Borrow Views with borrow-limit logic ====

@login_required
def borrow_book(request):
    if request.method == 'POST':
        form = BorrowForm(request.POST)
        if form.is_valid():
            book = form.cleaned_data['book']
            days = form.cleaned_data['days']
            student = form.student

            borrowed_count = Borrow.objects.filter(
                student=student,
                shelf=book.shelf,
                returned=False
            ).count()

            if borrowed_count >= book.shelf.max_borrow_per_student:
                messages.error(request, f"You've reached the borrowing limit for shelf '{book.shelf.shelf_name}'.")
                return redirect(request.META.get('HTTP_REFERER', reverse("borrow_list")))

            Borrow.objects.create(
                book=book,
                student=student,
                due_date=timezone.now() + timezone.timedelta(days=days),
                processed_by=request.user,
                shelf=book.shelf
            )
            messages.success(request, f'Book "{book.title}" borrowed by {student.first_name} ({student.admission_number}).')
            return render(request, 'registration/loading.html', {"redirect_url": reverse("borrow_list")})
    else:
        form = BorrowForm()
    return render(request, 'books/borrow_form.html', {'form': form})


@login_required
def book_borrow_from_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == "POST":
        form = BorrowForm(request.POST)
        form.fields['book'].initial = book
        form.fields['book'].widget = forms.HiddenInput()
        if form.is_valid():
            days = form.cleaned_data['days']
            student = form.student

            borrowed_count = Borrow.objects.filter(
                student=student,
                shelf=book.shelf,
                returned=False
            ).count()

            if borrowed_count >= book.shelf.max_borrow_per_student:
                messages.error(request, f"Borrowing limit reached for shelf '{book.shelf.shelf_name}'.")
                return redirect(request.META.get('HTTP_REFERER', reverse("book_detail", args=[book.pk])))

            Borrow.objects.create(
                book=book,
                student=student,
                due_date=timezone.now() + timezone.timedelta(days=days),
                processed_by=request.user,
                shelf=book.shelf
            )
            messages.success(request, f'Book "{book.title}" borrowed by {student.first_name} ({student.admission_number}).')
            return render(request, 'registration/loading.html', {"redirect_url": reverse("borrow_list")})
    else:
        form = BorrowForm(initial={'book': book})
        form.fields['book'].widget = forms.HiddenInput()
    return render(request, 'books/borrow_form.html', {'form': form, 'book': book})


@login_required
def student_assign_book(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        form = BorrowForm(request.POST)
        form.fields['admission_number'].initial = student.admission_number
        form.fields['admission_number'].widget = forms.HiddenInput()
        if form.is_valid():
            book = form.cleaned_data['book']
            days = form.cleaned_data['days']

            borrowed_count = Borrow.objects.filter(
                student=student,
                shelf=book.shelf,
                returned=False
            ).count()

            if borrowed_count >= book.shelf.max_borrow_per_student:
                messages.error(request, f"{student.first_name} has reached the borrow limit for shelf '{book.shelf.shelf_name}'.")
                return redirect(request.META.get('HTTP_REFERER', reverse("student_detail", args=[student.pk])))

            Borrow.objects.create(
                book=book,
                student=student,
                due_date=timezone.now() + timezone.timedelta(days=days),
                processed_by=request.user,
                shelf=book.shelf
            )
            messages.success(request, f'Book "{book.title}" borrowed by {student.first_name} ({student.admission_number}).')
            return render(request, 'registration/loading.html', {"redirect_url": reverse("borrow_list")})
    else:
        form = BorrowForm(initial={'admission_number': student.admission_number})
        form.fields['admission_number'].widget = forms.HiddenInput()
    return render(request, 'books/borrow_form.html', {'form': form, 'student': student})

# ==== Return / List / Abort and other views remain unchanged ====

@login_required
def borrow_return(request, pk):
    borrow = get_object_or_404(Borrow, pk=pk)
    if request.method == 'POST' and not borrow.returned:
        borrow.returned = True
        borrow.returned_date = timezone.now()
        borrow.save()
        shelf = borrow.book.shelf
        shelf.shelf_count = shelf.books.count()
        shelf.save(update_fields=['shelf_count'])
        messages.success(request, f'Book "{borrow.book}" returned.')
        return render(request, 'registration/loading.html', {"redirect_url": reverse("borrow_list")})
    return render(request, 'books/return_form.html', {'borrow': borrow})


@login_required
def borrow_list(request):
    active_borrows = Borrow.objects.filter(returned=False).select_related('book', 'student').order_by('due_date')
    returned_borrows = Borrow.objects.filter(returned=True).select_related('book', 'student').order_by('-returned_date')[:20]
    recent_borrows = Borrow.objects.filter(returned=False).select_related('book', 'student').order_by('-borrowed_date')[:5]
    return render(request, 'books/borrow_list.html', {
        'active_borrows': active_borrows,
        'returned_borrows': returned_borrows,
        'recent_borrows': recent_borrows,
    })


@login_required
def abort_borrow(request, pk):
    borrow = get_object_or_404(Borrow, pk=pk)
    if request.method == 'POST':
        borrow.delete()
        messages.success(request, f'Borrow record for "{borrow.book.title}" by {borrow.student} aborted (deleted).')
        return render(request, 'registration/loading.html', {"redirect_url": reverse("borrow_list")})
    return render(request, 'books/abort_borrow_confirm.html', {'borrow': borrow})

# ==== Autocomplete, Shelf, Room, RevisionPaper, Student, Analysis views all unchanged and kept below ====

# (Include the rest of your code here following the same pattern.)

# ==== Autocomplete Views (for DAL) ====

class StudentAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Student.objects.all()
        if self.q:
            qs = qs.filter(
                Q(first_name__icontains=self.q) |
                Q(last_name__icontains=self.q) |
                Q(admission_number__icontains=self.q)
            )
        return qs

class BookAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        borrowed_books = Borrow.objects.filter(returned=False).values_list('book_id', flat=True)
        qs = Book.objects.exclude(id__in=borrowed_books)
        if self.q:
            qs = qs.filter(
                Q(title__icontains=self.q) |
                Q(ISBN__icontains=self.q) |
                Q(book_number__icontains=self.q)
            )
        return qs

# ==== Shelves ====

@login_required
@user_passes_test(is_librarian)
def shelf_list(request):
    shelves = Shelf.objects.all()
    return render(request, 'books/shelf_list.html', {'shelves': shelves})

@login_required
@user_passes_test(is_librarian)
def shelf_create(request):
    if request.method == 'POST':
        form = ShelfForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Shelf created successfully.")
            return render(request, 'registration/loading.html', {"redirect_url": reverse("shelf_list")})
    else:
        form = ShelfForm()
    return render(request, 'books/shelf_form.html', {'form': form})

@login_required
@user_passes_test(is_librarian)
def shelf_edit(request, pk):
    shelf = get_object_or_404(Shelf, pk=pk)
    if request.method == 'POST':
        form = ShelfForm(request.POST, instance=shelf)
        if form.is_valid():
            form.save()
            messages.success(request, "Shelf updated successfully.")
            return render(request, 'registration/loading.html', {"redirect_url": reverse("shelf_list")})
    else:
        form = ShelfForm(instance=shelf)
    return render(request, 'books/shelf_form.html', {'form': form, 'edit_mode': True})

@login_required
@user_passes_test(is_librarian)
def shelf_delete(request, pk):
    shelf = get_object_or_404(Shelf, pk=pk)
    if request.method == 'POST':
        shelf.delete()
        messages.success(request, "Shelf deleted.")
        return render(request, 'registration/loading.html', {"redirect_url": reverse("shelf_list")})
    return render(request, 'books/shelf_confirm_delete.html', {'shelf': shelf})

# ==== Rooms ====

@login_required
def room_list(request):
    rooms = Room.objects.all()
    return render(request, 'rooms/room_list.html', {'rooms': rooms})

@login_required
def room_create(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Room created successfully.")
            return render(request, 'registration/loading.html', {"redirect_url": reverse("room_list")})
    else:
        form = RoomForm()
    return render(request, 'rooms/room_form.html', {'form': form})

@login_required
def room_edit(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, "Room updated successfully.")
            return render(request, 'registration/loading.html', {"redirect_url": reverse("room_list")})
    else:
        form = RoomForm(instance=room)
    return render(request, 'rooms/room_form.html', {'form': form, 'edit_mode': True, 'room': room})

@login_required
def room_delete(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        room.delete()
        messages.success(request, "Room deleted successfully.")
        return render(request, 'registration/loading.html', {"redirect_url": reverse("room_list")})
    return render(request, 'rooms/room_confirm_delete.html', {'room': room})

# ==== Per-Room Dashboard ====

@login_required
def room_dashboard(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    students = Student.objects.filter(room=room).select_related('room').order_by('admission_number')
    borrows = Borrow.objects.filter(student__in=students, returned=False).select_related('book', 'student')
    student_borrows = {student.id: [] for student in students}
    for borrow in borrows:
        student_borrows[borrow.student_id].append(borrow)
    context = {
        'room': room,
        'students': students,
        'student_borrows': student_borrows,
    }
    return render(request, 'rooms/room_dashboard.html', context)

# ==== Drill-down: Form to Rooms ====

@login_required
def form_rooms(request, form_name):
    rooms = Room.objects.filter(form=form_name).order_by('stream')
    return render(request, 'rooms/form_rooms.html', {
        'form_name': form_name,
        'rooms': rooms,
    })

# ==== Revision Papers ====

def revision_papers_list(request):
    papers = RevisionPaper.objects.all()
    return render(request, 'revision_papers/revision_paper_list.html', {'papers': papers})

@login_required
def revision_paper_upload(request):
    if request.method == 'POST':
        form = RevisionPaperForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Revision paper uploaded successfully.")
            return render(request, 'registration/loading.html', {"redirect_url": reverse("revision_papers_list")})
    else:
        form = RevisionPaperForm()
    return render(request, 'revision_papers/revision_paper_form.html', {'form': form})

# ==== Students ====

@login_required
def student_list(request):
    query = request.GET.get('q')
    students = Student.objects.all()
    if query:
        students = students.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(admission_number__icontains=query) |
            Q(room__form__icontains=query) |
            Q(room__stream__icontains=query)
        )
    return render(request, 'students/student_list.html', {'students': students, 'query': query})

@login_required
def student_create(request):
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Student created successfully.")
            return render(request, 'registration/loading.html', {"redirect_url": reverse("student_list")})
    else:
        form = StudentForm()
    return render(request, 'students/student_form.html', {'form': form})

@login_required
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Student updated successfully.")
            return render(request, 'registration/loading.html', {"redirect_url": reverse("student_list")})
    else:
        form = StudentForm(instance=student)
    return render(request, 'students/student_form.html', {'form': form, 'edit_mode': True, 'student': student})

@login_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.delete()
        messages.success(request, "Student deleted successfully.")
        return render(request, 'registration/loading.html', {"redirect_url": reverse("student_list")})
    return render(request, 'students/student_confirm_delete.html', {'student': student})

@login_required
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    borrows = Borrow.objects.filter(student=student).select_related("book")
    return render(request, 'students/student_detail.html', {
        'student': student,
        'borrows': borrows
    })

# ==== Analysis ====

@login_required
def analysis(request):
    total_books = Book.objects.count()
    total_students = Student.objects.count()
    borrowed_books = Borrow.objects.filter(returned=False).count()
    overdue_books = Borrow.objects.filter(returned=False, due_date__lt=timezone.now()).count()
    books_due_soon = Borrow.objects.filter(returned=False, due_date__gte=timezone.now(), due_date__lte=timezone.now()+timezone.timedelta(days=7)).count()
    total_shelves = Shelf.objects.count()
    total_rooms = Room.objects.count()
    active_students = Student.objects.filter(borrow__returned=False).distinct().count()

    # Borrows per room (for chart)
    borrows_per_room = (
        Room.objects
        .annotate(
            label=Concat(F('form'), Value(' '), F('stream'), output_field=CharField()),
            count=Count('students__borrow', filter=Q(students__borrow__returned=False), distinct=True)
        )
        .values('label', 'count')
        .order_by('form', 'stream')
    )
    borrows_per_room = list(borrows_per_room)

    # Top borrowed books (for chart)
    top_books = (
        Borrow.objects
        .values('book__title')
        .annotate(borrow_count=Count('id'))
        .order_by('-borrow_count')[:10]
    )
    top_books = [
        {'title': b['book__title'], 'borrow_count': b['borrow_count']}
        for b in top_books if b['book__title']
    ]

    # Most active students (for table)
    top_students = (
        Student.objects
        .annotate(borrow_count=Count('borrow'))
        .filter(borrow_count__gt=0)
        .order_by('-borrow_count')[:10]
    )
    top_students = [
        {'full_name': f"{s.first_name} {s.last_name}", 'room': s.room, 'borrow_count': s.borrow_count}
        for s in top_students
    ]

    context = {
        'total_books': total_books,
        'borrowed_books': borrowed_books,
        'total_students': total_students,
        'overdue_books': overdue_books,
        'books_due_soon': books_due_soon,
        'total_shelves': total_shelves,
        'total_rooms': total_rooms,
        'active_students': active_students,
        'borrows_per_room': borrows_per_room,
        'top_books': top_books,
        'top_students': top_students,
    }
    return render(request, 'dashboards/analysis.html', context)

