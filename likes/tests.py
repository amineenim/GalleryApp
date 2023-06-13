import datetime
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from photoshare.models import Photo, Category
from .models import Comment
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
# Create your tests here.
class LikesViewTests(TestCase) :

    # testes the likes_per_photo with an inexisting photo 
    def test_likes_per_photo_with_unexsiting_photo(self):
        # create a user 
        self.user = User.objects.create_user(username="test", password="testpassword")
        self.client.login(username="test", password="testpassword")
        test_url = reverse('likes:likes_per_photo', args=(80,))
        response = self.client.get(test_url)
        self.assertEqual(response.status_code, 404)

    # tests the likes_per_photo with a user owner of the photo 
    def test_likes_per_photo_with_owner_of_photo(self):
        self.user = User.objects.create_user(username="test", password="test123")
        self.client.login(username="test", password="test123")
        # create a category 
        test_category = Category.objects.create(name="testCat")
        # simulate the image file 
        image_file = SimpleUploadedFile('bg.jpg', b"file_content", "image/jpeg")
        photo = Photo.objects.create(description="blabla",category=test_category, image=image_file, created_by=self.user)
        test_url = reverse('likes:likes_per_photo', args=(photo.id,))
        response = self.client.get(test_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Total number of likes')

    # tests the likes_per_photo with a user who doesn't own the photo 
    def test_likes_per_photo_with_not_owner_of_photo(self):
        self.user1 = User.objects.create_user(username="owner", password="test")
        self.user2 = User.objects.create_user(username="notowner", password="test12")
        test_category = Category.objects.create(name="test")
        image_file = SimpleUploadedFile('mypic.jpg', b"content_file", "image/jpeg")
        photo = Photo.objects.create(description="testest", category=test_category, image=image_file, created_by=self.user1)
        # authenticate the second user 
        self.client.login(username="notowner", password="test12")
        test_url = reverse('likes:likes_per_photo', args=(photo.id,))
        response = self.client.get(test_url)
        self.assertEqual(response.status_code, 302)
        


# class to test the comment Model method 
class CommentModelTests(TestCase) :
    
    # function that creates a comment in a given time
    def create_comment(self,comment_text, created_before):
        # create a user instance
        user = User.objects.create_user(username="testUser", password="test")
        # create a test category 
        test_category = Category.objects.create(name="my test category")
        # create a photo instance first
        image_file = SimpleUploadedFile('testimage.jpg', b"content_file", 'image/jpeg')
        test_photo = Photo.objects.create(description="test photo", category=test_category, image=image_file, created_by = user)
        created_at = timezone.now() - timezone.timedelta(seconds=created_before)
        test_comment = Comment.objects.create(comment_text=comment_text, photo=test_photo, created_by = user, created_at=created_at)
        return test_comment
    
    # test the get_when_created with comment in the last minute
    def test_get_when_created_with_comment_in_last_minute(self) :
        test_comment = self.create_comment('in last minute', 59)
        self.assertIn('seconds ago', test_comment.get_when_created())
    
    # test the get_when_created with comment in a minute and 1 second 
    def test_get_when_created_with_comment_before_one_minute_and_one_second(self) :
        test_comment = self.create_comment('before a minute and 1 second', 61)
        self.assertIn('minutes ago', test_comment.get_when_created())
    
    # test the get_when_created with comment created 59 minutes ago 
    def test_get_when_created_with_comment_before_59_minutes(self) :
        test_comment = self.create_comment("before 59 minutes", 59*60)
        self.assertIn('minutes ago', test_comment.get_when_created())
    
    # test the get_when_created with a comment in 1 hour and 1 second 
    def test_get_when_created_with_comment_before_1hour_and_1second(self) :
        test_comment = self.create_comment('before 1 hour, 1second', 3601)
        self.assertIn('1 hour ago', test_comment.get_when_created())
    
    # test get_when_created with a comment from a day minus 1 second 
    def test_get_when_created_with_comment_before_23hours_59minutes_and_59seconds(self) :
        test_comment = self.create_comment('before 23 hours 59 minutes 59 seconds', 23*3600+59*60+59)
        self.assertIn('23 hours ago', test_comment.get_when_created())
    
    # test get_when_created with a comment from a day plus 1 second 
    def test_get_when_created_with_comment_before_1day_and_1second(self) :
        test_comment = self.create_comment('before 1 day and 1 second ', 24*3600 + 1)
        self.assertIn('yesterday', test_comment.get_when_created())
    
    # test get_when_created with a comment from a day, 23hours, 59minutes and 59 seconds 
    def test_get_when_created_with_comment_before_1day_23hours_59minutes_and_59seconds(self) :
        test_comment = self.create_comment('before 1day 23 hours 59 minutes 59 seconds', 24*3600+23*3600+59*60+59)
        self.assertIn('yesterday', test_comment.get_when_created())
    
    # test get_when_created with a comment from 2 days 1 second
    def test_get_when_created_with_comment_before_2days_and_1second(self) :
        test_comment = self.create_comment('before 2 days and 1 second', 48*3600 + 1)
        self.assertTrue(isinstance(test_comment.get_when_created(), datetime.datetime))