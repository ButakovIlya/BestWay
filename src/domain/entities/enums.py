from enum import Enum


# Перечисления для категорий мест
class CityCategory(Enum):
    PERM = "Пермь"


# Перечисления для категорий мест
class PlaceCategory(Enum):
    RESTAURANT = "Ресторан"
    CAFE = "Кофейня"
    MUSEUM = "Музей"
    LANDMARKS = "Достопримечательности"
    INSTA_PLACES = "Инста-места"
    GALLERY = "Галерея"
    THEATER = "Театр"
    WATER_PROCEDURES = "Водные процедуры"
    SKI_RESORTS = "Горнолыжные курорты"
    MASTER_CLASSES = "Мастер-классы"
    DRIVE = "Драйв"
    RELAX = "Расслабиться"
    NIGHT_LIFE = "Жаркая ночь"
    HOTELS = "Отели"
    WALK = "Прогуляться"
    EVENTS = "События"
    FOR_KIDS = "Детям"


# Перечисления для типов мест
class PlaceType(Enum):
    GEORGIAN = "Грузинский"
    ITALIAN = "Итальянский"
    CAFE_KAFE = "Кофейня+кафе"
    JUST_CAFE = "Просто кофейня"

    # Музеи
    LOCAL_HISTORY = "Краеведческий"
    MODERN_ART = "Современное искусство"
    MILITARY = "Военный"
    MEMORIAL = "Мемориальный"
    HISTORICAL = "Исторический"
    FAMOUS_PEOPLE = "Известные личности"
    RETRO_CARS = "Ретро-автомобили"
    CHILDREN = "Детский"
    ETHNOGRAPHIC = "Этнографический"
    TECHNICAL = "Технический"
    PLANETARIUM = "Планетарий"

    # Галереи
    ART = "Художественная"
    PRIVATE = "Частная"
    PERM_ARTISTS = "Пермских художников"

    # Театры
    MUSICAL = "Мюзикл"
    DRAMA = "Драма"
    BALLET = "Балет"
    CONCERT = "Музыкальный концерт"
    SHADOW_THEATER = "Театр теней"
    OPERA = "Опера"
    ECCENTRIC_COMEDY = "Эксцентрическая комедия"
    CHILDREN_PERFORMANCE = "Детский спектакль"
    COMEDY = "Комедия"
    CONTEMPORARY_DRAMA = "Современная драматургия"
    MULTICULTURAL = "Мультикультурность"
    DOCUMENTARY = "Документальность"
    FAIRY_TALE = "Сказка"
    SATIRE = "Сатира"
    POSTER_PERFORMANCE = "Спектакль-плакат"

    # Водные процедуры
    WP_SPA = "Термы/бани/бассейны"

    # Горнолыжные курорты
    GUBAKHA = "Губаха"
    TAKMAN = "Такман"
    ZHEBREI = "Жебреи"

    # Мастер-классы
    POTTERY = "Гончарная мастерская"
    MC_ART = "Художественная мастерская"
    JEWELRY = "Ювелирная мастерская"

    # Драйв
    KARTING = "Картинг"
    ROPE_PARK = "Веревочный парк"

    # Расслабление
    MASSAGE = "Массаж"
    SPA = "Спа"

    # Ночная жизнь
    CLUB = "Клуб"
    BAR = "Бар"

    # Отели
    ONE_STAR = "1 звезды"
    TWO_STARS = "2 звезды"
    THREE_STARS = "3 звезды"
    FOUR_STARS = "4 звезды"
    FIVE_STARS = "5 звезды"

    # Прогулки
    PARK = "Парк"
    GARDEN = "Сад"

    # События
    CONCERTS = "Концерты"
    PERFORMANCES = "Спектакли"

    # Детям
    ZOO = "Зоопарк"
    FUN_PARK = "Фанпарк"
    FK_PLANETARIUM = "Планетарий"
