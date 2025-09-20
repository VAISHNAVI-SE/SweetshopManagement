from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from .models import Sweet, Purchase

class AuthAndSweetTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(username='admin', password='adminpass')
        self.user = User.objects.create_user(username='alice', password='alicepass')

    def obtain_token(self, username, password):
        url = reverse('login')
        resp = self.client.post(url, {'username': username, 'password': password}, format='json')
        print(resp.status_code, resp.data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        return resp.data['access']

    def test_register_and_login(self):
        url = reverse('register')
        resp = self.client.post(url, {'username': 'bob', 'password': 'Bob@1234!', 'password2': 'Bob@1234!'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', resp.data)

        token = self.obtain_token('bob', 'Bob@1234!')
        self.assertTrue(token)

    def test_create_sweet_requires_auth(self):
        url = reverse('sweet-list')
        data = {"name": "Ladoo", "category": "Indian", "price": "10.00", "quantity": 20}
        # unauthenticated → 401/403
        resp = self.client.post(url, data, format='json')
        self.assertIn(resp.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

        # authenticated via token
        token = self.obtain_token('alice', 'alicepass')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        resp = self.client.post(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Sweet.objects.count(), 1)

    def test_purchase_decrements_stock(self):
        sweet = Sweet.objects.create(name='Barfi', category='Indian', price='5.00', quantity=10)
        token = self.obtain_token('alice', 'alicepass')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        url = reverse('sweet-purchase', kwargs={'pk': sweet.pk})
        resp = self.client.post(url, {'quantity': 3}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        sweet.refresh_from_db()
        self.assertEqual(sweet.quantity, 7)
        self.assertEqual(Purchase.objects.count(), 1)

    def test_restock_admin_only(self):
        sweet = Sweet.objects.create(name='Rasgulla', category='Indian', price='4.00', quantity=5)
        # normal user token
        token = self.obtain_token('alice', 'alicepass')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        url = reverse('sweet-restock', kwargs={'pk': sweet.pk})
        resp = self.client.post(url, {'quantity': 10}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        # admin token
        admin_token = self.obtain_token('admin', 'adminpass')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
        resp = self.client.post(url, {'quantity': 10}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        sweet.refresh_from_db()
        self.assertEqual(sweet.quantity, 15)
