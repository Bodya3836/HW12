import pickle
from collections import UserDict
from datetime import datetime
import pickle

class Field:
    def __init__(self, value):
        self._value = None
        self.value = value

    def __str__(self):
        return str(self._value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self.validate(val)
        self._value = val

    def validate(self, val):
        pass

class Name(Field):
    pass

class Phone(Field):
    def validate(self, val):
        if not isinstance(val, str) or not val.isdigit() or len(val) != 10:
            raise ValueError("Неправильний формат номера телефону")

class Birthday(Field):
    def validate(self, val):
        try:
            datetime.strptime(val, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Неправильний формат дати. Використовуйте РРРР-ММ-ДД")

class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday) if birthday else None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if str(p) != str(phone)]

    def edit_phone(self, old_phone, new_phone):
        for i, phone in enumerate(self.phones):
            if str(phone) == str(old_phone):
                self.phones[i] = Phone(new_phone)
                break
        else:
            raise ValueError("Номер телефону не знайдено в записі")

    def find_phone(self, phone):
        for p in self.phones:
            if str(p) == str(phone):
                return p
        return None

    def days_to_birthday(self):
        if not self.birthday:
            return None
        today = datetime.now()
        next_birthday = datetime(today.year, self.birthday.value.month, self.birthday.value.day)
        if today > next_birthday:
            next_birthday = datetime(today.year + 1, self.birthday.value.month, self.birthday.value.day)
        days_remaining = (next_birthday - today).days
        return days_remaining

    def __str__(self):
        phone_str = "; ".join(str(p) for p in self.phones)
        birthday_str = f", день народження: {self.birthday.value}" if self.birthday else ""
        return f"Контакт: {self.name.value}, телефони: {phone_str}{birthday_str}"

class AddressBook(UserDict):
    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        self.load_data()

    def add_record(self, record):
        self.data[record.name.value] = record
        self.save_data()

    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
            self.save_data()

    def iterator(self, chunk_size=10):
        record_names = list(self.data.keys())
        num_records = len(record_names)
        current_index = 0

        while current_index < num_records:
            end_index = current_index + chunk_size
            records_chunk = [self.data[record_name] for record_name in record_names[current_index:end_index]]
            yield records_chunk
            current_index = end_index

    def save_data(self):
        with open(self.filename, 'wb') as file:
            pickle.dump(self.data, file)

    def load_data(self):
        try:
            with open(self.filename, 'rb') as file:
                self.data = pickle.load(file)
        except FileNotFoundError:
            self.data = {}

if __name__ == "__main__":
    address_book = AddressBook("address_book.pkl")
    while True:
        print("Меню:")
        print("1. Додати контакт")
        print("2. Знайти контакт")
        print("3. Видалити контакт")
        print("4. Вивести список контактів")
        print("5. Завершити роботу")

        choice = input("Виберіть опцію: ")

        if choice == "1":
            name = input("Введіть ім'я: ")
            phone = input("Введіть номер телефону: ")
            birthday = input("Введіть дату народження (рррр-мм-дд): ")
            record = Record(name, birthday)
            record.add_phone(phone)
            address_book.add_record(record)
            print("Контакт додано!")

        elif choice == "2":
            search_term = input("Введіть ім'я або номер телефону для пошуку: ")
            found_records = []
            for record in address_book.data.values():
                if search_term in str(record) or search_term in [str(p) for p in record.phones]:
                    found_records.append(record)
            if found_records:
                print("Знайдені контакти:")
                for record in found_records:
                    print(record)
            else:
                print("Контакти не знайдені.")

        elif choice == "3":
            name = input("Введіть ім'я контакту для видалення: ")
            address_book.delete(name)
            print("Контакт видалено!")

        elif choice == "4":
            for records_chunk in address_book.iterator():
                for record in records_chunk:
                    print(record)

        elif choice == "5":
            address_book.save_data()
            print("Дані збережено. Завершення роботи.")
            break

        else:
            print("Неправильний вибір. Спробуйте ще раз.")