# Payment Management Specification

## Document Information
- **Version**: 1.0
- **Date**: July 29, 2025
- **System**: KICKAI - AI-Powered Football Team Management
- **Domain**: Payment Management & Financial Operations

## Executive Summary

The Payment Management system handles all financial operations for amateur Sunday League football teams, including player fees, match expenses, equipment costs, and budget management. It integrates with Collectiv payment gateway for seamless transactions and provides comprehensive financial tracking and reporting capabilities.

## Business Context

### Sunday League Financial Management
- **Player Fees**: Weekly/monthly subscription fees for participation
- **Match Expenses**: Referee fees, pitch rental, travel costs
- **Equipment Costs**: Jerseys, balls, training equipment
- **Tournament Fees**: League registration, cup competition fees
- **Administrative Costs**: Insurance, league memberships

### Core Financial Challenges
1. **Manual Payment Tracking**: Eliminate spreadsheet-based financial management
2. **Payment Collection**: Streamline player fee collection
3. **Expense Management**: Track and categorize team expenses
4. **Budget Control**: Monitor spending against allocated budgets
5. **Financial Reporting**: Generate reports for committee and league requirements

## System Architecture

### Clean Architecture Implementation
```
payment_management/
├── application/
│   ├── commands/           # Payment commands with @command decorator
│   └── handlers/           # Command handlers (delegate to agents)
├── domain/
│   ├── entities/          # Payment, Budget, Expense entities
│   ├── interfaces/        # Service and gateway interfaces
│   ├── repositories/      # Repository interfaces
│   ├── services/          # Business logic services
│   └── tools/            # CrewAI tools for payment operations
├── infrastructure/        # Collectiv integration, Firebase repositories
└── tests/                # Unit, integration, and E2E tests
```

### Agent Integration
- **Primary Agent**: `TEAM_ADMINISTRATOR` - Handles payment-related requests
- **Secondary Agents**: `ANALYTICS_AGENT` for financial reporting
- **Tools**: Payment-specific CrewAI tools for transactions and reporting

## Functional Requirements

### 1. Payment Collection Flow

#### 1.1 Payment Creation
1. **Leadership**: Uses `/createpayment` command with payment details
2. **System**: Creates payment record with unique ID
3. **System**: Generates Collectiv payment link
4. **System**: Sends payment notification to player
5. **Player**: Clicks payment link to complete transaction

#### 1.2 Payment Processing
1. **Player**: Completes payment via Collectiv gateway
2. **System**: Receives payment confirmation from Collectiv
3. **System**: Updates payment status to "completed"
4. **System**: Sends receipt to player
5. **System**: Updates team financial records

### 2. Payment Management Flow

#### 2.1 Payment Tracking
1. **Leadership**: Uses `/payments` to view payment history
2. **System**: Shows all payments with status and details
3. **Leadership**: Can filter by player, date, or status
4. **System**: Highlights overdue payments
5. **Leadership**: Can send payment reminders

#### 2.2 Manual Payment Recording
1. **Leadership**: Records cash or bank transfer payment
2. **Leadership**: Uses `/markpaid` to update payment status
3. **System**: Validates payment details
4. **System**: Updates payment record and financial totals
5. **System**: Sends confirmation to player

### 3. Expense Management

#### 3.1 Expense Categories
- **Match Expenses**: Referee fees, pitch rental, travel
- **Equipment**: Jerseys, balls, training equipment, medical supplies
- **Administrative**: Insurance, league fees, registration costs
- **Social**: Team events, end-of-season celebrations
- **Other**: Miscellaneous team-related expenses

#### 3.2 Expense Recording
- **Receipt Upload**: Photo capture and storage
- **Expense Approval**: Coach/treasurer approval workflow
- **Automatic Categorization**: AI-powered expense categorization
- **Recurring Expenses**: Set up recurring payments (pitch rental, insurance)

