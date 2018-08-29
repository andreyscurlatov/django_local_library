from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from django.contrib.auth.models import User, Permission
from catalog.models import BookInstance, Book, Genre

from catalog.models import Author

import datetime
import uuid

class AuthorListViewTest(TestCase):
    @classmethod

    def setUpTestData(cls):
        number_of_authors=3

        for author_id in range(number_of_authors):
            Author.objects.create(
                first_name='Christian'+' '+str(author_id),
                last_name='Surname'+' '+str(author_id),
            )

    def test_view_url_exists_at_desired_location(self):
        response=self.client.get('/catalog/authors/')
        self.assertEqual(response.status_code,200)

    def test_view_url_accessible_by_name(self):
        response=self.client.get(reverse('authors'))
        self.assertEqual(response.status_code,200)

    def test_view_uses_correct_template(self):
        response=self.client.get(reverse('authors'))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'author_list.html')

    def test_pagination_is_ten(self):
        response=self.client.get(reverse('authors'))
        self.assertEqual(response.status_code,200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated']==True)
        self.assertTrue(len(response.context['author_list'])==2)

    def test_lists_all_authors(self):
        response=self.client.get(reverse('authors')+'?page=2')
        self.assertEqual(response.status_code,200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated']==True)
        self.assertTrue(len(response.context['author_list'])==1)

class LoanedBooksByUserListView(TestCase):

    def setUp(self):
        test_user1=User.objects.create_user(username='testuser1',password='qazxswedc')
        test_user2=User.objects.create_user(username='testuser2',password='zaqwsxcde')

        test_user1.save()
        test_user2.save()

        test_author=Author.objects.create(first_name='John',last_name='Smith')
        test_genre=Genre.objects.create(name='Fantasy')
        test_book=Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFG',
            author=test_author
            )

        genre_objects_for_book=Genre.objects.all()
        test_book.genre.set(genre_objects_for_book)
        test_book.save()

        number_of_book_copies=30
        for book_copy in range(number_of_book_copies):
            return_date=timezone.now()+datetime.timedelta(days=book_copy%5)
            the_borrower=test_user1 if book_copy %2 else test_user2            
            status='m'
            BookInstance.objects.create(
                book=test_book,
                imprint='Unlikely Imprint, 2018',
                due_back=return_date,
                borrower=the_borrower,
                status=status,
                )
            
    def test_redirect_if_not_logged_in(self):
        response=self.client.get(reverse('my-borrowed'))
        self.assertRedirects(response,'/accounts/login/?next=/catalog/mybooks/')
        
    def test_logged_in_uses_correct_template(self):
        login=self.client.login(username='testuser1',password='qazxswedc')
        response=self.client.get(reverse('my-borrowed'))

        self.assertEqual(str(response.context['user']),'testuser1')
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'borrowed_list_user.html')

    def test_only_borrowed_books_in_list(self):
        login=self.client.login(username='testuser1',password='qazxswedc')
        response=self.client.get(reverse('my-borrowed'))
        
        self.assertEqual(str(response.context['user']),'testuser1')
        self.assertEqual(response.status_code,200)
        self.assertTrue('bookinstance_list' in response.context)
        self.assertEqual(len(response.context['bookinstance_list']),0)

        books=BookInstance.objects.all()[:10]
        
        for book in books:
            book.status='o'
            book.save()

        response=self.client.get(reverse('my-borrowed'))

        self.assertEqual(str(response.context['user']),'testuser1')
        self.assertEqual(response.status_code,200)

        self.assertTrue('bookinstance_list' in response.context)

        for bookitem in response.context['bookinstance_list']:
            self.assertEqual(response.context['user'],bookitem.borrower)
            self.assertEqual('o',bookitem.status)

    def test_pages_ordered_by_due_date(self):

        for book in BookInstance.objects.all():
            book.status='o'
            book.save()

        login=self.client.login(username='testuser1',password='qazxswedc')
        response=self.client.get(reverse('my-borrowed'))

        self.assertEqual(str(response.context['user']),'testuser1')
        self.assertEqual(response.status_code,200)        
        self.assertEqual(len(response.context['bookinstance_list']),15)

        last_date=0

        for book in response.context['bookinstance_list']:
            if last_date == 0:
                last_date=book.due_back
            else:
                self.assertTrue(last_date <= book.due_back)

