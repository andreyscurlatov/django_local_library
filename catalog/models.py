from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date
import uuid


# Create your models here.

class Genre(models.Model):
    name=models.CharField(max_length=200,help_text='Enter a book genre')
    
    def __str__(self):
        return self.name

class Author(models.Model):    
    first_name=models.CharField(max_length=100)
    last_name=models.CharField(max_length=100)
    date_of_birth=models.DateField(blank=True,null=True)
    date_of_death=models.DateField('Died',blank=True,null=True)
    
    def __str__(self):
        return self.last_name+' '+self.first_name

    def get_absolute_url(self):
        return reverse('author-detail',args=[str(self.id)])

class Book(models.Model):
    title=models.CharField(max_length=100)
    author=models.ForeignKey(Author,on_delete=models.SET_NULL,null=True)
    summary=models.TextField(max_length=1000,help_text='Enter a description')
    isbn=models.CharField('ISBN',max_length=13,help_text='13 Character')
    genre=models.ManyToManyField(Genre,help_text='Select a genre for this book')

    def display_genre(self):
        return ', '.join(genre.name for genre in self.genre.all()[:3])

    display_genre.short_description='Genre'
    
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('book-detail',args=[str(self.id)])
 
class BookInstance(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,help_text='Unique ID for this particular book')
    book=models.ForeignKey(Book,on_delete=models.SET_NULL,null=True)
    imprint=models.CharField(max_length=200)
    due_back=models.DateField(blank=True,null=True,help_text='Enter a date between now and 4 weeks (default 3).')
    borrower=models.ForeignKey(User,on_delete=models.SET_NULL,blank=True,null=True)

    LOAN_STATUS=(
        ('m','Maintenance'),
        ('o','On loan'),
        ('a','Available'),
        ('r','Reserved'),
        )

    status=models.CharField(max_length=1,choices=LOAN_STATUS,blank=True,default='m',help_text='Book availability',)
    
    def __str__(self):
        return str(self.id)+' '+self.book.title

    def display_title(self):
        return self.book.title

    @property
    def is_overdue(self):
        if self.due_back and date.today()>self.due_back:
            return True
        return False

    class Meta:
        permissions=(('can_mark_returned','Set book as returned'),)
        ordering=['book']
    

