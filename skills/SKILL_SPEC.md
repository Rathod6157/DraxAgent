# 🛠️ DraxAgent Skill Specification

Version: 0.1

---

# Goal

Every capability in DraxAgent is a Skill.

Skills are independent modules.

A skill should be removable, replaceable and upgradeable without changing the core of DraxAgent.

---

# Design Rules

A Skill must:

- Do one job well.
- Be independent.
- Not modify other skills.
- Receive a Task.
- Return a Result.

---

# Skill Structure

Every skill should expose:

NAME

INTENT

DESCRIPTION

VERSION

AUTHOR

execute(task)

---

# Example

NAME = "Open Application"

INTENT = "open_app"

DESCRIPTION = "Launch desktop applications."

VERSION = "1.0"

AUTHOR = "Harshith"

def execute(task):
    ...

---

# Communication

Understand

↓

Task Object

↓

Executor

↓

Skill

↓

Result

No skill should directly call another skill.

---

# Future Metadata

SUPPORTED_OS

ALIASES

EXAMPLES

PERMISSIONS

CATEGORY

---

# Categories

System

Browser

Files

Media

AI

Memory

Utilities

Productivity

Developer

Entertainment

---

# Design Philosophy

Adding a new skill should never require editing the core architecture.