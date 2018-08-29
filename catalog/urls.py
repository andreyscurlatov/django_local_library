"""locallibrary URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views


urlpatterns = [

    path('',views.index,name='index'),

    path('books/',       views.BookListView.as_view(),  name='books'),
    path('book/<int:pk>',views.BookDetailView.as_view(),name='book-detail'),
    
    path('authors/',               views.AuthorListView.as_view(),  name='authors'),  
    path('author/<int:pk>',        views.AuthorDetailView.as_view(),name='author-detail'),
    path('author/create/',         views.AuthorCreate.as_view(),    name='author-create'),
    path('author/<int:pk>/update/',views.AuthorUpdate.as_view(),    name='author-update'),
    path('author/<int:pk>/delete/',views.AuthorDelete.as_view(),    name='author-delete'),

    path('mybooks/', views.LoanedBooksByUserListView.as_view(),    name='my-borrowed'),
    path('borrowed/',views.LoanedBooksByAllUsersListView.as_view(),name='all-borrowed'),    
    
    path('book_instance/create/',          views.BookInstanceCreate.as_view(), name='book-instance-create'),
    path('book_instance/<uuid:pk>/update/',views.BookInstanceUpdate,           name='book-instance-update'),    
    path('book_instance/<uuid:pk>/delete/',views.BookInstanceDelete.as_view(), name='book-instance-delete'),
    path('book_instance/avail/',           views.BookInstanceAvail.as_view(),  name='book-instance-avail'),
]