#### 3.3 Expense Validation
- **Budget Constraints**: Validate against allocated budgets
- **Approval Limits**: Different approval levels based on amount
- **Receipt Requirements**: Mandatory receipts for expenses >£20
- **VAT Handling**: VAT calculation and reporting for registered clubs

### 4. Budget Management

#### 4.1 Budget Creation
- **Annual Budgets**: Season-long financial planning
- **Category Budgets**: Allocation per expense category
- **Match Budgets**: Per-match expense allocation
- **Emergency Fund**: Reserve allocation for unexpected costs

#### 4.2 Budget Monitoring
- **Real-time Tracking**: Budget utilization monitoring
- **Overspend Alerts**: Automatic notifications when approaching limits
- **Variance Analysis**: Budget vs actual spending comparison
- **Forecasting**: Predictive spending based on historical data

#### 4.3 Budget Controls
- **Approval Workflows**: Multi-level approval for budget changes
- **Spending Limits**: Role-based spending authorization
- **Budget Transfers**: Move allocation between categories
- **Budget Reviews**: Regular budget performance reviews

### 5. Financial Reporting

#### 5.1 Standard Reports
- **Income Statement**: Revenue vs expenses analysis
- **Player Payment Report**: Individual payment status
- **Expense Report**: Categorized expense breakdown
- **Budget Performance**: Budget vs actual analysis
- **Cash Flow**: Money in vs money out tracking

#### 5.2 Analytics and Insights
- **Payment Trends**: Payment behavior analysis
- **Cost per Player**: Per-player cost calculation
- **Seasonal Analysis**: Year-over-year financial comparison
- **ROI Analysis**: Cost effectiveness of different activities

## Technical Specifications

### 1. Data Models

#### 1.1 Payment Entity
```python
@dataclass
class Payment:
    id: Optional[str]
    player_id: str              # Link to Player entity
    team_id: str
    amount: float
    type: PaymentType           # MEMBERSHIP, MATCH_FEE, TOURNAMENT
    status: PaymentStatus       # PENDING, COMPLETED, FAILED, REFUNDED
    description: Optional[str]
    related_entity_id: Optional[str]  # Match ID, Tournament ID, etc.
    payment_method: Optional[str]     # CARD, BANK_TRANSFER, CASH
    gateway_transaction_id: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    due_date: Optional[datetime]
    paid_at: Optional[datetime]
```

#### 1.2 Budget Entity
```python
@dataclass
class Budget:
    id: Optional[str]
    team_id: str
    total_amount: Decimal
    allocated_amount: Decimal = Decimal("0")
    spent_amount: Decimal = Decimal("0")
    currency: str = "GBP"
    start_date: datetime
    end_date: Optional[datetime]
    description: Optional[str]
    status: str = "active"      # active, inactive, exceeded
    category: Optional[str]     # Overall, Match, Equipment, etc.
```

#### 1.3 Expense Entity
```python
@dataclass
class Expense:
    id: Optional[str]
    team_id: str
    amount: float
    category: ExpenseCategory   # MATCH, EQUIPMENT, ADMIN, SOCIAL
    description: Optional[str]
    receipt_url: Optional[str]
    submitted_by: str          # User ID of submitter
    approved_by: Optional[str] # User ID of approver
    status: str = "pending"    # pending, approved, rejected, paid
    created_at: Optional[datetime]
    approved_at: Optional[datetime]
```

### 2. Collectiv Integration

#### 2.1 Payment Gateway Interface
```python
class PaymentGatewayInterface(ABC):
    async def create_payment_link(self, amount: float, description: str, 
                                player_id: str) -> PaymentLink
    async def process_payment(self, payment_data: dict) -> PaymentResult
    async def refund_payment(self, transaction_id: str, 
                           amount: float) -> RefundResult
    async def get_payment_status(self, transaction_id: str) -> PaymentStatus
```

