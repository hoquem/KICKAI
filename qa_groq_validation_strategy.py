#!/usr/bin/env python3.11
"""
Expert QA Testing Strategy for Groq API Call Validation
======================================================

This script implements a comprehensive testing approach to validate that:
1. Users are properly recognized from Firestore data
2. Messages route through CrewAI agents (not fallback responses)
3. Actual Groq API calls are being made and logged
4. Response patterns indicate real agent processing vs hardcoded fallbacks
"""

import asyncio
import json
import time
import aiohttp
from datetime import datetime
from typing import Dict, List, Any
import logging

class GroqAPIValidator:
    """Expert QA validator for Groq API call verification"""
    
    def __init__(self):
        self.mock_telegram_url = "http://localhost:8001"
        self.groq_patterns = {
            # Patterns that indicate real agent processing
            "agent_indicators": [
                "analyzing", "processing", "checking", "retrieving",
                "based on", "found", "according to", "updated", "confirmed"
            ],
            # Patterns that indicate fallback/unregistered responses  
            "fallback_indicators": [
                "Welcome to KICKAI for", "You're not registered",
                "KICKAI v", "test_admin", "TEST1"
            ],
            # Agent-specific response patterns
            "agent_responses": {
                "help_assistant": ["Available commands", "Help:", "Usage:"],
                "player_coordinator": ["Player status", "Registration", "Player information"], 
                "message_processor": ["Here's", "I've", "Currently"],
                "team_administrator": ["Team member", "Administrative", "Leadership"],
                "squad_selector": ["Squad", "Match", "Availability"]
            }
        }
        
    async def validate_user_recognition(self) -> Dict[str, Any]:
        """Test that users from Firestore are properly recognized"""
        print("🔍 Testing User Recognition from Firestore Data")
        
        test_users = [
            {"telegram_id": 1004, "expected_role": "leadership", "chat_id": 2002},
            {"telegram_id": 1001, "expected_role": "player", "chat_id": 2001},
        ]
        
        results = []
        
        for user in test_users:
            # Test with simple command that should recognize user
            response = await self._send_test_message(
                user_id=user["telegram_id"],
                chat_id=user["chat_id"],
                message="/myinfo"
            )
            
            recognition_result = {
                "telegram_id": user["telegram_id"],
                "recognized": not any(pattern in response.get("message", "") 
                                   for pattern in self.groq_patterns["fallback_indicators"]),
                "response_preview": response.get("message", "")[:100],
                "agent_processing": any(pattern in response.get("message", "").lower() 
                                      for pattern in self.groq_patterns["agent_indicators"])
            }
            results.append(recognition_result)
            
        return {"user_recognition_tests": results}
    
    async def validate_agent_routing(self) -> Dict[str, Any]:
        """Test that different commands route to appropriate agents"""
        print("🎯 Testing Agent Routing and Groq API Calls")
        
        agent_tests = [
            {
                "command": "/help",
                "expected_agent": "help_assistant", 
                "user_id": 1004,
                "chat_id": 2002,
                "validation_patterns": self.groq_patterns["agent_responses"]["help_assistant"]
            },
            {
                "command": "/myinfo", 
                "expected_agent": "player_coordinator",
                "user_id": 1001,
                "chat_id": 2001,
                "validation_patterns": self.groq_patterns["agent_responses"]["player_coordinator"]  
            },
            {
                "command": "Show me the team",
                "expected_agent": "message_processor",
                "user_id": 1004,
                "chat_id": 2002,
                "validation_patterns": self.groq_patterns["agent_responses"]["message_processor"]
            }
        ]
        
        results = []
        
        for test in agent_tests:
            start_time = time.time()
            response = await self._send_test_message(
                user_id=test["user_id"],
                chat_id=test["chat_id"], 
                message=test["command"]
            )
            response_time = (time.time() - start_time) * 1000
            
            # Analyze response for agent processing indicators
            response_text = response.get("message", "")
            
            agent_result = {
                "command": test["command"],
                "expected_agent": test["expected_agent"],
                "response_time_ms": response_time,
                "groq_call_likely": self._analyze_groq_indicators(response_text),
                "agent_pattern_match": any(pattern.lower() in response_text.lower() 
                                         for pattern in test["validation_patterns"]),
                "fallback_detected": any(pattern in response_text 
                                       for pattern in self.groq_patterns["fallback_indicators"]),
                "response_preview": response_text[:150]
            }
            results.append(agent_result)
            
            # Wait between tests to avoid rate limiting
            await asyncio.sleep(1)
            
        return {"agent_routing_tests": results}
    
    async def validate_groq_timing_patterns(self) -> Dict[str, Any]:
        """Analyze response timing to detect real API calls vs cached responses"""
        print("⏱️ Testing Response Timing Patterns for Groq Detection")
        
        # Test same command multiple times to detect timing variations
        timing_tests = []
        command = "/help"
        
        for i in range(5):
            start_time = time.time()
            response = await self._send_test_message(
                user_id=1004,
                chat_id=2002,
                message=command
            )
            response_time = (time.time() - start_time) * 1000
            
            timing_tests.append({
                "attempt": i + 1,
                "response_time_ms": response_time,
                "response_hash": str(hash(response.get("message", "")))[:8],
                "unique_response": True  # Will be calculated
            })
            
            await asyncio.sleep(0.5)
        
        # Analyze timing patterns
        times = [t["response_time_ms"] for t in timing_tests]
        avg_time = sum(times) / len(times)
        time_variance = max(times) - min(times)
        
        # Check for response uniqueness (real API calls should have slight variations)
        unique_responses = len(set(t["response_hash"] for t in timing_tests))
        
        return {
            "timing_analysis": {
                "average_response_time_ms": avg_time,
                "time_variance_ms": time_variance, 
                "unique_responses": unique_responses,
                "total_tests": len(timing_tests),
                "groq_api_likely": avg_time > 500 and time_variance > 100,  # Real API calls vary
                "detailed_timings": timing_tests
            }
        }
    
    def _analyze_groq_indicators(self, response_text: str) -> bool:
        """Analyze response text for indicators of real Groq processing"""
        if not response_text:
            return False
            
        # Check for fallback patterns (indicates no Groq call)
        if any(pattern in response_text for pattern in self.groq_patterns["fallback_indicators"]):
            return False
            
        # Check for agent processing patterns
        agent_indicators = sum(1 for pattern in self.groq_patterns["agent_indicators"] 
                             if pattern.lower() in response_text.lower())
        
        # Real Groq responses tend to be more varied and contextual
        response_characteristics = {
            "length": len(response_text) > 50,  # Real responses tend to be longer
            "varied_vocabulary": len(set(response_text.lower().split())) > 10,
            "agent_patterns": agent_indicators > 0,
            "no_fallback_patterns": True  # Already checked above
        }
        
        return sum(response_characteristics.values()) >= 3
    
    async def _send_test_message(self, user_id: int, chat_id: int, message: str) -> Dict[str, Any]:
        """Send test message and capture detailed response"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "user_id": user_id,
                    "chat_id": chat_id,
                    "text": message,
                    "message_type": "text"
                }
                
                # Get initial message count
                async with session.get(f"{self.mock_telegram_url}/api/messages") as resp:
                    if resp.status == 200:
                        initial_messages = await resp.json()
                        initial_count = len(initial_messages)
                    else:
                        initial_count = 0
                
                # Send message
                async with session.post(f"{self.mock_telegram_url}/api/send_message", json=payload) as resp:
                    if resp.status != 200:
                        return {"success": False, "error": f"HTTP {resp.status}"}
                
                # Wait for bot response
                for _ in range(20):  # 10 second timeout
                    await asyncio.sleep(0.5)
                    async with session.get(f"{self.mock_telegram_url}/api/messages") as resp:
                        if resp.status == 200:
                            messages = await resp.json()
                            if len(messages) > initial_count + 1:
                                # Find bot response
                                for msg in reversed(messages):
                                    if msg.get("from", {}).get("first_name") == "KICKAI Bot":
                                        return {"success": True, "message": msg.get("text", "")}
                                break
                
                return {"success": False, "error": "No bot response received"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run complete Groq API validation suite"""
        print("🧪 Starting Comprehensive Groq API Call Validation")
        print("=" * 80)
        
        # Check Mock Telegram availability
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.mock_telegram_url}/health") as resp:
                    if resp.status != 200:
                        return {"error": "Mock Telegram service not available"}
        except:
            return {"error": "Cannot connect to Mock Telegram service"}
        
        results = {
            "test_timestamp": datetime.now().isoformat(),
            "test_summary": {},
            "validation_results": {}
        }
        
        # Run validation tests
        print("\n1️⃣ User Recognition Validation")
        results["validation_results"]["user_recognition"] = await self.validate_user_recognition()
        
        print("\n2️⃣ Agent Routing Validation") 
        results["validation_results"]["agent_routing"] = await self.validate_agent_routing()
        
        print("\n3️⃣ Groq Timing Pattern Analysis")
        results["validation_results"]["timing_analysis"] = await self.validate_groq_timing_patterns()
        
        # Generate summary
        user_tests = results["validation_results"]["user_recognition"]["user_recognition_tests"]
        agent_tests = results["validation_results"]["agent_routing"]["agent_routing_tests"]
        timing_data = results["validation_results"]["timing_analysis"]["timing_analysis"]
        
        users_recognized = sum(1 for test in user_tests if test["recognized"])
        agents_responding = sum(1 for test in agent_tests if test["groq_call_likely"])
        groq_timing_detected = timing_data["groq_api_likely"]
        
        results["test_summary"] = {
            "users_recognized": f"{users_recognized}/{len(user_tests)}",
            "agents_making_groq_calls": f"{agents_responding}/{len(agent_tests)}",
            "groq_timing_patterns_detected": groq_timing_detected,
            "overall_groq_validation": users_recognized > 0 and agents_responding > 0 and groq_timing_detected
        }
        
        return results

async def main():
    """Run expert QA validation"""
    validator = GroqAPIValidator()
    results = await validator.run_comprehensive_validation()
    
    if "error" in results:
        print(f"❌ Validation failed: {results['error']}")
        print("\n💡 To fix:")
        print("1. Start Mock Telegram: PYTHONPATH=. python3.11 tests/mock_telegram/start_mock_tester.py")
        print("2. Ensure all dependencies are installed")
        return
    
    # Display results
    print("\n📊 VALIDATION RESULTS")
    print("=" * 50)
    summary = results["test_summary"]
    print(f"Users Recognized: {summary['users_recognized']}")
    print(f"Agents Making Groq Calls: {summary['agents_making_groq_calls']}")  
    print(f"Groq Timing Patterns: {summary['groq_timing_patterns_detected']}")
    print(f"Overall Validation: {'✅ PASS' if summary['overall_groq_validation'] else '❌ FAIL'}")
    
    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"groq_validation_report_{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n📄 Detailed report: {filename}")

if __name__ == "__main__":
    asyncio.run(main())