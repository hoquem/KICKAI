/**
 * Quick Test Panel - Enhanced Frontend Integration
 * 
 * This module provides the frontend integration for the Quick Test Scenarios framework
 * with real-time progress tracking, comprehensive logging, and detailed reporting.
 */

class QuickTestPanel {
    constructor() {
        this.apiBase = 'http://localhost:8001/api';
        this.runningTests = new Set();
        this.testResults = [];
        this.currentSession = null;
        this.initializePanel();
    }

    initializePanel() {
        console.log('🚀 Initializing Quick Test Panel');
        this.setupEventListeners();
        this.initializeTestScenariosAPI();
    }

    setupEventListeners() {
        // Control buttons
        document.getElementById('runAllTestsBtn')?.addEventListener('click', () => this.runAllTests());
        document.getElementById('stopTestsBtn')?.addEventListener('click', () => this.stopAllTests());
        document.getElementById('clearResultsBtn')?.addEventListener('click', () => this.clearResults());
        document.getElementById('exportResultsBtn')?.addEventListener('click', () => this.exportResults());

        // Individual test scenario buttons are handled via onclick attributes in HTML
    }

    async initializeTestScenariosAPI() {
        try {
            // Initialize the backend Quick Test Controller
            const response = await fetch(`${this.apiBase}/quick-tests/initialize`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            if (response.ok) {
                console.log('✅ Quick Test Controller initialized');
                this.updateSessionInfo('Ready');
            } else {
                console.warn('⚠️ Quick Test Controller initialization failed');
                this.updateSessionInfo('Backend Unavailable');
            }
        } catch (error) {
            console.error('❌ Error initializing Quick Test Controller:', error);
            this.updateSessionInfo('Connection Error');
        }
    }

    async runQuickTest(scenarioName) {
        console.log(`🏃 Running quick test: ${scenarioName}`);

        if (this.runningTests.has(scenarioName)) {
            console.log(`⚠️ Test ${scenarioName} is already running`);
            return;
        }

        try {
            this.runningTests.add(scenarioName);
            this.updateTestStatus(scenarioName, 'running');
            this.showTestProgress(scenarioName, 0);

            // Start test execution via API
            const response = await fetch(`${this.apiBase}/quick-tests/run`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ scenario: scenarioName })
            });

