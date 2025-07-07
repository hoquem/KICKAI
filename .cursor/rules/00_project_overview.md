# Project Overview: KICKAI

### 1. Mission & Problem Statement
KICKAI is an AI-powered platform designed to solve the common challenges of Sunday League football team management, such as fragmented communication, manual coordination, and administrative overload. It provides a comprehensive, automated system for all team operations.

### 2. Core Functional Pillars
The system is built around five key functional domains, as defined in the project's Product Requirements Documents (PRDs):

* **Comprehensive Command System:** A rich set of commands available through a Telegram bot, supporting both explicit slash-commands (e.g., `/add`, `/list`) and natural language processing. The system covers all aspects of player, match, and team administration.
* **Role-Based Team Management:** The system is designed for a structured management team with defined user personas (Admin, Secretary, Manager, Helpers). It enables sophisticated, multi-step workflows for core operations like fixture management, squad selection, and financial tracking.
* **Detailed Match & Schedule Management:** Manages the full lifecycle of various event types (Training, Friendlies, League/Cup Matches). This includes player availability and attendance tracking, post-match data collection (manager/player ratings), and AI-powered performance analysis.
* **Structured Player Onboarding:** A robust, step-by-step process for registering new players. The flow guides users from an admin-generated invitation to final approval, featuring automated reminders and detailed progress tracking for administrators.
* **Secure Payment System:** Integration with Collectiv payment platform for automated payment processing of match fees, membership fees, fines, and miscellaneous items. Features individual payment links for privacy, real-time tracking, automated reminders, and comprehensive financial reporting.

### 3. Key Architectural & Product Principles
* **Agentic Workforce:** A multi-agent CrewAI system orchestrates complex tasks, provides intelligent insights, and powers the natural language interface.
* **Segregated Communication & Access Control:** The system strictly utilizes separate communication channels (e.g., a private "Leadership Chat" and a public "Main Chat"). The information, commands, and level of detail displayed are tailored to the user's role and the chat type they are in, ensuring security and clarity.

### 4. Technology Summary
* **Core Engine**: A sophisticated multi-agent **CrewAI** system.
* **User Interface**: **Telegram Bot**.
* **Backend**: **Firebase Firestore** for real-time data persistence.
* **Payment Processing**: **Collectiv** payment platform integration for secure payment processing.
* **Deployment**: The application is containerized with **Docker** and deployed on the **Railway** platform.
* **AI Models**: Model-agnostic, supporting **Google Gemini**, OpenAI, and local models via Ollama.