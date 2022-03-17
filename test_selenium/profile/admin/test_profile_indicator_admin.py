from test_selenium.test_base import BaseTestCase

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from django.urls import reverse


class TestProfileIndicatorAdmin(BaseTestCase):
    def test_if_private_variables_are_filtered_correctly(self):
        self.login_into_adminpanel()
        add_profile_indicator_url = self.get_url(reverse("admin:profile_profileindicator_add"))
        self.selenium.get(add_profile_indicator_url)

        main_div = self.get_element("content")

        # no profile is selected, permission type is private. variable select should be disabled
        self.set_permission_type('private')
        assert main_div.find_element(by=By.CSS_SELECTOR, value="select#id_indicator").get_attribute(
            "disabled") == "true"

        # profile 1, public
        self.select_profile('public_profile')
        self.set_permission_type('public')

        self.assert_variable_options(
            ["-------------", "public_profile : dataset1 -> indicator1", "public_profile2 : dataset3 -> indicator3"])

        # profile 2
        self.select_profile('public_profile2')
        self.set_permission_type('private')

        self.assert_variable_options(
            ["-------------", "public_profile2 : dataset4 -> indicator4"])

    def select_profile(self, profile):
        profile_field = WebDriverWait(self.selenium, 2).until(
            EC.element_to_be_clickable((By.ID, "id_profile"))
        )
        profile_field = Select(profile_field)

        profile_field.select_by_visible_text(profile)

    def set_permission_type(self, type):
        main_div = self.get_element("content")
        main_div.find_element(by=By.CSS_SELECTOR, value="#variable-permission-filter input[value=" + type + "]").click()

    def assert_variable_options(self, options):
        main_div = self.get_element("content")

        main_div.find_element(by=By.CSS_SELECTOR, value="select#id_indicator").click()

        ele = main_div.find_elements(by=By.CSS_SELECTOR, value="select#id_indicator option:not([class^='hidden'])")
        assert len(ele) == len(options)

        index = 0
        for option in options:
            assert ele[index].text == option
            index += 1