#### 2.2 Collectiv-Specific Implementation
```python
class CollectivPaymentGateway(PaymentGatewayInterface):
    """Collectiv API integration for payment processing"""
    
    def __init__(self, api_key: str, webhook_secret: str):
        self.api_key = api_key
        self.webhook_secret = webhook_secret
        self.base_url = "https://api.collectiv.co.uk"
    
    async def create_payment_link(self, amount: float, description: str, 
                                player_id: str) -> PaymentLink:
        """Create payment link using Collectiv API"""
        
    async def handle_webhook(self, payload: dict, signature: str) -> bool:
        """Handle Collectiv webhook notifications"""
```

### 3. Commands and Tools

#### 3.1 Payment Commands
```python
@command(name="pay", description="Make a payment or view payment options")
async def payment_command(context: CommandContext) -> CommandResult

@command(name="balance", description="Check payment balance and history")
async def balance_command(context: CommandContext) -> CommandResult

@command(name="receipt", description="Get payment receipt")
async def receipt_command(context: CommandContext) -> CommandResult
```

#### 3.2 Administrative Commands
```python
@command(name="expenses", description="Manage team expenses")
async def expenses_command(context: CommandContext) -> CommandResult

@command(name="budget", description="Manage team budget")
async def budget_command(context: CommandContext) -> CommandResult

@command(name="financial_report", description="Generate financial reports")
async def financial_report_command(context: CommandContext) -> CommandResult
```

#### 3.3 CrewAI Tools
```python
@tool
def create_payment_request(player_id: str, amount: float, 
                         description: str) -> str:
    """Create a payment request for a player"""

@tool
def record_expense(team_id: str, amount: float, category: str, 
                  description: str, receipt_url: str = None) -> str:
    """Record a team expense"""

@tool  
def get_payment_status(player_id: str, payment_id: str = None) -> str:
    """Get payment status for a player or specific payment"""

@tool
def generate_financial_summary(team_id: str, period: str) -> str:
    """Generate financial summary for specified period"""
```

## ID Generation System

### Payment ID Format
- **Format**: `P{DD}{MM}-{TYPE}-{NUMBER}` (e.g., `P1501-FEE-01`)
- **Examples**:
  - Player fee on Jan 15 → `P1501-FEE-01`
  - Equipment payment on Feb 20 → `P2002-EQP-01`
  - Match fee on Mar 10 → `P1003-MAT-01`

### Payment Type Codes
- **FEE**: Player fees and subscriptions
- **EQP**: Equipment and kit payments
- **MAT**: Match-specific fees
- **TOU**: Tournament entry fees
- **ADM**: Administrative costs
- **SOC**: Social event payments

### Payment ID Generation Rules
1. **Prefix**: Always starts with "P" for Payment
2. **Date**: DD (day) + MM (month) format
3. **Type**: 3-letter payment type code
4. **Number**: Sequential number for that date/type (01, 02, 03...)
5. **Separator**: Hyphen (-) between components
6. **Collision Resolution**: Increment number automatically

### Payment ID Examples
```
Payment Details → Generated IDs
Player fee, Jan 15 → P1501-FEE-01
Equipment payment, Jan 15 → P1501-EQP-01
Match fee, Feb 20 → P2002-MAT-01
Tournament fee, Mar 10 → P1003-TOU-01
```

### Benefits for Sunday League
- ✅ **Simple**: Easy to read and understand
- ✅ **Date Context**: Clear payment date information
- ✅ **Type Context**: Obvious payment type identification
- ✅ **Typable**: Short enough for quick entry (12-13 characters)
- ✅ **Human-readable**: Meaningful to users
- ✅ **Sequential**: Easy to track multiple payments per day

## Available Commands

### Leadership Commands (Leadership Chat)
- `/createpayment` - Create a new payment record
- `/payments` - View payment history
- `/markpaid` - Mark payment as paid

## User Experience Flows

### 1. Player Fee Payment Flow

