from abc import ABC, abstractmethod

class Pet(ABC):
    @abstractmethod
    def get_name(self):
        pass
    
    @abstractmethod
    def make_noise(self):
        pass

class Parrot(Pet):
    def __init__(self, name):
        self.name = name
    
    def get_name(self):
        return self.name
    
    def make_noise(self):
        return "Попугай говорит"

class Turtle(Pet):
    def __init__(self, name):
        self.name = name
    
    def get_name(self):
        return self.name
    
    def make_noise(self):
        return "Черепаха издает звук"

class Person:
    def __init__(self, name, pet):
        self.name = name
        self.pet = pet
    
    def get_pet_info(self):
        pet_name = self.pet.get_name()
        pet_sound = self.pet.make_noise()
        print(f"Человек: {self.name}")
        print(f"Питомец: {pet_name}")
        print(f"Звук: {pet_sound}")
        print("-" * 20)

parrot = Parrot("Кеша")
turtle = Turtle("Лео")

person1 = Person("Иван", parrot)
person2 = Person("Мария", turtle)
    
person1.get_pet_info()
person2.get_pet_info()
input()


