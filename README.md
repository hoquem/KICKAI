Project KICKAI: System Design & Feature Roadmap
1. Overview
Project KICKAI is an AI-powered management system for a Sunday League football team. It uses a CrewAI agent workforce to automate administrative and logistical tasks, a Supabase backend for data persistence, and a WhatsApp-based interface for easy interaction with players and managers.

2. System Architecture
The system will be composed of five primary components:

User Interface (WhatsApp): This is how players and the manager interact with the system. We'll use the Twilio API for WhatsApp to send and receive messages. Players will be able to respond to simple commands (e.g., "Y" for available, "N" for unavailable, or "pay").

API Bridge (e.g., FastAPI/Flask on a server): This is a lightweight web service that acts as the crucial link between WhatsApp (Twilio) and our CrewAI application. It receives webhooks, translates messages into tasks for the crew, and sends back the results.

Backend Logic (CrewAI): This is the brain of the operation. We will define a "crew" of AI agents with specific roles to handle various tasks.

Database & Storage (Supabase): This is our system's memory. It stores player info, fixtures, availability, team selections, match fees, fines, ratings, task assignments, and leaderboards.

Payment Gateway (Stripe): To handle online payments for match fees and fines securely. The API bridge will communicate with Stripe to create payment links and confirm transactions.

3. CrewAI Agent Definitions
We'll expand our crew to handle the new responsibilities.

ManagerAgent (The Orchestrator):

Goal: Oversee all team management tasks.

Function: Interprets high-level commands and delegates tasks to the appropriate specialist agents.

LogisticsCoordinatorAgent (The Numbers Guy):

Goal: Manage all data-related tasks concerning players and matches.

Function: Interacts directly with the Supabase database for player and fixture data.

Tools: get_fixture_details, get_all_players, update_player_availability, get_player_availability_list, record_match_result.

CommunicationsOfficerAgent (The Town Crier):

Goal: Handle all outgoing communications to the team's WhatsApp group.

Function: Crafts and sends messages, polls, and announcements.

Tools: send_whatsapp_message, send_whatsapp_poll.

TreasurerAgent (The Treasurer) - NEW:

Goal: Manage all team finances.

Function: Handles match fees, fines, and online payments.

Tools: create_payment_link(player_id, amount, reason), issue_fine(player_id, amount, reason), check_payment_status(player_id), get_financial_ledger().

TeamAdminAgent (The Club Secretary) - NEW:

Goal: Manage team engagement and administrative duties.

Function: Handles ratings, leaderboards, and delegation of chores.

Tools: initiate_peer_rating_poll(fixture_id), record_player_rating(player_id, rater_id, rating), update_leaderboard(), get_leaderboard(metric), assign_weekly_task(task_name).

4. Feature Roadmap
Phase 1: MVP - Core Logistics

The goal of the MVP is to solve the most immediate and repetitive problem: getting a team out on a Sunday.

Feature ID

Feature Name

User Story

Agents Involved

Status

KAI-001

Player Registration

As a manager, I can add a new player with their name and phone number to the Supabase database.

LogisticsCoordinator

To-Do

KAI-002

Announce New Fixture

As a manager, I can announce the next match details (opponent, location, time) to the team WhatsApp group.

Manager, CommsOfficer

To-Do

KAI-003

Availability Polling

As a manager, I want to automatically send a "You in?" message for the next game and track player responses.

Manager, LogisticsCoordinator, CommsOfficer

To-Do

KAI-004

View Availability List

As a manager, I can ask the system "Who is available this week?" and get a simple list back.

Manager, LogisticsCoordinator

To-Do

KAI-005

Announce Squad

As a manager, I can provide a list of selected players and have the system announce the squad to the group.

Manager, CommsOfficer

To-Do

KAI-006

Match Fee Tracking (Manual)

As a manager, I want the system to know who played and needs to pay, and I can mark them as paid.

Manager, LogisticsCoordinator

To-Do

Phase 2: V2 Enhancements

| Feature ID | Feature Name                | User Story                                                                                              | Agents Involved                                                     | Status      |
| :--------- | :-------------------------- | :------------------------------------------------------------------------------------------------------ | :------------------------------------------------------------------ | Planned     |
| KAI-007| Automated Squad Selection   | As a manager, I want the system to suggest a squad of 11 starters and 3 subs based on availability.     | Manager, LogisticsCoordinator, (new) TacticalAssistantAgent | Planned     |
| KAI-010| Basic Stat Tracking       | As a manager, I can record goals and assists for players after a match to be stored in the database.      | Manager, LogisticsCoordinator                                   | Planned     |

Phase 3: Advanced Management & Engagement (NEW)

Feature ID

Feature Name

User Story

Agents Involved

Status

KAI-012

Online Payments (Fees)

As a player, I want to receive a WhatsApp message with a link to pay my match fees online.

Manager, Treasurer, CommsOfficer

Planned

KAI-013

Online Payments (Fines)

As a manager, I can issue a fine to a player, and they will receive a notification with a payment link.

Manager, Treasurer, CommsOfficer

Planned

KAI-014

Peer-to-Peer Ratings

After a match, I want players to be prompted to rate each other's performance to generate a team rating.

Manager, TeamAdmin, CommsOfficer

Planned

KAI-015

Player Leaderboard

As a player, I can request the "leaderboard" and see top players for goals, assists, and attendance.

TeamAdmin, CommsOfficer

Planned

KAI-016

Task Delegation

As a manager, I want the system to automatically assign weekly chores (e.g., "wash the kit") on a rota basis.

Manager, TeamAdmin, CommsOfficer

Planned

KAI-017

Automated Reminders

I want players who haven't paid fees/fines by Tuesday to get an automatic reminder.

Manager, Treasurer, CommsOfficer

Planned
