# Ghostclone

GhostClone – A tool for anonymously downloading student projects from GitLab, stripping commit metadata to protect privacy.

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/gunsh1p/ghostclone
   cd ghostclone
   ```

2. **Install Dependencies**
   Ensure you have Python installed, then run:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables**
   Create a `.env` file in the root directory and set the following variables:
   - `API_BASE`: The base URL for the GitLab API. Default is `https://git.culab.ru/api/v4`.
   - `ACCESS_TOKEN`: Your personal access token for authenticating with the GitLab API. This variable is required.
   - `PROJECTS_REGEX_BASE`: Regex pattern for matching project paths. Default is `^courses/fundamentals-of-industrial-programming-2025/fundamentals-of-industrial-programming-2025-\\d+/(Java|Golang|Python)+$`.
   - `TECH_TASKS_REGEX_BASE`: Regex pattern for matching tech task URLs. Default is `https://git\\.culab\\.ru/bsc-development-basics-2nd-semester/dev-basics-2025-longreads/[^\\s)]+`.

## Usage

To run the project, execute:
```bash
python main.py
```

## License

This project is licensed under the MIT License. See the LICENSE file for details. 