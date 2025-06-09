"""
Auto-fix missing imports for common undefined names in the 'app' folder.
This script inserts necessary import statements if they are missing.
"""

import os

TARGET_DIR = "app"

# Maps undefined names to import statements
IMPORT_FIXES = {'CommunicationPreferences': 'from app.shared.models.notification import CommunicationPreferences', 'InteractionLog': 'from app.shared.models.interaction import InteractionLog', 'ProjectLead': 'from app.project.models.project import ProjectLead', 'CallInteraction': 'from app.shared.models.interaction import CallInteraction', 'Request': 'from fastapi import Request', 'Session': 'from sqlalchemy.orm import Session', 'Depends': 'from fastapi import Depends', 'User': 'from app.shared.models.user import User', 'get_db': 'from app.shared.db.session import get_db', 'HTTPException': 'from fastapi import HTTPException', 'datetime': 'from datetime import datetime', 'Dict': 'from typing import Dict', 'Any': 'from typing import Any', 'AuditLogger': 'from app.shared.core.audit import AuditLogger', 'logger': 'from app.shared.core.logging import logger', 'ValidationError': 'from app.shared.core.exceptions import ValidationError', 'func': 'from sqlalchemy import func', 'timedelta': 'from datetime import timedelta'}

def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    undefined_imports = [name for name in IMPORT_FIXES if any(name in line for line in lines)]
    new_lines = lines.copy()

    insert_index = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("import") or line.strip().startswith("from"):
            insert_index = i + 1

    imports_to_add = [IMPORT_FIXES[name] + "\n" for name in undefined_imports if IMPORT_FIXES[name] not in lines]
    if imports_to_add:
        new_lines = new_lines[:insert_index] + imports_to_add + new_lines[insert_index:]
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"✔️  Fixed imports in: {file_path}")

def walk_directory(path):
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".py"):
                process_file(os.path.join(root, file))

if __name__ == "__main__":
    walk_directory(TARGET_DIR)
