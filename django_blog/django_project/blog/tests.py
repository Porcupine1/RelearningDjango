from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from .models import Post


class BlogTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = get_user_model().objects.create(
            username="testuser", email="test@email.com", password="secret"
        )

        cls.post = Post.objects.create(
            title="A good title",
            body="Nice body content",
            author=cls.user,
        )

    def test_post_model(self):
        self.assertEqual(self.post.title, "A good title")
        self.assertEqual(self.post.body, "Nice body content")
        self.assertEqual(self.post.author.username, "testuser")
        self.assertEqual(str(self.post), "A good title")
        self.assertEqual(self.post.get_absolute_url(), "/post/1/")

    def test_url_exists_at_correct_location_listview(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_url_exists_at_correct_location_detailview(self):
        response = self.client.get("/post/1/")
        self.assertEqual(response.status_code, 200)

    def test_post_listview(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nice body content")
        self.assertTemplateUsed("home.html")

    def test_post_detailview(self):
        response = self.client.get(reverse("post-detail", kwargs={"pk": self.post.pk}))
        no_response = self.client.get("/post/10000/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(no_response.status_code, 404)
        self.assertContains(response, "A good title")
        self.assertTemplateUsed("post-detail.html")

    def test_post_createview(self):
        response = self.client.post(
            reverse("post-new"),
            {"title": "Test title", "body": "Test body", "author": self.user.id},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Post.objects.last().title, "Test title")
        self.assertEqual(Post.objects.last().body, "Test body")

    def test_post_update(self):
        response = self.client.post(
            reverse("post-edit", kwargs={'pk': 1}),
            {"title": "New title", "body": "New body"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Post.objects.last().title, "New title")
        self.assertEqual(Post.objects.last().body, "New body")

    def test_post_delete(self):
        response = self.client.post(
            reverse('post-delete', kwargs={'pk': self.post.pk})
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Post.objects.count(), 0)
