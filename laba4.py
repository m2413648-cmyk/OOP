from abc import ABC, abstractmethod
from enum import Enum
import random
import pickle
import os
from typing import Dict


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


# ===== 10. ДЕКОРАТОР (ЛАБА 4) =====
class BaseEnemyDecorator(Enemy):
    """Базовый декоратор для врагов"""

    def __init__(self, wrapee: Enemy):
        super().__init__()
        self._wrapee = wrapee

    @property
    def name(self):
        return self._wrapee.name

    @property
    def health(self):
        return self._wrapee.health

    def is_alive(self):
        return self._wrapee.is_alive()

    def take_damage(self, damage: int):
        self._wrapee.take_damage(damage)

    def attack(self, player):
        self._wrapee.attack(player)


class LegendaryEnemyDecorator(BaseEnemyDecorator):
    """Декоратор легендарного врага - добавляет дополнительный урон"""

    def __init__(self, wrapee: Enemy):
        super().__init__(wrapee)
        self._additional_damage = 20

    @property
    def name(self):
        return f"Легендарный {super().name}"

    def attack(self, player):
        super().attack(player)
        self._logger.log("Враг легендарный и наносит дополнительный урон!!!")
        player.take_damage(self._additional_damage)


class WindfuryEnemyDecorator(BaseEnemyDecorator):
    """Декоратор неистовства ветра - добавляет вторую атаку"""

    def __init__(self, wrapee: Enemy):
        super().__init__(wrapee)

    @property
    def name(self):
        return f"Обладающий Неистовством Ветра {super().name}"

    def attack(self, player):
        super().attack(player)
        self._logger.log("Неистовство ветра позволяет врагу атаковать второй раз!!!")
        super().attack(player)


# ===== 11. АДАПТЕР (ЛАБА 4) =====
class WeaponToEnemyAdapter(Enemy):
    """Адаптер для преобразования оружия во врага"""

    def __init__(self, weapon: Weapon):
        super().__init__()
        self._name = "Магическое оружие"
        self._health = 50
        self._weapon = weapon
        self._damage = weapon.get_damage()
        self._dispel_probability = 0.2

    def take_damage(self, damage: int):
        self._logger.log(f"{self._name} получает {damage} урона!")
        self._health -= damage

        dispel_roll = random.random()
        if dispel_roll <= self._dispel_probability:
            self._logger.log("Атака рассеяла заклятие с оружия!")
            self._health = 0

        if self._health > 0:
            self._logger.log(f"У {self._name} осталось {self._health} здоровья")

    def attack(self, player):
        self._logger.log(f"{self._name} атакует {player.name}!")
        player.take_damage(self._damage)


# ===== 12. ФАСАД (ЛАБА 4) =====
class WeaponEquipmentFacade:
    """Фасад для получения оружия по классу персонажа"""

    def __init__(self, character_class: CharacterClass):
        self._character_class = character_class

        if character_class == CharacterClass.WARRIOR:
            self._equipment_chest = WarriorEquipmentChest()
        elif character_class == CharacterClass.THIEF:
            self._equipment_chest = ThiefEquipmentChest()
        elif character_class == CharacterClass.MAGE:
            self._equipment_chest = MagicalEquipmentChest()
        else:
            raise ValueError("Неизвестный класс персонажа")

    def get_weapon(self) -> Weapon:
        return self._equipment_chest.get_weapon()


# ===== 13. ПРОКСИ (ЛАБА 4) =====
class PlayerProfile:
    """POJO с информацией об игроке"""

    def __init__(self, name: str, score: int = 0):
        self.name = name
        self.score = score


class PlayerProfileRepository(ABC):
    """Интерфейс репозитория для работы с профилями"""

    @abstractmethod
    def get_profile(self, name: str) -> PlayerProfile:
        pass

    @abstractmethod
    def update_high_score(self, name: str, score: int):
        pass


class PlayerProfileDBRepository(PlayerProfileRepository):
    """Реализация репозитория через хранение в файле"""

    def __init__(self):
        self._score_filename = "score.pkl"
        self._initialize_db()

    def _initialize_db(self):
        """Инициализация базы данных"""
        if not os.path.exists(self._score_filename):
            empty_db = {}
            self._update_db(empty_db)

    def get_profile(self, name: str) -> PlayerProfile:
        print("Из базы данных достается информация о профилях игроков..")
        player_profile_map = self._find_all()

        if name not in player_profile_map:
            print("В базе данных создается новый профиль...")
            player_profile_map[name] = PlayerProfile(name, 0)
            self._update_db(player_profile_map)

        return player_profile_map[name]

    def update_high_score(self, name: str, score: int):
        print("В базе данных обновляются очки игрока...")
        player_profile_map = self._find_all()

        if name not in player_profile_map:
            print("В базе данных создается новый профиль...")
            player_profile_map[name] = PlayerProfile(name, 0)

        player_profile_map[name].score = score
        self._update_db(player_profile_map)

    def _find_all(self) -> Dict[str, PlayerProfile]:
        """Чтение всех профилей из файла"""
        try:
            with open(self._score_filename, 'rb') as f:
                scores = pickle.load(f)
                return scores
        except Exception as e:
            raise RuntimeError(f"Ошибка чтения базы данных: {e}")

    def _update_db(self, scores: Dict[str, PlayerProfile]):
        """Обновление базы данных"""
        try:
            with open(self._score_filename, 'wb') as f:
                pickle.dump(scores, f)
        except Exception as e:
            raise RuntimeError(f"Ошибка записи в базу данных: {e}")


