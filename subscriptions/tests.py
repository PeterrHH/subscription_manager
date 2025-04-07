from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Subscription
from .serializers import SubscriptionSerializer

class SubscriptionModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.subscription = Subscription.objects.create(
            user=self.user,
            service_name='Netflix',
            subscription_type='PAID',
            price=Decimal('9.99'),
            billing_cycle='MONTHLY',
            start_date=timezone.now().date(),
            category='STREAMING',
            send_reminder=True,
            reminder_days_ahead=1,
            reminder_hour=9,
            reminder_minute=0,
            reminder_ampm='AM'
        )

    def test_subscription_creation(self):
        """Test that a subscription can be created with all fields"""
        self.assertEqual(self.subscription.service_name, 'Netflix')
        self.assertEqual(self.subscription.price, Decimal('9.99'))
        self.assertTrue(self.subscription.send_reminder)
        self.assertEqual(self.subscription.reminder_hour, 9)

    def test_get_next_charge_date_monthly(self):
        """Test next charge date calculation for monthly subscriptions"""
        next_date = self.subscription.get_next_charge_date()
        self.assertIsNotNone(next_date)
        self.assertTrue(next_date >= timezone.now().date())

    def test_get_next_charge_date_weekly(self):
        """Test next charge date calculation for weekly subscriptions"""
        self.subscription.billing_cycle = 'WEEKLY'
        self.subscription.save()
        next_date = self.subscription.get_next_charge_date()
        self.assertIsNotNone(next_date)
        self.assertTrue(next_date >= timezone.now().date())

    def test_free_trial_subscription(self):
        """Test creating a free trial subscription"""
        free_trial = Subscription.objects.create(
            user=self.user,
            service_name='Spotify',
            subscription_type='FREE_TRIAL',
            billing_cycle='MONTHLY',
            start_date=timezone.now().date(),
            category='MUSIC',
            free_trial_length=30,
            free_trial_unit='DAYS'
        )
        self.assertEqual(free_trial.subscription_type, 'FREE_TRIAL')
        self.assertEqual(free_trial.free_trial_length, 30)

class SubscriptionSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.subscription_data = {
            'service_name': 'Netflix',
            'subscription_type': 'PAID',
            'price': '9.99',
            'billing_cycle': 'MONTHLY',
            'start_date': timezone.now().date().isoformat(),
            'category': 'STREAMING',
            'send_reminder': True,
            'reminder_days_ahead': 1,
            'reminder_hour': 9,
            'reminder_minute': 0,
            'reminder_ampm': 'AM'
        }

    def test_valid_subscription_serialization(self):
        """Test that valid subscription data is properly serialized"""
        serializer = SubscriptionSerializer(data=self.subscription_data)
        self.assertTrue(serializer.is_valid())

    def test_negative_price_validation(self):
        """Test that negative prices are rejected"""
        self.subscription_data['price'] = '-9.99'
        serializer = SubscriptionSerializer(data=self.subscription_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('price', serializer.errors)

    def test_reminder_fields_cleared_when_disabled(self):
        """Test that reminder fields are cleared when send_reminder is False"""
        self.subscription_data['send_reminder'] = False
        serializer = SubscriptionSerializer(data=self.subscription_data)
        self.assertTrue(serializer.is_valid())
        self.assertIsNone(serializer.validated_data['reminder_days_ahead'])
        self.assertIsNone(serializer.validated_data['reminder_hour'])

class SubscriptionAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        self.subscription_data = {
            'service_name': 'Netflix',
            'subscription_type': 'PAID',
            'price': '9.99',
            'billing_cycle': 'MONTHLY',
            'start_date': timezone.now().date().isoformat(),
            'category': 'STREAMING',
            'send_reminder': True,
            'reminder_days_ahead': 1,
            'reminder_hour': 9,
            'reminder_minute': 0,
            'reminder_ampm': 'AM'
        }

    def test_create_subscription(self):
        """Test creating a new subscription"""
        response = self.client.post('/api/subscriptions/', self.subscription_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Subscription.objects.count(), 1)
        self.assertEqual(Subscription.objects.get().service_name, 'Netflix')

    def test_create_free_trial_subscription(self):
        """Test creating a free trial subscription"""
        self.subscription_data['subscription_type'] = 'FREE_TRIAL'
        self.subscription_data['free_trial_length'] = 30
        self.subscription_data['free_trial_unit'] = 'DAYS'
        response = self.client.post('/api/subscriptions/', self.subscription_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Subscription.objects.get().free_trial_length, 30)

    def test_update_subscription(self):
        """Test updating an existing subscription"""
        subscription = Subscription.objects.create(user=self.user, **self.subscription_data)
        update_data = {'service_name': 'Netflix Premium'}
        response = self.client.patch(f'/api/subscriptions/{subscription.id}/', 
                                   update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Subscription.objects.get().service_name, 'Netflix Premium')

    def test_delete_subscription(self):
        """Test deleting a subscription"""
        subscription = Subscription.objects.create(user=self.user, **self.subscription_data)
        response = self.client.delete(f'/api/subscriptions/{subscription.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Subscription.objects.count(), 0)

    def test_reminder_settings(self):
        """Test updating reminder settings"""
        subscription = Subscription.objects.create(user=self.user, **self.subscription_data)
        update_data = {
            'send_reminder': True,
            'reminder_days_ahead': 2,
            'reminder_hour': 10,
            'reminder_minute': 30,
            'reminder_ampm': 'PM'
        }
        response = self.client.patch(f'/api/subscriptions/{subscription.id}/', 
                                   update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_subscription = Subscription.objects.get()
        self.assertEqual(updated_subscription.reminder_days_ahead, 2)
        self.assertEqual(updated_subscription.reminder_hour, 10)
        self.assertEqual(updated_subscription.reminder_minute, 30)
        self.assertEqual(updated_subscription.reminder_ampm, 'PM')


class DeletedSubscriptionTests(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create test subscriptions
        self.active_subscription = Subscription.objects.create(
            user=self.user,
            service_name='Netflix',
            subscription_type='PAID',
            price='9.99',
            billing_cycle='MONTHLY',
            start_date=timezone.now().date(),
            category='STREAMING',
            status='ACTIVE'
        )
        
        self.deleted_subscription = Subscription.objects.create(
            user=self.user,
            service_name='Spotify',
            subscription_type='PAID',
            price='12.99',
            billing_cycle='MONTHLY',
            start_date=timezone.now().date(),
            category='MUSIC',
            status='DELETED',
            cancellation_date=timezone.now()
        )

    def test_view_deleted_subscriptions(self):
        """Test that deleted subscriptions can be viewed in a separate list"""
        response = self.client.get('/api/subscriptions/deleted/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['service_name'], 'Spotify')
        self.assertEqual(response.data[0]['status'], 'DELETED')

    def test_active_subscriptions_exclude_deleted(self):
        """Test that deleted subscriptions don't appear in active subscriptions list"""
        response = self.client.get('/api/subscriptions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['service_name'], 'Netflix')

    def test_restore_deleted_subscription(self):
        """Test that a deleted subscription can be restored"""
        response = self.client.post(
            f'/api/subscriptions/{self.deleted_subscription.id}/restore/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify the subscription is now active
        restored_subscription = Subscription.objects.get(id=self.deleted_subscription.id)
        self.assertEqual(restored_subscription.status, 'ACTIVE')
        self.assertIsNone(restored_subscription.deleted_at)

    def test_permanent_delete_subscription(self):
        """Test that a subscription can be permanently deleted"""
        response = self.client.delete(
            f'/api/subscriptions/{self.deleted_subscription.id}/permanent/'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify the subscription is completely removed
        with self.assertRaises(Subscription.DoesNotExist):
            Subscription.objects.get(id=self.deleted_subscription.id)

    def test_filter_deleted_by_date_range(self):
        """Test that deleted subscriptions can be filtered by deletion date"""
        # Create a subscription deleted in the past
        past_deleted = Subscription.objects.create(
            user=self.user,
            service_name='Past Service',
            subscription_type='PAID',
            price='5.99',
            billing_cycle='MONTHLY',
            start_date=timezone.now().date(),
            category='OTHER',
            status='DELETED',
            deleted_at=timezone.now() - timedelta(days=30)
        )

        # Test filtering by date range
        response = self.client.get(
            '/api/subscriptions/deleted/',
            {
                'from_date': (timezone.now() - timedelta(days=7)).date().isoformat(),
                'to_date': timezone.now().date().isoformat()
            }
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['service_name'], 'Spotify')

    def test_deleted_subscription_details(self):
        """Test that detailed information about a deleted subscription can be viewed"""
        response = self.client.get(
            f'/api/subscriptions/deleted/{self.deleted_subscription.id}/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['service_name'], 'Spotify')
        self.assertEqual(response.data['status'], 'DELETED')
        self.assertIsNotNone(response.data['deleted_at'])

    def test_cannot_restore_nonexistent_subscription(self):
        """Test that attempting to restore a non-existent subscription returns an error"""
        response = self.client.post('/api/subscriptions/999/restore/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_restore_active_subscription(self):
        """Test that attempting to restore an active subscription returns an error"""
        response = self.client.post(
            f'/api/subscriptions/{self.active_subscription.id}/restore/'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)