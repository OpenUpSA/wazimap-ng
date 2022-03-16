import time
from test_selenium.test_base import BaseTestCase

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from django.urls import reverse


class TestProfileVerisons(BaseTestCase):
    def test_if_version_field_updated_when_profile_is_changed(self):
        self.login_into_adminpanel()
        add_dataset_url = self.get_url(reverse("admin:datasets_dataset_add"))
        self.selenium.get(add_dataset_url)
        main_div = self.get_element("content")
        header_text = main_div.find_element(by=By.TAG_NAME, value="h1").text
        assert header_text == "Add dataset"

        profile_field = WebDriverWait(self.selenium, 2).until(
            EC.element_to_be_clickable((By.ID, "id_profile"))
        )
        assert profile_field.get_attribute("required") == "true"
        profile_field = Select(profile_field)
        assert len(profile_field.options) == 3
        profile_options = profile_field.options
        assert profile_options[0].text == "---------"
        assert profile_options[1].text == "private_profile"
        assert profile_options[2].text == "public_profile"

        version_field = WebDriverWait(self.selenium, 2).until(
            EC.element_to_be_clickable((By.ID, "id_version"))
        )
        assert version_field.get_attribute("required") == "true"
        version_field = Select(version_field)
        assert len(version_field.options) == 1
        version_options = version_field.options
        assert version_options[0].text == "---------"

        profile_field.select_by_visible_text("public_profile")
        version_field = WebDriverWait(self.selenium, 2).until(
            EC.element_to_be_clickable((By.ID, "id_version"))
        )
        version_field = Select(version_field)
        assert len(version_field.options) == 3
        version_options = version_field.options
        assert version_options[0].text == "-----------"
        assert version_options[1].text == "version1"
        assert version_options[2].text == "version2"

        profile_field.select_by_visible_text("private_profile")

        version_field = WebDriverWait(self.selenium, 2).until(
            EC.element_to_be_clickable((By.ID, "id_version"))
        )
        version_field = Select(version_field)
        assert len(version_field.options) == 2
        version_options = version_field.options
        assert version_options[0].text == "-----------"
        assert version_options[1].text == "version3"

    def test_if_error_message_is_shown_if_not_able_to_get_versions(self):
        self.login_into_adminpanel()
        add_dataset_url = self.get_url(reverse("admin:datasets_dataset_add"))
        self.selenium.get(add_dataset_url)
        main_div = self.get_element("content")
        header_text = main_div.find_element(by=By.TAG_NAME, value="h1").text
        assert header_text == "Add dataset"

        profile_field = WebDriverWait(self.selenium, 2).until(
            EC.element_to_be_clickable((By.ID, "id_profile"))
        )
        assert profile_field.get_attribute("required") == "true"
        profile_field = Select(profile_field)
        assert len(profile_field.options) == 3
        profile_options = profile_field.options
        assert profile_options[0].text == "---------"
        assert profile_options[1].text == "private_profile"
        assert profile_options[2].text == "public_profile"

        self.selenium.execute_script(
            "arguments[0].setAttribute('value','100000')", profile_options[1]
        )
        profile_field.select_by_visible_text("private_profile")

        toast = WebDriverWait(self.selenium, 3).until(
            EC.presence_of_element_located((By.CLASS_NAME, "toast-message"))
        )
        assert toast.text == "Something went wrong while fetching versions."
