import redis


# ============================================================
# 1. ПОДКЛЮЧЕНИЕ К REDIS
# ============================================================

r = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True,  # Redis возвращает str, а не bytes
)

print("=" * 60)
print("REDIS")
print("=" * 60)

print("Connected:", r.ping())
print()


# ============================================================
# 2. STRING
# ============================================================
# Самый простой тип Redis.
#
# key -> value
#
# Например:
#
# name -> "Shadow"
#
# Используется для:
# - простых значений
# - кэша
# - счётчиков
# - временных данных
# ============================================================

print("2. STRING")
print("-" * 60)

r.set("name", "Shadow")

print("name =", r.get("name"))

# SET с TTL (time-to-live)
#
# Через 60 секунд ключ автоматически исчезнет.
r.set("temporary", "hello", ex=60)

print("temporary =", r.get("temporary"))
print("TTL =", r.ttl("temporary"), "seconds")

# Проверяем существование ключа
print("exists:", r.exists("temporary"))

# Удаляем ключ
r.delete("temporary")

print("exists after delete:", r.exists("temporary"))
print()


# ============================================================
# 3. COUNTER
# ============================================================
# Redis умеет атомарно увеличивать числа.
#
# Это удобно для:
# - просмотров
# - лайков
# - счётчиков запросов
# - rate limiting
# ============================================================

print("3. COUNTER")
print("-" * 60)

# Начальное значение
r.set("views", 0)

# Увеличиваем на 1
r.incr("views")
r.incr("views")
r.incr("views")

print("views =", r.get("views"))

# Увеличиваем сразу на 10
r.incrby("views", 10)

print("views after +10 =", r.get("views"))
print()


# ============================================================
# 4. HASH
# ============================================================
# Hash похож на объект / структуру:
#
# user:1
#   ├── name = Alex
#   ├── age  = 20
#   └── role = admin
#
# Удобно хранить связанные поля одного объекта.
# ============================================================

print("4. HASH")
print("-" * 60)

# На всякий случай удаляем старый ключ
r.delete("user:1")

r.hset(
    "user:1",
    mapping={
        "name": "Alex",
        "age": "20",
        "role": "admin",
    },
)

# Получить весь объект
print("user:1 =", r.hgetall("user:1"))

# Получить одно поле
print("name =", r.hget("user:1", "name"))

# Изменить поле
r.hset("user:1", "age", "21")

print("after update =", r.hgetall("user:1"))

# Удалить отдельное поле
r.hdel("user:1", "role")

print("after removing role =", r.hgetall("user:1"))
print()


# ============================================================
# 5. LIST
# ============================================================
# List — упорядоченный список.
#
# Очень часто используется как простая очередь.
#
# Producer
#     |
#     | RPUSH
#     v
# Redis List
#     |
#     | LPOP / BLPOP
#     v
# Worker
# ============================================================

print("5. LIST / QUEUE")
print("-" * 60)

r.delete("jobs")

# Добавляем задачи в конец списка
r.rpush("jobs", "send_email")
r.rpush("jobs", "resize_image")
r.rpush("jobs", "generate_report")

# Посмотреть весь список
print("jobs =", r.lrange("jobs", 0, -1))

# Забрать первую задачу
job = r.lpop("jobs")

print("processing:", job)

print("remaining jobs =", r.lrange("jobs", 0, -1))
print()


# ============================================================
# 6. SET
# ============================================================
# Set хранит УНИКАЛЬНЫЕ значения.
#
# Если добавить одно значение два раза,
# Redis всё равно хранит его только один раз.
#
# Используется для:
# - уникальных пользователей
# - тегов
# - permissions
# - множества участников
# ============================================================

print("6. SET")
print("-" * 60)

r.delete("online_users")

r.sadd("online_users", 10)
r.sadd("online_users", 20)
r.sadd("online_users", 10)  # Второй раз не добавится

print("online users =", r.smembers("online_users"))

# Проверить, находится ли пользователь в Set
print(
    "user 10 online:",
    r.sismember("online_users", "10"),
)

print(
    "user 99 online:",
    r.sismember("online_users", "99"),
)

# Удалить пользователя
r.srem("online_users", 10)

print("after removing user 10:")
print(r.smembers("online_users"))
print()


