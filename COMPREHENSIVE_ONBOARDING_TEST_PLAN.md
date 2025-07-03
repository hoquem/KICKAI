# 🧪 Comprehensive Player Onboarding Test Plan

## 🎯 Overview

This test plan covers the complete player onboarding workflow that we haven't fully tested yet. The onboarding process is a critical path that new players must complete to join the team.

## 📋 Test Scenarios

### 1. **New User Detection & Admin Approval** 🆕

#### 1.1 New User Joins via Invite Link
- **Test**: User joins main chat via invite link
- **Expected**: Bot detects new member, creates pending approval
- **Commands to test**:
  ```bash
  # Simulate new user joining
  # Check if pending approval is created
  /pending
  ```

#### 1.2 Admin Approval Process
- **Test**: Admin approves new user in leadership chat
- **Expected**: User status changes from PENDING_APPROVAL to PENDING
- **Commands to test**:
  ```bash
  # In leadership chat
  /approve JS1
  /pending
  ```

#### 1.3 Admin Rejection Process
- **Test**: Admin rejects new user with reason
- **Expected**: User is removed from pending list
- **Commands to test**:
  ```bash
  # In leadership chat
  /reject JS1 "Already registered with another club"
  /pending
  ```

### 2. **Profile Completion Step** 📝

#### 2.1 Welcome Message Response - Confirm Details
- **Test**: User responds "yes" to confirm details
- **Expected**: Moves to profile completion step
- **User input**: `yes`
- **Expected response**: Profile completion prompt

#### 2.2 Welcome Message Response - Update Details
- **Test**: User responds "no" to update details
- **Expected**: Moves to profile completion step with update prompt
- **User input**: `no`
- **Expected response**: Profile update prompt

#### 2.3 Profile Update - Name Only
- **Test**: User updates only their name
- **User input**: `Name: John Smith`
- **Expected**: Name updated, moves to emergency contact

#### 2.4 Profile Update - Phone Only
- **Test**: User updates only their phone
- **User input**: `Phone: 07123456789`
- **Expected**: Phone updated, moves to emergency contact

#### 2.5 Profile Update - Position Only
- **Test**: User updates only their position
- **User input**: `Position: striker`
- **Expected**: Position updated, moves to emergency contact

#### 2.6 Profile Update - All Fields
- **Test**: User updates all profile fields
- **User input**: `Name: John Smith, Phone: 07123456789, Position: midfielder`
- **Expected**: All fields updated, moves to emergency contact

#### 2.7 Profile Update - Invalid Position
- **Test**: User provides invalid position
- **User input**: `Position: invalid_position`
- **Expected**: Error message with valid positions listed

#### 2.8 Profile Skip
- **Test**: User skips profile updates
- **User input**: `skip`
- **Expected**: Moves to emergency contact with current details

### 3. **Emergency Contact Step** 📞

#### 3.1 Valid Emergency Contact
- **Test**: User provides valid emergency contact
- **User input**: `Jane Smith, 07987654321`
- **Expected**: Emergency contact saved, moves to date of birth

#### 3.2 Emergency Contact with Relationship
- **Test**: User includes relationship in contact
- **User input**: `Jane Smith - Wife, 07987654321`
- **Expected**: Emergency contact saved, moves to date of birth

#### 3.3 Invalid Emergency Contact - Missing Comma
- **Test**: User provides contact without comma
- **User input**: `Jane Smith 07987654321`
- **Expected**: Error message with format instructions

#### 3.4 Invalid Emergency Contact - Invalid Phone
- **Test**: User provides invalid phone number
- **User input**: `Jane Smith, 12345`
- **Expected**: Error message about phone format

#### 3.5 Invalid Emergency Contact - Empty Name
- **Test**: User provides empty name
- **User input**: `, 07987654321`
- **Expected**: Error message about format

### 4. **Date of Birth Step** 📅

#### 4.1 Valid Date of Birth
- **Test**: User provides valid date
- **User input**: `15/05/1995`
- **Expected**: Date saved, moves to FA eligibility

#### 4.2 Invalid Date Format
- **Test**: User provides wrong format
- **User input**: `1995-05-15`
- **Expected**: Error message with DD/MM/YYYY format

#### 4.3 Invalid Date - Non-existent Date
- **Test**: User provides non-existent date
- **User input**: `31/02/1995`
- **Expected**: Error message about invalid date

#### 4.4 Invalid Date - Too Young
- **Test**: User provides date making them under 16
- **User input**: `15/05/2010`
- **Expected**: Date saved but may affect FA eligibility

#### 4.5 Invalid Date - Too Old
- **Test**: User provides date making them over 80
- **User input**: `15/05/1940`
- **Expected**: Error message about reasonable age range

### 5. **FA Eligibility Step** 🏆

#### 5.1 FA Eligible - Yes
- **Test**: User confirms FA eligibility
- **User input**: `yes`
- **Expected**: Moves to FA registration process

#### 5.2 FA Eligible - No
- **Test**: User indicates not FA eligible
- **User input**: `no`
- **Expected**: Moves to team access setup

