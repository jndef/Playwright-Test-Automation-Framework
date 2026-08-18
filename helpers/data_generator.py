import random
import string
from dataclasses import dataclass

from faker import Faker

fake = Faker()


@dataclass
class GetRegisterUserData:
    display_name: str
    username: str
    email: str
    password: str


class Generators:

    def generate_string(self, length: int = 10) -> str:
        """
        Generates random string with given length
        :param length:
        :return: str
        """
        letters = string.ascii_letters
        result = ""
        for _ in range(length):
            result += random.choice(letters)
        return result

    def generate_number(self, min_val: int = 0, max_val: int = 100) -> int:
        """
        Generates random number between min_val and max_val (default - 100)
        :param min_val:int - minimal generated value
        :param max_val:int - maximal generated value
        :return: int
        """
        return random.randint(min_val, max_val)

    def generate_password(self, max_val: int = 6) -> str:
        """
        Generates random password with specified length (default - 6)
        :param max_val:int - maximal length of generated password
        :return:str
        """
        return fake.password(length=max_val)

    def generate_email(self, domain: str = "example.com") -> str:
        """
        Generates random email with specified domain (default - example.com)
        :param domain:str - specified email domain
        :return:str
        """
        email = fake.email(domain=domain)
        return email

    def generate_phone_number(self, country_code: str = "+1") -> str:
        """
        Generates random phone number with specified phone number country code
        :param country_code:str - specified phone number country code (default - +1)
        :return:str
        """
        return f"{country_code} {random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"

    def generate_text(self, max_len: int = 100) -> str:
        """
        Generates random text  with specified max text length (default - 100)
        :param max_len:int - specified phone number country code (default - +1)
        :return:str
        """
        return fake.text(max_len)

    def generate_displayname(self) -> str:
        """
        Generates random users display name
        :return:str
        """
        return fake.name()

    def generate_username(self) -> str:
        """
        Generates random user_name
        :return:str
        """
        return fake.user_name()

    def get_register_rand_data_object(self) -> GetRegisterUserData:
        """
        Generates random user data object for registration
        :return:GetRegisterUserData object of dataclass
        """
        return GetRegisterUserData(email=self.generate_email(),
                                   password=self.generate_password(),
                                   display_name=self.generate_displayname(),
                                   username=self.generate_username())
