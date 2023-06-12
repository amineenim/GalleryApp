from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from photoshare.models import Photo, Category
from django.core.files.uploadedfile import SimpleUploadedFile
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
        