            if (response.ok) {
                const result = await response.json();
                await this.monitorTestExecution(scenarioName, result.execution_id);
            } else {
                throw new Error(`API request failed: ${response.status}`);
            }

        } catch (error) {
            console.error(`❌ Test ${scenarioName} failed:`, error);
            this.updateTestStatus(scenarioName, 'failed');
            this.logTestMessage(`❌ Test ${scenarioName} failed: ${error.message}`);
        } finally {
            this.runningTests.delete(scenarioName);
            this.hideTestProgress(scenarioName);
        }
    }

    async monitorTestExecution(scenarioName, executionId) {
        const maxPollingTime = 300000; // 5 minutes
        const pollingInterval = 1000; // 1 second
        let elapsedTime = 0;

        while (elapsedTime < maxPollingTime) {
            try {
                const response = await fetch(`${this.apiBase}/quick-tests/status/${executionId}`);
                
                if (response.ok) {
                    const status = await response.json();
                    
                    this.updateTestProgress(scenarioName, status);
                    
                    if (status.completed || status.failed) {
                        if (status.completed) {
                            this.updateTestStatus(scenarioName, 'completed');
                            this.logTestMessage(`✅ Test ${scenarioName} completed successfully`);
                        } else {
                            this.updateTestStatus(scenarioName, 'failed');
                            this.logTestMessage(`❌ Test ${scenarioName} failed: ${status.error}`);
                        }
                        break;
                    }
                }

                await new Promise(resolve => setTimeout(resolve, pollingInterval));
                elapsedTime += pollingInterval;

            } catch (error) {
                console.error('Error monitoring test execution:', error);
                break;
            }
        }
    }

    updateTestProgress(scenarioName, status) {
        // Update progress bar
        const progressPercentage = status.progress_percentage || 0;
        this.showTestProgress(scenarioName, progressPercentage);

        // Update current step
        if (status.current_step) {
            this.updateTestSteps(scenarioName, status.current_step);
        }

        // Log step completion
        if (status.completed_steps) {
            status.completed_steps.forEach(step => {
                this.logTestMessage(`📝 ${scenarioName}: ${step}`);
            });
        }
    }

    async runAllTests() {
        const scenarios = [
            'player-registration',
            'invite-link-validation',
            'command-testing',
            'natural-language-processing',
            'error-handling',
            'performance-load'
        ];

        console.log('🎯 Running all quick test scenarios');
        this.updateSessionInfo('Running All Tests');
        
        try {
            // Start session
            const sessionResponse = await fetch(`${this.apiBase}/quick-tests/session/start`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            if (sessionResponse.ok) {
                const session = await sessionResponse.json();
                this.currentSession = session;
            }

            // Run all scenarios
            const results = [];
            for (const scenario of scenarios) {
                try {
                    await this.runQuickTest(scenario);
                    results.push({ scenario, status: 'completed' });
                } catch (error) {
                    results.push({ scenario, status: 'failed', error: error.message });
                }

                // Small delay between tests
                await new Promise(resolve => setTimeout(resolve, 2000));
            }

            // End session and show results
            await this.endTestSession();
            this.showTestResults(results);
            this.updateSessionInfo(`All Tests Completed - ${this.calculateSuccessRate(results)}% Success`);

        } catch (error) {
            console.error('Error running all tests:', error);
            this.updateSessionInfo('Error Running Tests');
        }
    }

    async endTestSession() {
        if (this.currentSession) {
            try {
                const response = await fetch(`${this.apiBase}/quick-tests/session/end`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ session_id: this.currentSession.session_id })
                });

                if (response.ok) {
                    const finalSession = await response.json();
                    this.testResults = finalSession.executions || [];
                }
            } catch (error) {
                console.error('Error ending test session:', error);
            }
        }
    }

    stopAllTests() {
        console.log('🛑 Stopping all running tests');
        
        this.runningTests.forEach(scenarioName => {
            this.updateTestStatus(scenarioName, 'failed');
            this.hideTestProgress(scenarioName);
            this.logTestMessage(`🛑 Test ${scenarioName} stopped by user`);
        });

        this.runningTests.clear();
        this.updateSessionInfo('Tests Stopped');
    }

    clearResults() {
        console.log('🗑️ Clearing test results');

        const resultsElement = document.getElementById('testResults');
        const logElement = document.getElementById('testLog');

        if (resultsElement) {
            resultsElement.classList.remove('visible');
        }

        if (logElement) {
            logElement.textContent = '';
        }

        // Reset all test statuses
        document.querySelectorAll('.test-status').forEach(status => {
            status.className = 'test-status ready';
            status.textContent = 'Ready';
        });

        // Hide all progress bars
        document.querySelectorAll('.test-progress').forEach(progress => {
            progress.classList.remove('visible');
        });

        document.querySelectorAll('.progress-steps').forEach(steps => {
            steps.classList.remove('visible');
        });

        this.updateSessionInfo('Ready');
        this.testResults = [];
        this.currentSession = null;
    }

    exportResults() {
        const logElement = document.getElementById('testLog');
        if (logElement && logElement.textContent.trim()) {
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            const sessionInfo = this.currentSession ? ` (Session: ${this.currentSession.session_id})` : '';
            
            const exportData = {
                timestamp: new Date().toISOString(),
                session: this.currentSession,
                results: this.testResults,
                log: logElement.textContent
            };

            const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `quick-test-results-${timestamp}.json`;
            a.click();
            URL.revokeObjectURL(url);

            this.logTestMessage(`📤 Test results exported: quick-test-results-${timestamp}.json`);
        } else {
            alert('No test results to export');
        }
    }

    // UI Update Methods

    updateTestStatus(scenarioName, status) {
        const statusElement = document.getElementById(`status-${scenarioName}`);
        if (statusElement) {
            statusElement.className = `test-status ${status}`;
            statusElement.textContent = status.charAt(0).toUpperCase() + status.slice(1);
        }
    }

    showTestProgress(scenarioName, percentage) {
        const progressElement = document.getElementById(`progress-${scenarioName}`);
        if (progressElement) {
            progressElement.classList.add('visible');
            const progressBar = progressElement.querySelector('.progress-bar');
            if (progressBar) {
                progressBar.style.width = `${Math.min(100, Math.max(0, percentage))}%`;
            }
        }
    }

    hideTestProgress(scenarioName) {
        setTimeout(() => {
            const progressElement = document.getElementById(`progress-${scenarioName}`);
            if (progressElement) {
                progressElement.classList.remove('visible');
            }

            const stepsElement = document.getElementById(`steps-${scenarioName}`);
            if (stepsElement) {
                stepsElement.classList.remove('visible');
            }
        }, 3000);
    }

    updateTestSteps(scenarioName, stepText) {
        const stepsElement = document.getElementById(`steps-${scenarioName}`);
        if (stepsElement) {
            stepsElement.classList.add('visible');
            stepsElement.textContent = stepText;
        }
    }

    updateSessionInfo(info) {
        const sessionInfoElement = document.getElementById('sessionInfo');
        if (sessionInfoElement) {
            sessionInfoElement.textContent = info;
        }
    }

    logTestMessage(message) {
        const logElement = document.getElementById('testLog');
        if (logElement) {
            const timestamp = new Date().toLocaleTimeString();
            logElement.textContent += `[${timestamp}] ${message}\n`;
            logElement.scrollTop = logElement.scrollHeight;
        }
        console.log(`📝 Test Log: ${message}`);
    }

    showTestResults(results) {
        const resultsElement = document.getElementById('testResults');
        const summaryElement = document.getElementById('resultsSummary');

        if (resultsElement && summaryElement) {
            resultsElement.classList.add('visible');

            const totalTests = results.length;
            const completedTests = results.filter(r => r.status === 'completed').length;
            const failedTests = results.filter(r => r.status === 'failed').length;
            const successRate = this.calculateSuccessRate(results);

            summaryElement.innerHTML = `
                <div class="summary-item">
                    <span class="summary-value">${totalTests}</span>
                    <span class="summary-label">Total Tests</span>
                </div>
                <div class="summary-item">
                    <span class="summary-value" style="color: var(--primary-green);">${completedTests}</span>
                    <span class="summary-label">Passed</span>
                </div>
                <div class="summary-item">
                    <span class="summary-value" style="color: var(--primary-red);">${failedTests}</span>
                    <span class="summary-label">Failed</span>
                </div>
            `;

            this.logTestMessage(`📊 Test session completed: ${successRate}% success rate`);
            this.logTestMessage(`📈 Summary: ${completedTests}/${totalTests} tests passed`);
        }
    }

    calculateSuccessRate(results) {
        if (results.length === 0) return 0;
        const completedTests = results.filter(r => r.status === 'completed').length;
        return ((completedTests / results.length) * 100).toFixed(1);
    }

    // API Integration Methods

    async getAvailableScenarios() {
        try {
            const response = await fetch(`${this.apiBase}/quick-tests/scenarios`);
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('Error fetching available scenarios:', error);
        }
        return [];
    }

    async getSessionHistory(limit = 10) {
        try {
            const response = await fetch(`${this.apiBase}/quick-tests/history?limit=${limit}`);
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('Error fetching session history:', error);
        }
        return [];
    }

    async getScenarioMetrics(scenarioName) {
        try {
            const response = await fetch(`${this.apiBase}/quick-tests/metrics/${scenarioName}`);
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('Error fetching scenario metrics:', error);
        }
        return {};
    }
}

// Global function for onclick handlers
function runQuickTest(scenarioName) {
    if (window.quickTestPanel) {
        window.quickTestPanel.runQuickTest(scenarioName);
    } else {
        console.error('Quick Test Panel not initialized');
    }
}

// Initialize Quick Test Panel when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.quickTestPanel = new QuickTestPanel();
    console.log('🚀 Quick Test Panel initialized and ready');
});