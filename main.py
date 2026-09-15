import logging
import sys
import re


log_format = "%(asctime)s | [%(levelname)-7s] | %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"

logging.basicConfig(
    level=logging.DEBUG,
    format=log_format,
    datefmt=date_format,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/file_txt.log", encoding="utf-8")
    ]
)

logging.info("Логгер успешно сконфигурирован")
logging.info("Приложение запущено")


BLACKLIST = {
    "admin",
    "administrator",
    "root",
    "user",
    "test"
}


def mask_password(password_value):
    return "-".join(str(ord(character)) for character in password_value)


def validate_login(login_value):
    if not login_value:
        return False, "Логин не может быть пустым"

    if login_value.lower() in BLACKLIST:
        return False, "Логин находится в черном списке"

    phone_pattern = r"^\+\d-\d{3}-\d{3}-\d{4}$"
    email_pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    login_pattern = r"^[A-Za-z0-9_]{5,}$"

    if re.fullmatch(phone_pattern, login_value):
        return True, ""

    if re.fullmatch(email_pattern, login_value):
        return True, ""

    if re.fullmatch(login_pattern, login_value):
        return True, ""

    if len(login_value) < 5:
        return False, "Логин должен содержать минимум 5 символов"

    return False, (
        "Логин может содержать только латинские буквы, "
        "цифры и знак подчеркивания"
    )


def validate_password(password_value):
    if not password_value:
        return False, "Пароль не может быть пустым"

    if len(password_value) < 7:
        return False, "Пароль должен содержать минимум 7 символов"

    password_pattern = (
        r"[А-Яа-яЁё0-9!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]+"
    )

    if not re.fullmatch(password_pattern, password_value):
        return False, (
            "Пароль может содержать только кириллицу, "
            "цифры и специальные символы"
        )

    if not re.search(r"[А-ЯЁ]", password_value):
        return False, "Пароль должен содержать заглавную букву"

    if not re.search(r"[а-яё]", password_value):
        return False, "Пароль должен содержать строчную букву"

    if not re.search(r"\d", password_value):
        return False, "Пароль должен содержать цифру"

    if not re.search(
        r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]",
        password_value
    ):
        return False, "Пароль должен содержать специальный символ"

    return True, ""


def registration(login_value, password_value, confirmation_value):
    masked_password = mask_password(password_value)
    masked_confirmation = mask_password(confirmation_value)

    try:
        login_valid, login_error = validate_login(login_value)

        if not login_valid:
            logging.error(
                f"Неуспешная регистрация: login={login_value}, "
                f"password={masked_password}, "
                f"confirmation={masked_confirmation}, "
                f"ошибка={login_error}"
            )
            return False, login_error

        password_valid, password_error = validate_password(password_value)

        if not password_valid:
            logging.error(
                f"Неуспешная регистрация: login={login_value}, "
                f"password={masked_password}, "
                f"confirmation={masked_confirmation}, "
                f"ошибка={password_error}"
            )
            return False, password_error

        if password_value != confirmation_value:
            mismatch_error = "Пароль и подтверждение пароля не совпадают"

            logging.error(
                f"Неуспешная регистрация: login={login_value}, "
                f"password={masked_password}, "
                f"confirmation={masked_confirmation}, "
                f"ошибка={mismatch_error}"
            )

            return False, mismatch_error

        logging.info(
            f"Успешная регистрация: login={login_value}, "
            f"password={masked_password}, "
            f"confirmation={masked_confirmation}, "
            f"результат=True"
        )

        return True, ""

    except (ValueError, TypeError, re.error):
        logging.exception(
            f"Ошибка при проверке регистрации: login={login_value}, "
            f"password={masked_password}, "
            f"confirmation={masked_confirmation}"
        )
        return False, "Ошибка выполнения программы"


if __name__ == "__main__":
    user_login = input("Введите логин: ")
    user_password = input("Введите пароль: ")
    user_confirmation = input("Подтвердите пароль: ")

    registration_result, registration_message = registration(
        user_login,
        user_password,
        user_confirmation
    )

    print("Результат:", registration_result)
    print("Сообщение:", registration_message)