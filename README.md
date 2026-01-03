# Mini System: Weather Data Collection & Analytics (Python + PostgreSQL + Docker + Redash)

Небольшая учебная система для генерации, хранения и анализа данных “погода”.

Система состоит из:
- **Python генератора** (SQLAlchemy) — пишет реалистичные погодные показатели в PostgreSQL раз в 3 секунды.
- **PostgreSQL** — хранит таблицу `weather_readings`.
- **Redash** — подключается к PostgreSQL и визуализирует данные на дэшборде.
- (Опционально) **JupyterLab** — для ноутбуков и экспериментов.

---

## Стек

- Python 3.x
- SQLAlchemy (ORM)
- PostgreSQL
- Docker / Docker Compose
- Redash (UI аналитики)

---

## Архитектура и сервисы

Docker Compose поднимает несколько контейнеров:

- `db` — PostgreSQL с пользовательской базой (например `appdb`)
- `app` — Python контейнер с генератором погодных данных
- `jupyter` — JupyterLab (опционально)
- `redash_postgres` — отдельная PostgreSQL БД **для метаданных Redash** (не путать с `db`)
- `redash_redis` — Redis для Redash
- `redash_server`, `redash_scheduler`, `redash_worker` — сервисы Redash

Данные приложения (погода) лежат в **`db`**, метаданные Redash — в **`redash_postgres`**.

---

## Данные и таблица

Генератор пишет в таблицу:

`weather_readings`:
- `id` — PK
- `created_at` — время записи (TIMESTAMPTZ)
- `temperature_c` — температура (°C)
- `humidity_percent` — влажность (%)
- `pressure_hpa` — давление (hPa)
- `wind_speed_mps` — скорость ветра (m/s)

Таблица создаётся автоматически при старте генератора (через SQLAlchemy `create_all`), если её ещё нет.

---

## Быстрый старт

### 1) Предварительные требования
- Установленный Docker Desktop (или Docker Engine) и Docker Compose.

### 2) Переменные окружения
Создайте `.env` в корне проекта (не коммитить):

```env
POSTGRES_DB=appdb
POSTGRES_USER=appuser
POSTGRES_PASSWORD=apppass
