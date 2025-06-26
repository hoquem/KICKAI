#!/usr/bin/env python3
"""
Script to identify and delete duplicate GitHub issues
"""

import requests
from typing import List, Dict, Any
from collections import defaultdict

class GitHubIssueManager:
    def __init__(self, repo_owner: str, repo_name: str, github_token: str):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.github_token = github_token
        self.api_base = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def get_all_issues(self) -> List[Dict[str, Any]]:
        """Get all open issues from the repository"""
        issues = []
        page = 1
        
        while True:
            url = f"{self.api_base}/repos/{self.repo_owner}/{self.repo_name}/issues"
            params = {
                "state": "open",
                "per_page": 100,
                "page": page
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code != 200:
                print(f"❌ Failed to fetch issues: {response.status_code}")
                return []
            
            page_issues = response.json()
            if not page_issues:
                break
                
            issues.extend(page_issues)
            page += 1
        
        return issues
    
    def find_duplicates(self, issues: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Find duplicate issues by title"""
        duplicates = defaultdict(list)
        
        for issue in issues:
            title = issue['title']
            duplicates[title].append(issue)
        
        # Filter to only titles with more than one issue
        return {title: issues_list for title, issues_list in duplicates.items() if len(issues_list) > 1}
    
    def delete_issue(self, issue_number: int) -> bool:
        """Delete an issue by number"""
        url = f"{self.api_base}/repos/{self.repo_owner}/{self.repo_name}/issues/{issue_number}"
        
        # GitHub doesn't allow direct deletion of issues, but we can close them
        data = {"state": "closed"}
        response = requests.patch(url, headers=self.headers, json=data)
        
        if response.status_code == 200:
            print(f"✅ Closed issue #{issue_number}")
            return True
        else:
            print(f"❌ Failed to close issue #{issue_number}: {response.status_code}")
            return False
    
    def delete_duplicates(self, dry_run: bool = True) -> None:
        """Find and delete duplicate issues"""
        print("🔍 Fetching all issues...")
        issues = self.get_all_issues()
        
        if not issues:
            print("❌ No issues found!")
            return
        
        print(f"📋 Found {len(issues)} total issues")
        
        duplicates = self.find_duplicates(issues)
        
        if not duplicates:
            print("✅ No duplicate issues found!")
            return
        
        print(f"\n🔍 Found {len(duplicates)} titles with duplicates:")
        
        total_duplicates = 0
        for title, issues_list in duplicates.items():
            print(f"\n📝 '{title}' ({len(issues_list)} copies):")
            for issue in issues_list:
                print(f"   #{issue['number']} - Created: {issue['created_at']} - URL: {issue['html_url']}")
            total_duplicates += len(issues_list) - 1  # Keep one, delete the rest
        
        print(f"\n📊 Summary: {total_duplicates} duplicate issues to remove")
        
        if dry_run:
            print("\n🔍 DRY RUN MODE - No issues will be closed")
            print("Set dry_run=False to actually close duplicate issues")
            return
        
        # Ask for confirmation
        confirm = input(f"\n❓ Are you sure you want to close {total_duplicates} duplicate issues? (yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ Operation cancelled")
            return
        
        # Close duplicates (keep the oldest one)
        closed_count = 0
        for title, issues_list in duplicates.items():
            # Sort by creation date (oldest first)
            sorted_issues = sorted(issues_list, key=lambda x: x['created_at'])
            
            # Keep the oldest, close the rest
            for issue in sorted_issues[1:]:
                if self.delete_issue(issue['number']):
                    closed_count += 1
        
        print(f"\n✅ Successfully closed {closed_count} duplicate issues")

def main():
    print("🗑️  GitHub Duplicate Issue Cleaner")
    print("==================================")
    
    # Configuration
    repo_owner = input("Enter GitHub repository owner (username): ").strip()
    repo_name = input("Enter repository name: ").strip()
    github_token = input("Enter GitHub personal access token: ").strip()
    
    if not all([repo_owner, repo_name, github_token]):
        print("❌ All fields are required!")
        return
    
    # Create manager
    manager = GitHubIssueManager(repo_owner, repo_name, github_token)
    
    # Ask for dry run
    dry_run_input = input("\nRun in dry-run mode? (y/n, default: y): ").strip().lower()
    dry_run = dry_run_input != 'n'
    
    # Find and delete duplicates
    try:
        manager.delete_duplicates(dry_run=dry_run)
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 