# DraxAgent 🤖

> An AI desktop companion that observes your activity, understands context, and interacts with your computer through natural language.

DraxAgent is a modular AI desktop companion built to go beyond simple chatbot-style interaction.

Instead of only responding to messages, DraxAgent maintains awareness of the desktop around it — including the active application, window context, recent activity, conversations, and executed actions.

The goal is to build an assistant that doesn't just wait for commands.

It understands what's happening.

---

## 🧠 What is DraxAgent?

DraxAgent is designed around the idea of an **intelligent desktop companion**.

It combines:

- Desktop observation
- Context and memory
- AI-powered understanding
- Natural-language command execution
- Activity intelligence
- Conversational interaction

For example, instead of simply knowing:

> "Microsoft Edge is open"

DraxAgent can infer:

> "You're managing your weekly to-do list in Notion."

The distinction is important.

DraxAgent is not just tracking applications.

It is beginning to understand **what you're doing with them**.

---

## ✨ Current Features

### 🖥️ Desktop Awareness

Continuously observes the active desktop window and tracks:

- Application
- Process
- Executable
- Window title
- Foreground state
- Window changes

### 🧠 AI Activity Intelligence

Uses an AI-powered activity classifier to infer the user's current activity from desktop context.

Examples:

- `Reading Articles`
- `Managing To-do List`
- `Web Searching`
- `Taking Screenshot`

The system is designed to avoid relying on a giant hard-coded list of activities.

### 💾 Working Memory

Maintains recent conversational and desktop events so DraxAgent can use context instead of treating every interaction as completely independent.

### 🎯 Intent Understanding

Understands whether a request is:

- Conversational
- An actionable command
- A compound command
- A request requiring clarification or confirmation

### ⚡ Skill System

Executes desktop actions through natural language.

Examples:

```text
Open Chrome
Close Spotify
Set a timer

🔀 Compound Commands

Supports multiple actions within a single request.

Open Chrome and then open Spotify
💬 Context-Aware Conversation

DraxAgent can combine:

What the user said
Current desktop context
Recent memory
Action execution results
Current activity

to produce more context-aware responses.

🎭 Personality System

Maintains a consistent conversational personality instead of treating every response as an isolated AI completion.

📡 Event-Driven Architecture

Core components communicate through an internal event bus.

This allows systems such as:

Observer
   ↓
Event Bus
   ↓
Memory / Context / Activity Intelligence
   ↓
GUI

to remain relatively independent from each other.

🎨 Desktop GUI

A PyQt-based interface provides:

Live activity display
Chat interaction
Activity updates
Execution feedback
Desktop companion-style UI
🏗️ Architecture

DraxAgent is built as a collection of modular systems rather than one large assistant class.

                    ┌──────────────────┐
                    │      DraxAgent   │
                    └────────┬─────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
       Conversation Engine          Desktop Awareness
              │                             │
       ┌──────┴──────┐                ┌─────┴─────┐
       │             │                │           │
   Understanding  Execution       Observer     Context
       │             │                │           │
       └──────┬──────┘                └─────┬─────┘
              │                             │
              └─────────────┬───────────────┘
                            │
                       Event Bus
                            │
                 ┌──────────┴──────────┐
                 │                     │
          Activity Engine          Memory
                 │
          AI Activity Classifier
                 │
              Gemini

The architecture is intentionally modular so individual systems can evolve without rewriting the entire application.

🛠️ Tech Stack
Language: Python
AI: Google Gemini API
GUI: PyQt
Desktop Observation: Windows APIs / pywin32
Process Information: psutil
Architecture: Event-driven modular components
Configuration: Environment variables

🚀 Getting Started
Prerequisites
Python 3.10+
Windows
A Google Gemini API key
Installation
git clone https://github.com/Rathod6157/DraxAgent.git
cd DraxAgent


pip install -r requirements.txt

Create a .env file:

GEMINI_API_KEY=your_api_key_here

Then start DraxAgent using the project's entry point.

🧪 Project Status

DraxAgent is currently under active development.

The core systems are already working, including:

Desktop observation
Application identification
Context tracking
AI activity classification
Natural-language command execution
Conversation handling
Live GUI activity updates

The project is now moving toward making the assistant more reliable, context-aware, and genuinely useful in day-to-day desktop workflows.

🗺️ Roadmap
Intelligence
 Smarter activity classification
 Activity confidence and stability
 Activity history and patterns
 Context-aware reasoning
 Better handling of ambiguous activities
Memory
 Persistent long-term memory
 Memory relevance scoring
 Better session continuity
Desktop Awareness
 Richer desktop signals
 More application-specific context
 Improved activity transitions
Agent Capabilities
 More desktop skills
 Multi-step task execution
 Better confirmation and recovery
 Proactive assistance
Performance
 Activity classification caching
 Debouncing rapid desktop changes
 Reduced unnecessary AI calls
 Improved asynchronous processing

🤝 Contributing

DraxAgent is currently a personal project and an ongoing experiment in building an intelligent desktop companion.

Ideas, feedback, and contributions are welcome.

📜 License

License information will be added as the project develops.