#### 1.1 Happy Path
1. **System**: Generates weekly fee payment request
2. **Player**: Receives payment notification via Telegram
3. **Player**: Clicks payment link or uses `/pay` command
4. **System**: Redirects to Collectiv payment page
5. **Player**: Completes payment using preferred method
6. **Collectiv**: Processes payment and sends webhook
7. **System**: Updates payment status to "completed"
8. **Player**: Receives payment confirmation and receipt
9. **System**: Updates player balance and team finances

#### 1.2 Alternative Flows
- **Failed Payment**: Retry mechanism with alternative payment methods
- **Cash Payment**: Manual recording by coach/treasurer
- **Partial Payment**: Handle partial payments with remaining balance
- **Refund Request**: Process refunds through Collectiv API

### 2. Expense Management Flow

#### 2.1 Expense Submission
1. **Coach/Player**: Incurs team-related expense
2. **User**: Takes photo of receipt
3. **User**: Uses `/expenses add` command with details
4. **System**: Creates expense record with "pending" status
5. **System**: Routes to appropriate approver based on amount
6. **Approver**: Reviews expense and receipt
7. **Approver**: Approves or rejects with comments
8. **System**: Updates expense status and notifies submitter

#### 2.2 Budget Checking
1. **System**: Validates expense against relevant budget
2. **System**: Checks remaining budget allocation
3. **System**: Warns if expense exceeds budget limits
4. **Approver**: Can override budget limits with justification
5. **System**: Updates budget utilization

### 3. Financial Reporting Flow

#### 3.1 Regular Reports
1. **Coach/Treasurer**: Requests financial report using `/financial_report`
2. **ANALYTICS_AGENT**: Analyzes financial data
3. **System**: Generates comprehensive report
4. **System**: Delivers report via Telegram or email
5. **Stakeholders**: Review financial performance

#### 3.2 Real-time Monitoring
1. **System**: Continuously monitors budget utilization
2. **System**: Sends alerts when approaching budget limits
3. **System**: Provides daily/weekly financial summaries
4. **System**: Highlights unusual spending patterns

## Integration Requirements

### 1. External Services

#### 1.1 Collectiv Payment Gateway
- **API Integration**: RESTful API for payment processing
- **Webhook Handling**: Real-time payment status updates
- **Security**: PCI DSS compliance and secure token handling
- **Error Handling**: Comprehensive error handling and logging

#### 1.2 Banking Integration (Future)
- **Open Banking**: Direct bank account integration
- **Transaction Import**: Automatic transaction categorization
- **Reconciliation**: Match payments with bank transactions
- **Balance Monitoring**: Real-time account balance tracking

### 2. Internal System Integration

#### 2.1 Player Management Integration
- **Player Linking**: Link payments to player records
- **Status Updates**: Update player status based on payment history
- **Contact Integration**: Use player contact info for payment reminders
- **Reporting Integration**: Include payment data in player reports

#### 2.2 Match Management Integration
- **Match Fees**: Automatic fee calculation for matches
- **Squad Selection**: Consider payment status in squad selection
- **Match Expenses**: Link expenses to specific matches
- **Tournament Integration**: Handle tournament-specific payments

## Security and Compliance

### 1. Financial Data Security
- **PCI DSS Compliance**: Secure handling of payment card data
- **Data Encryption**: Encrypt sensitive financial information
- **Access Controls**: Role-based access to financial data
- **Audit Trails**: Complete audit log of all financial transactions

### 2. Payment Security
- **Secure Tokens**: Use secure payment tokens, never store card details
- **Webhook Security**: Verify webhook signatures
- **Fraud Detection**: Monitor for suspicious payment patterns
- **Secure Communications**: HTTPS/TLS for all payment communications

### 3. Data Privacy
- **GDPR Compliance**: Handle financial data in compliance with GDPR
- **Data Retention**: Retain financial records per legal requirements
- **Right to Erasure**: Handle deletion requests while maintaining legal records
- **Consent Management**: Clear consent for financial data processing

## Performance Requirements

### 1. Payment Processing
- **Payment Response Time**: < 3 seconds for payment creation
- **Webhook Processing**: < 1 second for webhook handling
- **Payment Status Updates**: Real-time status synchronization
- **Report Generation**: < 10 seconds for standard reports

