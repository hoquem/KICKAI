# Project KICKAI: System Design & Feature Roadmap

## 1. Overview

**Project KICKAI** is an AI-powered management system for a Sunday League football team. It uses a CrewAI agent workforce to automate administrative and logistical tasks, a Supabase backend for data persistence, and a WhatsApp-based interface for easy interaction with players and managers.

## 2. System Architecture

The system will be composed of five primary components:

1.  **User Interface (WhatsApp):** This is how players and the manager interact with the system. We'll use the Twilio API for WhatsApp to send and receive messages. Players will be able to respond to simple commands (e.g., "Y" for available, "N" for unavailable, or "pay").

2.  **API Bridge (e.g., FastAPI/Flask on a server):** This is a lightweight web service that acts as the crucial link between WhatsApp (Twilio) and our CrewAI application. It receives webhooks, translates messages into tasks for the crew, and sends back the results.

3.  **Backend Logic (CrewAI):** This is the brain of the operation. We will define a "crew" of AI agents with specific roles to handle various tasks.

4.  **Database & Storage (Supabase):** This is our system's memory. It stores player info, fixtures, availability, team selections, match fees, fines, ratings, task assignments, and leaderboards.

5.  **Payment Gateway (Stripe):** To handle online payments for match fees and fines securely. The API bridge will communicate with Stripe to create payment links and confirm transactions.

