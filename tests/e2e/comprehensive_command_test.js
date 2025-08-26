#!/usr/bin/env node
/**
 * Comprehensive End-to-End Test Suite for KICKAI Commands
 * 
 * Tests /addplayer, /addmember, and /update commands with:
 * - Mock Telegram UI automation via Puppeteer
 * - Real Firestore database validation
 * - Invite link processing and validation
 * - Cross-entity synchronization testing
 * - Permission and access control validation
 * 
 * @author Claude (Expert QA Tester)
 * @version 1.0
 */

const puppeteer = require('puppeteer');
const { initializeApp, cert } = require('firebase-admin/app');
const { getFirestore } = require('firebase-admin/firestore');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// Test configuration
const CONFIG = {
    MOCK_UI_URL: 'http://localhost:8001',
    TEST_TIMEOUT: 30000,
    FIRESTORE_TIMEOUT: 10000,
    TEST_DATA_PREFIX: 'E2E_TEST_',
    CLEANUP_ENABLED: true,
    
    // Test users with specific roles
    USERS: {
        LEADERSHIP: { telegram_id: 999999999, name: 'Leadership Admin', chat: 'leadership' },
        PLAYER: { telegram_id: 888888888, name: 'Test Player', chat: 'main' },
        NEW_USER: { telegram_id: 777777777, name: 'New User', chat: null },
        TEAM_MEMBER: { telegram_id: 666666666, name: 'Team Member', chat: 'leadership' }
    },
    
    // Test phone numbers (unique for each test run)
    PHONE_NUMBERS: {
        PLAYER_1: '+447001000001',
        PLAYER_2: '+447001000002', 
        MEMBER_1: '+447001000003',
        MEMBER_2: '+447001000004',
        DUPLICATE: '+447001000001' // Same as PLAYER_1 for duplicate testing
    }
};

class ComprehensiveTestSuite {
    constructor() {
        this.browser = null;
        this.page = null;
        this.db = null;
        this.testRunId = crypto.randomUUID();
        this.testResults = [];
        this.createdRecords = [];
        this.inviteLinks = [];
        
        console.log(`🧪 Starting E2E Test Suite - Run ID: ${this.testRunId}`);
    }

    /**
     * Initialize test environment
     */
    async initialize() {
        console.log('🔧 Initializing test environment...');
        
        try {
            // Initialize Firebase Admin
            await this.initializeFirestore();
            
            // Launch Puppeteer browser
            await this.initializeBrowser();
            
            // Navigate to Mock Telegram UI
            await this.navigateToMockUI();
            
            console.log('✅ Test environment initialized successfully');
            return true;
        } catch (error) {
            console.error('❌ Failed to initialize test environment:', error);
            return false;
        }
    }

    /**
     * Initialize Firestore connection
     */
    async initializeFirestore() {
        try {
            // Look for Firebase credentials
            const credentialsPath = path.join(__dirname, '../../credentials/firebase_credentials_testing.json');
            
            if (!fs.existsSync(credentialsPath)) {
                throw new Error(`Firebase credentials not found at: ${credentialsPath}`);
            }
            
            const serviceAccount = JSON.parse(fs.readFileSync(credentialsPath, 'utf8'));
            
            initializeApp({
                credential: cert(serviceAccount)
            });
            
            this.db = getFirestore();
            console.log('✅ Firestore initialized');
        } catch (error) {
            console.error('❌ Firestore initialization failed:', error);
            throw error;
        }
    }

    /**
     * Initialize Puppeteer browser
     */
    async initializeBrowser() {
        this.browser = await puppeteer.launch({
            headless: false, // Show browser for debugging
            defaultViewport: null,
            args: ['--start-maximized', '--no-sandbox']
        });
        
        this.page = await this.browser.newPage();
        
        // Set up console logging
        this.page.on('console', msg => {
            console.log(`🌐 Browser: ${msg.text()}`);
        });
        
        console.log('✅ Puppeteer browser initialized');
    }

