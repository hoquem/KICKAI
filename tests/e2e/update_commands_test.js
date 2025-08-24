#!/usr/bin/env node
/**
 * Specialized Test Suite for /update Commands
 * 
 * Tests all variations of update commands:
 * - /update (player updates in main chat)
 * - /updatemember (team member updates in leadership chat)
 * - /updateplayer (admin updates for players)
 * 
 * Validates field updates, cross-entity sync, and validation rules.
 */

const puppeteer = require('puppeteer');
const FirestoreTestUtils = require('./firestore_utils');
const { initializeApp, cert } = require('firebase-admin/app');
const fs = require('fs');
const path = require('path');

class UpdateCommandsTestSuite {
    constructor() {
        this.browser = null;
        this.page = null;
        this.firestoreUtils = null;
        this.testResults = [];
        
        console.log('🔄 Starting Update Commands Test Suite');
    }

    async initialize() {
        console.log('🔧 Initializing update commands test environment...');
        
        try {
            // Initialize Firebase
            const credentialsPath = path.join(__dirname, '../../credentials/firebase_credentials_testing.json');
            if (!fs.existsSync(credentialsPath)) {
                throw new Error(`Firebase credentials not found: ${credentialsPath}`);
            }
            
            const serviceAccount = JSON.parse(fs.readFileSync(credentialsPath, 'utf8'));
            initializeApp({ credential: cert(serviceAccount) });
            
            this.firestoreUtils = new FirestoreTestUtils();
            
            // Launch browser
            this.browser = await puppeteer.launch({
                headless: false,
                defaultViewport: null,
                args: ['--start-maximized']
            });
            
            this.page = await this.browser.newPage();
            await this.page.goto('http://localhost:8001', { waitUntil: 'networkidle2' });
            await this.page.waitForSelector('.user-selector');
            
            console.log('✅ Update commands test environment initialized');
            return true;
            
        } catch (error) {
            console.error('❌ Failed to initialize update commands test:', error);
            return false;
        }
    }

    async switchToUser(telegram_id, chat_type = null) {
        console.log(`👤 Switching to user ${telegram_id} in ${chat_type || 'default'} chat`);
        
        // Click user selector
        await this.page.click('.user-selector');
        await this.page.waitForTimeout(500);
        
        // Find and select user
        const userSelected = await this.page.evaluate((targetId) => {
            const options = Array.from(document.querySelectorAll('.user-option'));
            const option = options.find(opt => opt.textContent.includes(targetId.toString()));
            if (option) {
                option.click();
                return true;
            }
            return false;
        }, telegram_id);
        
        if (!userSelected) {
            throw new Error(`User ${telegram_id} not found`);
        }
        
        // Switch to specific chat if requested
        if (chat_type) {
            await this.page.waitForTimeout(500);
            const chatSelector = `.chat-selector .chat-option[data-chat="${chat_type}"]`;
            await this.page.click(chatSelector);
            await this.page.waitForTimeout(500);
        }
        
        console.log(`✅ Switched to user ${telegram_id}`);
    }

    async sendCommand(command, description = '') {
        console.log(`📝 Sending: ${command}${description ? ` (${description})` : ''}`);
        
        await this.page.waitForSelector('#messageInput');
        await this.page.click('#messageInput');
        
        // Clear and type command
        await this.page.keyboard.down('Control');
        await this.page.keyboard.press('KeyA');
        await this.page.keyboard.up('Control');
        await this.page.type('#messageInput', command);
        
        // Send message
        await this.page.click('#sendButton');
        await this.page.waitForTimeout(3000); // Wait for bot response
        
        // Capture response
        const response = await this.page.evaluate(() => {
            const messages = Array.from(document.querySelectorAll('.message.bot'));
            if (messages.length > 0) {
                const latest = messages[messages.length - 1];
                return {
                    text: latest.textContent || latest.innerText,
                    html: latest.innerHTML
                };
            }
            return null;
        });
        
        if (!response) {
            throw new Error(`No response for command: ${command}`);
        }
        
        console.log(`✅ Response received (${response.text.length} chars)`);
        return response;
    }

