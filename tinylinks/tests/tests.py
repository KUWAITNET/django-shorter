import datetime
import socket
from unittest.mock import Mock, patch
from urllib.request import OpenerDirector

import pytz
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from urllib3.exceptions import HTTPError, MaxRetryError, TimeoutError

from ..forms import TinylinkAdminForm, TinylinkForm
from ..models import Tinylink, TinylinkLog, get_url_response, validate_long_url
from ..utils import shortify_url

User = get_user_model()


class TinyLinkTest(APITestCase):
    def setUp(self):
        self.tiny_link_list_url = reverse("tinylink_list")
        self.tiny_link_create_url = reverse("tinylink_create")
        self.user = User.objects.create_superuser(
            username="gunjan_test",
            email="gunjan_test@kuwaitnet.com",
            password=make_password("test1234"),
        )
        self.tiny_link = Tinylink.objects.create(
            user=self.user,
            long_url="http://www.example.com/thisisalongURL",
            short_url="vB7f5b",
        )
        self.tiny_log = TinylinkLog.objects.create(
            tinylink=self.tiny_link,
            referrer="http://www.example.com/thisisalongURL",
            user_agent="Gunjan Modi",
            cookie="test:test",
            remote_ip="127.0.0.1",
            tracked=True,
        )
        self.tiny_link_update_long_url = reverse(
            "tinylink_update", kwargs={"pk": self.tiny_link.id, "mode": "change-long"}
        )
        self.tiny_link_update_short_url = reverse(
            "tinylink_update", kwargs={"pk": self.tiny_link.id, "mode": "change-short"}
        )

        self.tiny_link_statistics = reverse("tinylink_statistics")
        self.tiny_link_db_stats = reverse("api_db_stats")
        self.tiny_link_api_stats = reverse("api_stats")
        self.tiny_link_url_stats = reverse(
            "api_url_stats", kwargs={"short_url": self.tiny_link.short_url}
        )
        self.tiny_link_expand_stats = reverse(
            "api_tinylink_expand", kwargs={"short_url": self.tiny_link.short_url}
        )

    def test_api_urls(self):
        """
        Superuser has permission superuser and admin

        """
        self.client.force_authenticate(user=self.user)
        tiny_link_list_response = self.client.get(path=self.tiny_link_list_url)
        tiny_link_create_response = self.client.post(path=self.tiny_link_create_url)
        tiny_link_update_long_response = self.client.post(
            path=self.tiny_link_update_long_url,
            data={"long_url": "http://www.example.com/thisisalongURLCustom"},
        )
        tiny_link_update_short_response = self.client.post(
            path=self.tiny_link_update_short_url,
            data={
                "long_url": "http://www.example.com/thisisalongURLCustom",
                "short_url": "aaq12",
            },
        )
        tiny_link_statistics_response = self.client.get(
            path=self.tiny_link_statistics, data={"testing": True}
        )
        tiny_link_statistics_not_found_response = self.client.get(
            path=self.tiny_link_statistics
        )
        tiny_link_db_stats_response = self.client.get(path=self.tiny_link_db_stats)
        tiny_link_api_stats_response = self.client.get(path=self.tiny_link_api_stats)
        tiny_link_url_stats_response = self.client.get(path=self.tiny_link_url_stats)
        tiny_link_expand_stats_response = self.client.get(
            path=self.tiny_link_expand_stats
        )

        print("Testing:\nTiny Link List")
        self.assertEqual(tiny_link_list_response.status_code, status.HTTP_302_FOUND)
        print("Testing: Completed")

        print("\nTesting:\nTiny Link Created")
        self.assertEqual(tiny_link_create_response.status_code, status.HTTP_302_FOUND)
        print("Testing: Completed")

        print("\nTesting:\nTiny Link Updated For Long URL")
        self.assertEqual(
            tiny_link_update_long_response.status_code, status.HTTP_302_FOUND
        )
        print("Testing: Completed")

        print("\nTesting:\nTiny Link Updated For Short URL")
        self.assertEqual(
            tiny_link_update_short_response.status_code, status.HTTP_302_FOUND
        )
        print("Testing: Completed")

        print("\nTesting:\nTiny Link Statistics")
        self.assertEqual(tiny_link_statistics_response.status_code, status.HTTP_200_OK)
        print("Testing: Completed")

        print("\nTesting:\nTiny Link Not Found Statistics")
        self.assertEqual(
            tiny_link_statistics_not_found_response.status_code,
            status.HTTP_404_NOT_FOUND,
        )
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
        self.assertEqual(
            tiny_link_expand_stats_response.status_code, status.HTTP_200_OK
        )
        print("Testing: Completed")

    def test_tiny_link_stats(self):
        self.client.force_authenticate(user=self.user)
        self.tiny_link.short_url = "blah"
        self.tiny_link_url_stats = reverse(
            "api_url_stats", kwargs={"short_url": self.tiny_link.short_url}
        )
        response = self.client.get(self.tiny_link_url_stats)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_tiny_link_expand(self):
        self.client.force_authenticate(user=self.user)
        self.tiny_link.short_url = "blah"
        self.tiny_link_expand_stats = reverse(
            "api_tinylink_expand", kwargs={"short_url": self.tiny_link.short_url}
        )
        response = self.client.get(self.tiny_link_expand_stats)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)


