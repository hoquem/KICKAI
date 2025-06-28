# 🏆 Fixture Management Testing Guide

## 📅 **New Commands Available**

### **✅ /newfixture** - Create New Fixtures
**Location:** Leadership Chat Only  
**Role Required:** Admin, Secretary

### **✅ /listfixtures** - List Fixtures  
**Location:** Leadership Chat Only  
**Role Required:** Admin, Secretary, Manager

---

## 🧪 **Testing Commands**

### **📋 Test 1: Help and Usage**
```
/newfixture
```
**Expected:** Detailed usage instructions with examples

### **📋 Test 2: Create Basic Fixture**
```
/newfixture Thunder FC 2024-07-15 14:00 "Home - Central Park"
```
**Expected:** ✅ Fixture created successfully with confirmation message

### **�� Test 3: Create Fixture with All Details**
```
/newfixture Lightning United 2024-07-22 15:30 "Away - Lightning Ground" Cup "Blue kit required"
```
**Expected:** ✅ Fixture created with competition and notes

### **📋 Test 4: Test Date Formats**
```
/newfixture Storm Rovers 15/07/2024 2:30 PM "Home - Central Park"
```
**Expected:** ✅ Fixture created with different date/time format

### **📋 Test 5: Missing Information**
```
/newfixture Thunder FC 2024-07-15
```
**Expected:** ❌ Error message listing missing fields (time, venue)

### **📋 Test 6: Invalid Date**
```
/newfixture Thunder FC invalid-date 14:00 "Home - Central Park"
```
**Expected:** ❌ Error message about invalid date format

### **📋 Test 7: List Upcoming Fixtures**
```
/listfixtures
```
**Expected:** 📅 List of upcoming fixtures (default)

### **📋 Test 8: List Past Fixtures**
```
/listfixtures past
```
**Expected:** 📅 List of past fixtures

### **📋 Test 9: List All Fixtures**
```
/listfixtures all
```
**Expected:** 📅 List of all fixtures

### **📋 Test 10: Invalid Filter**
```
/listfixtures invalid
```
**Expected:** ❌ Error message with valid filter options

---

## �� **What to Monitor**

### **✅ Database Integration**
- Fixtures should be saved to Supabase `fixtures` table
- Command logs should be recorded in `command_logs` table
- User role validation should work correctly

### **✅ Dual-Chat Announcements**
- When fixture is created in leadership chat, it should automatically announce to main team chat
- Main team chat should receive a player-friendly version of the announcement

### **✅ Input Validation**
- Date formats: `2024-07-15`, `15/07/2024`, `15-07-2024`
- Time formats: `14:00`, `2:00 PM`, `2:00PM`
- Required fields: opponent, date, time, venue
- Optional fields: competition, notes

### **✅ Error Handling**
- Missing required fields should show specific error messages
- Invalid formats should be caught and explained
- Database errors should be handled gracefully

---

## 🎯 **Success Criteria**

✅ **All commands respond within 2-3 seconds**  
✅ **Database operations complete successfully**  
✅ **Error messages are clear and helpful**  
✅ **Dual-chat announcements work correctly**  
✅ **Input validation catches all edge cases**  
✅ **Role-based permissions are enforced**  
✅ **Command logging works properly**  

**Ready for testing! ��**
