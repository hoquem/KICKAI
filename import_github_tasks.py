#!/usr/bin/env python3
"""
GitHub Tasks Import Script for KICKAI Project
This script reads github_project_import.md and creates GitHub issues for each task.
"""

import os
import re
import requests
from typing import List, Dict, Optional, Any

class GitHubTaskImporter:
    def __init__(self, repo_owner: str, repo_name: str, github_token: str):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.github_token = github_token
        self.api_base = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def create_issue(self, title: str, description: str, labels: List[str], assignees: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """Create a GitHub issue"""
        data = {
            "title": title,
            "body": description,
            "labels": labels
        }
        if assignees:
            data["assignees"] = assignees
        
        url = f"{self.api_base}/repos/{self.repo_owner}/{self.repo_name}/issues"
        response = requests.post(url, headers=self.headers, json=data)
        
        if response.status_code == 201:
            print(f"✅ Created issue: {title}")
            return response.json()
        else:
            print(f"❌ Failed to create issue: {title}")
            print(f"   Error: {response.status_code} - {response.text}")
            return None
    
    def parse_tasks_from_markdown(self, file_path: str) -> List[Dict]:
        """Parse tasks from the markdown file"""
        tasks = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by task separators
        task_sections = content.split('---')
        
        for section in task_sections:
            if not section.strip():
                continue
                
            task = self.parse_task_section(section)
            if task:
                tasks.append(task)
        
        return tasks
    
    def parse_task_section(self, section: str) -> Optional[Dict]:
        """Parse a single task section"""
        lines = section.strip().split('\n')
        
        task = {}
        current_key = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('**Title:**'):
                task['title'] = line.replace('**Title:**', '').strip()
            elif line.startswith('**Description:**'):
                task['description'] = line.replace('**Description:**', '').strip()
            elif line.startswith('**Labels:**'):
                labels_text = line.replace('**Labels:**', '').strip()
                task['labels'] = [label.replace('`', '').strip() for label in labels_text.split(',') if label.strip()]
            elif line.startswith('**Assignees:**'):
                assignees_text = line.replace('**Assignees:**', '').strip()
                task['assignees'] = [assignee.strip() for assignee in assignees_text.split(',') if assignee.strip()]
            elif line.startswith('**Column:**'):
                task['column'] = line.replace('**Column:**', '').strip()
            elif line.startswith('**Checklist:**'):
                current_key = 'checklist'
                current_content = []
            elif line.startswith('- [ ]') and current_key == 'checklist':
                current_content.append(line)
            elif current_key == 'checklist' and line.startswith('- [ ]'):
                current_content.append(line)
            elif current_key == 'checklist' and not line.startswith('- [ ]') and line:
                # End of checklist
                task['checklist'] = current_content
                current_key = None
                current_content = []
        
        # Add any remaining checklist items
        if current_key == 'checklist' and current_content:
            task['checklist'] = current_content
        
        return task if task.get('title') else None
    
    def format_issue_body(self, task: Dict) -> str:
        """Format the task as a GitHub issue body"""
        body_parts = []
        
        if task.get('description'):
            body_parts.append(f"## Description\n{task['description']}")
        
        if task.get('checklist'):
            body_parts.append("## Checklist")
            for item in task['checklist']:
                body_parts.append(item)
        
        if task.get('column'):
            body_parts.append(f"\n**Target Column:** {task['column']}")
        
        return '\n\n'.join(body_parts)
    
    def import_tasks(self, file_path: str, dry_run: bool = True) -> None:
        """Import all tasks from the markdown file"""
        print(f"📖 Reading tasks from {file_path}...")
        tasks = self.parse_tasks_from_markdown(file_path)
        
        print(f"📋 Found {len(tasks)} tasks to import")
        
        if dry_run:
            print("\n🔍 DRY RUN MODE - No issues will be created")
            print("Set dry_run=False to actually create issues\n")
        
        created_issues = []
        
        for i, task in enumerate(tasks, 1):
            print(f"\n{i}/{len(tasks)}: {task['title']}")
            print(f"   Labels: {', '.join(task['labels'])}")
            
            if not dry_run:
                issue_body = self.format_issue_body(task)
                issue = self.create_issue(
                    title=task['title'],
                    description=issue_body,
                    labels=task['labels'],
                    assignees=task.get('assignees', [])
                )
                if issue:
                    created_issues.append(issue)
        
        if not dry_run:
            print(f"\n✅ Successfully created {len(created_issues)} issues")
        else:
            print(f"\n🔍 Would create {len(tasks)} issues in real mode")

def main():
    print("🚀 KICKAI GitHub Tasks Importer")
    print("===============================")
    
    # Configuration
    repo_owner = input("Enter GitHub repository owner (username): ").strip()
    repo_name = input("Enter repository name: ").strip()
    github_token = input("Enter GitHub personal access token: ").strip()
    
    if not all([repo_owner, repo_name, github_token]):
        print("❌ All fields are required!")
        return
    
    # Check if file exists
    file_path = "github_project_import.md"
    if not os.path.exists(file_path):
        print(f"❌ File {file_path} not found!")
        return
    
    # Create importer
    importer = GitHubTaskImporter(repo_owner, repo_name, github_token)
    
    # Ask for dry run
    dry_run_input = input("\nRun in dry-run mode? (y/n, default: y): ").strip().lower()
    dry_run = dry_run_input != 'n'
    
    # Import tasks
    try:
        importer.import_tasks(file_path, dry_run=dry_run)
    except Exception as e:
        print(f"❌ Error during import: {e}")

if __name__ == "__main__":
    main() 