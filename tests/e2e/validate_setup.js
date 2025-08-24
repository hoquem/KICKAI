#!/usr/bin/env node
/**
 * E2E Test Setup Validator
 * 
 * Validates that all prerequisites are met for running E2E tests
 * without actually executing the tests.
 */

const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

class SetupValidator {
    constructor() {
        this.errors = [];
        this.warnings = [];
        this.validations = [];
    }

    log(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        const prefix = {
            'info': '🔍',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌'
        }[type];
        
        console.log(`${prefix} [${timestamp}] ${message}`);
        
        if (type === 'error') {
            this.errors.push(message);
        } else if (type === 'warning') {
            this.warnings.push(message);
        }
        
        this.validations.push({ type, message, timestamp });
    }

    async validateNodeJS() {
        this.log('Validating Node.js installation...');
        
        try {
            const version = process.version;
            const majorVersion = parseInt(version.substring(1).split('.')[0]);
            
            if (majorVersion >= 16) {
                this.log(`Node.js version ${version} is compatible`, 'success');
            } else {
                this.log(`Node.js version ${version} is too old (need v16+)`, 'error');
            }
        } catch (error) {
            this.log(`Failed to check Node.js version: ${error.message}`, 'error');
        }
    }

    async validateFirebaseCredentials() {
        this.log('Validating Firebase credentials...');
        
        const credentialsPath = path.join(__dirname, '../../credentials/firebase_credentials_testing.json');
        
        if (!fs.existsSync(credentialsPath)) {
            this.log('Firebase credentials file not found', 'error');
            this.log(`Expected location: ${credentialsPath}`, 'info');
            return;
        }
        
        try {
            const credentials = JSON.parse(fs.readFileSync(credentialsPath, 'utf8'));
            
            const requiredFields = [
                'type', 'project_id', 'private_key_id', 'private_key',
                'client_email', 'client_id', 'auth_uri', 'token_uri'
            ];
            
            const missingFields = requiredFields.filter(field => !credentials[field]);
            
            if (missingFields.length === 0) {
                this.log('Firebase credentials file is valid', 'success');
                this.log(`Project ID: ${credentials.project_id}`, 'info');
            } else {
                this.log(`Firebase credentials missing fields: ${missingFields.join(', ')}`, 'error');
            }
        } catch (error) {
            this.log(`Firebase credentials file is invalid JSON: ${error.message}`, 'error');
        }
    }

    async validateFirebaseConnection() {
        this.log('Testing Firebase connection...');
        
        try {
            const { initializeApp, cert } = require('firebase-admin/app');
            const { getFirestore } = require('firebase-admin/firestore');
            
            const credentialsPath = path.join(__dirname, '../../credentials/firebase_credentials_testing.json');
            const serviceAccount = JSON.parse(fs.readFileSync(credentialsPath, 'utf8'));
            
            initializeApp({
                credential: cert(serviceAccount)
            });
            
            const db = getFirestore();
            
            // Test basic connection
            const testDoc = await db.collection('test').doc('connection-test').get();
            this.log('Firebase connection successful', 'success');
            
        } catch (error) {
            this.log(`Firebase connection failed: ${error.message}`, 'error');
        }
    }

    async validateDependencies() {
        this.log('Validating Node.js dependencies...');
        
        const packageJsonPath = path.join(__dirname, 'package.json');
        
        if (!fs.existsSync(packageJsonPath)) {
            this.log('package.json not found', 'error');
            return;
        }
        
        const nodeModulesPath = path.join(__dirname, 'node_modules');
        
        if (!fs.existsSync(nodeModulesPath)) {
            this.log('node_modules directory not found - run npm install', 'error');
            return;
        }
        
        // Check critical dependencies
        const criticalDeps = ['puppeteer', 'firebase-admin'];
        
        for (const dep of criticalDeps) {
            const depPath = path.join(nodeModulesPath, dep);
            if (fs.existsSync(depPath)) {
                this.log(`Dependency ${dep} is installed`, 'success');
            } else {
                this.log(`Dependency ${dep} is missing`, 'error');
            }
        }
    }

    async validateKickaiSystem() {
        this.log('Validating KICKAI system...');
        
        const projectRoot = path.join(__dirname, '../..');
        
        try {
            const result = await this.runCommand('python', [
                '-c',
                'from kickai.core.dependency_container import ensure_container_initialized; ensure_container_initialized(); print("SUCCESS")'
            ], { cwd: projectRoot, env: { ...process.env, PYTHONPATH: '.' } });
            
            if (result.includes('SUCCESS')) {
                this.log('KICKAI system initialization successful', 'success');
            } else {
                this.log('KICKAI system initialization failed', 'error');
                this.log(`Output: ${result}`, 'info');
            }
        } catch (error) {
            this.log(`KICKAI system validation failed: ${error.message}`, 'error');
        }
    }

