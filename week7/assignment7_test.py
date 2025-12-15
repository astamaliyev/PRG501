import unittest
from assignment7 import DataHandler, parse_date, parse_float


class TestDataHandler(unittest.TestCase):

    def test_parse_float(self):
        self.assertEqual(parse_float("10.24", "Amount"), 10.24)

    def test_parse_float_invalid_value(self):
        self.assertRaises(
            ValueError, parse_float, "This should throw an exception", "Amount"
        )

    def test_parse_float_negative(self):
        self.assertRaises(ValueError, parse_float, "-1", "Amount")

    def test_parse_date(self):
        self.assertEqual(parse_date("2024-01-20"), "2024-01-20")

    def test_parse_date_invalid(self):
        self.assertRaises(ValueError, parse_date, "20222-123-123")

    def test_income_addition(self):
        dh = DataHandler(autosave=False)
        # make sure that saved values don't mess with test
        dh.incomes = []
        dh.expenses = []
        dh.add_income("job", 1123)
        self.assertListEqual(dh.incomes, [{"source": "job", "amount": 1123}])

    def test_income_addition_negative(self):
        dh = DataHandler(autosave=False)
        self.assertRaises(ValueError, dh.add_income, "job", -1)

    def test_income_addition_empty_source(self):
        dh = DataHandler(autosave=False)
        self.assertRaises(ValueError, dh.add_income, "   ", 100)

    def test_expense_addition(self):
        dh = DataHandler(autosave=False)
        # make sure that saved values don't mess with test
        dh.incomes = []
        dh.expenses = []
        dh.add_expense("car lease", "transportation", 500, "2024-01-20")
        self.assertListEqual(
            dh.expenses,
            [
                {
                    "description": "car lease",
                    "category": "transportation",
                    "amount": 500,
                    "date": "2024-01-20",
                }
            ],
        )

    def test_expense_addition_negative(self):
        dh = DataHandler(autosave=False)
        self.assertRaises(
            ValueError, dh.add_expense, "car lease", "transportation", -10, "2024-01-01"
        )

    def test_expense_addition_empty_description(self):
        dh = DataHandler(autosave=False)
        self.assertRaises(
            ValueError, dh.add_expense, "   ", "transportation", 10, "2024-01-01"
        )

    def test_expense_addition_empty_category(self):
        dh = DataHandler(autosave=False)
        self.assertRaises(
            ValueError, dh.add_expense, "car lease", "   ", 10, "2024-01-01"
        )

    def test_expense_addition_invalid_date(self):
        dh = DataHandler(autosave=False)
        self.assertRaises(
            ValueError, dh.add_expense, "car lease", "transportation", 10, "not-a-date"
        )

    def test_balance(self):
        dh = DataHandler(autosave=False)
        # make sure that saved values don't mess with test
        dh.incomes = []
        dh.expenses = []
        dh.add_income("job", 1123)
        dh.add_expense("car lease", "transportation", 500, "2024-01-20")
        self.assertEqual(dh.balance(), 623)

    def test_total_income(self):
        dh = DataHandler(autosave=False)
        # make sure that saved values don't mess with test
        dh.incomes = []
        dh.expenses = []
        dh.add_income("job", 1123)
        dh.add_income("stocks", 1000)
        dh.add_income("side hustle", 100)
        self.assertEqual(dh.total_income(), 2223)

    def test_total_expenses(self):
        dh = DataHandler(autosave=False)
        # make sure that saved values don't mess with test
        dh.incomes = []
        dh.expenses = []
        dh.add_expense("car lease", "transportation", 500, "2024-01-20")
        dh.add_expense("rent", "housing", 2000, "2024-01-01")
        self.assertEqual(dh.total_expenses(), 2500)


if __name__ == "__main__":
    unittest.main()
