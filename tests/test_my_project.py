import os
import runpy
import unittest
from unittest.mock import patch

from src.my_project import mask_password, registration

VALID_LOGIN = "student_1"
VALID_PASSWORD = "Пароль1!"
PROJECT_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "src", "my_project.py"
)


class TestRegistration(unittest.TestCase):
    """Проверка всей цепочки регистрации: логин -> пароль -> подтверждение -> лог."""

    def register(self, login, password, confirmation):
        with self.assertLogs(level="DEBUG") as logs:
            result = registration(login, password, confirmation)
        return result, "\n".join(logs.output)

    def test_registration_success_with_simple_login(self):
        result, log = self.register(VALID_LOGIN, VALID_PASSWORD, VALID_PASSWORD)
        self.assertEqual(result, (True, ""))
        self.assertIn(mask_password(VALID_PASSWORD), log)
        self.assertNotIn(VALID_PASSWORD, log)

    def test_registration_success_with_phone_login(self):
        result, _ = self.register("+7-913-123-4567", VALID_PASSWORD, VALID_PASSWORD)
        self.assertEqual(result, (True, ""))

    def test_registration_success_with_email_login(self):
        result, _ = self.register("liza.v@mail.ru", VALID_PASSWORD, VALID_PASSWORD)
        self.assertEqual(result, (True, ""))

    def test_registration_fails_with_empty_login(self):
        result, _ = self.register("", VALID_PASSWORD, VALID_PASSWORD)
        self.assertEqual(result, (False, "Логин не может быть пустым"))

    def test_registration_fails_with_blacklisted_login(self):
        result, _ = self.register("ROOT", VALID_PASSWORD, VALID_PASSWORD)
        self.assertEqual(result, (False, "Логин находится в черном списке"))

    def test_registration_fails_with_short_login(self):
        result, _ = self.register("liza", VALID_PASSWORD, VALID_PASSWORD)
        self.assertEqual(result, (False, "Логин должен содержать минимум 5 символов"))

    def test_registration_fails_with_cyrillic_login(self):
        result, _ = self.register("студент", VALID_PASSWORD, VALID_PASSWORD)
        self.assertEqual(result[0], False)
        self.assertIn("только латинские буквы", result[1])

    def test_registration_fails_with_empty_password(self):
        result, _ = self.register(VALID_LOGIN, "", "")
        self.assertEqual(result, (False, "Пароль не может быть пустым"))

    def test_registration_fails_with_short_password(self):
        result, _ = self.register(VALID_LOGIN, "Па1!ль", "Па1!ль")
        self.assertEqual(result, (False, "Пароль должен содержать минимум 7 символов"))

    def test_registration_fails_with_latin_password(self):
        result, _ = self.register(VALID_LOGIN, "Password1!", "Password1!")
        self.assertEqual(result[0], False)
        self.assertIn("только кириллицу", result[1])

    def test_registration_fails_without_uppercase_letter(self):
        result, _ = self.register(VALID_LOGIN, "пароль1!", "пароль1!")
        self.assertEqual(result, (False, "Пароль должен содержать заглавную букву"))

    def test_registration_fails_without_lowercase_letter(self):
        result, _ = self.register(VALID_LOGIN, "ПАРОЛЬ1!", "ПАРОЛЬ1!")
        self.assertEqual(result, (False, "Пароль должен содержать строчную букву"))

    def test_registration_fails_without_digit(self):
        result, _ = self.register(VALID_LOGIN, "Пароль!!", "Пароль!!")
        self.assertEqual(result, (False, "Пароль должен содержать цифру"))

    def test_registration_fails_without_special_symbol(self):
        result, _ = self.register(VALID_LOGIN, "Пароль12", "Пароль12")
        self.assertEqual(result, (False, "Пароль должен содержать специальный символ"))

    def test_registration_fails_when_confirmation_differs(self):
        result, _ = self.register(VALID_LOGIN, VALID_PASSWORD, "Пароль2!")
        self.assertEqual(result, (False, "Пароль и подтверждение пароля не совпадают"))

    def test_registration_does_not_crash_when_all_values_are_none(self):
        result, _ = self.register(None, None, None)
        self.assertEqual(result, (False, "Логин не может быть пустым"))

    def test_registration_handles_non_string_login(self):
        result, _ = self.register(12345, VALID_PASSWORD, VALID_PASSWORD)
        self.assertEqual(result, (False, "Ошибка выполнения программы"))

    def test_registration_handles_non_string_password(self):
        result, _ = self.register(VALID_LOGIN, 1234567, 1234567)
        self.assertEqual(result, (False, "Ошибка выполнения программы"))


class TestHelpersAndProgramRun(unittest.TestCase):
    """Проверка маскировки пароля и запуска программы целиком."""

    def test_mask_password_converts_chars_to_codes(self):
        self.assertEqual(mask_password("Ab1"), "65-98-49")

    def test_program_run_prints_registration_result(self):
        inputs = [VALID_LOGIN, VALID_PASSWORD, VALID_PASSWORD]
        with patch("builtins.input", side_effect=inputs), \
                patch("builtins.print") as mock_print, \
                self.assertLogs(level="DEBUG"):
            runpy.run_path(PROJECT_FILE, run_name="__main__")
        mock_print.assert_any_call("Результат:", True)
        mock_print.assert_any_call("Сообщение:", "")


if __name__ == "__main__":
    unittest.main()
