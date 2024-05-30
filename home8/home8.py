import pickle
from datetime import datetime
from collections import UserDict

class Field:  # Базовий клас полів запису.
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):  # Клас зберігання імені контакту. Обов'язкове поле.
    def __init__(self, name):
        if not name:
            raise ValueError("Name must not be empty.")
        super().__init__(name)

class Phone(Field):  # Клас зберігання номера телефону. перевіряє телефон (10 цифр).
    def __init__(self, phone):
        if not phone.isdigit() or len(phone) != 10:
            raise ValueError("Phone number must have 10 digits.")
        super().__init__(phone)

class Birthday(Field):  # Клас зберігання дати народження.
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:  # Клас зберігання інформації про контакт. Ім'я та список телефонів.
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        for ph in self.phones:
            if ph.value == phone:
                self.phones.remove(ph)

    def edit_phone(self, old_phone, new_phone):
        phone_exists = False
        for p in self.phones:
            if p.value == old_phone:
                phone_exists = True
                break

        if not phone_exists:
            raise ValueError("Phone number to edit does not exist.")

        if not new_phone.isdigit() or len(new_phone) != 10:
            raise ValueError("New phone number must be a 10-digit number.")

        for ph in self.phones:
            if ph.value == old_phone:
                ph.value = new_phone

    def find_phone(self, phone):
        for ph in self.phones:
            if ph.value == phone:
                return ph
        return None

    def __str__(self):
        birthday_str = str(self.birthday.value.strftime("%d.%m.%Y")) if self.birthday else 'Not specified'
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, birthday: {birthday_str}"

class AddressBook(UserDict):  # Клас зберігання та управління записами.
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise ValueError("Name not found")

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming_birthdays = []
        for user in self.data.values():
            if user.birthday:
                birthday_this_year = datetime(today.year, user.birthday.value.month, user.birthday.value.day).date()
                if birthday_this_year < today:
                    continue
                elif (birthday_this_year - today).days < 7:
                    if birthday_this_year.weekday() == 5:  # Субота
                        birthday_this_year += timedelta(days=2)  # Зміна на понеділок
                    elif birthday_this_year.weekday() == 6:  # Неділя
                        birthday_this_year += timedelta(days=1)  # Зміна на понеділок
                    user_info = {"name": user.name.value, "congratulation_date": birthday_this_year.strftime("%d.%m.%Y")}
                    upcoming_birthdays.append(user_info)
        return upcoming_birthdays

def input_error(func):  # Функція-декоратор обробки виключень.
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "This command cannot be executed."
        except ValueError:
            return "Give me name and phone please."
        except IndexError:
            return "There is no such information."
        except Exception as e:
            return f"Error: {e}"
    return inner

@input_error
def add_birthday(args, book):
    name, birthday = args
    try:
        record = book.find(name)
        if record:
            record.add_birthday(birthday)
            print(f"Birthday added for {name}.")
        else:
            print(f"Contact {name} not found.")
    except ValueError as e:
        print(e)

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        print(f"{name}'s birthday: {record.birthday.value}")
    elif record and not record.birthday:
        print(f"{name} does not have a birthday specified.")
    else:
        print(f"Contact {name} not found.")

@input_error
def birthdays(args, book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if upcoming_birthdays:
        print("Upcoming birthdays:")
        for record in upcoming_birthdays:
            print(f"The congratulation date for {record['name']} is {record['congratulation_date']}")
    else:
        print("No upcoming birthdays.")

def parse_input(user_input):  # Парсинг вводу.
    if not user_input.strip():
        return "", []
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args

def print_help():
    print("Available commands:")
    print("  add <name> <phone>            - Add a new contact")
    print("  change <name> <new_phone>     - Change phone number of a contact")
    print("  phone <name>                  - Show phone number of a contact")
    print("  all                           - Show all contacts")
    print("  add-birthday <name> <birthday> - Add birthday to a contact (format DD.MM.YYYY)")
    print("  show-birthday <name>          - Show birthday of a contact")
    print("  birthdays                     - Show upcoming birthdays")
    print("  help                          - Show this help message")
    print("  close/exit                    - Exit the program")

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()    

# Main function
def main():
    #book = AddressBook()
    book = load_data()  
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command == "":
            continue

        if command in ["close", "exit"]:
            print("Good bye!")
            save_data(book) 
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            if len(args) != 2:
                print("Invalid number of arguments.")
                continue
            name, phone = args
            if not phone.isdigit() or len(phone) != 10:
                print("Phone number must be a 10-digit number.")
                continue
            record = Record(name)
            record.add_phone(phone)
            book.add_record(record)
            print(f"Added new contact: {name} - {phone}")

        elif command == "change":
            if len(args) != 2:
                print("Invalid number of arguments.")
                continue
            name, new_phone = args
            record = book.find(name)
            if record:
                if not new_phone.isdigit() or len(new_phone) != 10:
                    print("New phone number must be a 10-digit number.")
                    continue
                record.edit_phone(record.phones[0].value, new_phone)
                print(f"Phone number changed for {name}.")
            else:
                print(f"Contact {name} not found.")

        elif command == "phone":
            if len(args) != 1:
                print("Invalid number of arguments.")
                continue
            name = args[0]
            record = book.find(name)
            if record:
                print(f"Phone number for {name}: {record.phones[0]}")
            else:
                print(f"Contact {name} not found.")

        elif command == "all":
            print("All contacts:")
            for record in book.data.values():
                print(record)

        elif command == "add-birthday":
            if len(args) != 2:
                print("Invalid number of arguments.")
                continue
            add_birthday(args, book)

        elif command == "show-birthday":
            if len(args) != 1:
                print("Invalid number of arguments.")
                continue
            show_birthday(args, book)

        elif command == "birthdays":
            birthdays(args, book)

        elif command == "help":
            print_help()

        else:
            print("Invalid command. Type 'help' to see available commands.")

if __name__ == "__main__":
    main()
