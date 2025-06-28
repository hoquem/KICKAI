# KICKAI Testing Plan
## Dual Chat Architecture Testing with 6 Testers

**Version:** 1.0  
**Date:** December 2024  
**Team:** BP Hatters FC  
**Testers:** 6 team members

---

## 🎯 **Testing Overview**

### **Dual Chat Architecture**
- **Main Team Group**: All players + leadership (natural language + basic commands)
- **Leadership Group**: Management only (command-based interface)
- **Role-Based Permissions**: Different commands available based on user role

### **Current Setup Status**
- ✅ **Bot**: @BPHatters_bot connected and working
- ✅ **Main Team Group**: ID -4959662544 (BP Hatters FC)
- ✅ **Command Handler**: 17 commands implemented
- ✅ **Database**: Connected and ready
- 🔄 **Leadership Group**: Needs to be created

---

## 👥 **Tester Roles & Responsibilities**

### **🏆 Team Admin (Tester 1)**
**Name:** [Admin Name]  
**Role:** Full system access  
**Commands Available:** All commands  
**Testing Focus:** System administration, user management, financial oversight

### **📋 Team Secretary (Tester 2)**
**Name:** [Secretary Name]  
**Role:** Operations coordination  
**Commands Available:** Fixture management, availability, squad announcements  
**Testing Focus:** Fixture management, availability coordination, communications

### **⚽ Team Manager (Tester 3)**
**Name:** [Manager Name]  
**Role:** Tactical and performance management  
**Commands Available:** Squad selection, availability, performance tracking  
**Testing Focus:** Squad selection, tactical planning, performance analysis

### **💰 Treasurer/Helper (Tester 4)**
**Name:** [Treasurer Name]  
**Role:** Financial management  
**Commands Available:** Payment management, financial tracking  
**Testing Focus:** Payment collection, financial reporting, reminders

### **👤 Player 1 (Tester 5)**
**Name:** [Player 1 Name]  
**Role:** Regular player  
**Commands Available:** /help, /status  
**Testing Focus:** Natural language interactions, player experience

### **👤 Player 2 (Tester 6)**
**Name:** [Player 2 Name]  
**Role:** Regular player  
**Commands Available:** /help, /status  
**Testing Focus:** Natural language interactions, player experience

---

## 📋 **Phase 1: Setup & Foundation Testing**

### **Step 1: Leadership Group Creation**
**Duration:** 30 minutes  
**Participants:** All 6 testers  
**Objective:** Create and configure the leadership group

**Tasks:**
1. **Create Leadership Group**
   - Create new Telegram group: "BP Hatters FC - Leadership"
   - Add @bphatters_bot to the group
   - Make bot an admin (required for commands)
   - Add all leadership members (Admin, Secretary, Manager, Treasurer)

2. **Get Leadership Chat ID**
   - Send a message in the leadership group
   - Run: `curl -s 'https://api.telegram.org/bot[TOKEN]/getUpdates' | python -m json.tool`
   - Note the leadership chat ID (negative number)

3. **Update Database**
   - Run SQL in Supabase to add leadership_chat_id column
   - Update team_bots table with leadership chat ID

**Success Criteria:**
- ✅ Leadership group created and bot added
- ✅ Leadership chat ID obtained and stored
- ✅ Database schema updated

### **Step 2: User Role Assignment**
**Duration:** 15 minutes  
**Participants:** Admin  
**Objective:** Assign roles to all testers

**Tasks:**
1. **Add Team Members to Database**
   - Add all 6 testers with appropriate roles
   - Link Telegram user IDs to team members
   - Verify role assignments

2. **Test Role Permissions**
   - Test /help command in both groups
   - Verify different command availability based on role

**Success Criteria:**
- ✅ All testers added with correct roles
- ✅ Role-based permissions working
- ✅ /help shows appropriate commands for each role

---

## 🔄 **Phase 2: Command Testing**

### **Test 1: Basic Commands**
**Duration:** 30 minutes  
**Participants:** All testers  
**Objective:** Test basic commands in both groups

**Leadership Group Tests:**
- [ ] `/help` - Show available commands
- [ ] `/status` - Show team status
- [ ] `/listmembers` - List team members
- [ ] `/listfixtures` - List fixtures (if any exist)

**Main Team Group Tests:**
- [ ] `/help` - Show team commands
- [ ] `/status` - Show team status
- [ ] Natural language: "I'm available for Sunday's match"
- [ ] Natural language: "I've paid my match fee"

**Success Criteria:**
- ✅ Commands work in appropriate groups
- ✅ Role-based permissions enforced
- ✅ Natural language responses working

### **Test 2: Fixture Management**
**Duration:** 45 minutes  
**Participants:** Admin, Secretary  
**Objective:** Test fixture creation and management

**Tasks:**
1. **Create Test Fixture**
   - Use `/newfixture` command in leadership group
   - Test with various date/time formats
   - Verify fixture creation

2. **Manage Fixtures**
   - Use `/listfixtures` to view fixtures
   - Use `/updatefixture` to modify details
   - Use `/deletefixture` to remove test fixture

3. **Announce to Team**
   - Verify fixture appears in main team group
   - Test natural language queries about fixtures

**Success Criteria:**
- ✅ Fixtures created successfully
- ✅ Fixture management commands working
- ✅ Team announcements functioning

### **Test 3: Availability Management**
**Duration:** 30 minutes  
**Participants:** Secretary, Manager, Players  
**Objective:** Test availability polling and responses

**Tasks:**
1. **Send Availability Poll**
   - Use `/sendavailability` in leadership group
   - Verify poll appears in main team group

2. **Player Responses**
   - Players respond to poll in main team group
   - Test natural language responses
   - Verify responses tracked

