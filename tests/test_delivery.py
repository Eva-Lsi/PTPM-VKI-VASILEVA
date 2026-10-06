import unittest

from src.delivery_service import calculate_delivery_cost

ERROR_RESULT = (-1, "0000-00-00")
SHIPMENT_DATE = "2026-09-03"


class TestDeliveryService(unittest.TestCase):
    """Проверка расчета стоимости и даты доставки."""

    def test_weight_and_distance_out_of_limits_return_error(self):
        self.assertEqual(calculate_delivery_cost(0.09, 100, "обычный"), ERROR_RESULT)
        self.assertEqual(calculate_delivery_cost(1.0, 5001, "обычный"), ERROR_RESULT)

    def test_unknown_package_type_returns_error(self):
        self.assertEqual(calculate_delivery_cost(1.0, 100, "стеклянный"), ERROR_RESULT)

    def test_non_numeric_weight_returns_error(self):
        self.assertEqual(calculate_delivery_cost("abc", 100, "обычный"), ERROR_RESULT)

    def test_light_ordinary_package_cost_and_date(self):
        self.assertEqual(calculate_delivery_cost(1.0, 100, "обычный"), (700, "2026-09-04"))

    def test_medium_weight_applies_coefficient_1_2(self):
        self.assertEqual(calculate_delivery_cost(10.0, 100, "обычный")[0], 840)

    def test_heavy_weight_applies_coefficient_1_5(self):
        self.assertEqual(calculate_delivery_cost(20.0, 100, "обычный")[0], 1050)

    def test_fragile_package_adds_300(self):
        self.assertEqual(calculate_delivery_cost(1.0, 100, "хрупкий")[0], 1000)

    def test_dangerous_package_adds_1000(self):
        self.assertEqual(calculate_delivery_cost(1.0, 100, "опасный")[0], 1700)

    def test_express_delivery_costs_more_than_standard(self):
        standard_cost = calculate_delivery_cost(1.0, 100, "обычный")[0]
        express_cost = calculate_delivery_cost(1.0, 100, "обычный", True)[0]
        self.assertGreater(express_cost, standard_cost)

    def test_express_delivery_is_not_on_shipment_day(self):
        date = calculate_delivery_cost(1.0, 100, "обычный", True)[1]
        self.assertGreater(date, SHIPMENT_DATE)


if __name__ == "__main__":
    unittest.main()
