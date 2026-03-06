# Integrate MCP with Copilot

<img src="https://octodex.github.com/images/Professortocat_v2.png" align="right" height="200px" />

Hey joergjo!

Mona here. I'm done preparing your exercise. Hope you enjoy! 💚

Remember, it's self-paced so feel free to take a break! ☕️

[![](https://img.shields.io/badge/Go%20to%20Exercise-%E2%86%92-1f883d?style=for-the-badge&logo=github&labelColor=197935)](https://github.com/joergjo/skills-integrate-mcp-with-copilot/issues/1)

## Local Development

1. Install dependencies:

	```bash
	pip install -r requirements.txt
	```

2. Run the API from `src/`:

	```bash
	cd src
	uvicorn app:app --reload
	```

3. Run tests from repository root:

	```bash
	pytest
	```

### Persistence and Migration Notes

- The application now uses SQLite (`src/mergington.db`) for persistence.
- Schema migrations are applied automatically on startup.
- Initial sample data is seeded if the activities table is empty.

---

&copy; 2025 GitHub &bull; [Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/code_of_conduct.md) &bull; [MIT License](https://gh.io/mit)

