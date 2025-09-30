class Vehicle:
    def __init__(self, make, model, year):
        self.make = make
        self.model = model
        self.year = year
        self.speed = 0

    def display_info(self):
        print(f"Make: {self.make}, Model: {self.model}, Year: {self.year}")

    def move(self, speed):
        self.speed = speed
        print(f"{self.make} {self.model} is moving at {self.speed} km/h.")

    def stop(self):
        self.speed = 0
        print(f"{self.make} {self.model} has stopped.")

class Car(Vehicle):
    def __init__(self, make, model, year, engine_type, number_of_doors):
        super().__init__(make, model, year)
        self.engine_type = engine_type
        self.number_of_doors = number_of_doors

    def honk(self):
        print(f"{self.make} {self.model} honks: Beep-beep!")

    def display_info(self):
        super().display_info() 
        print(f"Engine Type: {self.engine_type}, Doors: {self.number_of_doors}")

class ElectricCar(Car):
    def __init__(self, make, model, year, number_of_doors, battery_capacity):
        super().__init__(make, model, year, "electric", number_of_doors)
        self.battery_capacity = battery_capacity
        self.charge_level = 100

    def charge_battery(self):
        self.charge_level = 100
        print(f"The battery of {self.make} {self.model} is fully charged.")

    def display_info(self):
        super().display_info()
        print(f"Battery Capacity: {self.battery_capacity} kWh, Charge Level: {self.charge_level}%")

class Truck(Car):
    def __init__(self, make, model, year, engine_type, payload_capacity):
        super().__init__(make, model, year, engine_type, 2)
        self.payload_capacity = payload_capacity 
        self.current_load = 0

    def load_cargo(self, weight):
        if self.current_load + weight <= self.payload_capacity:
            self.current_load += weight
            print(f"Loaded {weight} kg into {self.make}. Current load: {self.current_load} kg.")
        else:
            print("Error: Maximum payload capacity exceeded!")

    def display_info(self):
        super().display_info()
        print(f"Payload Capacity: {self.payload_capacity} kg, Current Load: {self.current_load} kg.")

def main():
    # Создание и демонстрация объекта Car
    my_car = Car("Toyota", "Camry", 2022, "gasoline", 4)
    my_car.display_info()
    my_car.move(60)
    my_car.honk()
    my_car.stop()

    # Создание и демонстрация объекта ElectricCar
    my_electric_car = ElectricCar("Tesla", "Model S", 2023, 4, 100)
    my_electric_car.display_info()
    my_electric_car.move(80)
    my_electric_car.charge_battery()
    my_electric_car.stop()

    # Создание и демонстрация объекта Truck
    my_truck = Truck("Volvo", "FH16", 2021, "diesel", 20000)
    my_truck.display_info()
    my_truck.load_cargo(5000)
    my_truck.load_cargo(10000)
    my_truck.load_cargo(6000) # Это вызовет ошибку
    my_truck.move(70)

if __name__ == "__main__":
    main()