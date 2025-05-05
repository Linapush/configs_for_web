from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal
from .models import *
from .forms import *
from .serializers import *


class SomeoneModelTest(TestCase):
    def setUp(self):
        self.partner_type = SomeoneType.objects.create(type_name="Оптовый")
        self.address = Address.objects.create(city="Москва", street="Ленина", house_number="10")
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.admin = User.objects.create_superuser(
            username='admin',
            password='admin',
            email='admin@example.com'
        )
        self.partner = Someone.objects.create(
            name="Test Someone",
            partner_type=self.partner_type,
            address=self.address,
            phone="+79001234567",
            email="test@example.com",
            rating=5
        )

    def test_partner_creation(self):
        self.assertEqual(self.partner.name, "Test Someone")
        self.assertEqual(self.partner.email, "test@example.com")
        self.assertEqual(self.partner.phone, "+79001234567")

    def test_partner_unique_email(self):
        with self.assertRaises(Exception):
            Someone.objects.create(
                name="Duplicate Someone",
                partner_type=self.partner_type,
                address=self.address,
                phone="+79001234568",
                email="test@example.com"
            )

    def test_partner_form_validation(self):
        form = SomeoneForm(data={
            "name": "Test",
            "email": "test@example.com",
            "phone": "1234567890",  # ← без + → должно вызвать ошибку
            "partner_type": self.partner_type.id,
            "address": self.address.id
        })
        self.assertFalse(form.is_valid())
        self.assertIn("phone", form.errors)

    def test_partner_serializer_validation(self):
        data = {
            "name": "Invalid Phone",
            "email": "test@example.com",
            "phone": "12345",
            "partner_type": self.partner_type.id,
            "address": self.address.id
        }
        serializer = SomeoneSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("phone", serializer.errors)

    def test_sale_history_serializer_validation(self):
        data = {
            "partner": self.partner.id,
            "product": Something.objects.create(
                title="Test Something",
                product_type=SomethingType.objects.create(title="Тип", coefficient=1.0),
                price=Decimal('100.00')
            ).id,


            "quantity": -5  # negative quantity should be invalid
        }
        serializer = SaleHistorySerializer(data=data)
        
        is_valid = serializer.is_valid()
        if is_valid:
            print("Serializer unexpectedly valid with data:", data)
            print("Validated data:", serializer.validated_data)

        else:
            print("Serializer errors:", serializer.errors)
        
        self.assertFalse(is_valid)

        self.assertIn("quantity", serializer.errors)

    def test_partner_list_view(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('partner_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Someone")

    def test_add_sale_view(self):
        self.client.login(username='admin', password='admin')
        product_type = SomethingType.objects.create(title="Телефоны", coefficient=1.0)
        product = Something.objects.create(title="iPhone", product_type=product_type, price=Decimal('1000.00'))
        data = {
            "product": product.id,
            "quantity": 10,
            "sale_date": "2025-01-01",
            "price_per_unit": "100.00"
        }
        response = self.client.post(reverse('add_sale', args=[self.partner.id]), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(SaleHistory.objects.filter(quantity=10).exists())

    def test_partner_edit_view(self):
        self.client.login(username='admin', password='admin')
        data = {
            "name": "Updated Name",
            "email": "updated@example.com",
            "phone": "+79007654321",
            "partner_type": self.partner_type.id,

            "address": self.address.id,
            "rating": 5
        }
        response = self.client.post(reverse('partner_edit', args=[self.partner.id]), data)

        self.assertEqual(response.status_code, 302)
        
        self.partner.refresh_from_db()
        self.assertEqual(self.partner.name, "Updated Name")


    def test_unauthorized_access_to_add_sale(self):
        response = self.client.post(reverse('add_sale', args=[self.partner.id]), {
            "product": Something.objects.create(
                title="Test",
                product_type=SomethingType.objects.create(title="Тип", coefficient=1.0),
                price=Decimal('100.00')
            ).id,
            "quantity": 5,
            "price_per_unit": "100.00"
        })
        self.assertEqual(response.status_code, 302)