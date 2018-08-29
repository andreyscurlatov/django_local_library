from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .models import Book, Author, BookInstance, Genre
from .forms import RenewBookModelForm

import datetime

# Create your views here.

def index(request):
    num_books=Book.objects.all().count()
    num_instances=BookInstance.objects.all().count()
    num_instances_avail=BookInstance.objects.filter(status__exact='a').count()
    num_authors=Author.objects.all().count()
    num_visits=request.session.get('num_visits',0)
    request.session['num_visits']=num_visits + 1

    context={
        'num_books': num_books,
        'num_authors': num_authors,
        'num_instances': num_instances,
        'num_instances_avail': num_instances_avail,
        'num_visits': num_visits,
        }

    return render(request,'index.html',context)
    
class LoanedBooksByUserListView(LoginRequiredMixin,ListView):
    model=BookInstance
    template_name='borrowed_list_user.html'

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

class LoanedBooksByAllUsersListView(PermissionRequiredMixin,ListView):    
    permission_required='catalog.can_mark_returned'
    model=BookInstance
    paginate_by=2
    template_name='borrowed_list_all_users.html'

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')

class BookListView(ListView):
    model=Book
    paginate_by=2
    context_object_name='book_list'
    queryset=Book.objects.all()
    template_name='book_list.html'

class BookDetailView(DetailView):
    model=Book
    context_object_name='book'
    queryset=Book.objects.all()
    template_name='book_detail.html'

class AuthorListView(ListView):
    model=Author
    paginate_by=2
    context_object_name='author_list'
    queryset=Author.objects.all()
    template_name='author_list.html'

class AuthorDetailView(DetailView):
    model=Author
    context_object_name='author'
    queryset=Author.objects.all()
    template_name='author_detail.html'

class AuthorCreate(PermissionRequiredMixin,CreateView):
    permission_required='catalog.can_mark_returned'
    model=Author
    fields='__all__'
    initial={'date_of_death': '05/01/2018'}
    template_name='author_form.html'

class AuthorUpdate(PermissionRequiredMixin,UpdateView):
    permission_required='catalog.can_mark_returned'
    model=Author
    fields=['first_name','last_name','date_of_birth','date_of_death']
    template_name='author_form.html'

class AuthorDelete(PermissionRequiredMixin,DeleteView):
    permission_required='catalog.can_mark_returned'
    model=Author
    success_url=reverse_lazy('authors')
    template_name='author_confirm_delete.html'

class BookInstanceCreate(PermissionRequiredMixin,CreateView):
    permission_required='catalog.can_mark_returned'
    model=BookInstance
    fields='__all__'    
    success_url=reverse_lazy('book-instance-avail')
    template_name='bookinstance_form.html'

@permission_required('catalog.can_mark_returned')
def BookInstanceUpdate(request,pk):
    book_instance=get_object_or_404(BookInstance,pk=pk)

    if request.method=='POST':
        book_renewal_form=RenewBookModelForm(request.POST)

        if book_renewal_form.is_valid():
            book_instance.due_back=book_renewal_form.clean_due_back()
            book_instance.borrower=book_renewal_form.cleaned_data['borrower']
            book_instance.status=book_renewal_form.cleaned_data['status']
            book_instance.save()
            return HttpResponseRedirect(reverse('all-borrowed'))

    else:
        suggest_renewal_date=datetime.date.today()+datetime.timedelta(weeks=3)
        book_renewal_form=RenewBookModelForm(initial={'due_back': suggest_renewal_date})

    context={
        'form': book_renewal_form,
        'book_instance': book_instance,
        }

    return render(request,'bookinstance_form.html',context)

class BookInstanceDelete(PermissionRequiredMixin,DeleteView):
    permission_required='catalog.can_mark_returned'
    model=BookInstance
    success_url=reverse_lazy('book-instance-avail')
    template_name='bookinstance_confirm_delete.html'

class BookInstanceAvail(PermissionRequiredMixin,ListView):    
    permission_required='catalog.can_mark_returned'
    model=BookInstance
    paginate_by=2
    template_name='bookinstance_list_avail.html'

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='a')
    
    
    
