from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from ..models import Tinylink, TinylinkLog
from .factories import TinylinkFactory, UserFactory, TinyLogFactory


class TinyLinkTest(APITestCase):

    def setUp(self):
        super(TinyLinkTest, self).setUp()
        self.tiny_link_list_url = reverse('tinylink_list')
        self.tiny_link_create_url = reverse('tinylink_create')
        self.user = User.objects.create_superuser(username='gunjan_test',
                                                  email='gunjan_test@kuwaitnet.com',
                                                  password=make_password('test1234'))
        self.tiny_link = Tinylink.objects.create(user=self.user,
                                                 long_url="http://www.example.com/thisisalongURL",
                                                 short_url="vB7f5b")
        self.tiny_log = TinylinkLog.objects.create(tinylink=self.tiny_link,
                                                   referrer='http://www.example.com/thisisalongURL',
                                                   user_agent='Gunjan Modi',
                                                   cookie='test:test',
                                                   remote_ip='127.0.0.1',
                                                   tracked=True)
        self.tiny_link_update_long_url = reverse('tinylink_update', kwargs={'pk': self.tiny_link.id,
                                                                            'mode': 'change-long'})
        self.tiny_link_update_short_url = reverse('tinylink_update', kwargs={'pk': self.tiny_link.id,
                                                                            'mode': 'change-short'})

        self.tiny_link_statistics = reverse('tinylink_statistics')
        self.tiny_link_db_stats = reverse('api_db_stats')
        self.tiny_link_api_stats = reverse('api_db_stats')
        self.tiny_link_url_stats = reverse('api_url_stats', kwargs={'short_url': self.tiny_link.short_url})
        self.tiny_link_expand_stats = reverse('api_tinylink_expand', kwargs={'short_url': self.tiny_link.short_url})

    def test_api_urls(self):
        """
        Superuser has permission superuser and admin

        """
        self.client.force_authenticate(user=self.user)
        tiny_link_list_response = self.client.get(path=self.tiny_link_list_url)
        tiny_link_create_response = self.client.post(path=self.tiny_link_create_url)
        tiny_link_update_long_response = self.client.post(path=self.tiny_link_update_long_url,
                                                          data={'long_url': 'http://www.example.com/thisisalongURLCustom'})
        tiny_link_update_short_response = self.client.post(path=self.tiny_link_update_short_url,
                                                           data={'long_url': 'http://www.example.com/thisisalongURLCustom', 'short_url': 'aaq12'})
        tiny_link_statistics_response = self.client.get(path=self.tiny_link_statistics, data={'testing': True})
        tiny_link_db_stats_response = self.client.get(path=self.tiny_link_db_stats)
        tiny_link_api_stats_response = self.client.get(path=self.tiny_link_api_stats)
        tiny_link_url_stats_response = self.client.get(path=self.tiny_link_url_stats)
        tiny_link_expand_stats_response = self.client.get(path=self.tiny_link_expand_stats)

        print("Testing:\nTiny Link List")
        self.assertEqual(tiny_link_list_response.status_code, status.HTTP_302_FOUND)
        print("Testing: Completed")

        print("\nTesting:\nTiny Link Created")
        self.assertEqual(tiny_link_create_response.status_code, status.HTTP_302_FOUND)
        print("Testing: Completed")

        print("\nTesting:\nTiny Link Updated For Long URL")
        self.assertEqual(tiny_link_update_long_response.status_code, status.HTTP_302_FOUND)
        print("Testing: Completed")

        print("\nTesting:\nTiny Link Updated For Short URL")
        self.assertEqual(tiny_link_update_short_response.status_code, status.HTTP_302_FOUND)
        print("Testing: Completed")

        print("\nTesting:\nTiny Link Statistics")
        self.assertEqual(tiny_link_statistics_response.status_code, status.HTTP_200_OK)
        print("Testing: Completed")

        print("\nTesting:\nTiny Link DB Stats")
        self.assertEqual(tiny_link_db_stats_response.status_code, status.HTTP_200_OK)
        print("Testing: Completed")

        print("\nTesting:\nTiny Link API Stats")
        self.assertEqual(tiny_link_api_stats_response.status_code, status.HTTP_200_OK)
        print("Testing: Completed")

        print("\nTesting:\nTiny Link API URL Stats")
        self.assertEqual(tiny_link_url_stats_response.status_code, status.HTTP_200_OK)
        print("Testing: Completed")

        print("\nTesting:\nTiny Link API Expand")
        self.assertEqual(tiny_link_expand_stats_response.status_code, status.HTTP_200_OK)
        print("Testing: Completed")