class RenewBookInstancesViewTest(TestCase):

    def setUp(self):
        test_user1=User.objects.create_user(username='testuser1',password='qazxswedc')
        test_user2=User.objects.create_user(username='testuser2',password='zaqwsxcde')

        test_user1.save()
        test_user2.save()

        permission=Permission.objects.get(name='Set book as returned')

        test_user2.user_permissions.add(permission)
        test_user2.save()
        
        test_author=Author.objects.create(first_name='John',last_name='Smith')
        test_genre=Genre.objects.create(name='Fantasy')
        test_book=Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFG',
            author=test_author
            )

        genre_objects_for_book=Genre.objects.all()
        test_book.genre.set(genre_objects_for_book)
        test_book.save()
        
        return_date=datetime.date.today()+datetime.timedelta(days=5)
        self.test_bookinstance1=BookInstance.objects.create(
                book=test_book,
                imprint='Unlikely Imprint, 2018',
                due_back=return_date,
                borrower=test_user1,
                status='o',
                )

        return_date=datetime.date.today()+datetime.timedelta(days=5)
        self.test_bookinstance2=BookInstance.objects.create(
                book=test_book,
                imprint='Unlikely Imprint, 2018',
                due_back=return_date,
                borrower=test_user2,
                status='o',
                )

    def test_redirect_if_not_logged_in(self):
        response=self.client.get(reverse('book-instance-update',kwargs={'pk':self.test_bookinstance1.pk}))
        self.assertEqual(response.status_code,302)
        self.assertTrue(response.url.startswith('/accounts/login/'))
        
    def test_redirect_if_logged_in_but_not_correct_permission(self):
        login=self.client.login(username='testuser1',password='qazxswedc')
        response=self.client.get(reverse('book-instance-update',kwargs={'pk':self.test_bookinstance1.pk}))
        self.assertEqual(response.status_code,302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_logged_in_with_permission_borrowed_book(self):    
        login=self.client.login(username='testuser2',password='zaqwsxcde')
        response=self.client.get(reverse('book-instance-update',kwargs={'pk':self.test_bookinstance2.pk}))
        self.assertEqual(response.status_code,200)

    def test_logged_in_with_permission_another_users_borrowed_book(self):
        login=self.client.login(username='testuser2',password='zaqwsxcde')
        response=self.client.get(reverse('book-instance-update',kwargs={'pk':self.test_bookinstance2.pk}))
        self.assertEqual(response.status_code,200)
        
    def test_HTTP404_for_invalid_book_if_logged_in(self):
        test_uid=uuid.uuid4()
        
        login=self.client.login(username='testuser2',password='zaqwsxcde')
        response=self.client.get(reverse('book-instance-update',kwargs={'pk':test_uid}))
        self.assertEqual(response.status_code,404)

    def test_uses_correct_template(self):
        login=self.client.login(username='testuser2',password='zaqwsxcde')
        response=self.client.get(reverse('book-instance-update',kwargs={'pk':self.test_bookinstance1.pk}))
       
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'bookinstance_form.html')

    def test_form_update_date_initially_has_date_three_weeks_in_future(self):
        login=self.client.login(username='testuser2',password='zaqwsxcde')
        response=self.client.get(reverse('book-instance-update',kwargs={'pk':self.test_bookinstance1.pk}))
       
        self.assertEqual(response.status_code,200)
        date_3_weeks_in_future=datetime.date.today()+datetime.timedelta(weeks=3)
        self.assertEqual(response.context['form'].initial['due_back'],date_3_weeks_in_future)

    def test_redirects_to_all_borrowed_book_list_on_success(self):
        login=self.client.login(username='testuser2',password='zaqwsxcde')
        valid_date_in_future=datetime.date.today()+datetime.timedelta(weeks=2)
        response=self.client.post(reverse('book-instance-update',kwargs={'pk':self.test_bookinstance1.pk,}),{'due_back':valid_date_in_future,})
        self.assertRedirects(response,reverse('all-borrowed'))
        
    def test_form_invalid_update_date_past(self):
        login=self.client.login(username='testuser2',password='zaqwsxcde')
        date_in_past=datetime.date.today()-datetime.timedelta(weeks=1)
        response=self.client.post(reverse('book-instance-update',kwargs={'pk':self.test_bookinstance1.pk,}),{'due_back':date_in_past,})
       
        self.assertEqual(response.status_code,200)
        self.assertFormError(response,'form','due_back','Invalid date - renewal in past')

    def test_form_invalid_update_date_future(self):
        login=self.client.login(username='testuser2',password='zaqwsxcde')
        date_in_future=datetime.date.today()+datetime.timedelta(weeks=5)
        response=self.client.post(reverse('book-instance-update',kwargs={'pk':self.test_bookinstance1.pk,}),{'due_back':date_in_future,})
       
        self.assertEqual(response.status_code,200)
        self.assertFormError(response,'form','due_back','Invalid date - renewal more than 4 weeks ahead')

        

    


        


        

        
        

        

        
            
        
        

        



        
                
    
