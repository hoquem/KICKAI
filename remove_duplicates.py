#!/usr/bin/env python3
"""
Script to remove duplicate PlayerCommandHandler classes from player_registration_handler.py
"""

import re

def remove_duplicate_classes():
    """Remove all duplicate PlayerCommandHandler classes, keeping only the first one."""
    
    # Read the file
    with open('src/telegram/player_registration_handler.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all class definitions
    class_pattern = r'class PlayerCommandHandler:.*?(?=class PlayerCommandHandler:|class \w+:|$)'
    matches = list(re.finditer(class_pattern, content, re.DOTALL))
    
    if len(matches) <= 1:
        print("No duplicate classes found or only one class exists.")
        return
    
    print(f"Found {len(matches)} PlayerCommandHandler classes")
    
    # Keep only the first class
    first_match = matches[0]
    first_class = first_match.group()
    
    # Find the end of the first class (before the next class)
    start_pos = first_match.end()
    
    # Find the next class after the first one
    next_class_pattern = r'class \w+:'
    next_class_match = re.search(next_class_pattern, content[start_pos:])
    
    if next_class_match:
        # Keep everything up to the next class
        end_pos = start_pos + next_class_match.start()
        new_content = content[:end_pos]
    else:
        # Keep everything after the first class
        new_content = content[:start_pos]
    
    # Write the cleaned content back
    with open('src/telegram/player_registration_handler.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("Successfully removed duplicate classes!")

if __name__ == "__main__":
    remove_duplicate_classes() 