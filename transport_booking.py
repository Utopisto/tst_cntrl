import sys
from abc import ABC, abstractmethod


class Transport(ABC):
    def __init__(self, transport_id, capacity):
        self.id = transport_id
        self.capacity = capacity
        self.booked_seats = []

    def book_seat(self, seat_number):
        if seat_number > 0 and seat_number <= self.capacity:
            if seat_number not in self.booked_seats:
                self.booked_seats.append(seat_number)
                return True
        return False

    def get_available_seats(self):
        available = []
        for i in range(1, self.capacity + 1):
            if i not in self.booked_seats:
                available.append(i)
        return available

    @abstractmethod
    def get_info(self):
        pass

    def __str__(self):
        available = self.capacity - len(self.booked_seats)
        return (
            f"{self.__class__.__name__} №{self.id}, "
            f"свободно: {available}/{self.capacity}"
        )


class Bus(Transport):
    def __init__(self, transport_id, capacity, route):
        super().__init__(transport_id, capacity)
        self.route = route

    def get_info(self):
        return f"bus №{self.id}, {self.capacity} мест, маршрут: {self.route}"


class Train(Transport):
    def __init__(self, transport_id, capacity, wagons):
        super().__init__(transport_id, capacity)
        self.wagons = wagons

    def get_info(self):
        return f"train №{self.id}, {self.capacity} мест, вагоны: {self.wagons}"


class Plane(Transport):
    def __init__(self, transport_id, capacity, model):
        super().__init__(transport_id, capacity)
        self.model = model

    def get_info(self):
        return f"plane №{self.id}, {self.capacity} мест, модель: {self.model}"


class Passenger:
    def __init__(self, name, passport_number):
        self.name = name
        self.passport_number = passport_number

    def __str__(self):
        return f"пассажир {self.name}, паспорт: {self.passport_number}"


class Booking:
    def __init__(self, passenger, transport, seat_number):
        self.passenger = passenger
        self.transport = transport
        self.seat_number = seat_number

    def confirm(self):
        if self.transport.book_seat(self.seat_number):
            return (
                f"бронь подтверждена: {self.passenger.name}, "
                f"место {self.seat_number} в {self.transport.__class__.__name__} "
                f"№{self.transport.id}"
            )
        return None

    def __repr__(self):
        return (f"<{self.passenger.name} -> "
                f"{self.transport.__class__.__name__} #{self.transport.id}, "
                f"место {self.seat_number}>")


class BookingSystem:
    def __init__(self):
        self.transports = {}
        self.bookings = []

    def add_transport(self, transport):
        if transport.id in self.transports:
            print(f"ой, транспорт с id {transport.id} уже есть в системе.")
            return
        self.transports[transport.id] = transport
        print(f"транспорт '{transport.id}' успешно добавлен в гараж.")

    def make_booking(self, passenger, transport_id, seat_number):
        transport = self.transports.get(transport_id)
        if not transport:
            return "ошибка: транспорт не найден."

        if seat_number not in transport.get_available_seats():
            return f"ошибка: место {seat_number} недоступно."

        booking = Booking(passenger, transport, seat_number)
        confirmation = booking.confirm()

        if confirmation:
            self.bookings.append(booking)
            return confirmation
        
        return "ошибка бронирования. возможно, место только что заняли."

    def list_bookings(self):
        if not self.bookings:
            print("список броней пока что пуст, как моя душа в понедельник.")
            return
        
        print("--- вот все бронирования ---")
        for b in self.bookings:
            print(b)
        print("---------------------------")

    def list_transports(self):
        if not self.transports:
            print("в гараже пусто, ни одной машины.")
            return
        print("--- наш автопарк ---")
        for t in self.transports.values():
            print(t)
        print("--------------------")


def main_menu(booking_system):
    while True:
        print("\n===== система бронирования \"поехали!\" =====")
        print("1. показать весь транспорт")
        print("2. узнать инфо о транспорте")
        print("3. забронировать билет")
        print("4. показать мои брони")
        print("5. свалить отсюда")

        choice = input("чего хочешь? (введи цифру): ")

        if choice == "1":
            booking_system.list_transports()

        elif choice == "2":
            transport_id = input("введи id транспорта: ")
            transport = booking_system.transports.get(transport_id)
            if transport:
                print(transport.get_info())
                print(f"свободные места: {sorted(transport.get_available_seats())}")
            else:
                print("такого транспорта у нас нет, сорян.")

        elif choice == "3":
            name = input("как тебя зовут?: ")
            passport = input("номер паспорта, пожалуйста: ")
            passenger = Passenger(name, passport)

            transport_id = input("введи id транспорта: ")
            try:
                seat = int(input("какое место хочешь занять?: "))
                message = booking_system.make_booking(passenger, transport_id, seat)
                print(message)
            except ValueError:
                print("ошибка: номер места - это цифра. попробуй еще раз.")

        elif choice == "4":
            booking_system.list_bookings()

        elif choice == "5":
            print("бывай! заходи еще!")
            sys.exit()

        else:
            print("не-а, такой команды нет. выбери цифру из меню.")


if __name__ == "__main__":
    system = BookingSystem()
    system.add_transport(Bus("101", 50, "Москва - Санкт-Петербург"))
    system.add_transport(Train("S77", 250, 12))
    system.add_transport(Plane("A320", 180, "Airbus A320"))
    p1 = Passenger("Иван Иванов", "AA123456")
    p2 = Passenger("Мария Петрова", "BB654321")
    system.make_booking(p1, "101", 25)
    system.make_booking(p2, "S77", 100)
    system.make_booking(p1, "A320", 1)
    main_menu(system) 