class PlayerProfileCacheRepository(PlayerProfileRepository):
    """Кеширующая прокси для репозитория профилей"""

    def __init__(self):
        self._cached_profiles: Dict[str, PlayerProfile] = {}
        self._database = PlayerProfileDBRepository()

    def get_profile(self, name: str) -> PlayerProfile:
        if name not in self._cached_profiles:
            print("Профиль игрока не найден в кеше...")
            player_profile_from_database = self._database.get_profile(name)
            self._cached_profiles[name] = player_profile_from_database

        print("Профиль игрока достается из кеша...")
        return self._cached_profiles[name]

    def update_high_score(self, name: str, score: int):
        if name not in self._cached_profiles:
            print("Профиль игрока не найден в кеше...")
            self._database.update_high_score(name, score)
            player_profile_from_database = self._database.get_profile(name)
            self._cached_profiles[name] = player_profile_from_database
            return

        # write-through кеш - пишет сначала в кеш, а потом в БД
        cached_profile = self._cached_profiles[name]
        cached_profile.score = score
        self._database.update_high_score(name, score)


# ===== 14. НОВАЯ ЛОКАЦИЯ (ЛАБА 4) =====
class HauntedManor(Location):
    """Проклятый особняк - новая локация"""

    def __init__(self):
        super().__init__()
        random_class = random.choice(list(CharacterClass))
        self._weapon_equipment_facade = WeaponEquipmentFacade(random_class)

    def spawn_enemy(self) -> Enemy:
        weapon = self._weapon_equipment_facade.get_weapon()
        enchanted_weapon = WeaponToEnemyAdapter(weapon)
        return enchanted_weapon

    def get_location_name(self) -> str:
        return "проклятый особняк"


# ===== 15. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====
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
                 .set_name("Елисей")
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
    locations = [Forest(), DragonBarrow(), HauntedManor()]

    for location in locations:
        enemy = location.spawn_enemy()
        print(f"Локация {location.get_location_name()} создает врага: {enemy.name}")
    print()


# ===== 16. ДЕМОНСТРАЦИИ НОВЫХ ПАТТЕРНОВ (ЛАБА 4) =====
def test_decorator():
    """Демонстрация работы Декоратора"""
    print("=== Демонстрация Decorator ===")

    # Создаем обычного гоблина
    basic_goblin = Goblin()
    print(f"Обычный враг: {basic_goblin.name}")

    # Добавляем декоратор легендарного врага
    legendary_goblin = LegendaryEnemyDecorator(basic_goblin)
    print(f"С легендарным модификатором: {legendary_goblin.name}")

    # Добавляем декоратор неистовства ветра
    windfury_goblin = WindfuryEnemyDecorator(basic_goblin)
    print(f"С неистовством ветра: {windfury_goblin.name}")

    # Комбинируем оба декоратора
    super_goblin = LegendaryEnemyDecorator(WindfuryEnemyDecorator(basic_goblin))
    print(f"Комбинированный враг: {super_goblin.name}")
    print()


def test_adapter():
    """Демонстрация работы Адаптера"""
    print("=== Демонстрация Adapter ===")

    # Создаем обычное оружие
    sword = Sword()
    print(f"Обычное оружие: {sword.__class__.__name__}, урон: {sword.get_damage()}")

    # Адаптируем оружие под врага
    weapon_enemy = WeaponToEnemyAdapter(sword)
    print(f"Адаптированное оружие-враг: {weapon_enemy.name}, здоровье: {weapon_enemy.health}")

    # Демонстрация работы адаптированного врага
    test_player = (PlayableCharacter.Builder()
                   .set_name("Тестовый игрок")
                   .set_character_class(CharacterClass.WARRIOR)
                   .set_weapon(Sword())
                   .set_armor(HeavyArmor())
                   .build())
    weapon_enemy.attack(test_player)
    print()


