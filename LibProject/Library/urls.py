from django.urls import path
from . import views

urlpatterns = [
    path('book_list/', views.book_list, name='book_list'),
    path('import_books/', views.import_books_from_api, name='import_books_from_api'),

    path('book_create/', views.book_create, name='book_create'),
    path('book_update/<int:pk>/', views.book_update, name='book_update'),
    path('book_delete/<int:pk>/', views.book_delete, name='book_delete'),

    path('member_list/', views.member_list, name='member_list'),
    path('member_create/', views.member_create, name='member_create'),
    path('member_update/<int:pk>/', views.member_update, name='member_update'),
    path('member_delete/<int:pk>/', views.member_delete, name='member_delete'),

    path('issue_book/<int:book_id>/<int:member_id>/', views.issue_book, name='issue_book'),
    path('return_book/<int:transaction_id>/', views.return_book, name='return_book'),

    path('search_books/', views.search_books, name='search_books'),
    path('charge_rent_fee/<int:member_id>/', views.charge_rent_fee, name='charge_rent_fee'),
]
