import re

FILE = r'reg_numbers.txt'
UNAUTHORIZED = 2


class Database:

    def __init__(self):
        pass

    @staticmethod
    def print_formatted_reg_num(reg_num):
        data = re.search(r'([a-zA-Z]{2})([0-9]{2})([a-zA-Z]{1,2})([0-9]{1,4})', reg_num)
        print("{state_code} {district_code} {unique_code} {unique_number}".format(state_code=data.group(1),
                                                                                  district_code=data.group(2),
                                                                                  unique_code=data.group(3),
                                                                                  unique_number=data.group(4)))

    @staticmethod
    def format_reg_number(reg_number):
        return ''.join([x for x in reg_number if x.isalnum()])

    @staticmethod
    def is_valid_number(reg_number):
        if re.search(r'^[a-zA-Z]{2}[0-9]{2}[a-zA-Z]{1,2}[0-9]{1,4}$', reg_number):
            return True
        return False

    @staticmethod
    def number_exists(reg_number):
        with open(FILE, 'r') as _file:
            for data in _file.readlines():
                re_num, vtype = data.split(',')
                if re_num == reg_number:
                    return int(vtype[:-1])

        return UNAUTHORIZED

    def load_reg_number(self, reg_number):
        formatted_reg_number = self.format_reg_number(reg_number)
        if self.is_valid_number(formatted_reg_number):
            if not self.number_exists(formatted_reg_number):
                with open(FILE, 'a') as _file:
                    _file.write('{}\n'.format(formatted_reg_number))
            else:
                print("Entered registration number already exists in records")
        else:
            print("Entered registration number is invalid. Please enter a valid one")
            # raise  # TODO: Raise a valid exception

    def display_numbers(self):
        with open(FILE, 'r') as _file:
            for re_num in _file.readlines():
                self.print_formatted_reg_num(re_num)


if __name__ == "__main__":
    r = Database()
    while True:
        print("""
        1) Add the registration number
        2) Display all the registration numbers
        3) Check registration number exists
        4) Exit""")
        try:
            choice = int(input("Enter the choice: "))
        except TypeError:
            print("Invalid value entered. Please enter a valid choice")
            continue

        if choice == 1:
            number = input("Enter the registration number: ")
            r.load_reg_number(number)
        elif choice == 2:
            r.display_numbers()
        elif choice == 3:
            number = input("Enter the registration number: ")
            if r.number_exists(r.format_reg_number(number)):
                print("Entered registration number: {} exists".format(number))
            else:
                print("Entered registration number: {} does not exist in records".format(number))
            pass
        elif choice == 4:
            print("Thank you")
            exit(0)
        else:
            print("Invalid choice. Please select a valid choice")
