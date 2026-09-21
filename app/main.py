"""FastAPI-сайт с отдельными URL и встраиваемым виджетом EchoQube."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
import os
from pathlib import Path
from typing import Final

from fastapi import FastAPI
from fastapi.responses import HTMLResponse


PROJECT_DIR: Final = Path(__file__).resolve().parent.parent
DOTENV_PATH_ENV_NAME: Final = "DOTENV_PATH"
WIDGET_ENV_NAMES: Final = (
    "WIDGET_SCRIPT_URL",
    "WIDGET_RUNTIME_URL",
    "WIDGET_BOT_KEY",
)


@dataclass(frozen=True, slots=True)
class Page:
    """Одна пользовательская страница: URL, идентификатор и видимое название."""

    path: str
    slug: str
    title: str
    description: str


PAGES: Final[tuple[Page, ...]] = (
    Page("/", "home", "Главная", "Добро пожаловать на демонстрационный сайт."),
    Page("/about", "about", "О проекте", "Узнайте, для чего создан этот сайт."),
    Page("/services", "services", "Услуги", "Выберите подходящую услугу."),
    Page("/pricing", "pricing", "Тарифы", "Сравните доступные тарифы."),
    Page("/contacts", "contacts", "Контакты", "Свяжитесь с нашей командой."),
    Page("/blog", "blog", "Блог", "Читайте новые публикации."),
    Page("/faq", "faq", "Вопросы и ответы", "Ответы на популярные вопросы."),
    Page("/portfolio", "portfolio", "Портфолио", "Посмотрите выполненные работы."),
    Page("/team", "team", "Команда", "Познакомьтесь с командой."),
    Page("/careers", "careers", "Вакансии", "Присоединяйтесь к команде."),
    Page("/news", "news", "Новости", "Следите за свежими новостями."),
    Page("/events", "events", "События", "Найдите ближайшее событие."),
    Page("/partners", "partners", "Партнёры", "Познакомьтесь с партнёрами."),
    Page("/reviews", "reviews", "Отзывы", "Прочитайте отзывы клиентов."),
    Page("/case-studies", "case_studies", "Кейсы", "Изучите примеры решений."),
    Page("/resources", "resources", "Материалы", "Полезные материалы в одном месте."),
    Page("/guides", "guides", "Руководства", "Пошаговые руководства."),
    Page("/support", "support", "Поддержка", "Получите помощь."),
    Page("/status", "status", "Статус сервиса", "Проверьте доступность сервиса."),
    Page("/security", "security", "Безопасность", "Принципы защиты данных."),
    Page("/privacy", "privacy", "Конфиденциальность", "Как используются данные."),
    Page("/terms", "terms", "Условия использования", "Правила использования сайта."),
    Page("/features", "features", "Возможности", "Основные возможности продукта."),
    Page("/integrations", "integrations", "Интеграции", "Подключаемые сервисы."),
    Page("/api", "api", "Программный интерфейс", "Сведения о программном интерфейсе."),
    Page("/developers", "developers", "Разработчикам", "Материалы для разработчиков."),
    Page("/community", "community", "Сообщество", "Общайтесь с единомышленниками."),
    Page("/webinars", "webinars", "Вебинары", "Записи и анонсы вебинаров."),
    Page("/academy", "academy", "Обучение", "Учебные материалы."),
    Page("/documentation", "documentation", "Документация", "Справочные материалы по продукту."),
    Page("/roadmap", "roadmap", "План развития", "Будущие улучшения продукта."),
    Page("/changelog", "changelog", "История изменений", "Что изменилось в продукте."),
    Page("/press", "press", "Пресса", "Материалы для прессы."),
    Page("/media-kit", "media_kit", "Материалы для СМИ", "Логотипы и информационные материалы."),
    Page("/sustainability", "sustainability", "Устойчивое развитие", "Наш подход к устойчивому развитию."),
    Page("/accessibility", "accessibility", "Доступность", "Доступность сайта для всех посетителей."),
    Page("/customers", "customers", "Клиенты", "Компании, которые нас выбрали."),
    Page("/industries", "industries", "Отрасли", "Решения для разных отраслей."),
    Page("/solutions", "solutions", "Решения", "Подходящие решения для задач."),
    Page("/start", "start", "Начать работу", "Сделайте первый шаг."),
    Page("/request-demo", "request_demo", "Запросить демонстрацию", "Оставьте заявку на показ продукта."),
    Page("/login", "login", "Вход", "Войдите в учётную запись."),
    Page("/register", "register", "Регистрация", "Создайте учётную запись."),
    Page("/account", "account", "Учётная запись", "Управляйте учётной записью."),
    Page("/billing", "billing", "Оплата", "Управляйте оплатой."),
    Page("/notifications", "notifications", "Уведомления", "Настройте уведомления."),
    Page("/search", "search", "Поиск", "Найдите нужную информацию."),
    Page("/sitemap", "sitemap", "Карта сайта", "Полная карта сайта."),
    Page("/help", "help", "Справка", "Получите справочную информацию."),
)

app = FastAPI(
    title="EchoQube FastAPI Site",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


def parse_dotenv(path: Path) -> dict[str, str]:
    """Разбирает простой файл .env без изменения переменных процесса Python."""

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return {}

    values: dict[str, str] = {}
    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line.removeprefix("export ").lstrip()
        if "=" not in line:
            continue

        key, value = line.split("=", maxsplit=1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        values[key] = value
    return values


def get_widget_embed_snippet() -> str:
    """Создаёт точную строку встраивания EchoQube из актуального файла .env."""

    dotenv_path = Path(os.environ.get(DOTENV_PATH_ENV_NAME, PROJECT_DIR / ".env"))
    dotenv_values = parse_dotenv(dotenv_path)
    configuration = {
        name: dotenv_values.get(name, os.environ.get(name, "")).strip()
        for name in WIDGET_ENV_NAMES
    }
    if not all(configuration.values()):
        return ""

    return (
        f'<script src="{escape(configuration["WIDGET_SCRIPT_URL"], quote=True)}" '
        f'data-bot-key="{escape(configuration["WIDGET_BOT_KEY"], quote=True)}" '
        f'data-runtime-url="{escape(configuration["WIDGET_RUNTIME_URL"], quote=True)}" '
        "async></script>"
    )


def render_page(page: Page) -> str:
    """Строит HTML одной страницы и добавляет сформированный тег виджета."""

    widget_embed_snippet = get_widget_embed_snippet()
    navigation = "".join(
        f'<a href="{escape(item.path, quote=True)}">{escape(item.title)}</a>' for item in PAGES
    )
    return f"""<!doctype html>