### 2. System Reliability
- **Payment Availability**: 99.9% uptime for payment processing
- **Data Consistency**: Ensure payment data consistency across systems
- **Error Recovery**: Automatic recovery from failed transactions
- **Backup Systems**: Regular backups of financial data

### 3. Scalability
- **Concurrent Payments**: Handle 50+ simultaneous payments
- **Transaction Volume**: Support 1000+ transactions per month per team
- **Report Scalability**: Generate reports for multi-year data
- **Storage Scaling**: Efficient storage of payment and receipt data

## Quality Assurance

### 1. Testing Strategy
- **Unit Tests**: 95%+ coverage for payment logic
- **Integration Tests**: End-to-end payment flow testing
- **Mock Testing**: Comprehensive Collectiv API mocking
- **Load Testing**: Payment system performance under load

### 2. Financial Accuracy
- **Double Entry**: Implement double-entry bookkeeping principles
- **Reconciliation**: Regular automated reconciliation processes
- **Audit Functions**: Built-in audit and verification tools
- **Error Detection**: Automated detection of financial discrepancies

### 3. User Acceptance
- **Payment UX**: Intuitive payment process with minimal steps
- **Error Handling**: Clear error messages and recovery options
- **Receipt Delivery**: Reliable receipt generation and delivery
- **Support Integration**: Easy access to payment support

## Monitoring and Analytics

### 1. Financial Metrics
- **Payment Success Rate**: Track payment completion rates
- **Average Payment Time**: Monitor payment processing times
- **Outstanding Balance**: Track overdue payments
- **Budget Utilization**: Monitor budget performance

### 2. User Behavior Analytics
- **Payment Patterns**: Analyze when and how players pay
- **Expense Trends**: Track spending patterns over time
- **Budget Compliance**: Monitor adherence to budgets
- **Cost Analysis**: Analyze cost per player, per match, etc.

### 3. System Health Monitoring
- **API Performance**: Monitor Collectiv API response times
- **Error Rates**: Track payment processing errors
- **Webhook Reliability**: Monitor webhook delivery success
- **Data Integrity**: Continuous data consistency checking

## Future Enhancements

### 1. Advanced Payment Features
- **Subscription Management**: Automated recurring payments
- **Payment Plans**: Installment payment options
- **Group Payments**: Collective payments for tournaments
- **Dynamic Pricing**: Variable pricing based on participation

### 2. Enhanced Financial Management
- **Accounting Integration**: Xero/QuickBooks integration
- **Tax Management**: VAT calculation and reporting
- **Financial Forecasting**: AI-powered budget forecasting
- **Investment Tracking**: Equipment and asset management

### 3. Mobile and Convenience Features
- **Mobile Wallet Integration**: Apple Pay, Google Pay support
- **QR Code Payments**: Quick payment via QR codes
- **Voice Payments**: Alexa/Google Assistant payment commands
- **Offline Payments**: Offline payment recording with sync

## Success Metrics

### 1. Payment Efficiency
- **Collection Rate**: >95% of fees collected within due date
- **Payment Time**: <2 minutes average payment completion
- **Failed Payment Rate**: <5% payment failure rate
- **User Satisfaction**: >4.5/5 payment experience rating

### 2. Financial Management
- **Budget Accuracy**: <5% variance between budget and actual
- **Expense Processing Time**: <24 hours average approval time
- **Financial Reporting**: 100% accurate automated reports
- **Cash Flow**: Maintain positive cash flow throughout season

### 3. System Performance
- **Payment Uptime**: 99.9% payment system availability
- **Data Accuracy**: Zero financial data discrepancies
- **Report Generation**: <10 seconds for standard reports
- **Integration Reliability**: 100% webhook processing success

---

**Document Status**: Draft v1.0
**Next Review**: August 15, 2025
**Stakeholders**: Product Manager, Financial Controller, Team Treasurers