import time

from django.test import TestCase
from django.http import HttpRequest
from django.contrib.auth.models import User
from app_users.models import UserProfile, Address
from app_users.forms import RegisterForm
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By


class TestRegistrationForm(TestCase):

    @classmethod
    def setUpTestData(cls):
        pass

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_correct_registration_link(self):
        self.browser.get('http://localhost:8000')
        self.browser.find_element(By.PARTIAL_LINK_TEXT, "sign").click()
        self.assertEqual(self.browser.current_url, 'http://localhost:8000/registration/')

    def test_registration_form_no_input(self):
        self.browser.get('http://localhost:8000/registration/')
        self.browser.find_element(By.TAG_NAME, "button").click()
        self.assertEqual(self.browser.current_url, 'http://localhost:8000/registration/')

    def test_registration_form_without_flat(self):
        request = HttpRequest()
        request.POST = {'username': 'test_username',
                        'password1': 'Glavr1b@',
                        'password2': 'Glavr1b@',
                        'name': 'test_name',
                        'surname': 'test_surname',
                        'country': 'Russia',
                        'town': 'SmallTown',
                        'street': 'Obyvnaya',
                        'house': '1'}
        form = RegisterForm(request.POST)
        form.save()
        User.objects.get(username='test_username')

    def test_registration_form_redirect(self):
        self.browser.get('http://localhost:8000/registration/')
        username_enter = self.browser.find_element(By.NAME, 'username')
        username_enter.send_keys('test_username')
        password_1_enter = self.browser.find_element(By.NAME, 'password1')
        password_1_enter.send_keys('Glavr1b@')
        password_2_enter = self.browser.find_element(By.NAME, 'password2')
        password_2_enter.send_keys('Glavr1b@')
        name_enter = self.browser.find_element(By.NAME, 'name')
        name_enter.send_keys('test_name')
        name_enter = self.browser.find_element(By.NAME, 'surname')
        name_enter.send_keys('test_surname')
        country_enter = self.browser.find_element(By.NAME, 'country')
        country_enter.send_keys('Russia')
        town_enter = self.browser.find_element(By.NAME, 'town')
        town_enter.send_keys('SmallTown')
        street_enter = self.browser.find_element(By.NAME, 'street')
        street_enter.send_keys('Obyvnaya')
        house_enter = self.browser.find_element(By.NAME, 'house')
        house_enter.send_keys('1')
        button = self.browser.find_element(By.XPATH, "//button[text()='Sign in']")
        button.click()


class TestLoginForm(TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_correct_login_link(self):
        self.browser.get('http://localhost:8000')
        response = self.browser.find_element(By.PARTIAL_LINK_TEXT, "login").click()
        self.assertTemplateUsed(response, '/app_users/login_page.html')





