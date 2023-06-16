import datetime
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from photoshare.models import Photo, Category
from .models import Comment
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from photoshare import urls
from .forms import CommentEditForm
# Create your tests here.
class LikesViewTests(TestCase) :

    # tests the likes_per_photo with an unauthenticated user 
    def test_likes_per_photo_with_unauthenticated_user(self) :
        target_url = reverse('likes:likes_per_photo', args=(1,))
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        redirect_url = f"{reverse('login')}?next={target_url}"
        self.assertRedirects(response, redirect_url)

    # testes the likes_per_photo with an inexisting photo 
    def test_likes_per_photo_with_unexisting_photo(self):
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
        # check the context of the response 
        self.assertEqual(response.context['photo'].description, 'blabla')
        self.assertEqual(response.context['photo'], photo)
        self.assertQuerysetEqual(response.context['likes'], [])

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



class AddCommentViewTests(TestCase) :
    def create_photo(self, description, category) :
        # create a test user and authenticate him
        self.user = User.objects.create_user(username='testuser', password='test')
        self.client.login(username='testuser', password='test')
        # create a test category 
        test_cat = Category.objects.create(name=category)
        image = SimpleUploadedFile('test_photo.jpg', b"content_file", 'image/jpeg')
        test_photo = Photo.objects.create(description=description, category=test_cat, image=image, created_by=self.user)
        self.client.logout()
        return test_photo


    # tests the view function with an unauthenticated user  
    def test_add_comment_with_unauthenticated_user(self) :
        photo = self.create_photo('test photo', 'travel')
        target_url = reverse('likes:add_comment', args=(photo.id,))
        response = self.client.post(target_url)
        self.assertEqual(response.status_code, 302)
        expected_url = f"{reverse('login')}?next={target_url}"
        #expected_query_strings = {'next' : target_url}
        self.assertRedirects(response, expected_url)

    # tests the view function with unexsting photo 
    def test_add_comment_to_unexisting_photo(self) :
        target_url = reverse('likes:add_comment', args=(1,))
        # create a user and log him in
        user = User.objects.create_user(username='test', password='testpass')
        self.client.login(username='test', password='testpass')
        response = self.client.post(target_url, {'description' : 'test'})
        self.assertEqual(response.status_code, 404)
    
    # tests the view function with axisting photo 
    def test_add_comment_with_existing_photo(self) :
        # create a photo 
        test_photo = self.create_photo('test photo', 'test category')
        # create a user instance and log him in
        user = User.objects.create_user(username='test', password='testpassword')
        self.client.login(username='test', password='testpassword')
        target_url = reverse('likes:add_comment', args=(test_photo.id,))
        response = self.client.post(target_url, {'comment_text' : 'this is a test for adding a comment'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('detail_photo', args=(test_photo.id,)))
        # get the last comment 
        last_comment = Comment.objects.last()
        self.assertEqual(last_comment.comment_text, 'this is a test for adding a comment')
        self.assertEqual(last_comment.created_by, user)
        self.assertEqual(last_comment.photo, test_photo)

# class to test the operation of comments_per_photo view 
class CommentsPerPhotoViewTests(TestCase) :
    # function that creates a photo 
    def create_photo_for_test(self, description, category, is_user_authenticated) :
        test_category = Category.objects.create(name=category)
        image_file = SimpleUploadedFile('myimage.png', b"content_file", 'image/png')
        self.user = User.objects.create_user(username='test', password='test')
        self.client.login(username='test', password='test')
        test_photo = Photo.objects.create(description=description, category=test_category, image=image_file, created_by=self.user)
        if is_user_authenticated : 
            return self.user, test_photo
        self.client.logout()
        return test_photo
    # test comments_per_photo for unauthenticated user 
    def test_comments_per_photo_with_unauthenticated_user(self) :
        test_photo = self.create_photo_for_test('this is a test', 'test category', False)
        target_url = reverse('likes:comments_per_photo', args=(test_photo.id,))
        # send a get request to the target url
        response = self.client.get(target_url)
        # check that response is a redirect 
        self.assertEqual(response.status_code, 302)
        redirect_url = f"{reverse('login')}?next={target_url}"
        self.assertRedirects(response, redirect_url)

    # test comments_per_photo with unexisting photo 
    def test_comments_per_photo_with_unexisting_photo(self) :
        # create a user and log him in
        self.user = User.objects.create_user(username='test', password='test')
        self.client.login(username='test', password='test')
        target_url = reverse('likes:comments_per_photo', args=(1,))
        response = self.client.get(target_url)
        # check that the response is 404 
        self.assertEqual(response.status_code, 404)
    
    # test comments_per_photo with a user to which the photo doesn't belong 
    def test_comments_per_photo_with_user_not_owner_of_photo(self) :
        test_photo = self.create_photo_for_test('test image', 'test category', False)
        # create a user and authenticate him 
        self.user = User.objects.create_user(username='testtest', password='pass')
        self.client.login(username='testtest', password='pass')
        target_url = reverse('likes:comments_per_photo', args=(test_photo.id,))
        response = self.client.get(target_url)
        # check that the response is a redirect 
        self.assertEqual(response.status_code, 302)
        # check that the redirect url is the following 
        redirect_url = f"{reverse('gallery')}"
        self.assertRedirects(response, redirect_url)
    
    # test the comments_per_photo with user who created the photo (owner)
    def test_comments_per_photo_with_creator_of_photo(self) :
        user, test_photo = self.create_photo_for_test('test photo', 'categ', True)
        target_url = reverse('likes:comments_per_photo', args=(test_photo.id,))
        response = self.client.get(target_url)
        # check the response is 200 OK
        self.assertEqual(response.status_code, 200)
        # check the context of response has the photo just created 
        self.assertTrue(isinstance(response.context['photo'], Photo))
        self.assertEqual(response.context['photo'].description, 'test photo')
        

# class that tests the operation of edit_comment view 
class EditCommentViewTests(TestCase) :
    # method that creates and returns a user 
    def create_user(self, username, password) :
        user = User.objects.create_user(username=username, password=password)
        return user 
    # method that creates a photo and a comment 
    def create_photo_and_comment(self, description_photo, category, comment_text) :
        user = self.create_user('testuser', 'testpassword')
        category = Category.objects.create(name="testCategory")
        image_file = SimpleUploadedFile('image.jpg', b"content_file", 'image/jpeg')
        photo = Photo.objects.create(description=description_photo, category=category,image=image_file, created_by=user)
        comment = Comment.objects.create(comment_text=comment_text, photo=photo, created_by=user)
        return user, photo, comment 
    # tests the edit_comment for an unauthenticated user 
    def test_edit_comment_with_unauthenticated_user(self) :
        # no such commment with id=1 exists in testdatabase, since it's not created
        target_url = reverse('likes:edit_comment', args=(1,))
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={target_url}")

    # tests the edit_comment with an unexisting comment 
    def test_edit_comment_with_unexisting_comment(self) :
        user = self.create_user('test', 'test')
        self.client.login(username='test', password='test')
        target_url = reverse('likes:edit_comment', args=(1,))
        response = self.client.get(target_url)
        # check that the response returned a 404 
        self.assertEqual(response.status_code, 404)

    # tests the edit_comment with a user not owner of the comment 
    def test_edit_comment_with_user_not_owner_of_comment(self) :
        user1, photo_of_user1, comment_of_user1 = self.create_photo_and_comment('test photo', 'test category', 'testcomment')
        # create a second user and authenticate him
        user2 = self.create_user('user2', 'user2')
        self.client.login(username='user2', password='user2')
        # request the edit page for the comment of user1
        target_url = reverse('likes:edit_comment', args=(comment_of_user1.id,))
        response_for_get = self.client.get(target_url)
        response_for_post = self.client.post(target_url,{})
        # check that the response is a redirect 
        self.assertEqual(response_for_get.status_code, 302)
        self.assertRedirects(response_for_get, reverse('gallery'))
        self.assertEqual(response_for_post.status_code, 302)
        self.assertRedirects(response_for_post, reverse('gallery'))

    # tests the edit_comment with a user owner of the comment in get request
    def test_edit_comment_with_get_request(self) :
        # first create a user, photo of the user and comment of the same user 
        user, photo, comment = self.create_photo_and_comment('my photo', 'my category', 'my comment')
        self.client.login(username='testuser', password='testpassword')
        target_url = reverse('likes:edit_comment', args=(comment.id,))
        response = self.client.get(target_url)
        # check the response status and context 
        self.assertEqual(response.status_code, 200)
        self.assertEqual(isinstance(response.context['form'], CommentEditForm), True)
    
    # test the edit_comment with a user owner of the comment in POST request 
    def test_edit_comment_with_post_request(self) :
        user, photo, comment = self.create_photo_and_comment('myphoto', 'testcategory', 'mycomment')
        self.client.login(username='testuser', password='testpassword')
        target_url = reverse('likes:edit_comment', args=(comment.id,))
        response = self.client.post(target_url, {'comment_text' : 'test'})
        # check the response status and context
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('likes:comments_per_photo', args=(photo.id,)))

