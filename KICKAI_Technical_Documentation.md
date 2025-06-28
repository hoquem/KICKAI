# KICKAI Technical Documentation
## AI-Powered Sunday League Football Team Management System

**Version:** 2.0  
**Date:** December 2024  
**Status:** Production Ready  
**Document Type:** Technical Specification & Architecture Guide

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Overview](#system-overview)
3. [Business Features](#business-features)
4. [System Architecture](#system-architecture)
5. [Technical Components](#technical-components)
6. [Database Design](#database-design)
7. [API Integration](#api-integration)
8. [Multi-Team Architecture](#multi-team-architecture)
9. [AI Agent System](#ai-agent-system)
10. [Deployment & Operations](#deployment--operations)
11. [Security & Compliance](#security--compliance)
12. [Monitoring & Support](#monitoring--support)
13. [Future Roadmap](#future-roadmap)

---

## Executive Summary

KICKAI is an intelligent football team management platform designed specifically for Sunday League teams. The system leverages artificial intelligence to automate routine team management tasks, streamline communications, and enhance team coordination through a sophisticated multi-agent architecture.

### Key Value Propositions

- **Automated Team Management**: AI agents handle player coordination, fixture management, and communications
- **Multi-Team Scalability**: Support for unlimited teams with isolated environments
- **Real-time Communications**: Instant messaging via Telegram with intelligent polling and announcements
- **Data-Driven Insights**: Comprehensive tracking of player availability, payments, and performance
- **Cost-Effective**: Local AI models reduce operational costs while maintaining high performance

### Success Metrics

- ✅ **BP Hatters FC**: Fully operational with dedicated AI management
- ✅ **7+ Message Types**: Automated communications working
- ✅ **4 AI Agents**: Coordinated team management
- ✅ **Multi-team Ready**: Architecture supports unlimited teams
- ✅ **Production Ready**: System deployed and tested

---

## System Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        KICKAI v2.0                              │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Team A    │  │   Team B    │  │   Team C    │             │
│  │  (Isolated) │  │  (Isolated) │  │  (Isolated) │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
├─────────────────────────────────────────────────────────────────┤
│                    Multi-Team Manager                           │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ Team Manager│  │Player Coord.│  │Match Analyst│             │
│  │   Agent     │  │   Agent     │  │   Agent     │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
├─────────────────────────────────────────────────────────────────┤
│                    CrewAI Framework                             │
│                    (Ollama Local Models)                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  Telegram   │  │  Supabase   │  │   Tools     │             │
│  │    API      │  │  Database   │  │  Layer      │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

### Core Principles

1. **Team Isolation**: Each team operates in complete isolation with dedicated resources
2. **AI-First Design**: All operations are AI-driven with human oversight
3. **Scalable Architecture**: Support for unlimited teams without performance degradation
4. **Real-time Communication**: Instant messaging and notifications
5. **Data Integrity**: Comprehensive audit trails and data consistency

---

## Business Features

### 1. Team Management

#### Player Coordination
- **Automated Player Registration**: AI agents handle new player onboarding
- **Availability Tracking**: Real-time player availability for matches
- **Contact Management**: Centralized player contact information
- **Role Assignment**: Automatic assignment of team roles and responsibilities

#### Fixture Management
- **Match Scheduling**: Intelligent fixture creation and management
- **Venue Coordination**: Automated venue booking and communication
- **Opponent Tracking**: Comprehensive opponent information and history
- **Result Recording**: Match outcomes and statistics tracking

### 2. Communication System

#### Telegram Integration
- **Team Announcements**: Automated match announcements and updates
- **Availability Polls**: Interactive polls for player availability
- **Squad Announcements**: Automated squad selection notifications
- **Payment Reminders**: Intelligent payment tracking and reminders
- **General Messaging**: Direct team communications

#### Message Types
1. **Basic Messages**: General team announcements and updates
2. **Interactive Polls**: Team decision-making and voting
3. **Availability Polls**: Match availability confirmation
4. **Squad Announcements**: Starting XI and substitute notifications
5. **Payment Reminders**: Fee collection and payment tracking

### 3. Financial Management

#### Payment Tracking
- **Match Fees**: Automated fee collection and tracking
- **Payment Reminders**: Intelligent reminder system for unpaid fees
- **Fine Management**: Automated fine calculation and collection
- **Financial Reporting**: Comprehensive financial summaries

### 4. Performance Analytics

#### Player Ratings
- **Peer-to-Peer Ratings**: Player performance evaluation system
- **Match Statistics**: Comprehensive match data collection
- **Performance Trends**: Historical performance analysis
- **Team Analytics**: Overall team performance metrics

---

## System Architecture

### Component Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Presentation Layer                           │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  Telegram   │  │   Web API   │  │   CLI       │             │
│  │   Bots      │  │  (Future)   │  │  Tools      │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
├─────────────────────────────────────────────────────────────────┤
│                    Application Layer                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ Multi-Team  │  │   CrewAI    │  │   Task      │             │
│  │  Manager    │  │  Framework  │  │  Manager    │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
├─────────────────────────────────────────────────────────────────┤
│                    Business Logic Layer                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  Telegram   │  │  Supabase   │  │   Team      │             │
│  │   Tools     │  │   Tools     │  │ Management  │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
├─────────────────────────────────────────────────────────────────┤
│                    Data Layer                                   │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  Supabase   │  │   Local     │  │   External  │             │
│  │ PostgreSQL  │  │   Storage   │  │    APIs     │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack

#### Backend Technologies
- **Python 3.11+**: Core application language
- **CrewAI**: Multi-agent AI framework
- **Ollama**: Local AI model hosting
- **LangChain**: AI model integration
- **FastAPI**: API framework (future)

#### Database & Storage
- **Supabase**: PostgreSQL database with real-time features
- **PostgreSQL**: Primary database engine
- **Row Level Security**: Multi-tenant data isolation

#### External Integrations
- **Telegram Bot API**: Messaging platform
- **Supabase API**: Database operations
- **Ollama API**: Local AI model inference

#### Development & Operations
- **Git**: Version control
- **Docker**: Containerization (future)
- **Python venv**: Environment management

---

## Technical Components

### 1. Multi-Team Manager (`src/multi_team_manager.py`)

**Purpose**: Orchestrates operations across multiple teams

**Key Features**:
- Team isolation and resource management
- Dynamic agent creation per team
- Coordinated task execution
- Resource allocation and cleanup

**Technical Implementation**:
```python
class MultiTeamManager:
    def __init__(self):
        self.teams = {}
        self.agents = {}
        self.resources = {}
    
    def add_team(self, team_id: str, config: dict):
        # Create isolated team environment
        # Initialize team-specific agents
        # Setup team resources
```

### 2. AI Agent System (`src/agents.py`)

**Purpose**: Implements intelligent team management agents

**Agent Types**:
1. **Team Manager**: Overall team coordination and strategy
2. **Player Coordinator**: Player management and availability
3. **Match Analyst**: Fixture analysis and squad selection
4. **Communication Specialist**: Team communications and announcements

**Agent Architecture**:
```python
def create_agents_for_team(llm, team_id: str):
    # Create team-specific agents
    # Assign team-aware tools
    # Configure agent roles and goals
```

### 3. Tool Layer (`src/tools/`)

#### Telegram Tools (`telegram_tools.py`)
- **SendTelegramMessageTool**: Basic messaging
- **SendTelegramPollTool**: Interactive polls
- **SendAvailabilityPollTool**: Availability tracking
- **SendSquadAnnouncementTool**: Squad announcements
- **SendPaymentReminderTool**: Payment management

#### Supabase Tools (`supabase_tools.py`)
- **PlayerTools**: Player CRUD operations
- **FixtureTools**: Fixture management
- **AvailabilityTools**: Availability tracking

#### Team Management Tools (`team_management_tools.py`)
- **TeamTools**: Team configuration
- **BotManagementTools**: Bot credential management

### 4. Task Management (`src/tasks.py`)

**Purpose**: Defines and executes team management tasks

**Task Types**:
- Player availability checks
- Fixture announcements
- Payment reminders
- Squad selections
- Team communications

---

## Database Design

### Entity Relationship Diagram

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    teams    │    │ team_bots   │    │   players   │
│             │    │             │    │             │
│ id (PK)     │◄───┤ team_id (FK)│    │ id (PK)     │
│ name        │    │ bot_token   │    │ name        │
│ description │    │ chat_id     │    │ phone       │
│ is_active   │    │ is_active   │    │ team_id (FK)│
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       │                   │                   │
       ▼                   │                   ▼
┌─────────────┐            │            ┌─────────────┐
│  fixtures   │            │            │team_members │
│             │            │            │             │
│ id (PK)     │            │            │ id (PK)     │
│ team_id (FK)│            │            │ team_id (FK)│
│ opponent    │            │            │ player_id   │
│ match_date  │            │            │ role        │
│ venue       │            │            │ is_active   │
└─────────────┘            │            └─────────────┘
       │                   │                   │
       │                   │                   │
       ▼                   │                   ▼
┌─────────────┐            │            ┌─────────────┐
│availability │            │            │squad_select.│
│             │            │            │             │
│ id (PK)     │            │            │ id (PK)     │
│ team_id (FK)│            │            │ fixture_id  │
│ player_id   │            │            │ player_id   │
│ fixture_id  │            │            │ status      │
│ status      │            │            └─────────────┘
│ has_paid    │            │
└─────────────┘            │
                           │
                           ▼
                   ┌─────────────┐
                   │   ratings   │
                   │             │
                   │ id (PK)     │
                   │ team_id (FK)│
                   │ player_id   │
                   │ fixture_id  │
                   │ rating      │
                   └─────────────┘
```

### Database Schema Details

#### Core Tables

**teams**
- Primary team information
- Multi-tenant isolation
- Active/inactive status tracking

**team_bots**
- Telegram bot credentials per team
- One-to-one relationship with teams
- Secure credential storage

**players**
- Player information
- Team association
- Contact details

**fixtures**
- Match scheduling
- Team-specific fixtures
- Venue and opponent information

**availability**
- Player availability tracking
- Payment status
- Fine management

### Data Isolation Strategy

1. **Row-Level Security**: Database-level team isolation
2. **Team ID Filtering**: Application-level data filtering
3. **Bot Isolation**: Separate Telegram bots per team
4. **Agent Isolation**: Team-specific AI agents

---

## API Integration

### Telegram Bot API

#### Authentication
```python
def get_team_bot_credentials(team_id: str) -> Tuple[str, str]:
    # Fetch bot token and chat ID from database
    # Return tuple of (token, chat_id)
```

#### Message Types
1. **Text Messages**: Basic team communications
2. **Polls**: Interactive team decision-making
3. **HTML Formatting**: Rich text formatting
4. **Error Handling**: Comprehensive error management

#### Rate Limiting
- Telegram API rate limits: 30 messages/second
- Implementation: Request queuing and throttling
- Error handling: Retry logic with exponential backoff

### Supabase Integration

#### Connection Management
```python
def get_supabase_client() -> Client:
    # Initialize Supabase client
    # Configure authentication
    # Setup connection pooling
```

#### Real-time Features
- **Live Updates**: Real-time data synchronization
- **WebSocket Support**: Live team updates
- **Event Handling**: Automated notifications

#### Security Features
- **Row Level Security**: Database-level access control
- **API Key Management**: Secure credential handling
- **Audit Logging**: Comprehensive access logging

---

## Multi-Team Architecture

### Team Isolation Strategy

```
┌─────────────────────────────────────────────────────────────────┐
│                    KICKAI Platform                              │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Team A        │  │   Team B        │  │   Team C        │ │
│  │                 │  │                 │  │                 │ │
│  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │ ┌─────────────┐ │ │
│  │ │ Bot A       │ │  │ │ Bot B       │ │  │ │ Bot C       │ │ │
│  │ │ Chat ID A   │ │  │ │ Chat ID B   │ │  │ │ Chat ID C   │ │ │
│  │ └─────────────┘ │  │ └─────────────┘ │  │ └─────────────┘ │ │
│  │                 │  │                 │  │                 │ │
│  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │ ┌─────────────┐ │ │
│  │ │ Agents A    │ │  │ │ Agents B    │ │  │ │ Agents C    │ │ │
│  │ │ (4 agents)  │ │  │ │ (4 agents)  │ │  │ │ (4 agents)  │ │ │
│  │ └─────────────┘ │  │ └─────────────┘ │  │ └─────────────┘ │ │
│  │                 │  │                 │  │                 │ │
│  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │ ┌─────────────┐ │ │
│  │ │ Data A      │ │  │ │ Data B      │ │  │ │ Data C      │ │ │
│  │ │ (Filtered)  │ │  │ │ (Filtered)  │ │  │ │ (Filtered)  │ │ │
│  │ └─────────────┘ │  │ └─────────────┘ │  │ └─────────────┘ │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Scalability Features

1. **Horizontal Scaling**: Add teams without performance impact
2. **Resource Isolation**: Each team has dedicated resources
3. **Database Partitioning**: Team-based data partitioning
4. **Load Balancing**: Distributed agent execution

### Team Management CLI

```bash
# List all teams
python manage_team_bots.py list

# Add team bot mapping
python manage_team_bots.py add --team-id <id> --bot-token <token> --chat-id <chat_id>

# Deactivate team bot
python manage_team_bots.py deactivate --team-id <id>
```

---

## AI Agent System

### Agent Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    CrewAI Framework                             │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ Team Manager│  │Player Coord.│  │Match Analyst│             │
│  │             │  │             │  │             │             │
│  │ Role:       │  │ Role:       │  │ Role:       │             │
│  │ - Strategy  │  │ - Players   │  │ - Fixtures  │             │
│  │ - Planning  │  │ - Availability│  │ - Analysis │             │
│  │ - Coordination│  │ - Communication│  │ - Selection│             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│         │                 │                 │                   │
│         └─────────────────┼─────────────────┘                   │
│                           │                                     │
│  ┌─────────────┐          │                                     │
│  │Communication│          │                                     │
│  │ Specialist  │          │                                     │
│  │             │          │                                     │
│  │ Role:       │          │                                     │
│  │ - Messaging │          │                                     │
│  │ - Polls     │          │                                     │
│  │ - Announcements│       │                                     │
│  └─────────────┘          │                                     │
├─────────────────────────────────────────────────────────────────┤
│                    Tool Layer                                   │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  Telegram   │  │  Supabase   │  │   Team      │             │
│  │   Tools     │  │   Tools     │  │ Management  │             │
│  │             │  │             │  │   Tools     │             │
│  │ - Messages  │  │ - Players   │  │ - Teams     │             │
│  │ - Polls     │  │ - Fixtures  │  │ - Bots      │             │
│  │ - Announcements│  │ - Availability│  │ - Config   │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

### Agent Communication Flow

1. **Task Assignment**: Multi-team manager assigns tasks to agents
2. **Tool Execution**: Agents use appropriate tools for tasks
3. **Result Processing**: Results are processed and stored
4. **Communication**: Relevant information is communicated to teams
5. **Feedback Loop**: System learns from interactions

### AI Model Configuration

```python
# Ollama Configuration
llm = Ollama(
    model="ollama/llama3.1:8b-instruct-q4_0",
    system=CREWAI_SYSTEM_PROMPT,
    temperature=0.7
)
```

**Model Specifications**:
- **Model**: llama3.1:8b-instruct-q4_0
- **Parameters**: 8 billion parameters
- **Quantization**: Q4_0 (4-bit quantization)
- **Context Window**: 8K tokens
- **Performance**: Optimized for local inference

---

## Deployment & Operations

### System Requirements

#### Minimum Requirements
- **CPU**: 4 cores (2.4 GHz+)
- **RAM**: 8 GB
- **Storage**: 20 GB SSD
- **Network**: Stable internet connection
- **OS**: Linux/macOS/Windows

#### Recommended Requirements
- **CPU**: 8 cores (3.0 GHz+)
- **RAM**: 16 GB
- **Storage**: 50 GB NVMe SSD
- **Network**: High-speed internet
- **OS**: Ubuntu 20.04+ / macOS 12+

### Environment Setup

#### Required Environment Variables
```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# Optional (now stored in database)
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
```

#### Installation Steps
```bash
# 1. Clone repository
git clone https://github.com/hoquem/KICKAI.git
cd KICKAI

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup database
psql -h your-host -U your-user -d your-db -f kickai_schema.sql
psql -h your-host -U your-user -d your-db -f kickai_sample_data.sql

# 5. Configure environment
cp env.example .env
# Edit .env with your credentials

# 6. Test installation
python test_telegram_features.py
```

### Production Deployment

#### Docker Deployment (Future)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "src/main.py"]
```

#### Systemd Service (Linux)
```ini
[Unit]
Description=KICKAI Football Team Manager
After=network.target

[Service]
Type=simple
User=kickai
WorkingDirectory=/opt/kickai
Environment=PATH=/opt/kickai/venv/bin
ExecStart=/opt/kickai/venv/bin/python src/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### Monitoring & Logging

#### Log Configuration
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('kickai.log'),
        logging.StreamHandler()
    ]
)
```

#### Health Checks
- **Database Connectivity**: Regular connection tests
- **Telegram API**: Bot status verification
- **AI Model**: Ollama service health
- **Agent Status**: Agent availability monitoring

---

## Security & Compliance

### Data Security

#### Database Security
- **Row Level Security**: Team data isolation
- **Encrypted Connections**: TLS 1.3 for all database connections
- **Access Control**: Role-based permissions
- **Audit Logging**: Comprehensive access logs

#### API Security
- **Token Management**: Secure bot token storage
- **Rate Limiting**: API request throttling
- **Input Validation**: Comprehensive input sanitization
- **Error Handling**: Secure error responses

#### Communication Security
- **Telegram Security**: End-to-end encryption
- **Bot Authentication**: Secure bot verification
- **Message Validation**: Content validation and filtering

### Compliance Considerations

#### Data Protection
- **GDPR Compliance**: Data minimization and retention
- **Data Localization**: Local data storage options
- **Consent Management**: User consent tracking
- **Data Portability**: Export capabilities

#### Privacy Features
- **Anonymization**: Optional data anonymization
- **Access Controls**: Granular permission system
- **Audit Trails**: Complete activity logging
- **Data Deletion**: Secure data removal

---

## Monitoring & Support

### System Monitoring

#### Performance Metrics
- **Response Time**: API response times
- **Throughput**: Messages per second
- **Error Rates**: System error tracking
- **Resource Usage**: CPU, memory, storage

#### Business Metrics
- **Team Activity**: Active teams and users
- **Message Volume**: Communication statistics
- **Agent Performance**: AI agent effectiveness
- **User Satisfaction**: Team feedback scores

### Support Procedures

#### Issue Resolution
1. **Problem Identification**: Automated error detection
2. **Impact Assessment**: Service impact evaluation
3. **Resolution Steps**: Standardized fix procedures
4. **Verification**: Post-resolution testing
5. **Documentation**: Issue and resolution logging

#### Maintenance Schedule
- **Daily**: Health checks and monitoring
- **Weekly**: Performance analysis and optimization
- **Monthly**: Security updates and patches
- **Quarterly**: Feature updates and improvements

### Troubleshooting Guide

#### Common Issues

**Database Connection Issues**
```bash
# Check Supabase connectivity
python -c "from src.tools.supabase_tools import get_supabase_client; print('Connected')"
```

**Telegram Bot Issues**
```bash
# Test bot functionality
python test_telegram_features.py
```

**AI Model Issues**
```bash
# Check Ollama service
curl http://localhost:11434/api/tags
```

---

## Future Roadmap

### Phase 1: Enhanced Features (Q1 2025)
- **Payment Integration**: Stripe/PayPal integration
- **Advanced Analytics**: Team performance insights
- **Mobile App**: Native mobile application
- **API Documentation**: Comprehensive API docs

### Phase 2: Advanced AI (Q2 2025)
- **Predictive Analytics**: Match outcome predictions
- **Player Recommendations**: AI-powered squad selection
- **Natural Language Processing**: Advanced message understanding
- **Multi-language Support**: International team support

### Phase 3: Enterprise Features (Q3 2025)
- **League Management**: Multi-team league support
- **Advanced Reporting**: Comprehensive analytics dashboard
- **Integration APIs**: Third-party system integration
- **White-label Solution**: Customizable branding

### Phase 4: Platform Expansion (Q4 2025)
- **Other Sports**: Basketball, cricket, rugby support
- **Educational Institutions**: School and university teams
- **Professional Teams**: Semi-professional team support
- **Global Expansion**: International market entry

### Technical Debt & Improvements

#### Immediate Improvements
- **Code Optimization**: Performance improvements
- **Test Coverage**: Comprehensive testing suite
- **Documentation**: Enhanced technical documentation
- **Security Hardening**: Additional security measures

#### Long-term Improvements
- **Microservices Architecture**: Service decomposition
- **Cloud Native**: Kubernetes deployment
- **Event-driven Architecture**: Asynchronous processing
- **Machine Learning Pipeline**: Advanced AI capabilities

---

## Appendices

### Appendix A: API Reference

#### Telegram Bot API Endpoints
- `sendMessage`: Send text messages
- `sendPoll`: Create interactive polls
- `getUpdates`: Retrieve bot updates
- `getMe`: Get bot information

#### Supabase API Operations
- `select`: Query data with filters
- `insert`: Add new records
- `update`: Modify existing records
- `delete`: Remove records

### Appendix B: Configuration Files

#### Environment Configuration
```bash
# .env file structure
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
```

#### Database Configuration
```sql
-- Database connection parameters
host=your-supabase-host
port=5432
database=postgres
user=postgres
password=your-password
```

### Appendix C: Troubleshooting

#### Common Error Codes
- **400 Bad Request**: Invalid API parameters
- **401 Unauthorized**: Authentication failure
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: System error

#### Debug Procedures
1. **Enable Debug Logging**: Set log level to DEBUG
2. **Check Network Connectivity**: Verify API endpoints
3. **Validate Credentials**: Confirm API keys and tokens
4. **Review Error Logs**: Analyze detailed error messages
5. **Test Components**: Isolate and test individual components

---

## Document Information

**Document Version**: 2.0  
**Last Updated**: December 2024  
**Author**: KICKAI Development Team  
**Review Cycle**: Quarterly  
**Next Review**: March 2025  

**Distribution**:  
- Product Owners  
- System Engineers  
- Development Team  
- Operations Team  

**Contact Information**:  
- **Technical Support**: support@kickai.com  
- **Development Team**: dev@kickai.com  
- **Product Management**: product@kickai.com  

---

*This document is maintained by the KICKAI development team and should be updated with each major release.* 