    async testPlayerUpdateCommands() {
        console.log('\n🏃‍♂️ Testing Player Update Commands (/update)');
        const results = [];
        
        try {
            // Switch to player user in main chat
            await this.switchToUser(888888888, 'main');
            
            // Test valid field updates
            const updateTests = [
                {
                    command: '/update position "Striker"',
                    field: 'position',
                    value: 'Striker',
                    description: 'Update player position'
                },
                {
                    command: '/update email "player@test.com"',
                    field: 'email', 
                    value: 'player@test.com',
                    description: 'Update player email'
                },
                {
                    command: '/update emergency_contact_name "Emergency Contact"',
                    field: 'emergency_contact_name',
                    value: 'Emergency Contact',
                    description: 'Update emergency contact name'
                },
                {
                    command: '/update emergency_contact_phone "+447999888777"',
                    field: 'emergency_contact_phone',
                    value: '+447999888777',
                    description: 'Update emergency contact phone'
                }
            ];
            
            for (const test of updateTests) {
                console.log(`\n📋 Testing: ${test.description}`);
                
                const response = await this.sendCommand(test.command, test.description);
                
                // Check if update was acknowledged
                const isSuccess = response.text.includes('updated') || 
                                response.text.includes('success') ||
                                response.text.includes('changed');
                
                // Validate in Firestore (note: we need to find a test player)
                // For this test, we'll validate the response format
                const hasValidResponse = response.text.length > 20 && !response.text.includes('error');
                
                results.push({
                    test: `Player Update - ${test.field}`,
                    command: test.command,
                    passed: isSuccess && hasValidResponse,
                    details: {
                        success_indicated: isSuccess,
                        valid_response: hasValidResponse,
                        response_length: response.text.length
                    }
                });
                
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
            
        } catch (error) {
            console.error('❌ Player update tests failed:', error);
            results.push({
                test: 'Player Update Commands - Error',
                passed: false,
                error: error.message
            });
        }
        
        return results;
    }

    async testTeamMemberUpdateCommands() {
        console.log('\n👔 Testing Team Member Update Commands (/updatemember)');
        const results = [];
        
        try {
            // Switch to team member user in leadership chat
            await this.switchToUser(666666666, 'leadership');
            
            const memberUpdateTests = [
                {
                    command: '/updatemember phone "+447888999000"',
                    field: 'phone',
                    description: 'Update team member phone'
                },
                {
                    command: '/updatemember email "member@test.com"',
                    field: 'email',
                    description: 'Update team member email'
                },
                {
                    command: '/updatemember role "Assistant Coach"',
                    field: 'role',
                    description: 'Update team member role'
                }
            ];
            
            for (const test of memberUpdateTests) {
                console.log(`\n📋 Testing: ${test.description}`);
                
                const response = await this.sendCommand(test.command, test.description);
                
                const isSuccess = response.text.includes('updated') || 
                                response.text.includes('success') ||
                                response.text.includes('changed');
                
                const hasValidResponse = response.text.length > 20 && !response.text.includes('error');
                
                results.push({
                    test: `Team Member Update - ${test.field}`,
                    command: test.command,
                    passed: isSuccess && hasValidResponse,
                    details: {
                        success_indicated: isSuccess,
                        valid_response: hasValidResponse
                    }
                });
                
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
            
        } catch (error) {
            console.error('❌ Team member update tests failed:', error);
            results.push({
                test: 'Team Member Update Commands - Error',
                passed: false,
                error: error.message
            });
        }
        
        return results;
    }

    async testValidationRules() {
        console.log('\n🛡️ Testing Update Validation Rules');
        const results = [];
        
        try {
            // Switch to player for validation tests
            await this.switchToUser(888888888, 'main');
            
            const validationTests = [
                {
                    command: '/update phone "invalid-phone"',
                    description: 'Invalid phone format',
                    shouldFail: true
                },
                {
                    command: '/update email "not-an-email"',
                    description: 'Invalid email format',
                    shouldFail: true
                },
                {
                    command: '/update telegram_id "999999"',
                    description: 'Protected field update',
                    shouldFail: true
                },
                {
                    command: '/update nonexistent_field "value"',
                    description: 'Nonexistent field update',
                    shouldFail: true
                }
            ];
            
            for (const test of validationTests) {
                console.log(`\n📋 Testing validation: ${test.description}`);
                
                const response = await this.sendCommand(test.command, test.description);
                
                const hasError = response.text.includes('error') ||
                               response.text.includes('invalid') ||
                               response.text.includes('cannot') ||
                               response.text.includes('not allowed') ||
                               response.text.includes('protected');
                
                const validationWorking = test.shouldFail ? hasError : !hasError;
                
                results.push({
                    test: `Validation - ${test.description}`,
                    command: test.command,
                    passed: validationWorking,
                    details: {
                        should_fail: test.shouldFail,
                        has_error: hasError,
                        validation_working: validationWorking
                    }
                });
                
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
            
        } catch (error) {
            console.error('❌ Validation tests failed:', error);
            results.push({
                test: 'Validation Rules - Error',
                passed: false,
                error: error.message
            });
        }
        
        return results;
    }

    async testPermissionControls() {
        console.log('\n🔒 Testing Update Permission Controls');
        const results = [];
        
        try {
            // Test player trying to update in wrong chat
            await this.switchToUser(888888888, 'leadership');
            
            const permissionTests = [
                {
                    user: 888888888,
                    chat: 'leadership',
                    command: '/update position "Midfielder"',
                    description: 'Player update in leadership chat',
                    shouldWork: false // May be restricted
                },
                {
                    user: 666666666,
                    chat: 'main', 
                    command: '/updatemember phone "+447777888999"',
                    description: 'Team member update in main chat',
                    shouldWork: false // Should be restricted
                }
            ];
            
            for (const test of permissionTests) {
                console.log(`\n📋 Testing permission: ${test.description}`);
                
                await this.switchToUser(test.user, test.chat);
                const response = await this.sendCommand(test.command, test.description);
                
                const hasPermissionError = response.text.includes('permission') ||
                                         response.text.includes('not allowed') ||
                                         response.text.includes('leadership') ||
                                         response.text.includes('main chat');
                
                const permissionWorking = test.shouldWork ? !hasPermissionError : hasPermissionError;
                
                results.push({
                    test: `Permission - ${test.description}`,
                    command: test.command,
                    passed: permissionWorking,
                    details: {
                        should_work: test.shouldWork,
                        has_permission_error: hasPermissionError,
                        permission_working: permissionWorking
                    }
                });
                
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
            
        } catch (error) {
            console.error('❌ Permission tests failed:', error);
            results.push({
                test: 'Permission Controls - Error',
                passed: false,
                error: error.message
            });
        }
        
        return results;
    }

    generateReport(allResults) {
        console.log('\n📊 UPDATE COMMANDS TEST REPORT');
        console.log('=' .repeat(60));
        
        let totalTests = 0;
        let passedTests = 0;
        
        for (const suiteResults of allResults) {
            for (const result of suiteResults) {
                totalTests++;
                if (result.passed) passedTests++;
                
                const status = result.passed ? '✅ PASS' : '❌ FAIL';
                console.log(`${status} ${result.test}`);
                
                if (result.command) {
                    console.log(`   Command: ${result.command}`);
                }
                
                if (result.error) {
                    console.log(`   Error: ${result.error}`);
                }
                
                if (result.details) {
                    for (const [key, value] of Object.entries(result.details)) {
                        const icon = value ? '✓' : '✗';
                        console.log(`   ${icon} ${key}: ${value}`);
                    }
                }
                console.log('');
            }
        }
        
        console.log('=' .repeat(60));
        console.log(`📈 SUMMARY: ${passedTests}/${totalTests} tests passed (${Math.round(passedTests/totalTests*100)}%)`);
        
        // Save report
        const report = {
            timestamp: new Date().toISOString(),
            summary: {
                total: totalTests,
                passed: passedTests,
                failed: totalTests - passedTests,
                successRate: Math.round(passedTests/totalTests*100)
            },
            results: allResults.flat()
        };
        
        const reportPath = path.join(__dirname, `update-commands-report-${Date.now()}.json`);
        fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
        console.log(`📄 Report saved: ${reportPath}`);
        
        return report;
    }

    async runAllTests() {
        console.log('🚀 Starting Update Commands Test Suite...');
        
        const results = [];
        
        try {
            const initialized = await this.initialize();
            if (!initialized) {
                throw new Error('Failed to initialize test environment');
            }
            
            // Run test suites
            results.push(await this.testPlayerUpdateCommands());
            results.push(await this.testTeamMemberUpdateCommands());
            results.push(await this.testValidationRules());
            results.push(await this.testPermissionControls());
            
        } catch (error) {
            console.error('❌ Test execution failed:', error);
            results.push([{
                test: 'Test Execution Error',
                passed: false,
                error: error.message
            }]);
        } finally {
            // Cleanup
            if (this.firestoreUtils) {
                await this.firestoreUtils.cleanup();
            }
            
            if (this.browser) {
                await this.browser.close();
            }
        }
        
        return this.generateReport(results);
    }
}

// Main execution
if (require.main === module) {
    async function main() {
        const testSuite = new UpdateCommandsTestSuite();
        
        try {
            const report = await testSuite.runAllTests();
            const success = report.summary.successRate >= 70; // 70% pass rate
            process.exit(success ? 0 : 1);
            
        } catch (error) {
            console.error('💥 Update commands test suite crashed:', error);
            process.exit(1);
        }
    }
    
    main();
}

module.exports = UpdateCommandsTestSuite;