from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from api.models import ToDo
from api.serializers import ToDoSerializer


TODOS_URL = reverse('api:todo-list')


def get_todo_detail_url(todo_id):
    """ Return detail ToDo URL """
    return reverse('api:todo-detail', args=[todo_id])


class PublicToDoAPITests(TestCase):
    """ Test the publicly available ToDo API """

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """ Test login is required for accessing todo endpoints """
        response = self.client.get(TODOS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateToDoAPITests(TestCase):
    """ Test the authenticated ToDos API """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'djsbalakrishnan',
            'password123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_todos_for_user(self):
        """ Test retrieving list of todos """
        ToDo.objects.create(user=self.user, title="Complete the ToDo App")
        ToDo.objects.create(
            user=self.user, title="Another reminder!", description="Testing the Todos")

        res = self.client.get(TODOS_URL)

        todos = ToDo.objects.all().order_by('-title')
        serializer = ToDoSerializer(todos, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_todos_limited_to_user(self):
        """ Test that todos for the authenticated user are returned """
        sec_user = get_user_model().objects.create_user(
            'djsb',
            'password1234'
        )
        ToDo.objects.create(
            user=sec_user, title="Second User Todo", description="Second User Todo")
        todo = ToDo.objects.create(user=self.user, title="Current User Todo")

        response = self.client.get(TODOS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], todo.title)

    def test_create_valid_todo(self):
        """ Test valid todo creation for user """
        payload = {
            'title': 'This is a test Todo',
            'description': 'This is a test Todo description',
            'completed': True
        }

        self.client.post(TODOS_URL, payload)

        todo_exist = ToDo.objects.filter(
            user=self.user,
            title=payload['title']
        ).exists()

        self.assertTrue(todo_exist)

    def test_create_invalid_todo(self):
        """ Test invalid todo creation for user """
        payload = {
            'title': ''
        }
        response = self.client.post(TODOS_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_todos_by_id(self):
        """ Test viewing a todo detail """
        todo = ToDo.objects.create(user=self.user, title="A sample todo")
        url = get_todo_detail_url(todo.id)

        response = self.client.get(url)
        serializer = ToDoSerializer(todo)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_todos_by_id_wrong_user(self):
        """ Test retrieving a todo detail by unathorized user """
        sec_user = get_user_model().objects.create_user(
            'djsb',
            'password1234'
        )
        todo = ToDo.objects.create(
            user=sec_user, title="Second User Todo", description="Second User Todo")
        url = get_todo_detail_url(todo.id)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_todo_by_id_correct_user(self):
        """ Test deleting a todo by user """
        todo = ToDo.objects.create(
            user=self.user, title="A sample todo to delete")
        url = get_todo_detail_url(todo.id)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_todo_by_id_wrong_user(self):
        """ Test deleting a todo by unathorized user """
        sec_user = get_user_model().objects.create_user(
            'djsb',
            'password1234'
        )
        todo = ToDo.objects.create(
            user=sec_user, title="Second User Todo", description="Second User Todo")
        url = get_todo_detail_url(todo.id)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_partial_update_todo(self):
        """ Test updating a todo with http patch """
        todo = ToDo.objects.create(
            user=self.user, title="A sample todo to patch")
        payload = {
            'description': 'Adding new description',
            'completed': True
        }
        url = get_todo_detail_url(todo.id)
        self.client.patch(url, payload)

        todo.refresh_from_db()
        self.assertEqual(todo.description, payload['description'])
        self.assertEqual(todo.completed, payload['completed'])

    def test_full_update_todo(self):
        """ Test updating a todo with http put """
        todo = ToDo.objects.create(
            user=self.user, title="A sample todo to put")
        payload = {
            'title': 'New Title',
            'description': 'New description',
            'completed': True
        }
        url = get_todo_detail_url(todo.id)
        self.client.put(url, payload)

        todo.refresh_from_db()
        self.assertEqual(todo.title, payload['title'])
        self.assertEqual(todo.description, payload['description'])
        self.assertEqual(todo.completed, payload['completed'])