# ============================================================
# 7. SORTED SET
# ============================================================
# Sorted Set = уникальные элементы + score.
#
# Например:
#
# Alice -> 100
# Bob   -> 250
# John  -> 180
#
# Redis автоматически поддерживает сортировку по score.
#
# Используется для:
# - рейтингов
# - leaderboard
# - приоритетов
# - ranking
# ============================================================

print("7. SORTED SET / LEADERBOARD")
print("-" * 60)

r.delete("rating")

r.zadd(
    "rating",
    {
        "Alice": 100,
        "Bob": 250,
        "John": 180,
    },
)

# От меньшего score к большему
print(
    "ascending:",
    r.zrange(
        "rating",
        0,
        -1,
        withscores=True,
    ),
)

# От большего score к меньшему
print(
    "descending:",
    r.zrevrange(
        "rating",
        0,
        -1,
        withscores=True,
    ),
)

# Изменяем score
r.zincrby("rating", 50, "Alice")

print(
    "after Alice +50:",
    r.zrevrange(
        "rating",
        0,
        -1,
        withscores=True,
    ),
)

print()


# ============================================================
# 8. TYPES
# ============================================================
# Redis позволяет узнать тип значения конкретного ключа.
#
# string
# hash
# list
# set
# zset
# ============================================================

print("8. TYPES")
print("-" * 60)

keys = [
    "name",
    "user:1",
    "jobs",
    "online_users",
    "rating",
]

for key in keys:
    print(f"{key:20} -> {r.type(key)}")

print()


# ============================================================
# 9. KEYS
# ============================================================
# Для обучения удобно посмотреть все ключи.
#
# В production НЕ стоит постоянно делать KEYS "*"
# на большом Redis.
#
# Там лучше использовать SCAN.
# ============================================================

print("9. KEYS")
print("-" * 60)

print("all keys:")

for key in r.keys("*"):
    print(" ", key)

print()


# ============================================================
# 10. SCAN
# ============================================================
# Более безопасный способ постепенно перебирать ключи.
#
# Особенно полезен, когда ключей очень много.
# ============================================================

print("10. SCAN")
print("-" * 60)

for key in r.scan_iter(match="user:*"):
    print("found:", key)

print()


# ============================================================
# 11. TTL
# ============================================================
# TTL = Time To Live
#
# Можно посмотреть, сколько осталось жить ключу.
#
# -1 -> ключ существует бесконечно
# -2 -> ключа не существует
# ============================================================

print("11. TTL")
print("-" * 60)

r.set("session:123", "user-data", ex=120)

print(
    "session TTL:",
    r.ttl("session:123"),
    "seconds",
)

print()


# ============================================================
# 12. ПРИМЕР CACHE
# ============================================================
# Типичный backend use-case:
#
# Request
#    |
#    v
# Redis GET
#    |
#    +---- есть ----> вернуть данные
#    |
#    +---- нет
#          |
#          v
#      PostgreSQL
#          |
#          v
#      Redis SET
#          |
#          v
#        return
# ============================================================

print("12. CACHE EXAMPLE")
print("-" * 60)


def get_user(user_id: int):
    key = f"cache:user:{user_id}"

    # 1. Сначала ищем данные в Redis
    cached_user = r.get(key)

    if cached_user is not None:
        print("CACHE HIT")
        return cached_user

    # 2. Представим, что здесь запрос в PostgreSQL
    print("CACHE MISS")
    print("Loading from PostgreSQL...")

    user = f"User {user_id}"

    # 3. Кладём результат в Redis на 60 секунд
    r.set(key, user, ex=60)

    return user


print(get_user(42))
print(get_user(42))

print()


# ============================================================
# 13. RATE LIMITING
# ============================================================
# Например:
#
# Пользователь может сделать максимум 5 запросов
# за 60 секунд.
#
# INCR является атомарной операцией.
# ============================================================

print("13. RATE LIMITING")
print("-" * 60)

user_id = 100

rate_key = f"rate:user:{user_id}"

# Начинаем новый период
r.delete(rate_key)

for request_number in range(1, 8):

    count = r.incr(rate_key)

    # Устанавливаем TTL только для первого запроса
    if count == 1:
        r.expire(rate_key, 60)

    if count <= 5:
        print(
            f"request {request_number}: ALLOWED"
        )
    else:
        print(
            f"request {request_number}: BLOCKED"
        )

print()


# ============================================================
# 14. FINISH
# ============================================================

print("=" * 60)
print("DONE")
print("=" * 60)