3. **Check Availability**
   - Use `/checkavailability` in leadership group
   - Verify response summary

**Success Criteria:**
- ✅ Availability polls sent successfully
- ✅ Player responses captured
- ✅ Availability status tracked correctly

### **Test 4: Squad Management**
**Duration:** 30 minutes  
**Participants:** Manager, Secretary  
**Objective:** Test squad selection and announcement

**Tasks:**
1. **Select Squad**
   - Use `/selectsquad` in leadership group
   - Test with various player combinations
   - Verify squad selection

2. **Announce Squad**
   - Use `/announcesquad` in leadership group
   - Verify announcement in main team group
   - Test squad queries from players

**Success Criteria:**
- ✅ Squad selection working
- ✅ Squad announcements sent
- ✅ Team can query squad information

### **Test 5: Payment Management**
**Duration:** 30 minutes  
**Participants:** Treasurer, Admin  
**Objective:** Test payment tracking (manual for now)

**Tasks:**
1. **Payment Commands**
   - Use `/createpayment` in leadership group
   - Use `/checkpayments` to view status
   - Use `/sendpayment` for reminders

2. **Payment Responses**
   - Players respond with payment confirmations
   - Test natural language payment messages
   - Verify payment tracking

**Success Criteria:**
- ✅ Payment commands working
- ✅ Payment tracking functional
- ✅ Payment reminders sent

---

## 📊 **Phase 3: Integration Testing**

### **Test 6: End-to-End Workflow**
**Duration:** 60 minutes  
**Participants:** All testers  
**Objective:** Test complete team management workflow

**Workflow:**
1. **Fixture Creation** (Secretary)
   - Create fixture for next Sunday
   - Announce to team

2. **Availability Poll** (Secretary)
   - Send availability poll
   - Players respond

3. **Squad Selection** (Manager)
   - Review availability
   - Select squad
   - Announce squad

4. **Payment Tracking** (Treasurer)
   - Create payment link
   - Send payment reminders
   - Track payments

5. **Team Communication** (All)
   - Test natural language queries
   - Verify appropriate responses

**Success Criteria:**
- ✅ Complete workflow executed successfully
- ✅ All team members can participate
- ✅ Information flows correctly between groups

---

## 🎯 **Success Metrics**

### **Technical Metrics**
- **Command Success Rate**: >95% of commands execute successfully
- **Response Time**: <2 seconds for command responses
- **Error Rate**: <5% of interactions result in errors
- **Uptime**: 100% system availability during testing

### **User Experience Metrics**
- **Ease of Use**: 90% of testers find system intuitive
- **Command Clarity**: 95% of commands work as expected
- **Natural Language**: 80% of natural language queries understood
- **Role Clarity**: 100% of testers understand their permissions

### **Business Metrics**
- **Workflow Efficiency**: 50% reduction in coordination time
- **Communication Quality**: 90% of messages delivered correctly
- **Team Engagement**: 100% of testers actively participate
- **Management Satisfaction**: 90% satisfaction with management tools

---

## 📝 **Testing Checklist**

### **Setup Phase**
- [ ] Leadership group created
- [ ] Bot added to leadership group
- [ ] Bot made admin in leadership group
- [ ] Leadership chat ID obtained
- [ ] Database schema updated
- [ ] All testers added with roles
- [ ] Role permissions tested

### **Command Testing**
- [ ] Basic commands work in both groups
- [ ] Role-based permissions enforced
- [ ] Natural language processing working
- [ ] Fixture management commands functional
- [ ] Availability management working
- [ ] Squad management operational
- [ ] Payment management functional

### **Integration Testing**
- [ ] End-to-end workflow completed
- [ ] All team members can participate
- [ ] Information flows correctly
- [ ] Error handling working
- [ ] Performance acceptable

### **User Experience**
- [ ] Interface intuitive for all roles
- [ ] Commands clear and understandable
- [ ] Natural language responses appropriate
- [ ] Role permissions clear
- [ ] System responsive and reliable

---

## 🚨 **Issue Reporting**

### **Bug Report Template**
```
**Bug Title:** [Brief description]

**Severity:** [Critical/High/Medium/Low]

**Steps to Reproduce:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Expected Result:** [What should happen]

**Actual Result:** [What actually happened]

**Environment:**
- Role: [Admin/Secretary/Manager/Treasurer/Player]
- Chat: [Leadership/Main Team]
- Command: [If applicable]

**Additional Notes:** [Any other relevant information]
```

### **Feedback Collection**
- **Daily Standup**: Brief feedback session after each testing phase
- **End-of-Day Review**: Comprehensive feedback collection
- **Final Assessment**: Overall system evaluation

---

## 📅 **Testing Schedule**

### **Day 1: Setup & Foundation**
- **Morning**: Leadership group setup, user role assignment
- **Afternoon**: Basic command testing, role verification

### **Day 2: Feature Testing**
- **Morning**: Fixture management, availability management
- **Afternoon**: Squad management, payment management

### **Day 3: Integration & Validation**
- **Morning**: End-to-end workflow testing
- **Afternoon**: User experience validation, feedback collection

### **Day 4: Refinement**
- **Morning**: Bug fixes and improvements
- **Afternoon**: Final testing and documentation

---

## 🎉 **Success Criteria**

The testing is successful when:
1. **All 6 testers** can use the system effectively
2. **Dual chat architecture** works seamlessly
3. **Role-based permissions** are properly enforced
4. **Natural language processing** understands player queries
5. **Command-based interface** enables efficient management
6. **Complete workflows** can be executed end-to-end
7. **User satisfaction** is high across all roles
8. **System performance** meets expectations

---

**Testing Plan Version:** 1.0  
**Last Updated:** December 2024  
**Status:** Ready for Execution  
**Next Review:** After Testing Completion 