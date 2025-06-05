from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import Book, Student, Borrow
from .forms import BookForm, StudentForm, BorrowForm, ReturnForm
from django.http import HttpResponse
from django.contrib.auth.models import User
# Create your views here.

@login_required
def dashboard(request):
    total_books = Book.objects.count()
    total_students = Student.objects.count()
    overdue_borrows = Borrow.objects.filter(
        returned=False, 
        due_date__lt=timezone.now()
    ).count()
    
    context = {
        'total_books': total_books,
        'total_students': total_students,
        'overdue_borrows': overdue_borrows,
    }
    return render(request, 'books/dashboard.html', context)

@login_required
def Book_list(response):
    book=Book.objects.all()
    return render(response,'books/book_list.html',{'book':book})

def Book_create(response):
    form=BookForm(response.POST or None)
    if response.method =='POST':
        form=BookForm(response.POST or None)
        if form.is_valid():
            form.save()
            return redirect('Book_list')
    else:
        form=BookForm(response.POST or None)    
    return render(response,'books/book_form.html',{'form':form})

def Book_edit(response,pk):
    book=get_object_or_404(Book,pk=pk)
    form=BookForm(response.POST or None ,instance=book)
    if response.method =='POST':
        form=BookForm(response.POST or None,instance=book)
        if form.is_valid():
            form.save()
            return redirect('Book_list')
    else:
        form=BookForm(response.POST or None, instance=book)
    return render(response,'books/book_form.html',{'form':form})

def Book_delete(response,pk):
    book=get_object_or_404(Book,pk=pk)
    form=BookForm(response.POST or None ,instance=book)
    if response.method =='POST':
        book.delete()
        return redirect('Book_list')
    return render(response,'books/book_delete_cornfirm.html',{'book':book})

@login_required
def borrow_book(request):
    if request.method == 'POST':
        form = BorrowForm(request.POST)
        if form.is_valid():
            borrow = form.save(commit=False)
            borrow.processed_by = request.user
            borrow.save()
            
            # Update book available copies
            book = borrow.book
            book.available_copies -= 1
            book.save()
            
            messages.success(request, f'Book "{borrow.book}" borrowed by {borrow.student}')
            return redirect('borrow_list')
    else:
        form = BorrowForm()
    
    return render(request, 'books/borrow_form.html', {'form': form})

@login_required
def return_book(request, pk):
    borrow = get_object_or_404(Borrow, pk=pk)
    
    if request.method == 'POST':
        form = ReturnForm(request.POST, instance=borrow)
        if form.is_valid():
            borrow.returned = True
            borrow.returned_date = timezone.now()
            borrow.save()
            
            # Update book available copies
            book = borrow.book
            book.available_copies += 1
            book.save()
            
            messages.success(request, f'Book "{borrow.book}" returned by {borrow.student}')
            return redirect('borrow_list')
    else:
        form = ReturnForm(instance=borrow)
    
    return render(request, 'books/return_form.html', {
        'form': form,
        'borrow': borrow,
    })

@login_required
def borrow_list(request):
    active_borrows = Borrow.objects.filter(returned=False).order_by('due_date')
    returned_borrows = Borrow.objects.filter(returned=True).order_by('-returned_date')[:20]
    
    return render(request, 'books/borrow_list.html', {
        'active_borrows': active_borrows,
        'returned_borrows': returned_borrows,
    })

#students views

@login_required
def student_list(response):
    student=Student.objects.all()
    return render(response,'students/student_list.html',{'student':student})

def student_create(response):
    form=StudentForm(response.POST or None)
    if response.method =='POST':
        form=StudentForm(response.POST or None)
        if form.is_valid():
            form.save()
            return redirect('student_list')
    else:
        form=StudentForm(response.POST or None)    
    return render(response,'students/student_form.html',{'form':form})

def student_edit(response,pk):
    student=get_object_or_404(Student,pk=pk)
    form=StudentForm(response.POST or None ,instance=student)
    if response.method =='POST':
        form=StudentForm(response.POST or None,instance=student)
        if form.is_valid():
            form.save()
            return redirect('student_list')
    else:
        form=StudentForm(response.POST or None, instance=student)
    return render(response,'students/student_form.html',{'form':form})

def student_delete(response,pk):
    student=get_object_or_404(Student,pk=pk)
    form=StudentForm(response.POST or None ,instance=student)
    if response.method =='POST':
        student.delete()
        return redirect('student_list')
    return render(response,'students/student_delete_cornfirm.html',{'student':student})

@login_required
def student_borrows(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    borrows = student.borrow_set.all().order_by('-borrowed_date')
    
    return render(request, 'students/student_borrows.html', {
        'student': student,
        'borrows': borrows,
    })

@login_required
def book_borrows(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    borrows = book.borrow_set.all().order_by('-borrowed_date')
    
    return render(request, 'books/book_borrows.html', {
        'book': book,
        'borrows': borrows,
    })

@login_required
def profile_user(request):
    if User.is_authenticated:
        return render(request,'registration/profile.html')
    else:
        return HttpResponse(request,'you must be logged in')