# class to test the delete_comment view 
class DeleteCommentViewTests(TestCase) :
    # function that creates a comment 
    def create_comment(self, description_photo, category_photo,comment_text, is_regular_user):
        category = Category.objects.create(name='Test')
        image_file = SimpleUploadedFile('image.png', b"content_file", 'image/png')
        user = User.objects.create_user(username='regular', password='regular')
        superuser = User.objects.create_superuser(username='superuser', password='superuser')
        if is_regular_user :
            photo = Photo.objects.create(description=description_photo, category=category, image=image_file, created_by=superuser)
            # the comment belongs to a regular user
            comment_regular = Comment.objects.create(comment_text=comment_text, photo=photo, created_by=user)
            return user, comment_regular
        else :
            photo= Photo.objects.create(description=description_photo, category=category, image=image_file, created_by=user)
            # the comment belongs to regular user
            comment = Comment.objects.create(comment_text=comment_text, photo=photo, created_by=user)
            return superuser, comment


    # test the delete_comment with unauthenticated user 
    def test_delete_comment_with_unauthenticated_user(self) :
        target_url = reverse('likes:delete_comment', args=(1,))
        response = self.client.delete(target_url)
        # check the response status and redirect url
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={target_url}")
    
    # test the delete_comment with an unexisting comment 
    def test_delete_comment_with_unexisting_comment(self) :
        user = User.objects.create_user(username='testuser', password='test')
        self.client.login(username='testuser', password='test')
        target_url = reverse('likes:delete_comment', args=(1,))
        response = self.client.delete(target_url)
        # check that response is a 404
        self.assertEqual(response.status_code, 404)
    
    # test the delete_comment with a user not owner and not superuser 
    def test_delete_comment_with_regular_user_and_not_owner(self) :
        # the comment returned is created by regular user which is also returned
        user, comment = self.create_comment('myphoto', 'catphoto', 'my comment', True)
        # create a second user and authenticate him
        user2 = User.objects.create_user(username='testuser', password='testuser')
        self.client.login(username='testuser', password='testuser')
        target_url = reverse('likes:delete_comment', args=(comment.id,))
        # user2 is not a superuser and also not owner of the comment 
        response = self.client.delete(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('gallery'))
    
    # test delete_comment view with user owner of the comment 
    def test_delete_comment_with_user_owner_of_comment(self) :
        user, comment = self.create_comment('testphoto', 'testcategory', 'testcomment', True)
        # authenticate the user who owns the comment 
        self.client.login(username='regular', password='regular')
        target_url = reverse('likes:delete_comment',args=(comment.id,))
        response = self.client.delete(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('detail_photo', args=(comment.photo.id,)))
    
    # test delete_comment view with superuser and comment not his
    def test_delete_comment_with_super_user_and_not_owner_of_comment(self) :
        user, comment = self.create_comment('test photo', 'test category', 'comment test', True)
        # authenticate the superuser 
        self.client.login(username='superuser', password='superuser')
        target_url = reverse('likes:delete_comment', args=(comment.id,))
        response = self.client.delete(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('likes:comments_per_photo', args=(comment.photo.id,)))

