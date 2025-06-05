from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('profile/', views.profile_user, name='profile_user'),

    # URLs for books

    path('books/', views.Book_list, name='Book_list'),
    path('books/create/', views.Book_create, name='Book_create'),
    path('books/edit/<int:pk>/', views.Book_edit, name='Book_edit'),
    path('books/delete/<int:pk>/', views.Book_delete, name='Book_delete'),

    #urls for students
    path('students/', views.student_list, name='student_list'),
    path('students/create/', views.student_create, name='student_create'),
    path('students/edit/<int:pk>/', views.student_edit, name='student_edit'),
    path('students/delete/<int:pk>/', views.student_delete, name='student_delete'),
    path('students/<int:student_id>/borrows/', views.student_borrows, name='student_borrows'),

    # Borrow/Return
    path('borrow/', views.borrow_book, name='borrow_book'),
    path('borrow/list/', views.borrow_list, name='borrow_list'),
    path('return/<int:pk>/', views.return_book, name='return_book'),
    path('books/<int:book_id>/borrows/', views.book_borrows, name='book_borrows'),

    
]

