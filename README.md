# Playwright UI + API Test Automation Framework

A Page Object Model (POM) test automation framework built with **Playwright** and **Pytest**, covering the core flows of a social-network-style web application: feed, comments (with nested replies), likes, bookmarks, follows, direct messages, notifications, search, and admin/moderation.
The test framework was built on top of QA Automation Sandbox (https://github.com/manikosto/qa-automation-sandbox)

This is a personal project built to apply and demonstrate practical automation QA skills - architecture design, network-level verification, and debugging real framework-level issues (not just "happy path" click-through tests).

---

## Tech stack

- **Python** + **Playwright** (sync API)
- **Pytest** - test runner, fixtures, parametrization
- **Allure** - reporting, with request/response payloads attached to failed steps
- **PostgreSQL** (via `psycopg2`) - direct DB access for test data setup/cleanup
- **Faker** - randomized test data generation
- **requests** - API-level actions (login, token refresh, seeding posts, follow/unfollow) used to keep UI tests focused on UI behavior, not on repeatable setup

## Architecture highlights

- **Page Object Model with a Row Object pattern** for repeating elements (posts, comments, users in admin lists). Each row/component receives its own scoped `root: Locator` in the constructor - locators for that instance are built once and never re-resolved against the whole page, which avoids a whole class of "wrong element clicked" bugs common with generic string-selector helpers.
- **Network-level verification, not just DOM checks.** Actions like creating a post/comment, liking, following, and admin moderation are verified via `page.expect_response(...)`, asserting both the outgoing request payload and the returned response - not just that a toast appeared.
- **Session reuse across tests.** Each role's browser storage state is cached to disk and refreshed only when the token is close to expiring (with a fallback to a fresh login), instead of logging in through the UI on every single test.
- **Composition over inheritance** for page/component relationships - a page *owns* its components (`self.alert = AlertComponent(...)`) rather than inheriting their behavior, keeping responsibilities isolated.
- **CSS/test-id locators with anchored regex** (`^post-like-btn-[^-]+$`) preferred over brittle class-based or unanchored selectors, to avoid accidental matches between similarly-prefixed elements (e.g., a comment container vs. a "reply" button inside it).

## Coverage

| Area | Examples |
|---|---|
| Auth | login, invalid credentials, registration validation, banned-user login block |
| Feed / Posts | create post (text/max length/hashtag/image), delete own post, like/unlike, bookmark |
| Comments | create comment, nested replies (multi-level), like/unlike comment |
| Follow | follow/unfollow, "follows you" indicator, followers/following counts |
| Messages | start conversation, send message, unread badge, auto-read on open |
| Notifications | unread badge, mark all as read, filter unread, click-through to target (post/profile/chat) |
| Search | search by user, post content, hashtag, empty-state handling |
| Admin / Moderation | ban/unban, verify/unverify, role change, dashboard stats, moderator post removal |

## Project structure

```
├── base/                    # BasePage, BaseComponent, shared components (alert, sidebar)
├── config/                  # credentials, URLs, DB config
├── helpers/                 # API client, DB handler, storage/session manager, network interceptor, data generator
├── pages/
│   ├── feed_page/
│   │   └── components/      # post, comment, publish forms
│   ├── messages_page/
│   │   └── components/      # chat_component, publish_message_componet, start_conversation_flow
│   ├── notification_page/
│   ├── admin_page/
│   ├── search_page/
│   ├── profile_page/
│   └── login_page/
├── fixtures/                 # DB-backed fixtures (cleanup, seed data lookups)
├── tests/
├── conftest.py
└── pytest.ini
```
## How to run the app
- clone the repository containing the test environment and read the build guide
- configure the .env file by specifying the required details
- run the test environment locally in Docker
  
## Running the tests

```bash
pip install -r requirements.txt
playwright install

# run the full suite
pytest

# run a specific area
pytest -m feed
pytest -m messages

# generate an Allure report
allure serve allure-results
```

Environment variables (`.env`) are required for credentials, DB connection, and the target host - see `config/credentials.py`, `config/db_config.py`, and `config/urls.py` for the expected keys.

## Notes / current limitations

- CI pipeline is not wired up for this project yet - the same approach is planned here).
- A handful of `@pytest.mark.flaky(reruns=...)` markers remain on tests with inherent timing sensitivity (e.g., waiting on a second user's session for cross-user scenarios) rather than fully deterministic waits.

---