    /**
     * Navigate to Mock Telegram UI
     */
    async navigateToMockUI() {
        console.log(`🌐 Navigating to Mock UI: ${CONFIG.MOCK_UI_URL}`);
        
        await this.page.goto(CONFIG.MOCK_UI_URL, { 
            waitUntil: 'networkidle2',
            timeout: CONFIG.TEST_TIMEOUT 
        });
        
        // Wait for UI to load
        await this.page.waitForSelector('.user-selector', { timeout: CONFIG.TEST_TIMEOUT });
        console.log('✅ Mock Telegram UI loaded');
    }

    /**
     * Switch to specific user in Mock UI
     */
    async switchToUser(userKey) {
        const user = CONFIG.USERS[userKey];
        if (!user) {
            throw new Error(`Invalid user key: ${userKey}`);
        }
        
        console.log(`👤 Switching to user: ${user.name} (${user.telegram_id})`);
        
        // Click user selector
        await this.page.click('.user-selector');
        await this.page.waitForSelector('.user-option', { timeout: CONFIG.TEST_TIMEOUT });
        
        // Find and click the specific user
        const userOption = await this.page.evaluate((targetId) => {
            const options = Array.from(document.querySelectorAll('.user-option'));
            const option = options.find(opt => opt.textContent.includes(targetId.toString()));
            if (option) {
                option.click();
                return true;
            }
            return false;
        }, user.telegram_id);
        
        if (!userOption) {
            throw new Error(`User ${user.telegram_id} not found in selector`);
        }
        
        // Switch to appropriate chat if specified
        if (user.chat) {
            await this.switchToChat(user.chat);
        }
        
        await this.page.waitForTimeout(1000); // Allow UI to update
        console.log(`✅ Switched to ${user.name}`);
    }

    /**
     * Switch to specific chat type
     */
    async switchToChat(chatType) {
        console.log(`💬 Switching to ${chatType} chat`);
        
        const chatSelector = `.chat-selector .chat-option[data-chat="${chatType}"]`;
        await this.page.waitForSelector(chatSelector, { timeout: CONFIG.TEST_TIMEOUT });
        await this.page.click(chatSelector);
        
        await this.page.waitForTimeout(500);
        console.log(`✅ Switched to ${chatType} chat`);
    }

    /**
     * Send command and capture response
     */
    async sendCommand(command, description = '') {
        console.log(`📝 Sending command: ${command}${description ? ` (${description})` : ''}`);
        
        // Find message input
        await this.page.waitForSelector('#messageInput', { timeout: CONFIG.TEST_TIMEOUT });
        
        // Clear input and type command
        await this.page.click('#messageInput');
        await this.page.keyboard.down('Control');
        await this.page.keyboard.press('KeyA');
        await this.page.keyboard.up('Control');
        await this.page.type('#messageInput', command);
        
        // Send message
        await this.page.click('#sendButton');
        
        // Wait for response
        await this.page.waitForTimeout(3000); // Allow time for bot processing
        
        // Capture the latest bot response
        const response = await this.page.evaluate(() => {
            const messages = Array.from(document.querySelectorAll('.message.bot'));
            if (messages.length > 0) {
                const latestMessage = messages[messages.length - 1];
                return {
                    text: latestMessage.textContent || latestMessage.innerText,
                    html: latestMessage.innerHTML,
                    timestamp: Date.now()
                };
            }
            return null;
        });
        
        if (!response) {
            throw new Error(`No bot response received for command: ${command}`);
        }
        
        console.log(`✅ Command sent, response received (${response.text.length} chars)`);
        return response;
    }