<html lang="ru">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{escape(page.title)} — EchoQube FastAPI</title>
    <style>
      :root {{ color-scheme: light; font-family: Arial, sans-serif; }}
      body {{ margin: 0; background: #f4f7fb; color: #15243a; }}
      header {{ background: #15243a; color: white; padding: 1.5rem 2rem; }}
      main {{ max-width: 960px; margin: 2rem auto; padding: 0 1.25rem 3rem; }}
      .card {{ background: white; border-radius: 14px; padding: 2rem; box-shadow: 0 8px 24px #15243a18; }}
      .status {{ margin-top: 1.25rem; padding: 1rem; border-left: 4px solid #4b84d9; background: #edf5ff; }}
      nav {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(148px, 1fr)); gap: .55rem; margin-top: 2rem; }}
      nav a {{ border: 1px solid #d9e2f0; border-radius: 7px; color: #225ca8; padding: .6rem; text-decoration: none; }}
      nav a:hover {{ background: #eaf2ff; }}
    </style>
  </head>
  <body>
    <header><strong>EchoQube × FastAPI</strong></header>
    <main>
      <section class="card">
        <h1>{escape(page.title)}</h1>
        <p>{escape(page.description)}</p>
      </section>
      <nav aria-label="Все страницы">{navigation}</nav>
    </main>
    {widget_embed_snippet}
  </body>
</html>"""


def make_page_handler(page: Page):
    """Создаёт независимый обработчик для конкретного пользовательского URL."""

    async def page_handler() -> HTMLResponse:
        return HTMLResponse(render_page(page))

    page_handler.__name__ = f"page_{page.slug}"
    return page_handler


for registered_page in PAGES:
    app.add_api_route(
        registered_page.path,
        make_page_handler(registered_page),
        methods=["GET"],
        response_class=HTMLResponse,
        include_in_schema=False,
    )

