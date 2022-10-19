from test_selenium.test_base import BaseTestCase

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains

from django.urls import reverse
from tests.datasets.factories import GroupFactory


class TestSortableWidget(BaseTestCase):
    def order_subindictaor(self, index_from, index_to):
        drag = WebDriverWait(self.selenium, 2).until(
            EC.element_to_be_clickable((By.XPATH, f"//li[@data-val='{index_from}']"))
        )
        drop = WebDriverWait(self.selenium, 2).until(
            EC.element_to_be_clickable((By.XPATH, f"//li[@data-val='{index_to}']"))
        )
        ActionChains(self.selenium).drag_and_drop(drag, drop).perform()

    def test_admin_sortable_widget(self):
        self.login_into_adminpanel()

        group = GroupFactory(
            name="age",
            subindicators=[
                "20-30",
                "30-40",
                "10-20",
                "below 10",
                "40-50",
                "50+",
            ],
        )

        edit_group_url = self.get_url(
            reverse("admin:datasets_group_change", args=(group.id,))
        )
        self.selenium.get(edit_group_url)
        main_div = self.get_element("content")
        header_text = main_div.find_element(by=By.TAG_NAME, value="h1").text
        assert header_text == "Change SubindicatorsGroup"

        # Assert sortable widget values
        assert main_div.find_element_by_xpath("//li[@data-val='0']").text == "20-30"
        assert main_div.find_element_by_xpath("//li[@data-val='1']").text == "30-40"
        assert main_div.find_element_by_xpath("//li[@data-val='2']").text == "10-20"
        assert main_div.find_element_by_xpath("//li[@data-val='3']").text == "below 10"
        assert main_div.find_element_by_xpath("//li[@data-val='4']").text == "40-50"
        assert main_div.find_element_by_xpath("//li[@data-val='5']").text == "50+"

        main_div.find_element_by_xpath(
            "//input[@data-name='subindicators']"
        ).get_attribute("value") == "[0,1,2,3,4,5]"

        self.order_subindictaor(3, 0)
        self.order_subindictaor(2, 0)

        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element_value((By.XPATH, "//input[@data-name='subindicators']"), "[3,2,0,1,4,5]")
        )

        # Assert if reordered
        main_div.find_element_by_xpath(
            "//input[@data-name='subindicators']"
        ).get_attribute("value") == "[3,2,0,1,4,5]"

        # Save and continue
        main_div.find_element_by_css_selector(
            ".submit-row input[value='Save and continue editing']"
        ).click()

        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located((By.TAG_NAME, "h1"))
        )

        main_div = self.get_element("content")
        header_element = main_div.find_element(by=By.TAG_NAME, value="h1").text
        assert header_text == "Change SubindicatorsGroup"

        # Assert sortable widget values after save
        assert main_div.find_element_by_xpath("//li[@data-val='0']").text == "below 10"
        assert main_div.find_element_by_xpath("//li[@data-val='1']").text == "10-20"
        assert main_div.find_element_by_xpath("//li[@data-val='2']").text == "20-30"
        assert main_div.find_element_by_xpath("//li[@data-val='3']").text == "30-40"
        assert main_div.find_element_by_xpath("//li[@data-val='4']").text == "40-50"
        assert main_div.find_element_by_xpath("//li[@data-val='5']").text == "50+"

        main_div.find_element_by_xpath(
            "//input[@data-name='subindicators']"
        ).get_attribute("value") == "[0,1,2,3,4,5]"
