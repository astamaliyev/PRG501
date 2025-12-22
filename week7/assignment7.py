import json
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class DataHandler:
    def __init__(self, autosave=True):
        self.autosave = autosave
        self.incomes = []
        self.expenses = []
        self.files_loaded = True
        try:
            # if loading from file failed, initialize everything to empty
            # to avoid crashing the programm
            self.load_from_file()
        except Exception:
            self.incomes = []
            self.expenses = []
            self.files_loaded = False

    def add_income(self, source: str, amount: float):
        if amount < 0:
            raise ValueError("Income amount can't be negative")
        if not source.strip():
            raise ValueError("Income source must be non-empty")

        self.incomes.append({"source": source, "amount": amount})
        self.save_to_file()

    def add_expense(self, description: str, category: str, amount: float, date: str):
        if not category.strip():
            raise ValueError("Category must be non-empty")
        if not description.strip():
            raise ValueError("Description must be non-empty")
        if amount < 0:
            raise ValueError("Expense amount can't be negative")
        date = parse_date(date)
        self.expenses.append(
            {
                "description": description,
                "category": category,
                "amount": amount,
                "date": date,
            }
        )
        self.save_to_file()

    def delete_income(self, index: int):
        del self.incomes[index]
        self.save_to_file()

    def delete_expense(self, index: int):
        del self.expenses[index]
        self.save_to_file()

    def total_income(self) -> float:
        return sum(i["amount"] for i in self.incomes)

    def total_expenses(self) -> float:
        return sum(e["amount"] for e in self.expenses)

    def balance(self) -> float:
        return self.total_income() - self.total_expenses()

    def save_to_file(self):
        # avoid saving for unit tests
        if not self.autosave:
            return

        with open("finance_data.json", "w") as f:
            data = {"incomes": self.incomes, "expenses": self.expenses}
            json.dump(data, f, indent=4)
        with open("finance_data.txt", "w") as f:
            expense_lines = [
                f'Expense|{expense["description"]}|{expense["category"]}|{expense["amount"]}|{expense["date"]}\n'
                for expense in self.expenses
            ]
            income_lines = [
                f'Income|{income["source"]}|{income["amount"]}\n'
                for income in self.incomes
            ]
            f.writelines(expense_lines)
            f.writelines(income_lines)

    def load_from_file(self):
        # JSON is primary source of data
        # text is a fallback
        try:
            with open("finance_data.json", "r") as f:
                data = json.load(f)
                self.expenses = data["expenses"] or []
                self.incomes = data["incomes"] or []
        except (FileNotFoundError, json.JSONDecodeError):
            with open("finance_data.txt", "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    line_parts = line.split("|")
                    tag = line_parts[0]

                    if tag == "Income":
                        if len(line_parts) != 3:
                            raise ValueError(f"Bad Income line: {line}")
                        self.incomes.append(
                            {"source": line_parts[1], "amount": float(line_parts[2])}
                        )
                    elif tag == "Expense":
                        if len(line_parts) != 5:
                            raise ValueError(f"Bad Expense line: {line}")
                        self.expenses.append(
                            {
                                "description": line_parts[1],
                                "category": line_parts[2],
                                "amount": float(line_parts[3]),
                                "date": line_parts[4],
                            }
                        )
                    else:
                        raise ValueError(f"Unknown line format: {line}")


def parse_float(text: str, field_name: str) -> float:
    try:
        value = float(text)
    except ValueError:
        raise ValueError(f"{field_name} must be a number.")
    if value < 0:
        raise ValueError(f"{field_name} can't be negative.")
    return value


def parse_date(text: str) -> str:
    try:
        text = text.strip()
        if not text:
            # use toda's date by default
            return datetime.today().strftime("%Y-%m-%d")
        datetime.strptime(text, "%Y-%m-%d")
        return text
    except:
        raise ValueError("Date format should be %Y-%m-%d")


class FinanceManager(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Personal Finance Manager")
        self.geometry("1024x800")
        self.data = DataHandler()
        if not self.data.files_loaded:
            messagebox.showerror(
                "File loading error", "Failed to load incomes and expenses from file"
            )

        self.total_income_var = tk.StringVar(value="0.00")
        self.total_expenses_var = tk.StringVar(value="0.00")
        self.balance_var = tk.StringVar(value="0.00")

        self._build_ui()
        self._process_income_change()
        self._process_expense_change()

    def _build_ui(self):
        top = ttk.Frame(self)
        top.pack()
        forms = ttk.Frame(top)
        forms.pack()
        self._build_income_form(forms).pack(
            side="left", fill="x", expand=True, padx=(0, 8)
        )
        self._build_expense_form(forms).pack(
            side="left", fill="x", expand=True, padx=(8, 0)
        )
        mid = ttk.Frame(self, padding=(10, 0, 10, 10))
        mid.pack(fill="both", expand=True)
        self._build_income_list(mid).pack(
            side="left", fill="both", expand=True, padx=(0, 8)
        )
        self._build_expense_list(mid).pack(
            side="left", fill="both", expand=True, padx=(8, 0)
        )

        self._build_totals_bar().pack(fill="x", padx=10, pady=(0, 10))

    def _build_income_form(self, parent):
        box = ttk.LabelFrame(parent, padding=10)
        self.income_source = tk.StringVar()
        self.income_amount = tk.StringVar()
        ttk.Label(box, text="Source").grid(row=0, column=0, sticky="e", padx=5, pady=4)
        ttk.Entry(box, textvariable=self.income_source, width=24).grid(
            row=0, column=1, sticky="w", padx=5, pady=4
        )
        ttk.Label(box, text="Amount").grid(row=1, column=0, sticky="e", padx=5, pady=4)
        ttk.Entry(box, textvariable=self.income_amount, width=12).grid(
            row=1, column=1, sticky="w", padx=5, pady=4
        )
        ttk.Button(box, text="Add Income", command=self.add_income).grid(
            row=2, column=0, columnspan=2, pady=(8, 0)
        )

        return box

    def _build_expense_form(self, parent):
        box = ttk.LabelFrame(parent, padding=10)

        self.expense_description = tk.StringVar()
        self.expense_category = tk.StringVar()
        self.expense_amount = tk.StringVar()
        self.expense_date = tk.StringVar(value=datetime.today().strftime("%Y-%m-%d"))
        self.expense_categories = [
            "Housing",
            "Utilities",
            "Food",
            "Transportation",
            "Healthcare",
            "Insurance",
            "Personal & Lifestyle",
            "Debt & Financial",
            "Entertainment & Recreation",
            "Savings & Investments"
        ]

        ttk.Label(box, text="Description").grid(
            row=0, column=0, sticky="e", padx=5, pady=4
        )
        ttk.Entry(box, textvariable=self.expense_description, width=24).grid(
            row=0, column=1, sticky="w", padx=5, pady=4
        )
        ttk.Label(box, text="Category").grid(row=1, column=0, sticky="e", padx=5, pady=4)
        cb = ttk.Combobox(box, values=self.expense_categories, textvariable=self.expense_category)
        cb.set(self.expense_categories[0])  # Initialize category so it's visible
        cb.grid(row=1, column=1, sticky="w", padx=5, pady=4)
        ttk.Label(box, text="Amount").grid(row=2, column=0, sticky="e", padx=5, pady=4)
        ttk.Entry(box, textvariable=self.expense_amount, width=12).grid(
            row=2, column=1, sticky="w", padx=5, pady=4
        )
        ttk.Label(box, text="Date").grid(row=3, column=0, sticky="e", padx=5, pady=4)
        ttk.Entry(box, textvariable=self.expense_date, width=12).grid(
            row=3, column=1, sticky="w", padx=5, pady=4
        )
        ttk.Label(box, text="(YYYY-MM-DD)").grid(
            row=3, column=2, sticky="w", padx=5, pady=4
        )
        ttk.Button(box, text="Add Expense", command=self.add_expense).grid(
            row=4, column=0, columnspan=3, pady=(8, 0)
        )
        return box

    def _build_income_list(self, parent):
        box = ttk.LabelFrame(parent, text="Income", padding=10)
        self.income_list = tk.Listbox(box)
        self.income_list.pack(side="left", fill="both", expand=True)
        btns = ttk.Frame(box)
        btns.pack(side="left", fill="y", padx=(10, 0))
        ttk.Button(btns, text="Delete", command=self.delete_income).pack()
        return box

    def _build_expense_list(self, parent):
        box = ttk.LabelFrame(parent, text="Expenses", padding=10)
        self.expense_list = tk.Listbox(box)
        self.expense_list.pack(side="left", fill="both", expand=True)
        btns = ttk.Frame(box)
        btns.pack(side="left", fill="y", padx=(10, 0))
        ttk.Button(btns, text="Delete", command=self.delete_expense).pack()
        return box

    def _build_totals_bar(self):
        bar = ttk.Frame(self)
        ttk.Label(bar, text="Total Income:").pack(side="left", padx=(0, 6))
        ttk.Label(bar, textvariable=self.total_income_var).pack(
            side="left", padx=(0, 16)
        )
        ttk.Label(bar, text="Total Expenses:").pack(side="left", padx=(0, 6))
        ttk.Label(bar, textvariable=self.total_expenses_var).pack(
            side="left", padx=(0, 16)
        )
        ttk.Label(bar, text="Balance:").pack(side="left", padx=(0, 6))
        ttk.Label(bar, textvariable=self.balance_var).pack(side="left")

        return bar

    def add_income(self):
        try:
            source = self.income_source.get().strip()
            if not source:
                raise ValueError("Source is required.")
            amount = self.income_amount.get().strip()
            parsed_amount = parse_float(amount, "Amount")

            self.data.add_income(source, parsed_amount)
            self._reset_income_form()
            self._process_income_change()
        except ValueError as e:
            messagebox.showerror("Income Error", str(e))

    def _reset_income_form(self):
        self.income_source.set("")
        self.income_amount.set("")

    def add_expense(self):
        try:
            description = self.expense_description.get().strip()
            category = self.expense_category.get().strip()
            if not description:
                raise ValueError("Description is required.")
            if not category:
                raise ValueError("Category is required.")

            amount = parse_float(self.expense_amount.get().strip(), "Amount")
            date_str = parse_date(self.expense_date.get())

            self.data.add_expense(description, category, amount, date_str)
            self._reset_expense_form()
            self._process_expense_change()
        except ValueError as e:
            messagebox.showerror("Expense Error", str(e))

    def _reset_expense_form(self):
        self.expense_description.set("")
        self.expense_category.set(self.expense_categories[0])
        self.expense_amount.set("")
        self.expense_date.set(datetime.today().strftime("%Y-%m-%d"))

    def delete_income(self):
        sel = self.income_list.curselection()
        if not sel:
            return

        # do nothing if index is 0 to not delete header row
        if sel[0] == 0:
            return

        self.data.delete_income(sel[0] - 1)
        self._process_income_change()

    def delete_expense(self):
        sel = self.expense_list.curselection()
        if not sel:
            return

        # do nothing if index is 0 to not delete header row
        if sel[0] == 0:
            return

        self.data.delete_expense(sel[0] - 1)
        self._process_expense_change()

    def _process_income_change(self):
        # delete evrything from UI and re-populate from self.data
        self.income_list.delete(0, tk.END)
        self.income_list.insert(tk.END, "Income Source  |  Amount")
        for i in self.data.incomes:
            self.income_list.insert(tk.END, f"{i['source']}  |  ${i['amount']:.2f}")
        self._process_totals()

    def _process_expense_change(self):
        # delete evrything from UI and re-populate from self.data
        self.expense_list.delete(0, tk.END)
        self.expense_list.insert(tk.END, "Date  |  Description  |  Category  |  Amount")
        for e in self.data.expenses:
            self.expense_list.insert(
                tk.END,
                f"{e['date']}  |  {e['description']}  |  {e['category']}  |  ${e['amount']:.2f}",
            )
        self._process_totals()

    def _process_totals(self):
        self.total_income_var.set(f"${self.data.total_income():.2f}")
        self.total_expenses_var.set(f"${self.data.total_expenses():.2f}")
        self.balance_var.set(f"${self.data.balance():.2f}")


if __name__ == "__main__":
    FinanceManager().mainloop()