    /**
     * Extract invite link from bot response
     */
    extractInviteLink(responseText) {
        // Look for invite link patterns
        const patterns = [
            /🔗 Invite Link:\s*(https?:\/\/[^\s]+)/i,
            /Invite Link:\s*(https?:\/\/[^\s]+)/i,
            /(https?:\/\/[^\s]*invite[^\s]*)/i,
            /(https?:\/\/localhost:8001[^\s]*)/i
        ];
        
        for (const pattern of patterns) {
            const match = responseText.match(pattern);
            if (match) {
                const link = match[1].replace(/[^\w:\/\-\.?&=_]/g, ''); // Clean the link
                console.log(`🔗 Extracted invite link: ${link}`);
                this.inviteLinks.push(link);
                return link;
            }
        }
        
        console.warn('⚠️ No invite link found in response');
        return null;
    }

    /**
     * Process invite link by navigating to it
     */
    async processInviteLink(inviteLink, newUserKey = 'NEW_USER') {
        console.log(`🔄 Processing invite link: ${inviteLink}`);
        
        const newUser = CONFIG.USERS[newUserKey];
        
        // Open new tab for invite processing
        const invitePage = await this.browser.newPage();
        
        try {
            // Navigate to invite link
            await invitePage.goto(inviteLink, { 
                waitUntil: 'networkidle2',
                timeout: CONFIG.TEST_TIMEOUT 
            });
            
            // Wait for processing
            await invitePage.waitForTimeout(3000);
            
            // Capture the response
            const result = await invitePage.evaluate(() => {
                return {
                    url: window.location.href,
                    title: document.title,
                    body: document.body.textContent || document.body.innerText
                };
            });
            
            console.log('✅ Invite link processed successfully');
            return result;
            
        } catch (error) {
            console.error('❌ Failed to process invite link:', error);
            return null;
        } finally {
            await invitePage.close();
        }
    }

    /**
     * Validate record in Firestore
     */
    async validateFirestoreRecord(collection, conditions, expectedData = {}) {
        console.log(`🔍 Validating Firestore record in ${collection}...`);
        
        try {
            let query = this.db.collection(collection);
            
            // Apply conditions
            for (const [field, value] of Object.entries(conditions)) {
                query = query.where(field, '==', value);
            }
            
            const snapshot = await query.get();
            
            if (snapshot.empty) {
                console.error(`❌ No records found in ${collection} matching conditions:`, conditions);
                return null;
            }
            
            if (snapshot.size > 1) {
                console.warn(`⚠️ Multiple records found (${snapshot.size}), using first one`);
            }
            
            const doc = snapshot.docs[0];
            const data = doc.data();
            
            // Track created record for cleanup
            this.createdRecords.push({ collection, id: doc.id });
            
            // Validate expected data
            for (const [field, expectedValue] of Object.entries(expectedData)) {
                if (data[field] !== expectedValue) {
                    console.error(`❌ Field mismatch in ${collection}.${field}: expected ${expectedValue}, got ${data[field]}`);
                    return null;
                }
            }
            
            console.log(`✅ Firestore record validated in ${collection}: ${doc.id}`);
            return { id: doc.id, data };
            
        } catch (error) {
            console.error(`❌ Firestore validation failed for ${collection}:`, error);
            return null;
        }
    }