# class to test the operation of the hide_comment view 
class HideCommentViewTests(TestCase) :
    def create_photo_with_someone_else_comment_on_it(self, description, category, comment_text):
        self.user = User.objects.create_user(username='photo_owner', password='password')
        image_file = SimpleUploadedFile('image.png', b"content_file", 'image/png')
        category = Category.objects.create(name=category)
        # this is a photo instance created by the user photo_owner
        photo = Photo.objects.create(description=description, category=category,image=image_file, created_by=self.user)
        # create a comment on this photo, but by another user 
        self.user = User.objects.create_user(username='comment_owner', password='password')
        comment = Comment.objects.create(comment_text=comment_text, photo=photo, created_by=self.user)
        return photo, comment
    # test the hide_comment view with unauthenticated user 
    def test_hide_comment_with_unauthenticated_user(self) :
        target_url = reverse('likes:hide_comment', args=(1,))
        response = self.client.get(target_url)
        # check that the response is a redirect
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={target_url}")
    
    # test the hide_comment view with an unexisting comment 
    def test_hide_comment_with_unexisting_comment(self) :
        # create a user and authenticate him
        user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password ='testpassword')
        target_url = reverse('likes:hide_comment', args=(1,))
        response = self.client.get(target_url)
        # check that the response is a 404
        self.assertEqual(response.status_code, 404)
    
    # test hide_comment with a user trying to hide a comment not on one of his photos
    def test_hide_comment_not_on_his_own_photo(self) :
        # create a photo having someone else comment 
        photo, comment = self.create_photo_with_someone_else_comment_on_it('test photo', 'test category', 'test comment')
        # authenticate the comment_owner since the photo is not his 
        self.client.login(username='comment_owner', password='password')
        # try to hide the comment on a photo not his 
        target_url = reverse('likes:hide_comment', args=(comment.id,))
        reponse = self.client.get(target_url)
        # check that the response is a redirect 
        self.assertEqual(reponse.status_code, 302)
        self.assertRedirects(reponse, reverse('gallery'))


    













        
