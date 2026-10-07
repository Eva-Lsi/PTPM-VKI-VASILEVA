import unittest
from unittest.mock import patch

from src import my_project
from src.my_project import mask_password, registration

VALID_LOGIN = "student_1"
VALID_PASSWORD = "Пароль1!"
PROJECT_FILE = my_project.__file__


def run_program():
    """Запускает файл my_project.py целиком, как будто его запустили из терминала."""
    with open(PROJECT_FILE, encoding="utf-8") as file:
        code = file.read()
    exec(compile(code, PROJECT_FILE, "exec"), {"__name__": "__main__"})


class TestRegistraciya(unittest.TestCase):
    """Проверка всей цепочки регистрации: логин -> пароль -> подтверждение -> лог."""

    def register(self, login, password, confirmation):
        with self.assertLogs(level="DEBUG") as logs:
            result = registration(login, password, confirmation)
        return result, "\n".join(logs.output)

    def test_uspeshnaya_registraciya_s_obychnym_loginom(self):
        result, log = self.register(VALID_LOGIN, VALID_PASSWORD, VALID_PASSWORD)
        self.assertEqual(result, (True, ""))
        self.assertIn(mask_password(VALID_PASSWORD), log)
        self.assertNotIn(VALID_PASSWORD, log)

    def test_uspeshnaya_registraciya_s_loginom_telefonom(self):
        result, _ = self.register("+7-913-123-4567", VALID_PASSWORD, VALID_PASSWORD)
        self.assertEqual(result, (True, ""))

    def test_uspeshnaya_registraciya_s_loginom_email(self):
        result, _ = self.register("liza.v@mail.ru", VALID_PASSWORD, VALID_PASSWORD)
        self.assertEqual(result, (True, ""))

    def test_pustoy_login_vydaet_oshibku(self):
        result, _ = self.register("", VALID_PASSWORD, VALID_PASSWORD)
        self.assertEqual(result, (False, "Логин не может быть пустым"))

    def test_login_iz_chernogo_spiska_vydaet_oshibku(self):
        result, _ = self.register("ROOT", VALID_PASSWORD, VALID_PASSWORD)
        self.assertEqual(result, (False, "Логин находится в черном списке"))

    def test_korotkiy_login_vydaet_oshibku(self):
        result, _ = self.register("liza", VALID_PASSWORD, VALID_PASSWORD)
        self.assertEqual(result, (False, "Логин должен содержать минимум 5 символов"))

    def test_login_na_kirillice_vydaet_oshibku(self):
        result, _ = self.register("студент", VALID_PASSWORD, VALID_PASSWORD)
        self.assertEqual(result[0], False)
        self.assertIn("только латинские буквы", result[1])

    def test_pustoy_parol_vydaet_oshibku(self):
        result, _ = self.register(VALID_LOGIN, "", "")
        self.assertEqual(result, (False, "Пароль не может быть пустым"))

    def test_korotkiy_parol_vydaet_oshibku(self):
        result, _ = self.register(VALID_LOGIN, "Па1!ль", "Па1!ль")
        self.assertEqual(result, (False, "Пароль должен содержать минимум 7 символов"))

    def test_parol_na_latinice_vydaet_oshibku(self):
        result, _ = self.register(VALID_LOGIN, "Password1!", "Password1!")
        self.assertEqual(result[0], False)
        self.assertIn("только кириллицу", result[1])

    def test_parol_bez_zaglavnoy_bukvy_vydaet_oshibku(self):
        result, _ = self.register(VALID_LOGIN, "пароль1!", "пароль1!")
        self.assertEqual(result, (False, "Пароль должен содержать заглавную букву"))

    def test_parol_bez_strochnoy_bukvy_vydaet_oshibku(self):
        result, _ = self.register(VALID_LOGIN, "ПАРОЛЬ1!", "ПАРОЛЬ1!")
        self.assertEqual(result, (False, "Пароль должен содержать строчную букву"))

    def test_parol_bez_cifry_vydaet_oshibku(self):
        result, _ = self.register(VALID_LOGIN, "Пароль!!", "Пароль!!")
        self.assertEqual(result, (False, "Пароль должен содержать цифру"))

    def test_parol_bez_specsimvola_vydaet_oshibku(self):
        result, _ = self.register(VALID_LOGIN, "Пароль12", "Пароль12")
        self.assertEqual(result, (False, "Пароль должен содержать специальный символ"))

    def test_parol_i_podtverzhdenie_ne_sovpadayut(self):
        result, _ = self.register(VALID_LOGIN, VALID_PASSWORD, "Пароль2!")
        self.assertEqual(result, (False, "Пароль и подтверждение пароля не совпадают"))

    # БАГ 1 (найден и ИСПРАВЛЕН) — src/my_project.py, функция mask_password:
    # раньше mask_password(None) падала с TypeError до блока try.
    # Исправлено: добавлено "if password_value is None: return ''" и str(password_value).
    def test_vse_znacheniya_none_ne_lomayut_programmu(self):
        result, _ = self.register(None, None, None)
        self.assertEqual(result, (False, "Логин не может быть пустым"))

    # БАГ 2 (найден и ИСПРАВЛЕН) — src/my_project.py, функция registration, блок except:
    # логин-число вызывал AttributeError (.lower()), который не перехватывался.
    # Исправлено: except (ValueError, TypeError, AttributeError, re.error)
    def test_login_chislo_obrabatyvaetsya_bez_padeniya(self):
        result, _ = self.register(12345, VALID_PASSWORD, VALID_PASSWORD)
        self.assertEqual(result, (False, "Ошибка выполнения программы"))

    def test_parol_chislo_obrabatyvaetsya_bez_padeniya(self):
        result, _ = self.register(VALID_LOGIN, 1234567, 1234567)
        self.assertEqual(result, (False, "Ошибка выполнения программы"))

    # --- Крайние (граничные) случаи ---
    def test_login_rovno_5_simvolov_prinimaetsya(self):
        result, _ = self.register("liza5", VALID_PASSWORD, VALID_PASSWORD)
        self.assertEqual(result, (True, ""))

    def test_parol_rovno_7_simvolov_prinimaetsya(self):
        result, _ = self.register(VALID_LOGIN, "Пар1!ль", "Пар1!ль")
        self.assertEqual(result, (True, ""))

    def test_telefon_v_nevernom_formate_vydaet_oshibku(self):
        result, _ = self.register("+79131234567", VALID_PASSWORD, VALID_PASSWORD)
        self.assertEqual(result[0], False)

    def test_email_bez_domennoy_zony_vydaet_oshibku(self):
        result, _ = self.register("liza@mail", VALID_PASSWORD, VALID_PASSWORD)
        self.assertEqual(result[0], False)

    def test_login_proveryaetsya_ranshe_parolya(self):
        result, _ = self.register("admin", "", "")
        self.assertEqual(result, (False, "Логин находится в черном списке"))


class TestMaskirovkaIZapuskProgrammy(unittest.TestCase):
    """Проверка маскировки пароля и запуска программы целиком."""

    def test_maskirovka_parolya_v_kody_simvolov(self):
        self.assertEqual(mask_password("Ab1"), "65-98-49")

    def test_zapusk_vsey_programmy_vyvodit_rezultat(self):
        inputs = [VALID_LOGIN, VALID_PASSWORD, VALID_PASSWORD]
        with patch("builtins.input", side_effect=inputs), \
                patch("builtins.print") as mock_print, \
                self.assertLogs(level="DEBUG"):
            run_program()
        mock_print.assert_any_call("Результат:", True)
        mock_print.assert_any_call("Сообщение:", "")

    def test_zapusk_programmy_s_nevernym_loginom_vyvodit_false(self):
        inputs = ["admin", VALID_PASSWORD, VALID_PASSWORD]
        with patch("builtins.input", side_effect=inputs), \
                patch("builtins.print") as mock_print, \
                self.assertLogs(level="DEBUG"):
            run_program()
        mock_print.assert_any_call("Результат:", False)
        mock_print.assert_any_call("Сообщение:", "Логин находится в черном списке")


if __name__ == "__main__":
    unittest.main()
