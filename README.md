Playwright Test Automation Framework
Python-based UI test automation framework built with pytest and Playwright. The tests run against the separate QA Automation Sandbox application. The application under test is not developed or maintained in this repository.
Stack
- Python 3.14
- pytest and pytest-playwright
- Playwright for Python
- pytest-xdist for parallel execution
- Allure for test reporting and run history
- Docker Compose to start the application under test in CI
- GitHub Actions and GitHub Pages
Framework overview
The framework uses a shared UI layer and page/component composition:
- UIMain provides the common UI entry point, with BasePage and BaseComponent as shared abstractions.
- Page objects compose reusable components such as posts, comments, moderation controls, and chat UI rather than inheriting from component classes to reuse behavior.
- Components can operate in the context of a whole page or a specific locator root.
- Playwright locators and role-/test-id-based selectors are preferred where practical.
- API-based authentication and saved browser storage state reduce unnecessary UI login steps.
- API helpers and test-data utilities support setup and verification where UI-only interaction is unnecessary.
- Tests use Playwright's waiting and assertion mechanisms, and network-response checks when the backend result is part of the expected behavior.
The suite covers UI flows across application areas including authentication, feed/posts, comments, messages, search, notifications, and moderation.
Application under test
The tests use QA Automation Sandbox, which is cloned separately and started with Docker Compose in CI. In the current workflow, the application runs in containers while pytest/Playwright runs directly on the GitHub-hosted runner. This is intentional: the test process is not currently run from the framework's Dockerfile.

To start the sandbox locally:
git clone https://github.com/manikosto/qa-automation-sandbox.git
cd qa-automation-sandbox
docker compose up -d --build
The workflow waits for the backend at http://localhost:8000/docs and the frontend at http://localhost:3000 before starting tests.
Local setup
Use a Python version compatible with the current requirements.txt (the CI workflow uses Python 3.14).
git clone https://github.com/jndef/Playwright-Test-Automation-Framework.git
cd Playwright-Test-Automation-Framework
python -m venv .venv
Activate the virtual environment, then install the dependencies and Playwright browsers:

Windows PowerShell
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m playwright install
Linux/macOS
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m playwright install
Start the sandbox in a separate terminal as described above. Configure the environment variables required by the project's configuration and fixtures before running tests. In CI, .env is assembled from GitHub Environment secrets with names starting with ADMIN, MODERATOR, USER, DB, or ROLES, plus the DB_HOST and HOST variables. Use the actual keys referenced by the current configuration and fixtures; credentials and secret values must not be committed to the repository.
Running tests locally
Run the default configured test set:
pytest
Run tests selected by a pytest marker, for example:
pytest -m smoke
To select a browser explicitly:
pytest --browser chromium
pytest --browser firefox
pytest --browser webkit
The exact marker names and default pytest options are defined by the current pytest.ini, tests, and configuration. Check those files before combining marker expressions or changing the default run.
GitHub Actions
The workflow is defined in [`.github/workflows/tests.yml`](.github/workflows/tests.yml) and is started manually:
1. Open the repository's Actions tab and select UI Tests.
2. Select Run workflow.
3. Choose the main branch to publish the report and update the public Allure history.
4. Set the desired inputs and start the run.
Available inputs:
Input	Purpose
STAGE	GitHub Environment used by the run; defaults to local_docker.
BROWSER	chromium, firefox, webkit, or all.
SUITE	smoke, regression, or all.
SERVICES	Application service filter, or all.
TAGS	Marker/tag filter, or all.
THREADS	pytest-xdist worker count: 1, 3, or 5.


The workflow starts the sandbox, waits for the frontend and backend, creates .env from GitHub Environment secrets/variables, builds the pytest marker expression, installs Python dependencies and the selected browser(s), and runs pytest. Allure results are uploaded as an Actions artifact even when the test step fails, when results exist.

The report job runs with if: always() so it can generate an Allure report after an unsuccessful test run. A failed test therefore keeps the test job red, but does not by itself prevent report generation. Public GitHub Pages deployment and persistence of the report archive/history are restricted to runs started from main.
Allure reports
- Latest published report
Each published run is archived under runs/<run_number>-<run_attempt>/ (for example, runs/30-2/). The runs/ directory does not provide a directory listing; use the report links/history to open a specific archived run. Allure history is copied from the previous published run into the next report so that trends can be retained across runs.

Reports are published by the GitHub Actions workflow. A report generated by a run from a branch other than main is not deployed to the public Pages site and does not update the shared archive/history.
Scope and limitations
- This repository contains the automation framework, not the source code of the application under test.
- CI uses Docker Compose to run the sandbox, but currently runs pytest/Playwright on the GitHub runner rather than in the framework's Dockerfile.
- The report reflects the tests and test data available at the selected commit; a green report-generation/deployment job does not mean every test passed. Check the test job and Allure results separately.