    /**
     * Run Test Suite 1: /addplayer Command
     */
    async runTestSuite1() {
        console.log('\n🏃‍♂️ TEST SUITE 1: /addplayer Command');
        const results = [];
        
        try {
            // Test 1.1: Add New Player with Valid Data
            console.log('\n📋 Test 1.1: Add New Player with Valid Data');
            await this.switchToUser('LEADERSHIP');
            
            const playerName = 'Test Player One';
            const playerPhone = CONFIG.PHONE_NUMBERS.PLAYER_1;
            const command = `/addplayer "${playerName}" "${playerPhone}"`;
            
            const response = await this.sendCommand(command, 'Add new player');
            
            // Validate response contains success indicators
            const hasSuccess = response.text.includes('Player Added Successfully') || 
                              response.text.includes('added successfully');
            
            // Extract invite link
            const inviteLink = this.extractInviteLink(response.text);
            
            // Validate Firestore player creation
            const playerRecord = await this.validateFirestoreRecord(
                'kickai_players',
                { phone: playerPhone },
                { 
                    name: playerName,
                    status: 'pending'
                }
            );
            
            // Validate invite link record
            let inviteRecord = null;
            if (inviteLink) {
                // Extract invite ID from link
                const inviteId = inviteLink.split('invite=')[1]?.split('&')[0];
                if (inviteId) {
                    inviteRecord = await this.validateFirestoreRecord(
                        'kickai_invite_links',
                        { invite_id: inviteId }
                    );
                }
            }
            
            results.push({
                test: '1.1 - Add New Player',
                passed: hasSuccess && inviteLink && playerRecord && inviteRecord,
                details: {
                    response_ok: hasSuccess,
                    invite_link: !!inviteLink,
                    player_created: !!playerRecord,
                    invite_created: !!inviteRecord
                }
            });
            
            // Test 1.2: Process Player Invite Link
            if (inviteLink) {
                console.log('\n📋 Test 1.2: Process Player Invite Link');
                const inviteResult = await this.processInviteLink(inviteLink);
                
                // Wait for processing and check player status update
                await new Promise(resolve => setTimeout(resolve, 2000));
                
                const updatedPlayer = await this.validateFirestoreRecord(
                    'kickai_players',
                    { phone: playerPhone },
                    { status: 'active' }
                );
                
                results.push({
                    test: '1.2 - Process Invite Link',
                    passed: !!inviteResult && !!updatedPlayer,
                    details: {
                        invite_processed: !!inviteResult,
                        player_activated: !!updatedPlayer
                    }
                });
            }
            
            // Test 1.3: Duplicate Phone Number Rejection
            console.log('\n📋 Test 1.3: Duplicate Phone Number Rejection');
            const duplicateCommand = `/addplayer "Another Name" "${CONFIG.PHONE_NUMBERS.DUPLICATE}"`;
            const duplicateResponse = await this.sendCommand(duplicateCommand, 'Test duplicate phone');
            
            const isDuplicateRejected = duplicateResponse.text.includes('already exists') ||
                                      duplicateResponse.text.includes('duplicate') ||
                                      duplicateResponse.text.includes('already registered');
            
            results.push({
                test: '1.3 - Duplicate Phone Rejection',
                passed: isDuplicateRejected,
                details: {
                    duplicate_rejected: isDuplicateRejected
                }
            });
            
        } catch (error) {
            console.error('❌ Test Suite 1 failed:', error);
            results.push({
                test: 'Suite 1 - Error',
                passed: false,
                error: error.message
            });
        }
        
        return results;
    }

    /**
     * Run Test Suite 2: /addmember Command
     */
    async runTestSuite2() {
        console.log('\n👔 TEST SUITE 2: /addmember Command');
        const results = [];
        
        try {
            // Test 2.1: Add New Team Member
            console.log('\n📋 Test 2.1: Add New Team Member');
            await this.switchToUser('LEADERSHIP');
            
            const memberName = 'Test Coach Smith';
            const memberPhone = CONFIG.PHONE_NUMBERS.MEMBER_1;
            const command = `/addmember "${memberName}" "${memberPhone}"`;
            
            const response = await this.sendCommand(command, 'Add new team member');
            
            const hasSuccess = response.text.includes('Team Member Added Successfully') ||
                              response.text.includes('added successfully');
            
            const inviteLink = this.extractInviteLink(response.text);
            
            // Validate Firestore team member creation
            const memberRecord = await this.validateFirestoreRecord(
                'kickai_team_members',
                { phone_number: memberPhone },
                {
                    name: memberName,
                    role: 'Team Member'
                }
            );
            
            results.push({
                test: '2.1 - Add New Team Member',
                passed: hasSuccess && inviteLink && memberRecord,
                details: {
                    response_ok: hasSuccess,
                    invite_link: !!inviteLink,
                    member_created: !!memberRecord
                }
            });
            
            // Test 2.2: Process Team Member Invite Link
            if (inviteLink) {
                console.log('\n📋 Test 2.2: Process Team Member Invite Link');
                const inviteResult = await this.processInviteLink(inviteLink);
                
                await new Promise(resolve => setTimeout(resolve, 2000));
                
                const updatedMember = await this.validateFirestoreRecord(
                    'kickai_team_members',
                    { phone_number: memberPhone }
                );
                
                results.push({
                    test: '2.2 - Process Member Invite Link',
                    passed: !!inviteResult && !!updatedMember,
                    details: {
                        invite_processed: !!inviteResult,
                        member_updated: !!updatedMember
                    }
                });
            }
            
        } catch (error) {
            console.error('❌ Test Suite 2 failed:', error);
            results.push({
                test: 'Suite 2 - Error',
                passed: false,
                error: error.message
            });
        }
        
        return results;
    }