class TinyLinkRestViewTest(TestCase):
    def setUp(self):
        self.tiny_link_list_url = reverse("tinylink_list")
        self.user = User.objects.create_superuser(
            username="gerges",
            email="gerges_test@kuwaitnet.com",
            password=make_password("password123"),
        )
        self.tiny_link = Tinylink.objects.create(
            user=self.user,
            long_url="http://www.example.com",
            short_url="vB7f5b",
        )

    def test_authenticated_admin_links_list(self):
        """
        test get links list if user.is_admin = True
        """
        self.client.force_login(user=self.user)
        tiny_link_list_response = self.client.get("/s/api/tinylinks/")
        print(
            "\nTesting:\nTiny Link List Links : user.is_admin=True & user is authenticated"
        )
        self.assertEqual(tiny_link_list_response.status_code, status.HTTP_200_OK)

    def test_authenticated_user_links_list(self):
        """
        test get links list if user.is_admin = True
        """
        user = User.objects.create_user(
            username="test",
            email="gerges@gmail.com",
            password=make_password("password123"),
        )
        self.client.force_login(user=user)
        tiny_link_list_response = self.client.get("/s/api/tinylinks/")
        print(
            "\nTesting:\nTiny Link List Links : user.is_admin=True & user is authenticated"
        )
        self.assertEqual(tiny_link_list_response.status_code, status.HTTP_200_OK)

    def test_authenticated_admin_links_list_with_request_url(self):
        """
        test get links list if user.is_admin = True
        """

        self.client.force_login(user=self.user)
        self.query_parameter = "https://soundcloud.com/discover"
        tiny_link_list_response = self.client.get(
            "/s/api/tinylinks/", {"url": self.query_parameter}
        )
        print(
            "\nTesting:\nTiny Link List Links : user.is_admin=True & user is authenticated"
        )
        self.assertEqual(tiny_link_list_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_admin_links_list(self):
        """
        test get links list if user.is_admin = False
        """
        tiny_link_list_response = self.client.get("/s/api/tinylinks/")
        print(
            "\nTesting:\nTiny Link List Links : user.is_admin=False & user in not authenticated"
        )
        self.assertEqual(
            tiny_link_list_response.status_code, status.HTTP_401_UNAUTHORIZED
        )

    def test_authenticated_admin_create_link(self):
        self.query_parameter = "https://soundcloud.com/discover"
        self.client.force_login(user=self.user)
        tiny_link_create_response = self.client.post(
            "/s/api/tinylinks/", {"long_url": self.query_parameter}, format="json"
        )
        print("\nTesting:\nTiny Link create One Link")
        self.assertEqual(tiny_link_create_response.status_code, status.HTTP_201_CREATED)

    def test_shorter_url(self):
        self.query_parameter = "https://soundcloud.com/discover"
        self.client.force_login(user=self.user)
        tiny_link_create_response = self.client.post(
            "/s/yourls-api.php",
            {"url": self.query_parameter},
            format="json",
        )
        print("\nTesting:\nTiny Link shorter-url create One Link")
        self.assertEqual(tiny_link_create_response.status_code, status.HTTP_200_OK)

    def test_shorter_url_bad_request(self):
        self.query_parameter = "https://soundcloud.com/discover"
        self.client.force_login(user=self.user)
        tiny_link_create_response = self.client.post(
            "/s/yourls-api.php",
            {
                "url": self.query_parameter,
                "username": self.user.username,
                "password": self.user.password,
            },
            format="json",
        )
        print("\nTesting:\nTiny Link shorter-url bad request Link")
        self.assertEqual(
            tiny_link_create_response.status_code, status.HTTP_400_BAD_REQUEST
        )

    def test_shorter_url_with_no_user(self):
        self.query_parameter = "https://soundcloud.com/discover"
        self.client.force_login(user=self.user)
        tiny_link_create_response = self.client.post(
            "/s/yourls-api.php",
            {
                "url": self.query_parameter,
                "username": "test",
                "password": self.user.password,
            },
            format="json",
        )
        print("\nTesting:\nTiny Link shorter-url with no user Link")
        self.assertEqual(tiny_link_create_response.status_code, status.HTTP_200_OK)

    def test_redirect_exist(self):
        self.client.force_login(user=self.user)
        self.tiny_link_url_stats = reverse(
            "tinylink_redirect", kwargs={"short_url": self.tiny_link.short_url}
        )
        tiny_link_create_response = self.client.get(self.tiny_link_url_stats)
        print("\nTesting:\nTiny redirect short url")
        self.assertEqual(tiny_link_create_response.status_code, status.HTTP_302_FOUND)

    def test_redirect_not_exist(self):
        self.client.force_login(user=self.user)
        self.tiny_link.short_url = "blah"
        self.tiny_link_url_stats = reverse(
            "tinylink_redirect", kwargs={"short_url": self.tiny_link.short_url}
        )
        tiny_link_create_response = self.client.get(self.tiny_link_url_stats)
        print("\nTesting:\nTiny redirect short url")
        self.assertEqual(tiny_link_create_response.status_code, status.HTTP_302_FOUND)

    def test_redirect_with_no_url(self):
        self.client.force_login(user=self.user)
        self.tiny_link.long_url = ""
        self.tiny_link.save()
        self.tiny_link_url_stats = reverse(
            "tinylink_redirect", kwargs={"short_url": self.tiny_link.short_url}
        )
        tiny_link_create_response = self.client.get(self.tiny_link_url_stats)
        print("\nTesting:\nTiny redirect short url")
        self.assertEqual(tiny_link_create_response.status_code, status.HTTP_410_GONE)

    def test_tiny_link_create(self):
        self.client.force_login(user=self.user)
        self.url = reverse("tinylink_create")
        tiny_link_create_response = self.client.post(self.url)
        self.assertEqual(tiny_link_create_response.status_code, status.HTTP_200_OK)

    def test_list_api_with_get(self):
        self.client.force_login(user=self.user)
        response = self.client.get(self.tiny_link_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("Testing: Completed")

    def test_list_api_with_bad_post_request(self):
        self.tiny_link_list_url = reverse("tinylink_list")
        self.client.force_login(user=self.user)
        response = self.client.post(self.tiny_link_list_url, data={"validate": "test"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        print("Testing: Completed")

    def test_list_api_with_exist_link(self):
        self.tiny_link_list_url = reverse("tinylink_list")
        self.client.force_login(user=self.user)
        response = self.client.post(
            self.tiny_link_list_url,
            data={f"validate{self.tiny_link.id}": self.tiny_link.id},
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        print("Testing: Completed")

    def test_list_api_with_no_exist_link(self):
        self.tiny_link_list_url = reverse("tinylink_list")
        self.client.force_login(user=self.user)
        response = self.client.post(
            self.tiny_link_list_url, data={"validate123456": 123456}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        print("Testing: Completed")


class TinyLinkModelTest(TestCase):
    def setUp(self):
        self.pool = Mock()
        self.user = User.objects.create_superuser(
            username="gunjan_test",
            email="gunjan_test@kuwaitnet.com",
            password=make_password("test1234"),
        )
        self.link = Tinylink.objects.create(
            user=self.user,
            long_url="http://www.example.com/thisisalongURL",
            short_url="vB7f5b",
        )

    def test_get_url_response_when_encode_long_url(self):
        print("\nTesting:\nTiny Link encode long_url")
        self.assertEqual(
            self.link.long_url.encode("utf-8"), b"http://www.example.com/thisisalongURL"
        )
        print("Testing: Completed")

    def test_get_url_response_when_bad_encode_long_url(self):
        print("\nTesting:\nTiny Link bad encode long_url")
        url_mock = Mock()
        url_mock.encode.side_effect = UnicodeEncodeError("blah", "blah", 1, 1, "blah")
        get_url_response(self.pool, self.link, url_mock)
        self.assertEqual(
            self.link.validation_error, "Unicode error. Check URL characters."
        )
        print("Testing: Completed")

    def test_get_url_response_when_timeout_error(self):
        print("\nTesting:\nTiny Connection timeout error")
        self.pool.urlopen.side_effect = TimeoutError
        get_url_response(self.pool, self.link, self.link.long_url)
        self.assertEqual(self.link.validation_error, "Timeout after 8 seconds.")
        print("Testing: Completed")

    def test_get_url_response_when_max_retry_error(self):
        print("\nTesting:\nTiny Connection retry error")
        self.pool.urlopen.side_effect = MaxRetryError(self.pool, self.link.long_url)
        get_url_response(self.pool, self.link, self.link.long_url)
        self.assertEqual(self.link.validation_error, "Failed after retrying twice.")
        print("Testing: Completed")

    def test_get_url_response_when_http_error(self):
        print("\nTesting:\nTiny Connection http error")
        self.pool.urlopen.side_effect = HTTPError
        get_url_response(self.pool, self.link, self.link.long_url)
        self.assertEqual(self.link.validation_error, "Not found.")
        print("Testing: Completed")

    def test_get_url_response_when_socket_error(self):
        print("\nTesting:\nTiny Connection http error")
        self.pool.urlopen.side_effect = socket.gaierror
        get_url_response(self.pool, self.link, self.link.long_url)
        self.assertEqual(self.link.validation_error, "Not found.")
        print("Testing: Completed")

    @patch("tinylinks.models.get_url_response")
    def test_validate_long_url_with_status_ok(self, mock_fn):
        response = Mock()
        mock_fn.return_value = response
        response.status = 200
        validate_long_url(self.link)
        self.assertFalse(self.link.is_broken)

    @patch("tinylinks.models.get_url_response")
    def test_validate_long_url_with_status_response_pdf(self, mock_fn):
        response = Mock()
        mock_fn.return_value = response
        response.status = 302
        self.link.long_url = "blah.pdf"
        validate_long_url(self.link)
        self.assertFalse(self.link.is_broken)

    @patch("tinylinks.models.get_url_response")
    def test_validate_long_url_with_status_response_redirect(self, mock_fn):
        def get_redirect_location():
            return "blah"

        response = Mock()
        redirect = Mock()
        redirect.status = 200
        response.status = 302
        response.get_redirect_location = get_redirect_location
        mock_fn.side_effect = [response, redirect]
        validate_long_url(self.link)
        self.assertFalse(self.link.is_broken)

    @patch("tinylinks.models.get_url_response")
    def test_validate_long_url_with_status_redirect_two(self, mock_fn):
        def get_redirect_location():
            return "http://localhost"

        response = Mock()
        redirect = Mock()
        response.status = 302
        redirect.status = 302
        response.get_redirect_location = get_redirect_location
        mock_fn.side_effect = [response, redirect]
        with patch.object(OpenerDirector, "open") as mk:
            res = Mock()
            res.code = 200
            mk.return_value = res
            validate_long_url(self.link)
        self.assertFalse(self.link.is_broken)

    @patch("tinylinks.models.get_url_response")
    def test_validate_long_url_server_code_with_broken_link(self, mock_fn):
        response = Mock()
        mock_fn.return_value = response
        response.status = 502
        self.link.long_url = "http://www.example.com"
        validate_long_url(self.link)
        self.assertFalse(self.link.is_broken)

    @patch("tinylinks.models.get_url_response")
    def test_validate_long_url_with_error(self, mock_fn):
        response = Mock()
        mock_fn.return_value = response
        validate_long_url(self.link, True)
        self.assertEqual(self.link.validation_error, "URL not accessible.")

    def test_can_not_be_validated(self):
        self.assertEqual(False, self.link.can_be_validated())

    @patch("django.utils.timezone.now")
    def test_can_be_validated(self, mock_fn):
        mock_fn.return_value = datetime.datetime(
            2024, 6, 15, 8, 27, 0, 894109, pytz.UTC
        )
        self.assertEqual(True, self.link.can_be_validated())


class TinyLinkFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            username="gunjan_test",
            email="gunjan_test@kuwaitnet.com",
            password=make_password("test1234"),
        )
        self.link = Tinylink.objects.create(
            user=self.user,
            long_url="http://www.example.com/thisisalongURL",
            short_url="vB7f5b",
        )

    def test_tiny_link_admin_form_invalid(self):
        form_data = {
            "user": self.user,
            "long_url": self.link.long_url,
            "short_url": self.link.short_url,
        }
        form = TinylinkAdminForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_tiny_link_admin_form_empty(self):
        form_data = {}
        form = TinylinkAdminForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_tiny_link_admin_form_with_instance(self):
        self.link.short_url = "Et3y2a"
        form_data = {
            "user": self.user,
            "long_url": self.link.long_url,
            "short_url": self.link.short_url,
        }
        form = TinylinkAdminForm(instance=self.link, data=form_data)
        self.assertFalse(form.is_valid())

    def test_tiny_link_admin_form(self):
        form_data = {"user": self.user, "long_url": "blah", "short_url": "vB7f5b"}
        form = TinylinkAdminForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_tiny_link_form_invalid(self):
        form_data = {"long_url": "blah", "short_url": "vB7f5b"}
        form = TinylinkForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_tiny_link_form_with_instance(self):
        form_data = {"long_url": self.link.long_url, "short_url": self.link.short_url}
        form = TinylinkForm(instance=self.link, data=form_data)
        self.assertFalse(form.is_valid())

    def test_tiny_link_form_valid(self):
        self.link.short_url = "xT3y2a"
        form_data = {"long_url": self.link.long_url, "short_url": self.link.short_url}
        form = TinylinkForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_tiny_link_form_save(self):
        self.link.short_url = "xT3y2a"
        form_data = {"long_url": self.link.long_url, "short_url": self.link.short_url}
        form = TinylinkForm(data=form_data)
        form.save()
        self.assertTrue(form.is_valid())

    def test_shortify_url(self):
        form = TinylinkForm(
            {
                "data": {
                    "long_url": self.link.long_url,
                    "short_url": self.link.short_url,
                },
                "mode": None,
            }
        )
        print(form.errors)
        shortify_url(self.link.long_url)
        self.assertFalse(form.is_valid())
