from abc import ABC, abstractmethod
from enum import Enum
import random


# ===== 1. SINGLETON =====
class GameLogger:
    """
    Паттерн Одиночка - гарантирует, что у класса есть только один экземпляр
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True

    def log(self, message: str):
        """Метод для логирования игровых событий"""
        print(f"[GAME LOG]: {message}")


# ===== 2. ENUMS =====
class CharacterClass(Enum):
    """Перечисление классов персонажей"""
    WARRIOR = 100
    THIEF = 90
    MAGE = 80

    @property
    def starting_health(self):
        return self.value


# ===== 3. ABSTRACT INTERFACES =====
class Weapon(ABC):
    """Абстрактный класс оружия"""

    @abstractmethod
    def get_damage(self) -> int:
        pass

    @abstractmethod
    def use(self):
        pass


class Armor(ABC):
    """Абстрактный класс брони"""

    @abstractmethod
    def get_defense(self) -> float:
        pass

    @abstractmethod
    def use(self):
        pass


class Enemy(ABC):
    """Абстрактный класс врага"""

    def __init__(self):
        self._name = ""
        self._health = 0
        self._damage = 0
        self._logger = GameLogger()

    @property
    def name(self):
        return self._name

    @property
    def health(self):
        return self._health

    @abstractmethod
    def take_damage(self, damage: int):
        pass

    @abstractmethod
    def attack(self, player):
        pass

    def is_alive(self):
        return self._health > 0


# ===== 4. WEAPON IMPLEMENTATIONS =====
class Sword(Weapon):
    """Меч - оружие воина"""

    def __init__(self):
        self._damage = 20
        self._logger = GameLogger()

    def get_damage(self) -> int:
        return self._damage

    def use(self):
        self._logger.log("Удар мечом!")


class Bow(Weapon):
    """Лук - оружие вора"""

    def __init__(self):
        self._damage = 15
        self._critical_chance = 0.3
        self._critical_modifier = 2
        self._logger = GameLogger()

    def get_damage(self) -> int:
        roll = random.random()
        if roll <= self._critical_chance:
            self._logger.log("Критический урон!")
            return self._damage * self._critical_modifier
        return self._damage

    def use(self):
        self._logger.log("Выстрел из лука!")


class Staff(Weapon):
    """Посох - оружие мага"""

    def __init__(self):
        self._damage = 25
        self._scatter = 0.2
        self._logger = GameLogger()

    def get_damage(self) -> int:
        roll = random.random()
        factor = 1 + (roll * 2 * self._scatter - self._scatter)
        return round(self._damage * factor)

    def use(self):
        self._logger.log("Воздух накаляется, из посоха вылетает огненный шар!")


# ===== 5. ARMOR IMPLEMENTATIONS =====
class HeavyArmor(Armor):
    """Тяжелая броня"""

    def __init__(self):
        self._defense = 0.3
        self._logger = GameLogger()

    def get_defense(self) -> float:
        return self._defense

    def use(self):
        self._logger.log("Тяжелая броня блокирует значительную часть урона")


class LightArmor(Armor):
    """Легкая броня"""

    def __init__(self):
        self._defense = 0.2
        self._logger = GameLogger()

    def get_defense(self) -> float:
        return self._defense

    def use(self):
        self._logger.log("Легкая броня блокирует урон")


class Robe(Armor):
    """Роба мага"""

    def __init__(self):
        self._defense = 0.1
        self._logger = GameLogger()

    def get_defense(self) -> float:
        return self._defense

    def use(self):
        self._logger.log("Роба блокирует немного урона")


# ===== 6. BUILDER PATTERN =====
class PlayableCharacter:
    """
    Паттерн Строитель - для создания сложных объектов пошагово
    """

    def __init__(self, builder):
        self._logger = GameLogger()
        self._name = builder._name
        self._character_class = builder._character_class
        self._weapon = builder._weapon
        self._armor = builder._armor
        self._health = builder._character_class.starting_health

    class Builder:
        """Внутренний класс-строитель"""

        def __init__(self):
            self._name = None
            self._character_class = None
            self._weapon = None
            self._armor = None

        def set_name(self, name: str):
            self._name = name
            return self

        def set_character_class(self, character_class: CharacterClass):
            self._character_class = character_class
            return self

        def set_weapon(self, weapon: Weapon):
            self._weapon = weapon
            return self

        def set_armor(self, armor: Armor):
            self._armor = armor
            return self

        def build(self):
            """Создаем финальный объект"""
            return PlayableCharacter(self)

    @property
    def name(self):
        return self._name

    @property
    def health(self):
        return self._health

    def take_damage(self, damage: int):
        """Логика получения урона"""
        reduced_damage = round(damage * (1 - self._armor.get_defense()))
        reduced_damage = max(0, reduced_damage)

        self._health -= reduced_damage
        self._armor.use()
        self._logger.log(f"{self._name} получил урон: {reduced_damage}")

        if self._health > 0:
            self._logger.log(f"У {self._name} осталось {self._health} здоровья")

    def attack(self, enemy: Enemy):
        """Атака врага"""
        self._logger.log(f"{self._name} атакует врага {enemy.name}")
        self._weapon.use()
        enemy.take_damage(self._weapon.get_damage())

    def is_alive(self):
        return self._health > 0


# ===== 7. ABSTRACT FACTORY =====
class EquipmentChest(ABC):
    """Абстрактная фабрика для создания снаряжения"""

    @abstractmethod
    def get_weapon(self) -> Weapon:
        pass

    @abstractmethod
    def get_armor(self) -> Armor:
        pass


class WarriorEquipmentChest(EquipmentChest):
    """Фабрика для снаряжения воина"""

    def get_weapon(self) -> Weapon:
        return Sword()

    def get_armor(self) -> Armor:
        return HeavyArmor()


class ThiefEquipmentChest(EquipmentChest):
    """Фабрика для снаряжения вора"""

    def get_weapon(self) -> Weapon:
        return Bow()

    def get_armor(self) -> Armor:
        return LightArmor()


class MagicalEquipmentChest(EquipmentChest):
    """Фабрика для снаряжения мага"""

    def get_weapon(self) -> Weapon:
        return Staff()

    def get_armor(self) -> Armor:
        return Robe()


# ===== 8. ENEMY IMPLEMENTATIONS =====
class Goblin(Enemy):
    def __init__(self):
        super().__init__()
        self._name = "Гоблин"
        self._health = 50
        self._damage = 10

    def take_damage(self, damage: int):
        self._logger.log(f"{self._name} получает {damage} урона!")
        self._health -= damage
        if self._health > 0:
            self._logger.log(f"У {self._name} осталось {self._health} здоровья")

    def attack(self, player):
        self._logger.log(f"{self._name} атакует {player.name}!")
        player.take_damage(self._damage)


class Dragon(Enemy):
    def __init__(self):
        super().__init__()
        self._name = "Дракон"
        self._resistance = 0.2
        self._health = 100
        self._damage = 30

    def take_damage(self, damage: int):
        damage = round(damage * (1 - self._resistance))
        self._logger.log(f"{self._name} получает {damage} урона!")
        self._health -= damage
        if self._health > 0:
            self._logger.log(f"У {self._name} осталось {self._health} здоровья")

    def attack(self, player):
        self._logger.log("Дракон дышит огнем!")
        player.take_damage(self._damage)


# ===== 9. FACTORY METHOD =====
class Location(ABC):
    """Абстрактный класс локации с фабричным методом"""

    def __init__(self):
        self._game_logger = GameLogger()

    def enter_location(self, player) -> Enemy:
        """Общая логика входа в локацию"""
        self._game_logger.log(f"{player.name} отправился в {self.get_location_name()}")

        enemy = self.spawn_enemy()  # Фабричный метод
        self._game_logger.log(f"У {player.name} на пути возникает {enemy.name}, начинается бой!")

        return enemy

    @abstractmethod
    def spawn_enemy(self) -> Enemy:
        """Фабричный метод - создание врага"""
        pass

    @abstractmethod
    def get_location_name(self) -> str:
        pass


class Forest(Location):
    def spawn_enemy(self) -> Enemy:
        return Goblin()  # Реализация фабричного метода

    def get_location_name(self) -> str:
        return "мистический лес"


class DragonBarrow(Location):
    def spawn_enemy(self) -> Enemy:
        return Dragon()  # Реализация фабричного метода

    def get_location_name(self) -> str:
        return "логово дракона"


# ===== 10. DEMONSTRATION FUNCTIONS =====
def test_singleton():
    """Демонстрация работы Одиночки"""
    print("=== Демонстрация Singleton ===")
    logger1 = GameLogger()
    logger2 = GameLogger()

    print(f"logger1 is logger2: {logger1 is logger2}")  # Должно быть True
    logger1.log("Проверка работы логгера")
    print()


def test_builder():
    """Демонстрация работы Строителя"""
    print("=== Демонстрация Builder ===")
    character = (PlayableCharacter.Builder()
                 .set_name("Антон")
                 .set_character_class(CharacterClass.WARRIOR)
                 .set_weapon(Sword())
                 .set_armor(HeavyArmor())
                 .build())

    print(f"Создан персонаж: {character.name}")
    print(f"Здоровье: {character.health}")
    print()


def test_abstract_factory():
    """Демонстрация работы Абстрактной фабрики"""
    print("=== Демонстрация Abstract Factory ===")
    factories = {
        CharacterClass.WARRIOR: WarriorEquipmentChest(),
        CharacterClass.THIEF: ThiefEquipmentChest(),
        CharacterClass.MAGE: MagicalEquipmentChest()
    }

    for char_class, factory in factories.items():
        weapon = factory.get_weapon()
        armor = factory.get_armor()
        print(f"{char_class.name}: {weapon.__class__.__name__} + {armor.__class__.__name__}")
    print()


def test_factory_method():
    """Демонстрация работы Фабричного метода"""
    print("=== Демонстрация Factory Method ===")
    locations = [Forest(), DragonBarrow()]

    for location in locations:
        enemy = location.spawn_enemy()
        print(f"Локация {location.get_location_name()} создает врага: {enemy.name}")
    print()


# ===== 11. MAIN GAME LOGIC =====
def get_chest(character_class: CharacterClass) -> EquipmentChest:
    """Фабричный метод для получения сундука снаряжения"""
    chests = {
        CharacterClass.WARRIOR: WarriorEquipmentChest(),
        CharacterClass.THIEF: ThiefEquipmentChest(),
        CharacterClass.MAGE: MagicalEquipmentChest()
    }
    return chests.get(character_class)


def get_location(location_name: str) -> Location:
    """Фабричный метод для получения локации"""
    locations = {
        "мистический лес": Forest(),
        "логово дракона": DragonBarrow()
    }
    return locations.get(location_name.lower())


def main():
    """Основной игровой цикл"""
    print("=== ИГРА НАЧИНАЕТСЯ ===")
    print("Создайте своего персонажа:")

    name = input("Введите имя: ")

    print("Выберите класс из списка:", [cls.name for cls in CharacterClass])
    class_name = input().upper()

    try:
        character_class = CharacterClass[class_name]
    except KeyError:
        print("Неверный класс персонажа!")
        return

    # Получаем снаряжение через абстрактную фабрику
    starting_equipment_chest = get_chest(character_class)
    starting_armor = starting_equipment_chest.get_armor()
    starting_weapon = starting_equipment_chest.get_weapon()

    # Создаем персонажа через строитель
    player = (PlayableCharacter.Builder()
              .set_name(name)
              .set_character_class(character_class)
              .set_armor(starting_armor)
              .set_weapon(starting_weapon)
              .build())

    game_logger = GameLogger()
    game_logger.log(f"{player.name} очнулся на распутье!")

    print(f"Куда вы двинетесь? Выберите локацию: (мистический лес, логово дракона)")
    location_name = input()
    location = get_location(location_name)

    if not location:
        print("Неизвестная локация!")
        return

    # Входим в локацию - получаем врага через фабричный метод
    enemy = location.enter_location(player)

    # Игровой цикл
    while player.is_alive() and enemy.is_alive():
        input("Нажмите Enter чтобы атаковать! ")
        player.attack(enemy)

        if not enemy.is_alive():
            break

        # Шанс оглушения врага
        stunned = random.choice([True, False])
        if stunned:
            game_logger.log(f"{enemy.name} был оглушен атакой {player.name}!")
            continue

        enemy.attack(player)

    print()
    if not player.is_alive():
        game_logger.log(f"{player.name} был убит...")
    else:
        game_logger.log(f"Злой {enemy.name} был побежден! {player.name} отправился дальше по тропе судьбы...")


if __name__ == "__main__":
    # Запуск демонстраций паттернов
    test_singleton()
    test_builder()
    test_abstract_factory()
    test_factory_method()

    print("=" * 50)

    # Запуск основной игры
    main()