#### 5.3 FA Eligible - Alternative Responses
- **Test**: User uses alternative confirmations
- **User inputs**: `y`, `eligible`, `confirm`
- **Expected**: All should move to FA registration

#### 5.4 FA Eligible - Invalid Response
- **Test**: User provides unclear response
- **User input**: `maybe`
- **Expected**: Error message asking for yes/no

### 6. **FA Registration Process** 📋

#### 6.1 FA Registration - Ready
- **Test**: User confirms ready for FA registration
- **User input**: `ready`
- **Expected**: Admin notification sent, moves to team access

#### 6.2 FA Registration - Help
- **Test**: User requests help with FA registration
- **User input**: `help`
- **Expected**: Detailed help information about FA registration

#### 6.3 FA Registration - Invalid Response
- **Test**: User provides unclear response
- **User input**: `what?`
- **Expected**: Error message asking for ready/help

### 7. **Team Access Setup** ✅

#### 7.1 Onboarding Completion
- **Test**: Complete onboarding process
- **Expected**: Player gets full team access, welcome message

#### 7.2 Team Member Creation
- **Test**: Verify team member entry is created
- **Expected**: Player appears in team member list with correct permissions

### 8. **Error Handling & Edge Cases** ⚠️

#### 8.1 Invalid Onboarding Step
- **Test**: Player has invalid onboarding step
- **Expected**: Error message about invalid step

#### 8.2 Player Not Found
- **Test**: Process response for non-existent player
- **Expected**: Error message about player not found

#### 8.3 Database Errors
- **Test**: Simulate database connection issues
- **Expected**: Graceful error handling with user-friendly messages

#### 8.4 Concurrent Onboarding
- **Test**: Multiple players onboarding simultaneously
- **Expected**: Each player's progress is tracked independently

### 9. **Admin Commands During Onboarding** 👑

#### 9.1 View Pending Approvals
- **Test**: Admin checks pending approvals
- **Command**: `/pending`
- **Expected**: List of players awaiting approval

#### 9.2 Approve Player During Onboarding
- **Test**: Admin approves player mid-onboarding
- **Command**: `/approve JS1`
- **Expected**: Player can continue onboarding

#### 9.3 Reject Player During Onboarding
- **Test**: Admin rejects player mid-onboarding
- **Command**: `/reject JS1 "Reason"`
- **Expected**: Player removed from system

### 10. **Integration Tests** 🔗

#### 10.1 End-to-End Onboarding Flow
- **Test**: Complete onboarding from start to finish
- **Steps**:
  1. New user joins
  2. Admin approves
  3. User completes all steps
  4. Verify final state

#### 10.2 Onboarding with FA Registration
- **Test**: Complete onboarding including FA registration
- **Steps**:
  1. Complete all steps
  2. Confirm FA eligibility
  3. Request FA registration
  4. Verify admin notification

#### 10.3 Onboarding without FA Registration
- **Test**: Complete onboarding without FA registration
- **Steps**:
  1. Complete all steps
  2. Decline FA eligibility
  3. Verify team access granted

## 🛠️ Test Implementation

### Manual Testing Script

```bash
# 1. Test New User Detection
# Join main chat with new user account
# Verify pending approval created

# 2. Test Admin Approval
# In leadership chat:
/pending
/approve JS1

# 3. Test Onboarding Steps
# In main chat (as new user):
yes  # Confirm details
skip  # Skip profile updates
Jane Smith, 07987654321  # Emergency contact
15/05/1995  # Date of birth
yes  # FA eligible
ready  # Ready for FA registration

# 4. Verify Completion
/myinfo
/list
```

### Automated Test Script

```python
# test_comprehensive_onboarding.py
async def test_complete_onboarding_flow():
    """Test the complete onboarding workflow."""
    
    # 1. Test new user detection
    # 2. Test admin approval
    # 3. Test each onboarding step
    # 4. Test validation errors
    # 5. Test completion
    pass
```

## 📊 Success Criteria

### Functional Requirements
- ✅ New users are detected automatically
- ✅ Admin approval process works correctly
- ✅ All onboarding steps complete successfully
- ✅ Validation prevents invalid data
- ✅ Error handling provides clear messages
- ✅ Team access is granted upon completion

### User Experience Requirements
- ✅ Clear, helpful messages at each step
- ✅ Validation errors are user-friendly
- ✅ Progress is clearly indicated
- ✅ Users can skip optional steps
- ✅ Help is available at each step

### Technical Requirements
- ✅ Database state is consistent
- ✅ Concurrent onboarding works correctly
- ✅ Admin notifications are sent
- ✅ Team member permissions are correct
- ✅ Logging captures all events

## 🚨 Known Issues to Test

1. **Phone Number Validation**: Test various UK phone formats
2. **Date Validation**: Test edge cases for date of birth
3. **Position Validation**: Test all valid positions
4. **Emergency Contact**: Test various name formats
5. **FA Eligibility**: Test age-based eligibility

## 📝 Test Documentation

After running tests, document:
- ✅ Passed scenarios
- ❌ Failed scenarios
- 🔧 Issues found
- 📈 Performance metrics
- 💡 Improvement suggestions

---

**Next Steps**: Run these tests systematically to ensure the onboarding workflow is robust and user-friendly. 