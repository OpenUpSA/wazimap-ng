import socket
import time

from django.contrib.staticfiles.testing import LiveServerTestCase
from django.test import override_settings, tag
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# Support wait to check if element is loaded
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

# Support actions like enter
from selenium.webdriver.common.keys import Keys

from django.contrib.auth.models import User
from tests.profile.factories import ProfileFactory
from tests.datasets.factories import (
    GeographyHierarchyFactory,
    VersionFactory,
    DatasetFactory,
    IndicatorFactory,
)


@override_settings(ALLOWED_HOSTS=["*"])  # Disable ALLOW_HOSTS
class BaseTestCase(LiveServerTestCase):
    """
    Provides base test class which connects to the Docker
    container running Selenium.
    """

    host = "0.0.0.0"  # Bind to 0.0.0.0 to allow external access

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Set host to externally accessible web server address
        cls.host = socket.gethostbyname(socket.gethostname())

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('no-sandbox')
        chrome_options.add_argument('disable-dev-shm-usage')

        # Instantiate the remote WebDriver
        cls.selenium = webdriver.Remote(
            #  Set to: htttp://{selenium-container-name}:port/wd/hub
            #  In our example, the container is named `selenium`
            #  and runs on port 4444
            command_executor="http://selenium:4444/wd/hub",
            # Set to CHROME since we are using the Chrome container
            desired_capabilities=DesiredCapabilities.CHROME,
            options=chrome_options
        )

        print(cls.selenium.capabilities)

    def setUp(self):
        self.site_header_text = "Wazimap Administration"
        self.version1 = VersionFactory(name="version1")
        self.version2 = VersionFactory(name="version2")
        self.version3 = VersionFactory(name="version3")
        self.public_profile_hierarchy = GeographyHierarchyFactory(
            configuration={
                "default_version": self.version1.name,
                "versions": [self.version1.name, self.version2.name],
            }
        )
        self.public_profile_hierarchy2 = GeographyHierarchyFactory(
            configuration={
                "default_version": self.version2.name,
                "versions": [self.version2.name, self.version3.name],
            }
        )
        self.public_profile = ProfileFactory(
            name="public_profile", geography_hierarchy=self.public_profile_hierarchy
        )
        self.public_profile2 = ProfileFactory(
            name="public_profile2", geography_hierarchy=self.public_profile_hierarchy2
        )

        self.private_profile_hierarchy = GeographyHierarchyFactory(
            configuration={
                "default_version": self.version3.name,
                "versions": [self.version3.name],
            }
        )
        self.private_profile = ProfileFactory(
            name="private_profile",
            permission_type="private",
            geography_hierarchy=self.private_profile_hierarchy,
        )

        self.dataset1 = DatasetFactory(name="dataset1", profile=self.public_profile, permission_type="public")
        self.indicator1 = IndicatorFactory(name="indicator1", dataset=self.dataset1)

        self.dataset2 = DatasetFactory(name="dataset2", profile=self.public_profile, permission_type="private")
        self.indicator2 = IndicatorFactory(name="indicator2", dataset=self.dataset2)

        self.dataset3 = DatasetFactory(name="dataset3", profile=self.public_profile2, permission_type="public")
        self.indicator3 = IndicatorFactory(name="indicator3", dataset=self.dataset3)

        self.dataset4 = DatasetFactory(name="dataset4", profile=self.public_profile2, permission_type="private")
        self.indicator4 = IndicatorFactory(name="indicator4", dataset=self.dataset4)

        # Create superuser
        self.user_password = "mypassword"
        self.superuser = User.objects.create_user(
            "superuser", "superuser@testwazi.com", self.user_password
        )
        self.superuser.is_active = True
        self.superuser.is_superuser = True
        self.superuser.is_staff = True
        self.superuser.save()

    def get_url(self, path):
        return f"{self.live_server_url}{path}"

    def get_element(self, id, delay=3):
        try:
            element = WebDriverWait(self.selenium, delay).until(
                EC.presence_of_element_located((By.ID, id))
            )
            return element
        except TimeoutException:
            raise "Loading took too much time!"

    def find_by_id(self, id):
        return self.selenium.find_element(by=By.ID, value=id)

    def login_into_adminpanel(self):
        url = self.get_url("/admin/")
        self.selenium.get(url)
        admin_login_header = self.get_element("site-name")
        site_header_text = admin_login_header.find_element(
            by=By.XPATH, value=".//a[@href='/admin/']"
        ).text
        assert site_header_text == self.site_header_text

        # Login
        username_field = self.find_by_id("id_username")
        passowrd_field = self.find_by_id("id_password")
        username_field.send_keys("superuser")
        passowrd_field.send_keys(self.user_password)
        passowrd_field.send_keys(Keys.ENTER)

        admin_login_header = self.get_element("site-name")
        site_header_text = admin_login_header.find_element(
            by=By.XPATH, value=".//a[@href='/admin/']"
        ).text
        assert site_header_text == self.site_header_text

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()
