#!/usr/bin/env python3
"""
KICKAI Technical Documentation PDF Generator (Simple Version)
Creates a professional PDF using reportlab.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
import os
from datetime import datetime

def create_pdf_documentation():
    """Create a professional PDF documentation."""
    
    # Create the PDF document
    doc = SimpleDocTemplate(
        "KICKAI_Technical_Documentation.pdf",
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.darkblue,
        borderWidth=1,
        borderColor=colors.blue,
        borderPadding=5
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=8,
        spaceBefore=15,
        textColor=colors.darkblue
    )
    
    heading3_style = ParagraphStyle(
        'CustomHeading3',
        parent=styles['Heading3'],
        fontSize=12,
        spaceAfter=6,
        spaceBefore=10,
        textColor=colors.darkblue
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        alignment=TA_JUSTIFY
    )
    
    code_style = ParagraphStyle(
        'CustomCode',
        parent=styles['Code'],
        fontSize=9,
        fontName='Courier',
        spaceAfter=6,
        leftIndent=20,
        backColor=colors.lightgrey
    )
    
    # Build the story (content)
    story = []
    
    # Title page
    story.append(Paragraph("KICKAI Technical Documentation", title_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph("AI-Powered Sunday League Football Team Management System", heading1_style))
    story.append(Spacer(1, 30))
    
    # Version info
    version_info = [
        ["Version:", "2.0"],
        ["Date:", datetime.now().strftime('%B %Y')],
        ["Status:", "Production Ready"],
        ["Document Type:", "Technical Specification & Architecture Guide"]
    ]
    
    version_table = Table(version_info, colWidths=[2*inch, 4*inch])
    version_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(version_table)
    story.append(PageBreak())
    
    # Table of Contents
    story.append(Paragraph("Table of Contents", heading1_style))
    story.append(Spacer(1, 20))
    
    toc_items = [
        "1. Executive Summary",
        "2. System Overview", 
        "3. Business Features",
        "4. System Architecture",
        "5. Technical Components",
        "6. Database Design",
        "7. API Integration",
        "8. Multi-Team Architecture",
        "9. AI Agent System",
        "10. Deployment & Operations",
        "11. Security & Compliance",
        "12. Monitoring & Support",
        "13. Future Roadmap"
    ]
    
    for item in toc_items:
        story.append(Paragraph(item, normal_style))
    
    story.append(PageBreak())
    
    # Executive Summary
    story.append(Paragraph("1. Executive Summary", heading1_style))
    story.append(Paragraph("""
    KICKAI is an intelligent football team management platform designed specifically for Sunday League teams. 
    The system leverages artificial intelligence to automate routine team management tasks, streamline communications, 
    and enhance team coordination through a sophisticated multi-agent architecture.
    """, normal_style))
    
    story.append(Paragraph("Key Value Propositions:", heading2_style))
    value_props = [
        "• Automated Team Management: AI agents handle player coordination, fixture management, and communications",
        "• Multi-Team Scalability: Support for unlimited teams with isolated environments",
        "• Real-time Communications: Instant messaging via Telegram with intelligent polling and announcements",
        "• Data-Driven Insights: Comprehensive tracking of player availability, payments, and performance",
        "• Cost-Effective: Local AI models reduce operational costs while maintaining high performance"
    ]
    
    for prop in value_props:
        story.append(Paragraph(prop, normal_style))
    
    story.append(Paragraph("Success Metrics:", heading2_style))
    success_metrics = [
        "✅ BP Hatters FC: Fully operational with dedicated AI management",
        "✅ 7+ Message Types: Automated communications working",
        "✅ 4 AI Agents: Coordinated team management",
        "✅ Multi-team Ready: Architecture supports unlimited teams",
        "✅ Production Ready: System deployed and tested"
    ]
    
    for metric in success_metrics:
        story.append(Paragraph(metric, normal_style))
    
    story.append(PageBreak())
    
    # System Overview
    story.append(Paragraph("2. System Overview", heading1_style))
    story.append(Paragraph("""
    KICKAI operates on a multi-layered architecture that ensures team isolation, scalability, and maintainability. 
    Each team operates in complete isolation with dedicated AI agents, database context, and communication channels.
    """, normal_style))
    
    story.append(Paragraph("High-Level Architecture:", heading2_style))
    story.append(Paragraph("""
    The system is built on a foundation of CrewAI agents, Supabase database, and Telegram integration. 
    Each team has its own isolated environment with dedicated resources and AI agents.
    """, normal_style))
    
    story.append(Paragraph("Core Principles:", heading2_style))
    principles = [
        "• Team Isolation: Each team operates in complete isolation with dedicated resources",
        "• AI-First Design: All operations are AI-driven with human oversight",
        "• Scalable Architecture: Support for unlimited teams without performance degradation",
        "• Real-time Communication: Instant messaging and notifications",
        "• Data Integrity: Comprehensive audit trails and data consistency"
    ]
    
    for principle in principles:
        story.append(Paragraph(principle, normal_style))
    
    story.append(PageBreak())
    
    # Business Features
    story.append(Paragraph("3. Business Features", heading1_style))
    
    story.append(Paragraph("Team Management", heading2_style))
    story.append(Paragraph("""
    The system provides comprehensive team management capabilities including player coordination, 
    fixture management, and automated communications.
    """, normal_style))
    
    story.append(Paragraph("Player Coordination:", heading3_style))
    player_features = [
        "• Automated Player Registration: AI agents handle new player onboarding",
        "• Availability Tracking: Real-time player availability for matches",
        "• Contact Management: Centralized player contact information",
        "• Role Assignment: Automatic assignment of team roles and responsibilities"
    ]
    
    for feature in player_features:
        story.append(Paragraph(feature, normal_style))
    
    story.append(Paragraph("Communication System", heading2_style))
    story.append(Paragraph("""
    Telegram integration provides real-time communication with multiple message types for different purposes.
    """, normal_style))
    
    story.append(Paragraph("Message Types:", heading3_style))
    message_types = [
        "1. Basic Messages: General team announcements and updates",
        "2. Interactive Polls: Team decision-making and voting",
        "3. Availability Polls: Match availability confirmation",
        "4. Squad Announcements: Starting XI and substitute notifications",
        "5. Payment Reminders: Fee collection and payment tracking"
    ]
    
    for msg_type in message_types:
        story.append(Paragraph(msg_type, normal_style))
    
    story.append(PageBreak())
    
    # System Architecture
    story.append(Paragraph("4. System Architecture", heading1_style))
    
    story.append(Paragraph("Component Architecture:", heading2_style))
    story.append(Paragraph("""
    The system is built on a layered architecture with clear separation of concerns:
    """, normal_style))
    
    layers = [
        "• Presentation Layer: Telegram bots, CLI tools, and future web interface",
        "• Application Layer: Multi-team manager, CrewAI framework, and task management",
        "• Business Logic Layer: Telegram tools, Supabase tools, and team management",
        "• Data Layer: Supabase PostgreSQL, local storage, and external APIs"
    ]
    
    for layer in layers:
        story.append(Paragraph(layer, normal_style))
    
    story.append(Paragraph("Technology Stack:", heading2_style))
    tech_stack = [
        "Backend: Python 3.11+, CrewAI, Ollama, LangChain",
        "Database: Supabase PostgreSQL with real-time features",
        "External APIs: Telegram Bot API, Supabase API, Ollama API",
        "Development: Git, Python venv, Docker (future)"
    ]
    
    for tech in tech_stack:
        story.append(Paragraph(tech, normal_style))
    
    story.append(PageBreak())
    
    # Technical Components
    story.append(Paragraph("5. Technical Components", heading1_style))
    
    story.append(Paragraph("Multi-Team Manager", heading2_style))
    story.append(Paragraph("""
    The Multi-Team Manager orchestrates operations across multiple teams, ensuring isolation 
    and resource management.
    """, normal_style))
    
    story.append(Paragraph("AI Agent System", heading2_style))
    agents = [
        "• Team Manager: Overall team coordination and strategy",
        "• Player Coordinator: Player management and availability",
        "• Match Analyst: Fixture analysis and squad selection",
        "• Communication Specialist: Team communications and announcements"
    ]
    
    for agent in agents:
        story.append(Paragraph(agent, normal_style))
    
    story.append(Paragraph("Tool Layer", heading2_style))
    tools = [
        "• Telegram Tools: Messaging, polls, announcements, payment reminders",
        "• Supabase Tools: Player, fixture, and availability management",
        "• Team Management Tools: Team configuration and bot management"
    ]
    
    for tool in tools:
        story.append(Paragraph(tool, normal_style))
    
    story.append(PageBreak())
    
    # Database Design
    story.append(Paragraph("6. Database Design", heading1_style))
    
    story.append(Paragraph("Core Tables:", heading2_style))
    tables = [
        "• teams: Primary team information and multi-tenant isolation",
        "• team_bots: Telegram bot credentials per team (one-to-one relationship)",
        "• players: Player information with team association",
        "• fixtures: Match scheduling with team-specific fixtures",
        "• availability: Player availability tracking and payment status"
    ]
    
    for table in tables:
        story.append(Paragraph(table, normal_style))
    
    story.append(Paragraph("Data Isolation Strategy:", heading2_style))
    isolation = [
        "• Row-Level Security: Database-level team isolation",
        "• Team ID Filtering: Application-level data filtering",
        "• Bot Isolation: Separate Telegram bots per team",
        "• Agent Isolation: Team-specific AI agents"
    ]
    
    for strategy in isolation:
        story.append(Paragraph(strategy, normal_style))
    
    story.append(PageBreak())
    
    # API Integration
    story.append(Paragraph("7. API Integration", heading1_style))
    
    story.append(Paragraph("Telegram Bot API:", heading2_style))
    telegram_features = [
        "• Authentication: Dynamic bot token and chat ID management",
        "• Message Types: Text messages, polls, HTML formatting",
        "• Rate Limiting: Request queuing and throttling (30 msg/sec)",
        "• Error Handling: Comprehensive error management with retry logic"
    ]
    
    for feature in telegram_features:
        story.append(Paragraph(feature, normal_style))
    
    story.append(Paragraph("Supabase Integration:", heading2_style))
    supabase_features = [
        "• Connection Management: Secure client initialization",
        "• Real-time Features: Live data synchronization",
        "• Security Features: Row Level Security and audit logging"
    ]
    
    for feature in supabase_features:
        story.append(Paragraph(feature, normal_style))
    
    story.append(PageBreak())
    
    # Multi-Team Architecture
    story.append(Paragraph("8. Multi-Team Architecture", heading1_style))
    
    story.append(Paragraph("Team Isolation Strategy:", heading2_style))
    story.append(Paragraph("""
    Each team operates in complete isolation with dedicated resources, ensuring data privacy 
    and operational independence.
    """, normal_style))
    
    story.append(Paragraph("Scalability Features:", heading2_style))
    scalability = [
        "• Horizontal Scaling: Add teams without performance impact",
        "• Resource Isolation: Each team has dedicated resources",
        "• Database Partitioning: Team-based data partitioning",
        "• Load Balancing: Distributed agent execution"
    ]
    
    for feature in scalability:
        story.append(Paragraph(feature, normal_style))
    
    story.append(PageBreak())
    
    # AI Agent System
    story.append(Paragraph("9. AI Agent System", heading1_style))
    
    story.append(Paragraph("Agent Communication Flow:", heading2_style))
    flow = [
        "1. Task Assignment: Multi-team manager assigns tasks to agents",
        "2. Tool Execution: Agents use appropriate tools for tasks",
        "3. Result Processing: Results are processed and stored",
        "4. Communication: Relevant information is communicated to teams",
        "5. Feedback Loop: System learns from interactions"
    ]
    
    for step in flow:
        story.append(Paragraph(step, normal_style))
    
    story.append(Paragraph("AI Model Configuration:", heading2_style))
    model_info = [
        "• Model: llama3.1:8b-instruct-q4_0",
        "• Parameters: 8 billion parameters",
        "• Quantization: Q4_0 (4-bit quantization)",
        "• Context Window: 8K tokens",
        "• Performance: Optimized for local inference"
    ]
    
    for info in model_info:
        story.append(Paragraph(info, normal_style))
    
    story.append(PageBreak())
    
    # Deployment & Operations
    story.append(Paragraph("10. Deployment & Operations", heading1_style))
    
    story.append(Paragraph("System Requirements:", heading2_style))
    requirements = [
        "Minimum: 4 cores, 8 GB RAM, 20 GB SSD",
        "Recommended: 8 cores, 16 GB RAM, 50 GB NVMe SSD",
        "Network: Stable internet connection",
        "OS: Linux/macOS/Windows"
    ]
    
    for req in requirements:
        story.append(Paragraph(req, normal_style))
    
    story.append(Paragraph("Environment Setup:", heading2_style))
    setup_steps = [
        "1. Clone repository and create virtual environment",
        "2. Install dependencies: pip install -r requirements.txt",
        "3. Setup database: Run kickai_schema.sql and kickai_sample_data.sql",
        "4. Configure environment variables in .env file",
        "5. Test installation with test_telegram_features.py"
    ]
    
    for step in setup_steps:
        story.append(Paragraph(step, normal_style))
    
    story.append(PageBreak())
    
    # Security & Compliance
    story.append(Paragraph("11. Security & Compliance", heading1_style))
    
    story.append(Paragraph("Data Security:", heading2_style))
    security = [
        "• Row Level Security: Team data isolation",
        "• Encrypted Connections: TLS 1.3 for all connections",
        "• Access Control: Role-based permissions",
        "• Audit Logging: Comprehensive access logs"
    ]
    
    for sec in security:
        story.append(Paragraph(sec, normal_style))
    
    story.append(Paragraph("Compliance Considerations:", heading2_style))
    compliance = [
        "• GDPR Compliance: Data minimization and retention",
        "• Data Localization: Local data storage options",
        "• Consent Management: User consent tracking",
        "• Data Portability: Export capabilities"
    ]
    
    for comp in compliance:
        story.append(Paragraph(comp, normal_style))
    
    story.append(PageBreak())
    
    # Monitoring & Support
    story.append(Paragraph("12. Monitoring & Support", heading1_style))
    
    story.append(Paragraph("System Monitoring:", heading2_style))
    monitoring = [
        "Performance Metrics: Response time, throughput, error rates",
        "Business Metrics: Team activity, message volume, agent performance",
        "Health Checks: Database, Telegram API, AI model status"
    ]
    
    for metric in monitoring:
        story.append(Paragraph(metric, normal_style))
    
    story.append(Paragraph("Support Procedures:", heading2_style))
    support = [
        "Issue Resolution: Automated error detection and fix procedures",
        "Maintenance Schedule: Daily health checks, weekly optimization",
        "Troubleshooting: Comprehensive guides for common issues"
    ]
    
    for proc in support:
        story.append(Paragraph(proc, normal_style))
    
    story.append(PageBreak())
    
    # Future Roadmap
    story.append(Paragraph("13. Future Roadmap", heading1_style))
    
    story.append(Paragraph("Phase 1: Enhanced Features (Q1 2025)", heading2_style))
    phase1 = [
        "• Payment Integration: Stripe/PayPal integration",
        "• Advanced Analytics: Team performance insights",
        "• Mobile App: Native mobile application",
        "• API Documentation: Comprehensive API docs"
    ]
    
    for feature in phase1:
        story.append(Paragraph(feature, normal_style))
    
    story.append(Paragraph("Phase 2: Advanced AI (Q2 2025)", heading2_style))
    phase2 = [
        "• Predictive Analytics: Match outcome predictions",
        "• Player Recommendations: AI-powered squad selection",
        "• Natural Language Processing: Advanced message understanding",
        "• Multi-language Support: International team support"
    ]
    
    for feature in phase2:
        story.append(Paragraph(feature, normal_style))
    
    story.append(Paragraph("Phase 3: Enterprise Features (Q3 2025)", heading2_style))
    phase3 = [
        "• League Management: Multi-team league support",
        "• Advanced Reporting: Comprehensive analytics dashboard",
        "• Integration APIs: Third-party system integration",
        "• White-label Solution: Customizable branding"
    ]
    
    for feature in phase3:
        story.append(Paragraph(feature, normal_style))
    
    # Footer
    story.append(PageBreak())
    story.append(Paragraph("Document Information", heading1_style))
    story.append(Paragraph(f"Document Version: 2.0", normal_style))
    story.append(Paragraph(f"Last Updated: {datetime.now().strftime('%B %Y')}", normal_style))
    story.append(Paragraph("Author: KICKAI Development Team", normal_style))
    story.append(Paragraph("Review Cycle: Quarterly", normal_style))
    story.append(Paragraph("Next Review: March 2025", normal_style))
    
    # Build the PDF
    print("Generating PDF documentation...")
    doc.build(story)
    
    # Get file size
    file_size = os.path.getsize("KICKAI_Technical_Documentation.pdf")
    print("✅ PDF generated successfully: KICKAI_Technical_Documentation.pdf")
    print(f"📄 File size: {file_size / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    try:
        create_pdf_documentation()
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        print("Please ensure you have reportlab installed:")
        print("pip install reportlab") 