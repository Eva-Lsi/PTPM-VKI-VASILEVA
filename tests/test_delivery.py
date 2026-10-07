import unittest

from src.delivery_service import calculate_delivery_cost

ERROR_RESULT = (-1, "0000-00-00")
SHIPMENT_DATE = "2026-09-03"


class TestRaschetDostavki(unittest.TestCase):
    """Проверка расчета стоимости и даты доставки."""

    def test_ves_i_rasstoyanie_vne_granic_vydayut_oshibku(self):
        self.assertEqual(calculate_delivery_cost(0.09, 100, "обычный"), ERROR_RESULT)
        self.assertEqual(calculate_delivery_cost(1.0, 5001, "обычный"), ERROR_RESULT)

    def test_neizvestnyy_tip_posylki_vydaet_oshibku(self):
        self.assertEqual(calculate_delivery_cost(1.0, 100, "стеклянный"), ERROR_RESULT)

    # !!! ТЕСТ ПАДАЕТ (ERROR) — ошибка в src/delivery_service.py, строка 12:
    # сравнение "abc" < 0.1 вызывает TypeError вместо возврата (-1, "0000-00-00").
    # Исправление строки 12:
    # if not isinstance(weight, (int, float)) or not isinstance(distance, int) or weight < 0.1 or weight > 50.0 or distance < 1 or distance > 5000:
    def test_ves_ne_chislom_vydaet_oshibku(self):
        self.assertEqual(calculate_delivery_cost("abc", 100, "обычный"), ERROR_RESULT)

    def test_legkaya_obychnaya_posylka_cena_i_data(self):
        self.assertEqual(calculate_delivery_cost(1.0, 100, "обычный"), (700, "2026-09-04"))

    def test_sredniy_ves_umnozhaet_cenu_na_1_2(self):
        self.assertEqual(calculate_delivery_cost(10.0, 100, "обычный")[0], 840)

    def test_tyazhelyy_ves_umnozhaet_cenu_na_1_5(self):
        self.assertEqual(calculate_delivery_cost(20.0, 100, "обычный")[0], 1050)

    def test_hrupkaya_posylka_plyus_300(self):
        self.assertEqual(calculate_delivery_cost(1.0, 100, "хрупкий")[0], 1000)

    def test_opasnaya_posylka_plyus_1000(self):
        self.assertEqual(calculate_delivery_cost(1.0, 100, "опасный")[0], 1700)

    # !!! ТЕСТ ПАДАЕТ (FAIL) — ошибка в src/delivery_service.py, строка 36:
    # total_cost *= 0.5 делает экспресс в 2 раза ДЕШЕВЛЕ (350 вместо 700).
    # Исправление строки 36: total_cost *= 1.5
    def test_express_dorozhe_obychnoy_dostavki(self):
        standard_cost = calculate_delivery_cost(1.0, 100, "обычный")[0]
        express_cost = calculate_delivery_cost(1.0, 100, "обычный", True)[0]
        self.assertGreater(express_cost, standard_cost)

    # !!! ТЕСТ ПАДАЕТ (FAIL) — ошибка в src/delivery_service.py, строка 44:
    # при 1 дне доставки 1 // 2 = 0, экспресс "приходит" в день отправки (2026-09-03).
    # Исправление строки 44: days_needed = max(1, days_needed // 2)
    def test_express_ne_v_den_otpravki(self):
        date = calculate_delivery_cost(1.0, 100, "обычный", True)[1]
        self.assertGreater(date, SHIPMENT_DATE)


    # --- Крайние (граничные) случаи ---
    def test_minimalnyy_ves_0_1_kg_prinimaetsya(self):
        self.assertEqual(calculate_delivery_cost(0.1, 100, "обычный"), (700, "2026-09-04"))

    def test_maksimalnyy_ves_50_kg_prinimaetsya(self):
        self.assertEqual(calculate_delivery_cost(50.0, 100, "обычный")[0], 1050)

    def test_ves_bolshe_50_kg_vydaet_oshibku(self):
        self.assertEqual(calculate_delivery_cost(50.1, 100, "обычный"), ERROR_RESULT)

    def test_nulevoe_rasstoyanie_vydaet_oshibku(self):
        self.assertEqual(calculate_delivery_cost(1.0, 0, "обычный"), ERROR_RESULT)

    def test_minimalnoe_rasstoyanie_1_km_prinimaetsya(self):
        self.assertEqual(calculate_delivery_cost(1.0, 1, "обычный"), (205, "2026-09-04"))

    def test_maksimalnoe_rasstoyanie_5000_km_prinimaetsya(self):
        self.assertEqual(calculate_delivery_cost(1.0, 5000, "обычный"), (25200, "2026-09-13"))

    def test_ves_rovno_5_kg_bez_koefficienta(self):
        self.assertEqual(calculate_delivery_cost(5.0, 100, "обычный")[0], 700)

    def test_odin_den_dostavki_na_kazhdye_500_km(self):
        self.assertEqual(calculate_delivery_cost(1.0, 1000, "обычный")[1], "2026-09-05")

    def test_express_sokrashchaet_srok_vdvoe(self):
        self.assertEqual(calculate_delivery_cost(1.0, 2000, "обычный", True)[1], "2026-09-05")


if __name__ == "__main__":
    unittest.main()
