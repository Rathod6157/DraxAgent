# 🧠 DraxMemory Specification

Version: 0.1

---

# Goal

DraxMemory exists to make DraxAgent improve naturally over time.

Instead of only responding to commands, Drax learns:

- Preferences
- Habits
- Workflows
- Frequently used applications
- Frequently used folders
- Frequently used websites
- Frequently used commands

The user should never need to repeatedly teach Drax the same thing.

---

# Core Principles

## 1. Memory should be earned.

Drax should not immediately assume something is a preference.

Repeated behaviour increases confidence.

Example:

Chrome opened once.

↓

Not enough evidence.

↓

Chrome opened 80 times this month.

↓

Chrome becomes the preferred browser.

---

## 2. The user is always in control.

Everything stored by Drax should be:

- Viewable
- Editable
- Exportable
- Deletable

No hidden memory.

---

## 3. Privacy first.

Activity Tracking can be:

ON

OFF

When OFF:

No activity is recorded.

Existing memories remain.

---

## 4. Drax learns silently.

The user should not constantly be interrupted.

Bad:

"Do you like Chrome?"

Good:

After enough evidence,

Drax simply knows.

---

# Memory Types

## Preferences

Stores things the user prefers.

Examples:

Favorite browser

Favorite editor

Favorite terminal

Favorite music app

Favorite IDE

Preferred AI model

Preferred folders

---

## Activity

Stores events.

Example:

Opened Chrome

Opened VS Code

Opened Downloads

Edited project

Watched YouTube

Time

Duration

Frequency

---

## Habits

Built from Activity.

Examples:

Usually edits at 7 PM

Usually studies after dinner

Uses VS Code every morning

Opens Chrome before coding

Uses Calculator frequently during exams

---

## Knowledge

Facts learned.

Examples:

Project "DraxAgent"

Downloads folder

Anime folder

College folder

Documents folder

Git repositories

---

## Conversation Memory

Things explicitly told to Drax.

Example:

"My favorite editor is VS Code."

"My exams start next week."

"I don't like notifications."

---

# Confidence System

Every learned fact has confidence.

Example:

Chrome

Confidence:

12%

↓

35%

↓

67%

↓

95%

The higher the confidence,

the more willing Drax becomes to assume it.

---

# Forgetting

Drax should forget things that stop happening.

Example:

User switched from Chrome to Edge.

Confidence slowly changes.

Chrome:

95%

↓

78%

↓

54%

↓

20%

Edge grows instead.

---

# Commands

memory status

memory show

memory export

memory import

memory clear

forget chrome

forget today

stop tracking

resume tracking

---

# Data Storage

Store memory in JSON.

Example:

preferences.json

activity.json

habits.json

knowledge.json

conversation.json

---

# Future Ideas

Pattern prediction

Workflow prediction

Daily summaries

Weekly summaries

Productivity statistics

Suggestions

Routine detection

Context awareness

Automatic aliases

Learning folder names

Learning project names

Learning repeated commands

---

# Things Drax Should NEVER Store

Passwords

Bank details

Credit card numbers

Private keys

OTP codes

Sensitive files

Biometric information

Encrypted vault contents

Unless the user explicitly creates a secure vault in the future.

---

# Design Philosophy

Memory exists to reduce repetition.

Not to collect data.

The purpose of DraxMemory is:

Less typing.

Less explaining.

More understanding.