    async validateMockTelegramUI() {
        this.log('Checking Mock Telegram UI availability...');
        
        const mockUIPath = path.join(__dirname, '../../tests/mock_telegram/start_mock_tester.py');
        
        if (!fs.existsSync(mockUIPath)) {
            this.log('Mock Telegram UI script not found', 'error');
            this.log(`Expected: ${mockUIPath}`, 'info');
            return;
        }
        
        this.log('Mock Telegram UI script found', 'success');
        
        // Check if server is already running
        try {
            const response = await fetch('http://localhost:8001');
            if (response.ok) {
                this.log('Mock Telegram UI is already running on port 8001', 'success');
            } else {
                this.log('Port 8001 is occupied but not responding correctly', 'warning');
            }
        } catch (error) {
            this.log('Mock Telegram UI is not running (will be started by test script)', 'info');
        }
    }

    async validateTestStructure() {
        this.log('Validating test file structure...');
        
        const testFiles = [
            'comprehensive_command_test.js',
            'update_commands_test.js',
            'firestore_utils.js',
            'run_e2e_tests.sh'
        ];
        
        for (const file of testFiles) {
            const filePath = path.join(__dirname, file);
            if (fs.existsSync(filePath)) {
                this.log(`Test file ${file} exists`, 'success');
            } else {
                this.log(`Test file ${file} is missing`, 'error');
            }
        }
        
        // Check if run script is executable
        const runScript = path.join(__dirname, 'run_e2e_tests.sh');
        if (fs.existsSync(runScript)) {
            try {
                const stats = fs.statSync(runScript);
                if (stats.mode & parseInt('111', 8)) {
                    this.log('Test runner script is executable', 'success');
                } else {
                    this.log('Test runner script is not executable - run chmod +x run_e2e_tests.sh', 'warning');
                }
            } catch (error) {
                this.log(`Failed to check script permissions: ${error.message}`, 'warning');
            }
        }
    }

    async runCommand(command, args, options = {}) {
        return new Promise((resolve, reject) => {
            const child = spawn(command, args, options);
            let output = '';
            let error = '';
            
            child.stdout.on('data', (data) => {
                output += data.toString();
            });
            
            child.stderr.on('data', (data) => {
                error += data.toString();
            });
            
            child.on('close', (code) => {
                if (code === 0) {
                    resolve(output);
                } else {
                    reject(new Error(`Command failed with code ${code}: ${error}`));
                }
            });
            
            // Timeout after 10 seconds
            setTimeout(() => {
                child.kill();
                reject(new Error('Command timeout'));
            }, 10000);
        });
    }

    generateReport() {
        console.log('\n' + '='.repeat(60));
        console.log('📊 E2E TEST SETUP VALIDATION REPORT');
        console.log('='.repeat(60));
        
        const totalValidations = this.validations.length;
        const successCount = this.validations.filter(v => v.type === 'success').length;
        const errorCount = this.errors.length;
        const warningCount = this.warnings.length;
        
        console.log(`\n📈 SUMMARY:`);
        console.log(`   Total checks: ${totalValidations}`);
        console.log(`   ✅ Successful: ${successCount}`);
        console.log(`   ❌ Errors: ${errorCount}`);
        console.log(`   ⚠️ Warnings: ${warningCount}`);
        
        if (errorCount === 0) {
            console.log('\n🎉 SETUP VALIDATION PASSED!');
            console.log('✅ All prerequisites are met for running E2E tests');
            if (warningCount > 0) {
                console.log('⚠️ Note: There are warnings that should be addressed');
            }
        } else {
            console.log('\n🚨 SETUP VALIDATION FAILED!');
            console.log('❌ The following issues must be resolved:');
            this.errors.forEach((error, index) => {
                console.log(`   ${index + 1}. ${error}`);
            });
        }
        
        if (warningCount > 0) {
            console.log('\n⚠️ WARNINGS:');
            this.warnings.forEach((warning, index) => {
                console.log(`   ${index + 1}. ${warning}`);
            });
        }
        
        console.log('\n📋 NEXT STEPS:');
        if (errorCount === 0) {
            console.log('   Run E2E tests: ./run_e2e_tests.sh');
        } else {
            console.log('   Fix the errors above, then run this validator again');
            console.log('   Command: node validate_setup.js');
        }
        
        console.log('='.repeat(60));
        
        return {
            passed: errorCount === 0,
            errors: this.errors,
            warnings: this.warnings,
            summary: {
                total: totalValidations,
                success: successCount,
                errors: errorCount,
                warnings: warningCount
            }
        };
    }

    async runAllValidations() {
        console.log('🔍 Starting E2E Test Setup Validation...\n');
        
        await this.validateNodeJS();
        await this.validateDependencies();
        await this.validateFirebaseCredentials();
        await this.validateFirebaseConnection();
        await this.validateKickaiSystem();
        await this.validateMockTelegramUI();
        await this.validateTestStructure();
        
        return this.generateReport();
    }
}

// Main execution
if (require.main === module) {
    async function main() {
        const validator = new SetupValidator();
        
        try {
            const report = await validator.runAllValidations();
            process.exit(report.passed ? 0 : 1);
        } catch (error) {
            console.error('💥 Setup validation crashed:', error);
            process.exit(1);
        }
    }
    
    main();
}

module.exports = SetupValidator;