![System Architecture Diagram](https://placehold.co/800x450/1e293b/ffffff?text=WhatsApp+%3C-%3E+API+Bridge+%3C-%3E+CrewAI+%3C-%3E+Supabase%0A%5E%0A%7C%0Av%0AStripe)

---

## 3. CrewAI Agent Definitions

We'll expand our crew to handle the new responsibilities.

* **`ManagerAgent` (The Orchestrator):**
    * **Goal:** Oversee all team management tasks.
    * **Function:** Interprets high-level commands and delegates tasks to the appropriate specialist agents.

* **`LogisticsCoordinatorAgent` (The Numbers Guy):**
    * **Goal:** Manage all data-related tasks concerning players and matches.
    * **Function:** Interacts directly with the Supabase database for player and fixture data.
    * **Tools:** `get_fixture_details`, `get_all_players`, `update_player_availability`, `get_player_availability_list`, `record_match_result`.

* **`CommunicationsOfficerAgent` (The Town Crier):**
    * **Goal:** Handle all outgoing communications to the team's WhatsApp group.
    * **Function:** Crafts and sends messages, polls, and announcements.
    * **Tools:** `send_whatsapp_message`, `send_whatsapp_poll`.

* **`TreasurerAgent` (The Treasurer):**
    * **Goal:** Manage all team finances.
    * **Function:** Handles match fees, fines, and online payments.
    * **Tools:** `create_payment_link(player_id, amount, reason)`, `issue_fine(player_id, amount, reason)`, `check_payment_status(player_id)`, `get_financial_ledger()`.

* **`TeamAdminAgent` (The Club Secretary):**
    * **Goal:** Manage team engagement and administrative duties.
    * **Function:** Handles ratings, leaderboards, and delegation of chores.
    * **Tools:** `initiate_peer_rating_poll(fixture_id)`, `record_player_rating(player_id, rater_id, rating)`, `update_leaderboard()`, `get_leaderboard(metric)`, `assign_weekly_task(task_name)`.

---

## 4. Feature Roadmap

### Phase 1: MVP - Core Logistics

The goal of the MVP is to solve the most immediate and repetitive problem: getting a team out on a Sunday.

| Feature ID  | Feature Name                  | User Story                                                                                                | Agents Involved                                     | Status      |
| :---------- | :---------------------------- | :-------------------------------------------------------------------------------------------------------- | :-------------------------------------------------- | :---------- |
| **KAI-001** | Player Registration           | As a manager, I can add a new player with their name and phone number to the Supabase database.           | `LogisticsCoordinator`                              | To-Do       |
| **KAI-002** | Announce New Fixture          | As a manager, I can announce the next match details (opponent, location, time) to the team WhatsApp group.  | `Manager`, `CommsOfficer`                           | To-Do       |
| **KAI-003** | Availability Polling          | As a manager, I want to automatically send a "You in?" message for the next game and track player responses. | `Manager`, `LogisticsCoordinator`, `CommsOfficer`   | To-Do       |
| **KAI-004** | View Availability List        | As a manager, I can ask the system "Who is available this week?" and get a simple list back.                | `Manager`, `LogisticsCoordinator`                   | To-Do       |
| **KAI-005** | Announce Squad                | As a manager, I can provide a list of selected players and have the system announce the squad to the group. | `Manager`, `CommsOfficer`                           | To-Do       |
| **KAI-006** | Match Fee Tracking (Manual)   | As a manager, I want the system to know who played and needs to pay, and I can mark them as paid.         | `Manager`, `LogisticsCoordinator`                   | To-Do       |

### Phase 2: V2 Enhancements

| Feature ID  | Feature Name                | User Story                                                                                              | Agents Involved                                                     | Status      |
| :---------- | :-------------------------- | :------------------------------------------------------------------------------------------------------ | :------------------------------------------------------------------ | :---------- |
| **KAI-007** | Automated Squad Selection   | As a manager, I want the system to suggest a squad of 11 starters and 3 subs based on availability.     | `Manager`, `LogisticsCoordinator`, (new) `TacticalAssistantAgent` | Planned     |
| **KAI-010** | Basic Stat Tracking         | As a manager, I can record goals and assists for players after a match to be stored in the database.      | `Manager`, `LogisticsCoordinator`                                   | Planned     |

### Phase 3: Advanced Management & Engagement

| Feature ID  | Feature Name                | User Story                                                                                              | Agents Involved                                           | Status      |
| :---------- | :-------------------------- | :------------------------------------------------------------------------------------------------------ | :-------------------------------------------------------- | :---------- |
| **KAI-012** | Online Payments (Fees)      | As a player, I want to receive a WhatsApp message with a link to pay my match fees online.                | `Manager`, `Treasurer`, `CommsOfficer`                    | Planned     |
| **KAI-013** | Online Payments (Fines)     | As a manager, I can issue a fine to a player, and they will receive a notification with a payment link.   | `Manager`, `Treasurer`, `CommsOfficer`                    | Planned     |
| **KAI-014** | Peer-to-Peer Ratings        | After a match, I want players to be prompted to rate each other's performance to generate a team rating.    | `Manager`, `TeamAdmin`, `CommsOfficer`                    | Planned     |
| **KAI-015** | Player Leaderboard          | As a player, I can request the "leaderboard" and see top players for goals, assists, and attendance.      | `TeamAdmin`, `CommsOfficer`                               | Planned     |
| **KAI-016** | Task Delegation             | As a manager, I want the system to automatically assign weekly chores (e.g., "wash the kit") on a rota basis. | `Manager`, `TeamAdmin`, `CommsOfficer`                    | Planned     |
| **KAI-017** | Automated Reminders         | I want players who haven't paid fees/fines by Tuesday to get an automatic reminder.                         | `Manager`, `Treasurer`, `CommsOfficer`                    | Planned     |

---

## 5. Current Implementation Status

### ✅ Completed Features
- **Supabase Database Schema**: All tables (players, fixtures, availability, ratings, tasks, equipment) implemented with relationships
- **CrewAI Framework**: Five agents (Logistics, Manager, Communications, Tactical, Finance) defined with tools
- **Player Management**: Basic CRUD operations for players via Supabase
- **Sample Data**: 14 players, 3 fixtures, availability, squad, and payment data loaded
- **Task Framework**: Player, fixture, availability, team management, and communication tasks implemented
- **Error Handling**: Comprehensive validation and error handling
- **Environment Configuration**: All required environment variables validated

### 🔄 In Progress
- **LLM Integration**: Google Gemini setup but needs API key/auth fixes
- **Core Player Operations**: Basic functionality working, advanced features pending

### ❌ Not Yet Implemented
- **WhatsApp Integration**: Twilio API integration for messaging
- **API Bridge**: FastAPI/Flask web service for webhooks
- **Stripe Integration**: Payment processing
- **Advanced Features**: Automated squad selection, statistics, ratings, leaderboards, reminders

---

## 6. Development Workflow

### Branch-Based Development Process

All new feature implementations should follow this workflow:

1. **Create Feature Branch**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/KAI-XXX-description
   ```

2. **Implement Feature**
   - Write code for the feature
   - Add tests if applicable
   - Update documentation
   - Test thoroughly

3. **Commit and Push**
   ```bash
   git add .
   git commit -m "feat: implement KAI-XXX description"
   git push origin feature/KAI-XXX-description
   ```

4. **Create Pull Request**
   - Go to GitHub and create a PR from your feature branch to main
   - Add description of changes
   - Request review if needed

5. **Merge and Cleanup**
   ```bash
   # After PR is approved and merged
   git checkout main
   git pull origin main
   git branch -d feature/KAI-XXX-description
   ```

6. **Close GitHub Issue**
   - Mark the corresponding GitHub issue as closed
   - Move to "Done" column in project board

### Next Priority Features to Implement

Based on the current state, here are the recommended next features to implement:

#### 🔴 High Priority (MVP Completion)
1. **KAI-002: WhatsApp Integration** - Set up Twilio WhatsApp API
   - Install Twilio SDK
   - Create WhatsApp messaging tools
   - Set up webhook endpoints
   - Test message sending/receiving

2. **KAI-003: API Bridge (FastAPI)** - Create web service
   - Set up FastAPI application
   - Create webhook endpoints
   - Implement message routing
   - Add authentication

3. **KAI-004: Enhanced Player Management** - Complete player features
   - Add player search and filtering
   - Implement player status updates
   - Create player profile management
   - Add availability tracking

#### 🟡 Medium Priority (V2 Features)
4. **KAI-005: Fixture Management** - Complete fixture operations
5. **KAI-006: Availability System** - Implement polling and tracking
6. **KAI-007: Squad Management** - Create squad selection system

#### 🟢 Low Priority (Future)
7. **KAI-012: Stripe Integration** - Payment processing
8. **KAI-014: Statistics System** - Match stats and ratings
9. **KAI-015: Leaderboards** - Player rankings

### Development Guidelines

- **Always work in feature branches** - never commit directly to main
- **Test thoroughly** before creating PRs
- **Update documentation** with any new features
- **Follow the existing code patterns** and structure
- **Use descriptive commit messages** with feature IDs
- **Close GitHub issues** when features are complete

---

## 7. Getting Started

### Prerequisites
- Python 3.8+
- Supabase account and project
- Google AI API key (for Gemini LLM)
- Twilio account (for WhatsApp integration)
- Stripe account (for payments)

### Setup
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `env.example` to `.env` and fill in your credentials
4. Run the demo: `python src/main.py`

### Testing
- Run sample data setup: `python test_sample_data.py`
- Test specific features using the demo scenarios in `main.py`

---

## 8. Contributing

Please follow the development workflow outlined above. All contributions should be made through feature branches and pull requests.