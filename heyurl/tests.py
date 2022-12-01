from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import Url

from random import choice
from string import ascii_letters,digits

class IndexTests(TestCase):
    def test_no_urls(self):
        """
        If no URLs exist, an appropriate message is displayed
        """
        response = self.client.get(reverse('index'))

        self.assertEqual(response.status_code,200)
        self.assertContains(response,'There are no URLs in the system yet!')
    

    def test_submitting_new_url_failure(self):
        """
        When submitting an invalid URL, an error is returned to the user
        """
        response = self.client.post(reverse('store'), data ={'original_full_url':'fff' })
        self.assertEqual(response.status_code,200)
        self.assertContains(response,"INVALID URL")



    def test_submitting_new_url_success(self):
        """
        When submitting a valid URL, a success message is displayed
        """
        response = self.client.post(reverse('store'), data ={'original_full_url':'http://google.com' })
        self.assertEqual(response.status_code,200)
        self.assertContains(response,"Storing a new URL object into storag")

    def test_visiting_short_url_missing(self):
        """
        If short URL does not exist, custom 404 page is displayed
        """
        # response = self.client.get(reverse('u/dne'))
        response = self.client.get(reverse('short_url',kwargs={'short_url':"sdfsd"}))
        self.assertEqual(response.status_code,404)


    def test_visiting_short_url(self):
        """
        If short URL exists, stats logged and redirected to original URL
        """
        # response = self.client.get(reverse('u/dne'))

        original_url = "http://bing.com"
        short_url = ''.join(choice(ascii_letters+digits) for a in range(5))
        Url(short_url = short_url, original_url =original_url, created_at= timezone.now(), updated_at =timezone.now()  ).save()


        response = self.client.get(reverse('short_url',kwargs={'short_url':short_url}))
        self.assertEqual(response.status_code,302)




        
