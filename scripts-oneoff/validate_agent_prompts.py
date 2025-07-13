#!/usr/bin/env python3
"""
Comprehensive prompt validation for the three new agents.
This script analyzes prompt quality, completeness, and effectiveness.
"""

import sys
import os
import re
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.enums import AgentRole
from config.agents import get_agent_config

def analyze_prompt_structure(backstory: str, agent_name: str) -> dict:
    """Analyze the structure and completeness of a prompt."""
    analysis = {
        "agent": agent_name,
        "total_length": len(backstory),
        "sections": {},
        "quality_indicators": {},
        "recommendations": []
    }
    
    # Check for key sections
    key_sections = [
        "CORE RESPONSIBILITIES",
        "COMMUNICATION STYLE", 
        "EXAMPLES",
        "INTEGRATION POINTS",
        "ERROR HANDLING",
        "AUTOMATION FEATURES"
    ]
    
    for section in key_sections:
        if section in backstory:
            analysis["sections"][section] = True
            # Count lines in section
            section_start = backstory.find(section)
            if section_start != -1:
                # Find next section or end
                next_section_start = -1
                for other_section in key_sections:
                    if other_section != section:
                        pos = backstory.find(other_section, section_start + 1)
                        if pos != -1 and (next_section_start == -1 or pos < next_section_start):
                            next_section_start = pos
                
                if next_section_start == -1:
                    section_content = backstory[section_start:]
                else:
                    section_content = backstory[section_start:next_section_start]
                
                analysis["sections"][f"{section}_lines"] = len(section_content.split('\n'))
        else:
            analysis["sections"][section] = False
            analysis["recommendations"].append(f"Add {section} section")
    
    # Check for examples
    if "✅ Great:" in backstory and "❌ Bad:" in backstory:
        analysis["quality_indicators"]["has_good_bad_examples"] = True
    else:
        analysis["quality_indicators"]["has_good_bad_examples"] = False
        analysis["recommendations"].append("Add good/bad examples")
    
    # Check for emojis and formatting
    emoji_count = len(re.findall(r'[🎯🏆📋⚽📢🔍🧠💪✅❌⚠️]', backstory))
    analysis["quality_indicators"]["emoji_count"] = emoji_count
    
    # Check for bullet points and lists
    bullet_points = len(re.findall(r'^[•\-\*]\s', backstory, re.MULTILINE))
    analysis["quality_indicators"]["bullet_points"] = bullet_points
    
    # Check for numbered lists
    numbered_lists = len(re.findall(r'^\d+\.\s', backstory, re.MULTILINE))
    analysis["quality_indicators"]["numbered_lists"] = numbered_lists
    
    # Check for code blocks or commands
    code_blocks = len(re.findall(r'`[^`]+`', backstory))
    analysis["quality_indicators"]["code_blocks"] = code_blocks
    
    # Check for integration mentions
    integration_mentions = len(re.findall(r'integration|coordinate|work with', backstory, re.IGNORECASE))
    analysis["quality_indicators"]["integration_mentions"] = integration_mentions
    
    # Check for specific football terminology
    football_terms = len(re.findall(r'squad|match|availability|tactical|formation|substitute|kickoff|venue', backstory, re.IGNORECASE))
    analysis["quality_indicators"]["football_terms"] = football_terms
    
    return analysis

def evaluate_prompt_quality(analysis: dict) -> dict:
    """Evaluate the overall quality of a prompt."""
    score = 0
    max_score = 100
    feedback = []
    
    # Structure completeness (30 points)
    structure_score = 0
    required_sections = ["CORE RESPONSIBILITIES", "COMMUNICATION STYLE", "EXAMPLES"]
    for section in required_sections:
        if analysis["sections"].get(section, False):
            structure_score += 10
    
    score += structure_score
    if structure_score < 30:
        feedback.append(f"Missing required sections: {[s for s in required_sections if not analysis['sections'].get(s, False)]}")
    
    # Content quality (40 points)
    content_score = 0
    
    # Length check (10 points)
    if analysis["total_length"] > 2000:
        content_score += 10
    elif analysis["total_length"] > 1000:
        content_score += 5
    else:
        feedback.append("Prompt is too short - needs more detail")
    
    # Examples check (10 points)
    if analysis["quality_indicators"].get("has_good_bad_examples", False):
        content_score += 10
    else:
        feedback.append("Missing good/bad examples")
    
    # Football terminology (10 points)
    if analysis["quality_indicators"].get("football_terms", 0) > 5:
        content_score += 10
    elif analysis["quality_indicators"].get("football_terms", 0) > 2:
        content_score += 5
    else:
        feedback.append("Limited football-specific terminology")
    
    # Integration mentions (10 points)
    if analysis["quality_indicators"].get("integration_mentions", 0) > 3:
        content_score += 10
    elif analysis["quality_indicators"].get("integration_mentions", 0) > 1:
        content_score += 5
    else:
        feedback.append("Limited integration guidance")
    
    score += content_score
    
    # Formatting and readability (30 points)
    formatting_score = 0
    
    # Emojis for visual appeal (10 points)
    if analysis["quality_indicators"].get("emoji_count", 0) > 10:
        formatting_score += 10
    elif analysis["quality_indicators"].get("emoji_count", 0) > 5:
        formatting_score += 5
    else:
        feedback.append("Could use more visual elements (emojis)")
    
    # Structured lists (10 points)
    total_lists = analysis["quality_indicators"].get("bullet_points", 0) + analysis["quality_indicators"].get("numbered_lists", 0)
    if total_lists > 10:
        formatting_score += 10
    elif total_lists > 5:
        formatting_score += 5
    else:
        feedback.append("Could use more structured lists")
    
    # Code blocks or commands (10 points)
    if analysis["quality_indicators"].get("code_blocks", 0) > 0:
        formatting_score += 10
    else:
        feedback.append("Could include command examples")
    
    score += formatting_score
    
    # Determine grade
    if score >= 90:
        grade = "A+"
    elif score >= 80:
        grade = "A"
    elif score >= 70:
        grade = "B+"
    elif score >= 60:
        grade = "B"
    elif score >= 50:
        grade = "C"
    else:
        grade = "D"
    
    return {
        "score": score,
        "max_score": max_score,
        "grade": grade,
        "feedback": feedback,
        "structure_score": structure_score,
        "content_score": content_score,
        "formatting_score": formatting_score
    }

