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
            reminder_ampm='AM',
            status = "ACTIVE"
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
        
        # Convert the date string to a proper date object
        self.subscription_data = {
            'service_name': 'Netflix',
            'subscription_type': 'PAID',
            'price': '9.99',
            'billing_cycle': 'MONTHLY',
            'start_date': timezone.now().date(),  # Changed from isoformat string to actual date
            'category': 'STREAMING',
            'send_reminder': True,
            'reminder_days_ahead': 1,
            'reminder_hour': 9,
            'reminder_minute': 0,
            'reminder_ampm': 'AM',
            'status': 'ACTIVE'  # Also ensure status is set
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

    def test_cancel_subscription(self):
        """Test cancelling a subscription"""
        subscription = Subscription.objects.create(user=self.user, **self.subscription_data)
        # Use the cancel endpoint instead of delete
        response = self.client.post(f'/api/subscriptions/{subscription.id}/cancel/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify the subscription is cancelled but still exists
        updated_subscription = Subscription.objects.get(id=subscription.id)
        self.assertEqual(updated_subscription.status, 'CANCELLED')
        self.assertIsNotNone(updated_subscription.cancellation_date)

    # Add a separate test for deletion
    def test_delete_cancelled_subscription(self):
        """Test deleting a cancelled subscription"""
        # Create a cancelled subscription
        # subscription = Subscription.objects.create(
        #     user=self.user, 
        #     status='CANCELLED',
        #     cancellation_date=timezone.now().date(),
        #     **self.subscription_data
        # )
        # Fist Cancel
        subscription = Subscription.objects.create(user=self.user, **self.subscription_data)
        response = self.client.post(f'/api/subscriptions/{subscription.id}/cancel/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Now try to delete it
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
        
        # Create base subscription data
        self.subscription_data = {
            'service_name': 'Netflix',
            'subscription_type': 'PAID',
            'price': '9.99',
            'billing_cycle': 'MONTHLY',
            'start_date': timezone.now().date(),
            'category': 'STREAMING',
            'status': 'ACTIVE'
        }
        
        # Create an active subscription
        self.active_subscription = Subscription.objects.create(
            user=self.user,
            **self.subscription_data
        )
        
        # Create a cancelled subscription
        self.cancelled_subscription = Subscription.objects.create(
            user=self.user,
            service_name='Spotify',
            subscription_type='PAID',
            price='12.99',
            billing_cycle='MONTHLY',
            start_date=timezone.now().date(),
            category='MUSIC',
            status='CANCELLED',
            cancellation_date=timezone.now().date()
        )

    def test_view_cancelled_subscriptions(self):
        """Test that cancelled subscriptions can be viewed in a separate list"""
        response = self.client.get('/api/subscriptions/cancelled/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['cancelled_subscriptions']), 1)
        self.assertEqual(response.data['cancelled_subscriptions'][0]['service_name'], 'Spotify')
        self.assertEqual(response.data['cancelled_subscriptions'][0]['status'], 'CANCELLED')

    def test_active_subscriptions_exclude_cancelled(self):
        """Test that cancelled subscriptions don't appear in active subscriptions list"""
        response = self.client.get('/api/subscriptions/active/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['service_name'], 'Netflix')

    def test_cannot_delete_active_subscription(self):
        """Test that an active subscription cannot be deleted"""
        response = self.client.delete(f'/api/subscriptions/{self.active_subscription.id}/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Subscription.objects.filter(id=self.active_subscription.id).exists())

    def test_can_delete_cancelled_subscription(self):
        """Test that a cancelled subscription can be deleted"""
        response = self.client.delete(f'/api/subscriptions/{self.cancelled_subscription.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Subscription.objects.filter(id=self.cancelled_subscription.id).exists())

    def test_delete_all_cancelled(self):
        """Test that all cancelled subscriptions can be deleted at once"""
        # Create another cancelled subscription
        Subscription.objects.create(
            user=self.user,
            service_name='Disney+',
            subscription_type='PAID',
            price='7.99',
            billing_cycle='MONTHLY',
            start_date=timezone.now().date(),
            category='STREAMING',
            status='CANCELLED',
            cancellation_date=timezone.now().date()
        )
        
        # Verify we have 2 cancelled subscriptions
        self.assertEqual(Subscription.objects.filter(status='CANCELLED').count(), 2)
        
        # Delete all cancelled subscriptions
        response = self.client.delete('/api/subscriptions/delete_all_cancelled/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify all cancelled subscriptions are deleted
        self.assertEqual(Subscription.objects.filter(status='CANCELLED').count(), 0)
        # Verify active subscription still exists
        self.assertTrue(Subscription.objects.filter(status='ACTIVE').exists())

    def test_restore_cancelled_subscription(self):
        """Test that a cancelled subscription can be restored to active"""
        cancelled_subscription = Subscription.objects.create(
            user=self.user,
            service_name='Disney+',
            subscription_type='PAID',
            price='7.99',
            billing_cycle='MONTHLY',
            start_date=timezone.now().date(),
            category='STREAMING',
            status='CANCELLED',
            cancellation_date=timezone.now().date()
        )
        
        response = self.client.post(f'/api/subscriptions/{cancelled_subscription.id}/restore/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        restored_subscription = Subscription.objects.get(id=cancelled_subscription.id)
        self.assertEqual(restored_subscription.status, 'ACTIVE')
        self.assertIsNone(restored_subscription.cancellation_date)


# class FreeTrialEventTests(APITestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(
#             username='testuser',
#             email='test@example.com',
#             password='testpass123'
#         )
#         self.client = APIClient()
#         self.client.force_authenticate(user=self.user)
        
#         # Create base subscription data
#         self.no_reminder_subscription_data = {
#             'service_name': 'Netflix',
#             'subscription_type': 'FREE_TRIAL',
#             'price': '9.99',
#             'billing_cycle': 'MONTHLY',
#             'start_date': timezone.now().date(),
#             'category': 'STREAMING',
#             'status': 'ACTIVE'
#         }

#         self.with_reminder_subscription_data = {
#             'service_name': 'Youtube',
#             'subscription_type': 'FREE_TRIAL',
#             'price': '9.99',
#             'billing_cycle': 'MONTHLY',
#             'start_date': timezone.now().date(),
#             'category': 'STREAMING',
#             'status': 'ACTIVE',
#             'send_reminder': True,
#             'reminder_days_ahead': 1,
#             'reminder_hour': 9,
#             'reminder_minute': 0,
#             'reminder_ampm': 'AM'
#         }