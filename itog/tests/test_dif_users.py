from rest_framework import status
from rest_framework.test import APITestCase
from profiles.models import Profile
from posts.models import Ingredient, Recipi


class Account1Tests(APITestCase):
    def setUp(self):
        self.userS = Profile.objects.create_superuser(
            first_name='zxcdsadas',
            last_name='qwdasdasdsadsadadeqweqwe',
            email='asdasdsmail@mail.ru',
            username='USER_S'
        )
        self.user = Profile.objects.create(
            first_name='zxc',
            last_name='qweqweqwe',
            email='mail@mail.ru',
            username='USER'
        )

        self.ing = Ingredient.objects.create(
            name='ing1',
            measurement_unit='g'
        )
        self.ing2 = Ingredient.objects.create(
            name='ing2',
            measurement_unit='kg'
        )
        self.image = (
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAg"
            "MAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGV"
            "Kw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg=="
        )

    def test_user1(self):
        self.client.force_authenticate(user=self.user)
        url = '/api/recipes/'
        data = {
            'name': 'DabApps',
            "ingredients": [{"id": self.ing.id, "amount": 21}],
            "image": self.image,
            "text": "text",
            "cooking_time": 3
        }

        response = self.client.post(path=url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Recipi.objects.count(), 1)
        self.assertEqual(Recipi.objects.get().name, 'DabApps')
        self.assertEqual(Recipi.objects.get().author, self.user)

    def test_user2(self):
        self.client.force_authenticate(user=self.userS)
        url = '/api/recipes/'
        data = {
            'name': 'second',
            "ingredients": [{"id": self.ing2.id, "amount": 321}],
            "image": self.image,
            "text": "text",
            "cooking_time": 3
        }

        response = self.client.post(path=url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Recipi.objects.count(), 1)
        self.assertEqual(Recipi.objects.get().name, 'second')
        self.assertEqual(Recipi.objects.get().author, self.userS)
