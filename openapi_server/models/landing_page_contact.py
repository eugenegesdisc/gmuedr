# coding: utf-8

from datetime import date, datetime

from typing import List, Dict, Type

from openapi_server.models.base_model_ import Model
from openapi_server import util


class LandingPageContact(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, email: str=None, phone: str=None, fax: str=None, hours: str=None, instructions: str=None, address: str=None, postal_code: str=None, city: str=None, stateorprovince: str=None, country: str=None):
        """LandingPageContact - a model defined in OpenAPI

        :param email: The email of this LandingPageContact.
        :param phone: The phone of this LandingPageContact.
        :param fax: The fax of this LandingPageContact.
        :param hours: The hours of this LandingPageContact.
        :param instructions: The instructions of this LandingPageContact.
        :param address: The address of this LandingPageContact.
        :param postal_code: The postal_code of this LandingPageContact.
        :param city: The city of this LandingPageContact.
        :param stateorprovince: The stateorprovince of this LandingPageContact.
        :param country: The country of this LandingPageContact.
        """
        self.openapi_types = {
            'email': str,
            'phone': str,
            'fax': str,
            'hours': str,
            'instructions': str,
            'address': str,
            'postal_code': str,
            'city': str,
            'stateorprovince': str,
            'country': str
        }

        self.attribute_map = {
            'email': 'email',
            'phone': 'phone',
            'fax': 'fax',
            'hours': 'hours',
            'instructions': 'instructions',
            'address': 'address',
            'postal_code': 'postalCode',
            'city': 'city',
            'stateorprovince': 'stateorprovince',
            'country': 'country'
        }

        self._email = email
        self._phone = phone
        self._fax = fax
        self._hours = hours
        self._instructions = instructions
        self._address = address
        self._postal_code = postal_code
        self._city = city
        self._stateorprovince = stateorprovince
        self._country = country

    @classmethod
    def from_dict(cls, dikt: dict) -> 'LandingPageContact':
        """Returns the dict as a model

        :param dikt: A dict.
        :return: The landingPage_contact of this LandingPageContact.
        """
        return util.deserialize_model(dikt, cls)

    @property
    def email(self):
        """Gets the email of this LandingPageContact.

        Email address of service provider

        :return: The email of this LandingPageContact.
        :rtype: str
        """
        return self._email

    @email.setter
    def email(self, email):
        """Sets the email of this LandingPageContact.

        Email address of service provider

        :param email: The email of this LandingPageContact.
        :type email: str
        """

        self._email = email

    @property
    def phone(self):
        """Gets the phone of this LandingPageContact.

        Phone number of service provider

        :return: The phone of this LandingPageContact.
        :rtype: str
        """
        return self._phone

    @phone.setter
    def phone(self, phone):
        """Sets the phone of this LandingPageContact.

        Phone number of service provider

        :param phone: The phone of this LandingPageContact.
        :type phone: str
        """

        self._phone = phone

    @property
    def fax(self):
        """Gets the fax of this LandingPageContact.

        Fax number of service provider

        :return: The fax of this LandingPageContact.
        :rtype: str
        """
        return self._fax

    @fax.setter
    def fax(self, fax):
        """Sets the fax of this LandingPageContact.

        Fax number of service provider

        :param fax: The fax of this LandingPageContact.
        :type fax: str
        """

        self._fax = fax

    @property
    def hours(self):
        """Gets the hours of this LandingPageContact.


        :return: The hours of this LandingPageContact.
        :rtype: str
        """
        return self._hours

    @hours.setter
    def hours(self, hours):
        """Sets the hours of this LandingPageContact.


        :param hours: The hours of this LandingPageContact.
        :type hours: str
        """

        self._hours = hours

    @property
    def instructions(self):
        """Gets the instructions of this LandingPageContact.


        :return: The instructions of this LandingPageContact.
        :rtype: str
        """
        return self._instructions

    @instructions.setter
    def instructions(self, instructions):
        """Sets the instructions of this LandingPageContact.


        :param instructions: The instructions of this LandingPageContact.
        :type instructions: str
        """

        self._instructions = instructions

    @property
    def address(self):
        """Gets the address of this LandingPageContact.


        :return: The address of this LandingPageContact.
        :rtype: str
        """
        return self._address

    @address.setter
    def address(self, address):
        """Sets the address of this LandingPageContact.


        :param address: The address of this LandingPageContact.
        :type address: str
        """

        self._address = address

    @property
    def postal_code(self):
        """Gets the postal_code of this LandingPageContact.


        :return: The postal_code of this LandingPageContact.
        :rtype: str
        """
        return self._postal_code

    @postal_code.setter
    def postal_code(self, postal_code):
        """Sets the postal_code of this LandingPageContact.


        :param postal_code: The postal_code of this LandingPageContact.
        :type postal_code: str
        """

        self._postal_code = postal_code

    @property
    def city(self):
        """Gets the city of this LandingPageContact.


        :return: The city of this LandingPageContact.
        :rtype: str
        """
        return self._city

    @city.setter
    def city(self, city):
        """Sets the city of this LandingPageContact.


        :param city: The city of this LandingPageContact.
        :type city: str
        """

        self._city = city

    @property
    def stateorprovince(self):
        """Gets the stateorprovince of this LandingPageContact.


        :return: The stateorprovince of this LandingPageContact.
        :rtype: str
        """
        return self._stateorprovince

    @stateorprovince.setter
    def stateorprovince(self, stateorprovince):
        """Sets the stateorprovince of this LandingPageContact.


        :param stateorprovince: The stateorprovince of this LandingPageContact.
        :type stateorprovince: str
        """

        self._stateorprovince = stateorprovince

    @property
    def country(self):
        """Gets the country of this LandingPageContact.


        :return: The country of this LandingPageContact.
        :rtype: str
        """
        return self._country

    @country.setter
    def country(self, country):
        """Sets the country of this LandingPageContact.


        :param country: The country of this LandingPageContact.
        :type country: str
        """

        self._country = country