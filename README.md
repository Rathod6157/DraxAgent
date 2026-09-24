# DraxAgent 🤖

> An AI desktop companion designed to understand your desktop,
> respond to natural language, and assist with real computer tasks.

DraxAgent is an experimental, modular AI desktop agent built to go
beyond chatbot-style interaction.

It combines AI reasoning with desktop observation, application
context, activity intelligence, and computer interaction.

The long-term goal is an assistant that understands what is happening
on your computer and can help you act on that context—with appropriate
user permission.

---

## 🧠 What Is DraxAgent?

DraxAgent is designed around the idea of an intelligent desktop
companion.

Rather than treating every request as an isolated message, DraxAgent
is being developed to use signals such as:

- The active application and window
- Recent desktop activity
- Conversation context
- Available execution results
- Relevant information from the user's environment

For example, DraxAgent should eventually understand a request like:

> "Check what's wrong with my code here."

In a context-aware workflow, it could identify the relevant editor
and file, inspect the code, explain the issue, and ask before making
changes.

This is the direction of the project—not a claim that every part of
that workflow is already complete.

---

## ✨ Current Capabilities

DraxAgent is actively evolving. The following systems are present
in the project, though individual capabilities may still be under
development.

### 🖥️ Desktop Awareness

Observes desktop-window information, including signals such as:

- Application and process
- Executable path
- Window title
- Foreground-window changes

### 🧠 AI Activity Intelligence

Uses AI-assisted classification to infer the user's current activity
from desktop context and visual signals.

The goal is to identify what the user is doing—not merely which
application is open.

### 💬 AI Conversation

Uses the Google Gemini API for natural-language understanding and
response generation.

Conversation context and available execution information can be
included when generating a response.

### 🎯 Intent Understanding

DraxAgent includes intent-routing logic for distinguishing
conversational requests from actionable commands.

The system is being developed to support compound requests,
clarification, and confirmation.

### ⚡ Desktop Interaction

The project includes desktop-control and skill infrastructure for
computer interaction.

Examples of intended workflows include:

- Opening applications
- Interacting with desktop elements
- Running supported actions
- Reporting execution results

Available actions depend on the installed skills and current
implementation.

### 🕒 Activity History

Tracks recent activity classifications to provide continuity
and support context-aware features.

### 🎨 Desktop Interface

The current desktop interface is built with:

- Tauri 2
- HTML and CSS
- TypeScript

The Python backend runs through a bridge process that communicates
with the Tauri application.

---

## 🏗️ Architecture

DraxAgent uses a modular architecture. The frontend, Python
intelligence systems, desktop observation, and execution components
are designed to evolve independently.

```text
                 ┌─────────────────────┐
                 │   Tauri Desktop UI  │
                 │   HTML / CSS / TS   │
                 └──────────┬──────────┘
                            │
                     Python Bridge
                            │
                 ┌──────────▼──────────┐
                 │   Python Backend    │
                 └──────────┬──────────┘
                            │
              ┌─────────────┴─────────────┐
              │                           │
      Conversation & AI            Desktop Awareness
              │                           │
      Intent Understanding       Observer / Context
              │                           │
       Skills / Execution         Activity Intelligence
              │                           │
              └─────────────┬─────────────┘
                            │
                     Gemini API


The architecture is under active development. Components and execution flows may change as the agent becomes more capable. 
```

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Backend | Python |
| AI Provider | Google Gemini API |
| Desktop Shell | Tauri 2 |
| Frontend | TypeScript, HTML, CSS |
| Desktop Interaction | Python desktop-control libraries |
| Desktop Observation | Windows APIs and supporting libraries |
| Communication | Tauri ↔ Python bridge |

## 🚀 Development Setup

DraxAgent is currently developed for Windows.

### Prerequisites

- Python 3.10+
- Node.js and npm
- Rust toolchain
- Tauri 2 Windows development prerequisites
- A Google Gemini API key

### 1. Clone the Repository

Run these commands from the directory where you want the project:

```powershell
git clone https://github.com/Rathod657/DraxAgent.git
cd DraxAgent
```
If you already have the repository, skip this step.

### 2. Create a Python Virtual Environment
```powershell
python -m venv .venv
```
### 3. Activate the Virtual Environment

For PowerShell:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

This only changes the execution policy for the current PowerShell session.
Alternatively, use Command Prompt:
```bat
.venv\Scripts\activate.bat
```
### 4. Install Python Dependencies

If the repository contains a requirements.txt file:
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a .env file in the project root and add your Gemini API key:
```env
GEMINI_API_KEY=your_gemini_api_key
```
Do not commit your .env file or expose your API key.

### 6. Run DraxAgent

Start the Tauri development environment:
```powershell
cd drax-ui
npm install
npm run tauri dev
```
DraxAgent is under active development, so setup commands and dependencies may change as the project evolves.

