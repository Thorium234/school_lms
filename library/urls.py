from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Room Dashboards & Drilldown
    path('rooms/<int:room_id>/dashboard/', views.room_dashboard, name='room_dashboard'),
    path('forms/<str:form_name>/rooms/', views.form_rooms, name='form_rooms'),

    # Books
    path('books/available/', views.book_available_list, name='book_available'),

    path('books/', views.book_list, name='book_list'),
    path('books/create/', views.book_create, name='book_create'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('books/edit/<int:pk>/', views.book_edit, name='book_edit'),
    path('books/delete/<int:pk>/', views.book_delete, name='book_delete'),
    path('books/borrow/<int:pk>/', views.book_borrow_from_detail, name='book_borrow_from_detail'),

    # Shelves
    path('shelves/', views.shelf_list, name='shelf_list'),
    path('shelves/add/', views.shelf_create, name='shelf_create'),
    path('shelves/edit/<int:pk>/', views.shelf_edit, name='shelf_edit'),
    path('shelves/delete/<int:pk>/', views.shelf_delete, name='shelf_delete'),

    # Rooms
    path('rooms/', views.room_list, name='room_list'),
    path('rooms/create/', views.room_create, name='room_create'),
    path('rooms/edit/<int:pk>/', views.room_edit, name='room_edit'),
    path('rooms/delete/<int:pk>/', views.room_delete, name='room_delete'),

    # Revision Papers
    path('revision-papers/', views.revision_papers_list, name='revision_papers_list'),
    path('revision-papers/upload/', views.revision_paper_upload, name='revision_paper_upload'),

    # Students
    path('students/', views.student_list, name='student_list'),
    path('students/create/', views.student_create, name='student_create'),
    path('students/edit/<int:pk>/', views.student_edit, name='student_edit'),
    path('students/delete/<int:pk>/', views.student_delete, name='student_delete'),
    path('students/<int:pk>/', views.student_detail, name='student_detail'),
    path('students/assign-book/<int:pk>/', views.student_assign_book, name='student_assign_book'),

    # Borrows
    path('borrows/', views.borrow_list, name='borrow_list'),
    path('borrows/create/', views.borrow_book, name='borrow_book'),
    path('borrows/return/<int:pk>/', views.borrow_return, name='return_book'),
    path('borrows/<int:pk>/abort/', views.abort_borrow, name='abort_borrow'),

    # Analytics
    path('analysis/', views.analysis, name='analysis'),
]