def generate_prompt_report():
    """Generate a comprehensive prompt validation report."""
    print("🔍 COMPREHENSIVE PROMPT VALIDATION")
    print("="*60)
    
    new_agents = [
        AgentRole.AVAILABILITY_MANAGER,
        AgentRole.SQUAD_SELECTOR,
        AgentRole.COMMUNICATION_MANAGER
    ]
    
    all_analyses = []
    all_evaluations = []
    
    for agent_role in new_agents:
        print(f"\n📝 Analyzing {agent_role.value}...")
        
        config = get_agent_config(agent_role)
        if not config:
            print(f"  ❌ No config found for {agent_role.value}")
            continue
        
        # Analyze prompt structure
        analysis = analyze_prompt_structure(config.backstory, agent_role.value)
        all_analyses.append(analysis)
        
        # Evaluate quality
        evaluation = evaluate_prompt_quality(analysis)
        all_evaluations.append(evaluation)
        
        # Print detailed analysis
        print(f"  📏 Length: {analysis['total_length']} characters")
        print(f"  📊 Score: {evaluation['score']}/{evaluation['max_score']} ({evaluation['grade']})")
        print(f"  🎯 Structure: {evaluation['structure_score']}/30")
        print(f"  📝 Content: {evaluation['content_score']}/40")
        print(f"  🎨 Formatting: {evaluation['formatting_score']}/30")
        
        # Print sections
        print(f"  📋 Sections:")
        for section, present in analysis['sections'].items():
            if not section.endswith('_lines'):
                status = "✅" if present else "❌"
                print(f"    {status} {section}")
        
        # Print quality indicators
        print(f"  🎯 Quality Indicators:")
        for indicator, value in analysis['quality_indicators'].items():
            print(f"    {indicator}: {value}")
        
        # Print feedback
        if evaluation['feedback']:
            print(f"  💡 Feedback:")
            for item in evaluation['feedback']:
                print(f"    • {item}")
    
    # Overall summary
    print("\n" + "="*60)
    print("📊 OVERALL PROMPT QUALITY SUMMARY")
    print("="*60)
    
    total_score = sum(eval['score'] for eval in all_evaluations)
    max_total = sum(eval['max_score'] for eval in all_evaluations)
    average_score = total_score / len(all_evaluations) if all_evaluations else 0
    
    print(f"Average Score: {average_score:.1f}/100")
    print(f"Total Score: {total_score}/{max_total}")
    
    # Grade distribution
    grades = [eval['grade'] for eval in all_evaluations]
    grade_counts = {}
    for grade in grades:
        grade_counts[grade] = grade_counts.get(grade, 0) + 1
    
    print(f"Grade Distribution: {grade_counts}")
    
    # Recommendations
    print(f"\n💡 OVERALL RECOMMENDATIONS:")
    
    all_feedback = []
    for eval in all_evaluations:
        all_feedback.extend(eval['feedback'])
    
    # Count common feedback
    feedback_counts = {}
    for feedback in all_feedback:
        feedback_counts[feedback] = feedback_counts.get(feedback, 0) + 1
    
    for feedback, count in sorted(feedback_counts.items(), key=lambda x: x[1], reverse=True):
        if count > 1:
            print(f"  • {feedback} (appears in {count} agents)")
    
    # Overall assessment
    if average_score >= 85:
        print(f"\n🎉 EXCELLENT: Prompts are well-structured and comprehensive!")
    elif average_score >= 70:
        print(f"\n✅ GOOD: Prompts are solid with room for minor improvements.")
    elif average_score >= 50:
        print(f"\n⚠️  FAIR: Prompts need some improvements to be production-ready.")
    else:
        print(f"\n❌ POOR: Prompts need significant work before deployment.")
    
    return average_score >= 70

def main():
    """Main validation function."""
    print("🚀 Starting Comprehensive Prompt Validation...")
    print(f"⏰ Started at: {datetime.now()}")
    
    success = generate_prompt_report()
    
    print(f"\n⏰ Completed at: {datetime.now()}")
    
    if success:
        print("\n🎉 Prompt validation completed successfully!")
        return 0
    else:
        print("\n❌ Prompt validation indicates areas for improvement.")
        return 1

if __name__ == "__main__":
    exit(main()) 