def test_facade():
    """Демонстрация работы Фасада"""
    print("=== Демонстрация Facade ===")

    # Используем фасад для получения оружия
    for char_class in CharacterClass:
        facade = WeaponEquipmentFacade(char_class)
        weapon = facade.get_weapon()
        print(f"Фасад для {char_class.name}: {weapon.__class__.__name__} (урон: {weapon.get_damage()})")
    print()


def test_proxy():
    """Демонстрация работы Прокси"""
    print("=== Демонстрация Proxy ===")

    # Очищаем старые данные для демонстрации
    if os.path.exists("score.pkl"):
        os.remove("score.pkl")

    # Создаем прокси-репозиторий
    proxy_repository = PlayerProfileCacheRepository()

    print("Первый запрос профиля (должен идти в БД):")
    profile1 = proxy_repository.get_profile("test_player")
    print(f"Профиль: {profile1.name}, счет: {profile1.score}")

    print("\nВторой запрос того же профиля (должен браться из кеша):")
    profile2 = proxy_repository.get_profile("test_player")
    print(f"Профиль: {profile2.name}, счет: {profile2.score}")

    print("\nОбновление счета:")
    proxy_repository.update_high_score("test_player", 100)

    print("\nТретий запрос (из кеша):")
    profile3 = proxy_repository.get_profile("test_player")
    print(f"Профиль: {profile3.name}, счет: {profile3.score}")
    print()


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
        "проклятый особняк": HauntedManor(),
        "логово дракона": DragonBarrow()
    }

    location = locations.get(location_name.lower())
    if not location:
        raise ValueError("Неизвестная локация!")

    return location


def add_enemy_modifiers(enemy: Enemy) -> Enemy:
    """Добавляет модификаторы к врагу с определенной вероятностью"""
    decorator = BaseEnemyDecorator(enemy)

    # С вероятностью 30% на врага накладывается оба модификатора
    second_modifier_probability = 0.3
    second_modifier_proc = random.random() <= second_modifier_probability

    if random.choice([True, False]):
        decorator = LegendaryEnemyDecorator(decorator)
        if second_modifier_proc:
            decorator = WindfuryEnemyDecorator(decorator)
    else:
        decorator = WindfuryEnemyDecorator(decorator)
        if second_modifier_proc:
            decorator = LegendaryEnemyDecorator(decorator)

    return decorator


def get_score(location_name: str, strong_enemy: bool) -> int:
    """Рассчитывает очки в зависимости от локации и модификаторов"""
    base_score = 0

    if location_name.lower() == "мистический лес":
        base_score = 10
    elif location_name.lower() == "проклятый особняк":
        base_score = 50
    elif location_name.lower() == "логово дракона":
        base_score = 100
    else:
        raise ValueError("Неизвестная локация")

    if strong_enemy:
        return base_score * 2

    return base_score


# ===== 17. ОБНОВЛЕННЫЙ ОСНОВНОЙ КОД =====
def main():
    """Обновленный основной игровой цикл"""
    print("=== ИГРА НАЧИНАЕТСЯ ===")

    # Для работы с очками игрока используется кеширующая прокси
    repository = PlayerProfileCacheRepository()

    print("Создайте своего персонажа:")
    name = input("Введите имя: ")

    player_profile = repository.get_profile(name)
    print(f"Текущий счет игрока {player_profile.name}: {player_profile.score}")

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

    print("Куда вы двинетесь? Выберите локацию: (мистический лес, проклятый особняк, логово дракона)")
    location_name = input()
    location = get_location(location_name)

    game_logger.log(f"{player.name} отправился в {location_name}")

    enemy = location.enter_location(player)

    # С шансом в 50% игрок встречает сильного врага
    strong_enemy_curse = random.choice([True, False])
    if strong_enemy_curse:
        game_logger.log(f"Боги особенно немилостивы к {name}, сегодня его ждет страшная битва...")
        enemy = add_enemy_modifiers(enemy)

    game_logger.log(f"У {player.name} на пути возникает {enemy.name}, начинается бой!")

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
        repository.update_high_score(name, 0)
        player_profile = repository.get_profile(name)
        print(f"Новый счет игрока {player_profile.name}: {player_profile.score}")
        return

    game_logger.log(f"Злой {enemy.name} был побежден! {player.name} отправился дальше по тропе судьбы...")

    # Обновляем счет игрока в зависимости от локации и модификаторов врага
    score = get_score(location_name, strong_enemy_curse)
    repository.update_high_score(name, score)
    player_profile = repository.get_profile(name)
    print(f"Новый счет игрока {player_profile.name}: {player_profile.score}")


# Запуск обновленной игры
if __name__ == "__main__":
    # Запуск демонстраций новых паттернов из лабы 4
    test_decorator()
    test_adapter()
    test_facade()
    test_proxy()

    print("=" * 50)

    # Запуск обновленной основной игры
    main()