# 🚀 DraxAgent Roadmap

## Mission

DraxAgent is a desktop teammate that understands user intent, remembers preferences, and automates real work to make using a computer faster and smarter.

---

## Vision

Instead of forcing users to remember commands, DraxAgent should understand natural language, learn habits over time, and execute complete workflows.

---

## Core Principles

- Intent over keywords.
- Skills over giant if-else blocks.
- Memory before personality.
- Automate real work.
- AI is optional, architecture is permanent.

---

## Current Progress

### ✅ Foundation

- Git & GitHub setup
- Project architecture
- Task model
- Intent parser
- Executor
- Skills system
- Stop-word filtering
- Open Windows applications

---

## Roadmap

### Phase 1 — Foundation
- [x] Intent recognition
- [x] Task model
- [x] Skills architecture
- [ ] Skill Manager
- [ ] Better parser

### Phase 2 — Productivity
- [ ] Open folders
- [ ] Search Google
- [ ] Search YouTube
- [ ] Timers
- [ ] Notes
- [ ] File management
- [ ] Multiple Task Handling

### Phase 3 — Memory
- [ ] User preferences
- [ ] Recent history
- [ ] Favorite applications
- [ ] Personalized workflows

### Phase 4 — AI
- [ ] Natural conversations
- [ ] Planning
- [ ] Multi-step reasoning
- [ ] Offline + Online AI

### Phase 5 — Desktop Assistant
- [ ] GUI
- [ ] Voice input
- [ ] Voice output
- [ ] Plugin system

---

## Long-Term Goal

Build a desktop assistant that feels like a reliable teammate instead of another chatbot.

## Things We Won't Build

- We won't rebuild Windows Search.
- We won't rebuild File Explorer.
- We won't replace ChatGPT.
- We won't make features that already exist unless DraxAgent makes them significantly better.

## Future Ideas

- Workflow engine
- Dynamic Skill Loader
- DraxMemory
- AI Planner
- Local LLM support
- Cloud AI support
- Context awareness
- Plugin marketplace
- Multi-PC synchronization

## Design Decisions

### Why Task objects?

Using Task objects allows every module to communicate using the same format.

### Why Skills?

Each feature should be independent so new abilities can be added without modifying existing code.

### Why Memory?

The assistant should adapt to the user instead of asking the same questions repeatedly.

## Project Philosophy

Every new feature must answer two questions:

1. Does it solve a real problem?
2. Will it still make sense when DraxAgent has 100 skills?

If the answer to either question is "No", we redesign it before coding.