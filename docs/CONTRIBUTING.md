# Contributing to Agent Dashboard

🎉 Thanks for considering contributing to **Agent Dashboard**!  
We welcome all kinds of contributions: bug fixes, features, docs, tests, and ideas.

---

## 🛠️ How to Contribute

### 1. Fork & Clone
```bash
git clone https://github.com/<your-username>/agent_dashboard.git
cd agent_dashboard
````

### 2. Create a Branch

Always create a new branch for your work:

```bash
git checkout -b feature/your-feature-name
```

### 3. Make Changes

* Follow the project’s existing **code style and structure**
* Add/update **tests** for your changes (if applicable)
* Update **documentation** (README or inline comments) when needed

### 4. Commit

Write clear, descriptive commit messages:

```bash
git commit -m "Add support for agent versioning"
```

### 5. Push & Open PR

Push to your fork and open a pull request:

```bash
git push origin feature/your-feature-name
```

Then open a PR on the main repo.

---

## 📖 Code Guidelines

* **Backend**: Python (FastAPI, SQLAlchemy)

  * Use `black` for formatting and `isort` for imports
  * Keep functions/classes modular and documented

* **Frontend**: Vanilla JS/HTML/CSS (later can evolve to React/Vue)

  * Keep UI components small and reusable

* **Tests**:

  * Place tests under `tests/` directory
  * Use `pytest` for backend testing

---

## ✅ Pull Request Checklist

Before submitting a PR, make sure:

* [ ] Code builds and runs without errors
* [ ] Tests pass locally
* [ ] Documentation is updated
* [ ] PR title and description explain the change clearly

---

## 🐛 Reporting Issues

* Use the **Issues tab** to report bugs or request features
* When reporting a bug, include:

  * Steps to reproduce
  * Expected vs actual behavior
  * Environment details (OS, Python version, etc.)

---

## 🌱 Roadmap

If you’d like to work on bigger features, check out the [Roadmap in README](./README.md#roadmap--next-steps).
Feel free to claim an item by opening an issue or commenting on an existing one.

---

## 💬 Communication

* Open issues for discussions and proposals
* Use clear, respectful, and concise language
* We follow a **friendly open-source community standard**

---

## 📜 License

By contributing, you agree that your contributions will be licensed under the [MIT License](./LICENSE).