    /**
     * Run Test Suite 3: /update Commands
     */
    async runTestSuite3() {
        console.log('\n🔄 TEST SUITE 3: /update Commands');
        const results = [];
        
        try {
            // Test 3.1: Player Self-Update (Main Chat)
            console.log('\n📋 Test 3.1: Player Self-Update (Main Chat)');
            await this.switchToUser('PLAYER');
            await this.switchToChat('main');
            
            const updateCommands = [
                { command: '/update position "Striker"', field: 'position', value: 'Striker' },
                { command: '/update email "test@example.com"', field: 'email', value: 'test@example.com' },
                { command: '/update emergency_contact_name "John Doe"', field: 'emergency_contact_name', value: 'John Doe' }
            ];
            
            for (const updateTest of updateCommands) {
                const response = await this.sendCommand(updateTest.command, `Update ${updateTest.field}`);
                const isSuccess = response.text.includes('updated') || response.text.includes('success');
                
                results.push({
                    test: `3.1 - Update ${updateTest.field}`,
                    passed: isSuccess,
                    details: { update_confirmed: isSuccess }
                });
                
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
            
            // Test 3.2: Team Member Self-Update (Leadership Chat)
            console.log('\n📋 Test 3.2: Team Member Self-Update (Leadership Chat)');
            await this.switchToUser('TEAM_MEMBER');
            await this.switchToChat('leadership');
            
            const memberUpdateCommand = '/updatemember phone "+447333333333"';
            const memberResponse = await this.sendCommand(memberUpdateCommand, 'Update team member phone');
            const memberUpdateSuccess = memberResponse.text.includes('updated') || memberResponse.text.includes('success');
            
            results.push({
                test: '3.2 - Team Member Update',
                passed: memberUpdateSuccess,
                details: { member_update_confirmed: memberUpdateSuccess }
            });
            
            // Test 3.3: Field Validation Tests
            console.log('\n📋 Test 3.3: Field Validation Tests');
            const validationTests = [
                { command: '/update phone "invalid"', shouldFail: true, description: 'Invalid phone' },
                { command: '/update email "not-an-email"', shouldFail: true, description: 'Invalid email' },
                { command: '/update telegram_id "12345"', shouldFail: true, description: 'Protected field' }
            ];
            
            await this.switchToUser('PLAYER');
            
            for (const validationTest of validationTests) {
                const response = await this.sendCommand(validationTest.command, validationTest.description);
                const hasError = response.text.includes('error') || 
                               response.text.includes('invalid') || 
                               response.text.includes('cannot be updated');
                
                results.push({
                    test: `3.3 - Validation: ${validationTest.description}`,
                    passed: validationTest.shouldFail ? hasError : !hasError,
                    details: { 
                        validation_working: hasError,
                        expected_failure: validationTest.shouldFail
                    }
                });
                
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
            
        } catch (error) {
            console.error('❌ Test Suite 3 failed:', error);
            results.push({
                test: 'Suite 3 - Error',
                passed: false,
                error: error.message
            });
        }
        
        return results;
    }

    /**
     * Run Test Suite 4: Invite Link Edge Cases
     */
    async runTestSuite4() {
        console.log('\n🔗 TEST SUITE 4: Invite Link Edge Cases');
        const results = [];
        
        try {
            // Test reusing existing invite link
            if (this.inviteLinks.length > 0) {
                console.log('\n📋 Test 4.1: Reuse Existing Invite Link');
                const existingLink = this.inviteLinks[0];
                const reuseResult = await this.processInviteLink(existingLink);
                
                const isReuseBlocked = !reuseResult || 
                                     (reuseResult.body && (reuseResult.body.includes('already used') || 
                                                          reuseResult.body.includes('expired')));
                
                results.push({
                    test: '4.1 - Invite Link Reuse Prevention',
                    passed: isReuseBlocked,
                    details: { reuse_blocked: isReuseBlocked }
                });
            }
            
            // Test malformed invite link
            console.log('\n📋 Test 4.2: Malformed Invite Link');
            const malformedLink = `${CONFIG.MOCK_UI_URL}?invite=invalid&action=join`;
            const malformedResult = await this.processInviteLink(malformedLink);
            
            const isMalformedHandled = !malformedResult || 
                                     (malformedResult.body && malformedResult.body.includes('invalid'));
            
            results.push({
                test: '4.2 - Malformed Invite Link Handling',
                passed: isMalformedHandled,
                details: { malformed_handled: isMalformedHandled }
            });
            
        } catch (error) {
            console.error('❌ Test Suite 4 failed:', error);
            results.push({
                test: 'Suite 4 - Error',
                passed: false,
                error: error.message
            });
        }
        
        return results;
    }

    /**
     * Run Test Suite 5: Permission & Access Control
     */
    async runTestSuite5() {
        console.log('\n🔒 TEST SUITE 5: Permission & Access Control');
        const results = [];
        
        try {
            // Test 5.1: Non-leadership user attempts /addplayer
            console.log('\n📋 Test 5.1: Non-Leadership User Attempts /addplayer');
            await this.switchToUser('PLAYER');
            await this.switchToChat('main');
            
            const unauthorizedCommand = '/addplayer "Unauthorized Player" "+447555555555"';
            const unauthorizedResponse = await this.sendCommand(unauthorizedCommand, 'Unauthorized addplayer');
            
            const isPermissionDenied = unauthorizedResponse.text.includes('permission') ||
                                     unauthorizedResponse.text.includes('not allowed') ||
                                     unauthorizedResponse.text.includes('leadership');
            
            results.push({
                test: '5.1 - Permission Denied for Non-Leadership',
                passed: isPermissionDenied,
                details: { permission_denied: isPermissionDenied }
            });
            
            // Test 5.2: Chat Type Restrictions
            console.log('\n📋 Test 5.2: Chat Type Restrictions');
            
            // Try /addmember in main chat (should fail)
            const mainChatCommand = '/addmember "Wrong Chat Member" "+447666666666"';
            const mainChatResponse = await this.sendCommand(mainChatCommand, 'addmember in wrong chat');
            
            const isMainChatBlocked = mainChatResponse.text.includes('leadership') ||
                                    mainChatResponse.text.includes('permission') ||
                                    mainChatResponse.text.includes('not allowed');
            
            results.push({
                test: '5.2 - Main Chat Restriction',
                passed: isMainChatBlocked,
                details: { main_chat_blocked: isMainChatBlocked }
            });
            
        } catch (error) {
            console.error('❌ Test Suite 5 failed:', error);
            results.push({
                test: 'Suite 5 - Error', 
                passed: false,
                error: error.message
            });
        }
        
        return results;
    }

    /**
     * Clean up test data
     */
    async cleanup() {
        if (!CONFIG.CLEANUP_ENABLED) {
            console.log('⚠️ Cleanup disabled, skipping...');
            return;
        }
        
        console.log('\n🧹 Cleaning up test data...');
        
        try {
            const batch = this.db.batch();
            let deleteCount = 0;
            
            for (const record of this.createdRecords) {
                const docRef = this.db.collection(record.collection).doc(record.id);
                batch.delete(docRef);
                deleteCount++;
            }
            
            if (deleteCount > 0) {
                await batch.commit();
                console.log(`✅ Cleaned up ${deleteCount} test records`);
            } else {
                console.log('ℹ️ No records to clean up');
            }
            
        } catch (error) {
            console.error('❌ Cleanup failed:', error);
        }
    }

    /**
     * Generate test report
     */
    generateReport(allResults) {
        console.log('\n📊 TEST EXECUTION REPORT');
        console.log('=' .repeat(50));
        
        let totalTests = 0;
        let passedTests = 0;
        
        for (const suiteResults of allResults) {
            for (const result of suiteResults) {
                totalTests++;
                if (result.passed) passedTests++;
                
                const status = result.passed ? '✅ PASS' : '❌ FAIL';
                console.log(`${status} ${result.test}`);
                
                if (result.error) {
                    console.log(`   Error: ${result.error}`);
                }
                
                if (result.details) {
                    for (const [key, value] of Object.entries(result.details)) {
                        const icon = value ? '✓' : '✗';
                        console.log(`   ${icon} ${key}: ${value}`);
                    }
                }
            }
        }
        
        console.log('=' .repeat(50));
        console.log(`📈 SUMMARY: ${passedTests}/${totalTests} tests passed (${Math.round(passedTests/totalTests*100)}%)`);
        console.log(`🔗 Invite links generated: ${this.inviteLinks.length}`);
        console.log(`🗂️ Database records created: ${this.createdRecords.length}`);
        console.log(`🆔 Test Run ID: ${this.testRunId}`);
        
        // Save detailed report
        const report = {
            testRunId: this.testRunId,
            timestamp: new Date().toISOString(),
            summary: {
                total: totalTests,
                passed: passedTests,
                failed: totalTests - passedTests,
                successRate: Math.round(passedTests/totalTests*100)
            },
            inviteLinks: this.inviteLinks,
            results: allResults.flat(),
            environment: {
                mockUI: CONFIG.MOCK_UI_URL,
                firestoreRecords: this.createdRecords.length
            }
        };
        
        // Write report to file
        const reportPath = path.join(__dirname, `test-report-${this.testRunId}.json`);
        fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
        console.log(`📄 Detailed report saved: ${reportPath}`);
        
        return report;
    }

    /**
     * Run all test suites
     */
    async runAllTests() {
        console.log('🚀 Starting Comprehensive E2E Test Execution...');
        
        const results = [];
        
        try {
            // Initialize environment
            const initialized = await this.initialize();
            if (!initialized) {
                throw new Error('Failed to initialize test environment');
            }
            
            // Run all test suites
            results.push(await this.runTestSuite1()); // /addplayer
            results.push(await this.runTestSuite2()); // /addmember  
            results.push(await this.runTestSuite3()); // /update commands
            results.push(await this.runTestSuite4()); // Invite link edge cases
            results.push(await this.runTestSuite5()); // Permissions
            
        } catch (error) {
            console.error('❌ Test execution failed:', error);
            results.push([{
                test: 'Test Execution Error',
                passed: false,
                error: error.message
            }]);
        } finally {
            // Clean up
            await this.cleanup();
            
            // Close browser
            if (this.browser) {
                await this.browser.close();
            }
        }
        
        // Generate and return report
        return this.generateReport(results);
    }
}

// Main execution
if (require.main === module) {
    async function main() {
        const testSuite = new ComprehensiveTestSuite();
        
        try {
            const report = await testSuite.runAllTests();
            
            // Exit with appropriate code
            const success = report.summary.successRate >= 80; // 80% pass rate required
            process.exit(success ? 0 : 1);
            
        } catch (error) {
            console.error('💥 Test suite crashed:', error);
            process.exit(1);
        }
    }
    
    main();
}

module.exports = ComprehensiveTestSuite;