#!/usr/bin/env python3
"""
Firestore Validator

Real-time validation of Firestore data changes during functional testing.
Ensures data integrity, schema compliance, and proper relationships.
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from datetime import datetime, timezone
import json

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from kickai.core.dependency_container import ensure_container_initialized, get_container
from kickai.core.firestore_constants import (
    get_team_players_collection,
    get_team_members_collection,
    get_collection_name,
    COLLECTION_INVITE_LINKS,
    COLLECTION_TEAMS
)
from kickai.database.interfaces import DataStoreInterface
from loguru import logger

@dataclass
class ValidationRule:
    """Data validation rule definition"""
    field_name: str
    required: bool
    data_type: type
    validator_func: Optional[callable] = None
    description: str = ""

@dataclass 
class ValidationResult:
    """Validation result for a single check"""
    is_valid: bool
    field_name: str
    expected: Any
    actual: Any
    message: str

@dataclass
class DataSnapshot:
    """Snapshot of collection data at a point in time"""
    collection: str
    timestamp: datetime
    document_count: int
    documents: List[Dict[str, Any]]

class FirestoreValidator:
    """Validates Firestore data integrity during functional testing"""
    
    def __init__(self, team_id: str = "KTI"):
        self.team_id = team_id
        self.database: Optional[DataStoreInterface] = None
        self.validation_results: List[ValidationResult] = []
        self.snapshots: Dict[str, DataSnapshot] = {}
        self.phone_numbers: Set[str] = set()
        
        # Define validation rules
        self.player_rules = self._get_player_validation_rules()
        self.member_rules = self._get_member_validation_rules()
        self.invite_link_rules = self._get_invite_link_validation_rules()

    async def initialize(self):
        """Initialize database connection and baseline data"""
        try:
            ensure_container_initialized()
            container = get_container()
            self.database = container.get_database()
            
            # Take initial snapshots
            await self._take_baseline_snapshots()
            
            logger.info(f"✅ Firestore Validator initialized for team: {self.team_id}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Firestore Validator: {e}")
            raise

    def _get_player_validation_rules(self) -> List[ValidationRule]:
        """Get validation rules for player documents"""
        return [
            ValidationRule("player_id", True, str, None, "Player ID must be a string"),
            ValidationRule("name", True, str, lambda x: len(x.strip()) >= 2, "Name must be at least 2 characters"),
            ValidationRule("phone", True, str, self._validate_phone_format, "Phone must be valid format"),
            ValidationRule("telegram_id", True, int, lambda x: x > 0, "Telegram ID must be positive integer"),
            ValidationRule("status", True, str, lambda x: x in ["active", "pending", "inactive"], "Status must be valid"),
            ValidationRule("team_id", True, str, lambda x: x == self.team_id, f"Team ID must be {self.team_id}"),
            ValidationRule("created_at", True, str, self._validate_iso_datetime, "Created at must be ISO datetime"),
        ]

    def _get_member_validation_rules(self) -> List[ValidationRule]:
        """Get validation rules for member documents"""
        return [
            ValidationRule("member_id", True, str, None, "Member ID must be a string"),
            ValidationRule("name", True, str, lambda x: len(x.strip()) >= 2, "Name must be at least 2 characters"),
            ValidationRule("phone", True, str, self._validate_phone_format, "Phone must be valid format"),
            ValidationRule("telegram_id", True, int, lambda x: x > 0, "Telegram ID must be positive integer"),
            ValidationRule("role", True, str, lambda x: x in ["coach", "manager", "team_member"], "Role must be valid"),
            ValidationRule("status", True, str, lambda x: x in ["active", "pending", "inactive"], "Status must be valid"),
            ValidationRule("team_id", True, str, lambda x: x == self.team_id, f"Team ID must be {self.team_id}"),
            ValidationRule("created_at", True, str, self._validate_iso_datetime, "Created at must be ISO datetime"),
        ]

    def _get_invite_link_validation_rules(self) -> List[ValidationRule]:
        """Get validation rules for invite link documents"""
        return [
            ValidationRule("link_id", True, str, None, "Link ID must be a string"),
            ValidationRule("secure_token", True, str, lambda x: len(x) >= 32, "Secure token must be at least 32 chars"),
            ValidationRule("team_id", True, str, lambda x: x == self.team_id, f"Team ID must be {self.team_id}"),
            ValidationRule("expires_at", True, str, self._validate_iso_datetime, "Expires at must be ISO datetime"),
            ValidationRule("created_at", True, str, self._validate_iso_datetime, "Created at must be ISO datetime"),
            ValidationRule("status", True, str, lambda x: x in ["active", "used", "expired"], "Status must be valid"),
        ]

    def _validate_phone_format(self, phone: str) -> bool:
        """Validate phone number format"""
        if not phone:
            return False
        # Basic UK phone validation
        return phone.startswith(("+447", "07")) and len(phone.replace("+", "").replace(" ", "")) >= 10

    def _validate_iso_datetime(self, dt_str: str) -> bool:
        """Validate ISO datetime string format"""
        try:
            datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            return True
        except:
            return False

    async def _take_baseline_snapshots(self):
        """Take baseline snapshots of all collections"""
        try:
            collections = {
                "players": get_team_players_collection(self.team_id),
                "members": get_team_members_collection(self.team_id),
                "invite_links": get_collection_name(COLLECTION_INVITE_LINKS),
                "teams": get_collection_name(COLLECTION_TEAMS)
            }
            
            for name, collection in collections.items():
                documents = await self.database.query_documents(collection)
                
                snapshot = DataSnapshot(
                    collection=collection,
                    timestamp=datetime.now(timezone.utc),
                    document_count=len(documents),
                    documents=documents
                )
                
                self.snapshots[f"baseline_{name}"] = snapshot
                logger.info(f"📸 Baseline snapshot: {name} ({len(documents)} documents)")
                
                # Track phone numbers for uniqueness validation
                for doc in documents:
                    if "phone" in doc:
                        self.phone_numbers.add(doc["phone"])
                        
        except Exception as e:
            logger.error(f"❌ Failed to take baseline snapshots: {e}")
            raise

    async def validate_document(self, collection_type: str, document: Dict[str, Any]) -> List[ValidationResult]:
        """Validate a single document against rules"""
        try:
            results = []
            
            # Get appropriate rules
            if collection_type == "players":
                rules = self.player_rules
            elif collection_type == "members":
                rules = self.member_rules
            elif collection_type == "invite_links":
                rules = self.invite_link_rules
            else:
                logger.warning(f"⚠️ No validation rules for collection type: {collection_type}")
                return results

            # Validate each rule
            for rule in rules:
                result = self._validate_field(document, rule)
                results.append(result)
                
                if not result.is_valid:
                    logger.warning(f"❌ Validation failed: {result.message}")

            return results
            
        except Exception as e:
            logger.error(f"❌ Document validation failed: {e}")
            return [ValidationResult(False, "system", "valid", "error", str(e))]

    def _validate_field(self, document: Dict[str, Any], rule: ValidationRule) -> ValidationResult:
        """Validate a single field against a rule"""
        try:
            field_value = document.get(rule.field_name)
            
            # Check required fields
            if rule.required and field_value is None:
                return ValidationResult(
                    is_valid=False,
                    field_name=rule.field_name,
                    expected="required",
                    actual="missing",
                    message=f"Required field {rule.field_name} is missing"
                )
            
            # Skip validation if field is not required and missing
            if not rule.required and field_value is None:
                return ValidationResult(
                    is_valid=True,
                    field_name=rule.field_name,
                    expected="optional",
                    actual="missing",
                    message=f"Optional field {rule.field_name} not provided"
                )
            
            # Check data type
            if not isinstance(field_value, rule.data_type):
                return ValidationResult(
                    is_valid=False,
                    field_name=rule.field_name,
                    expected=rule.data_type.__name__,
                    actual=type(field_value).__name__,
                    message=f"Field {rule.field_name} has wrong type"
                )
            
            # Custom validation function
            if rule.validator_func and not rule.validator_func(field_value):
                return ValidationResult(
                    is_valid=False,
                    field_name=rule.field_name,
                    expected="valid",
                    actual=str(field_value),
                    message=f"Field {rule.field_name} failed custom validation: {rule.description}"
                )
            
            return ValidationResult(
                is_valid=True,
                field_name=rule.field_name,
                expected="valid",
                actual=str(field_value),
                message=f"Field {rule.field_name} is valid"
            )
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                field_name=rule.field_name,
                expected="valid",
                actual="error",
                message=f"Validation error for {rule.field_name}: {e}"
            )

    async def validate_phone_uniqueness(self) -> ValidationResult:
        """Validate phone number uniqueness across players and members"""
        try:
            # Get current phone numbers
            current_phones = set()
            duplicates = []
            
            # Check players
            players_collection = get_team_players_collection(self.team_id)
            players = await self.database.query_documents(players_collection)
            
            for player in players:
                phone = player.get("phone")
                if phone:
                    if phone in current_phones:
                        duplicates.append(f"Player phone: {phone}")
                    else:
                        current_phones.add(phone)
            
            # Check members
            members_collection = get_team_members_collection(self.team_id)
            members = await self.database.query_documents(members_collection)
            
            for member in members:
                phone = member.get("phone")
                if phone:
                    if phone in current_phones:
                        duplicates.append(f"Member phone: {phone}")
                    else:
                        current_phones.add(phone)
            
            if duplicates:
                return ValidationResult(
                    is_valid=False,
                    field_name="phone_uniqueness",
                    expected="unique phones",
                    actual=f"{len(duplicates)} duplicates",
                    message=f"Duplicate phone numbers found: {', '.join(duplicates)}"
                )
            else:
                return ValidationResult(
                    is_valid=True,
                    field_name="phone_uniqueness",
                    expected="unique phones",
                    actual=f"{len(current_phones)} unique",
                    message="All phone numbers are unique"
                )
                
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                field_name="phone_uniqueness",
                expected="valid check",
                actual="error",
                message=f"Phone uniqueness check failed: {e}"
            )

    async def validate_invite_links(self) -> List[ValidationResult]:
        """Validate invite link integrity"""
        try:
            results = []
            invite_links_collection = get_collection_name(COLLECTION_INVITE_LINKS)
            
            # Get all invite links for team
            invite_links = await self.database.query_documents(
                invite_links_collection,
                filters=[{"field": "team_id", "operator": "==", "value": self.team_id}]
            )
            
            active_tokens = set()
            
            for link in invite_links:
                # Validate document structure
                doc_results = await self.validate_document("invite_links", link)
                results.extend(doc_results)
                
                # Check token uniqueness
                token = link.get("secure_token")
                if token:
                    if token in active_tokens:
                        results.append(ValidationResult(
                            is_valid=False,
                            field_name="secure_token",
                            expected="unique token",
                            actual="duplicate",
                            message=f"Duplicate secure token found: {token[:8]}..."
                        ))
                    else:
                        active_tokens.add(token)
                
                # Validate expiration
                expires_at = link.get("expires_at")
                if expires_at:
                    try:
                        exp_time = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                        if exp_time <= datetime.now(timezone.utc):
                            results.append(ValidationResult(
                                is_valid=False,
                                field_name="expires_at",
                                expected="future date",
                                actual="expired",
                                message=f"Invite link has expired: {expires_at}"
                            ))
                    except:
                        pass  # Will be caught by datetime validation
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Invite link validation failed: {e}")
            return [ValidationResult(False, "invite_links", "valid", "error", str(e))]

    async def validate_data_integrity(self) -> Dict[str, Any]:
        """Perform comprehensive data integrity validation"""
        try:
            logger.info("🔍 Performing comprehensive data integrity validation...")
            
            validation_summary = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "team_id": self.team_id,
                "results": {
                    "players": [],
                    "members": [],
                    "invite_links": [],
                    "phone_uniqueness": None,
                    "overall_valid": True
                },
                "counts": {},
                "errors": []
            }
            
            # Validate players
            players_collection = get_team_players_collection(self.team_id)
            players = await self.database.query_documents(players_collection)
            validation_summary["counts"]["players"] = len(players)
            
            for player in players:
                player_results = await self.validate_document("players", player)
                validation_summary["results"]["players"].extend(player_results)
                
                # Check if any validation failed
                if any(not r.is_valid for r in player_results):
                    validation_summary["results"]["overall_valid"] = False
            
            # Validate members
            members_collection = get_team_members_collection(self.team_id)
            members = await self.database.query_documents(members_collection)
            validation_summary["counts"]["members"] = len(members)
            
            for member in members:
                member_results = await self.validate_document("members", member)
                validation_summary["results"]["members"].extend(member_results)
                
                if any(not r.is_valid for r in member_results):
                    validation_summary["results"]["overall_valid"] = False
            
            # Validate invite links
            invite_results = await self.validate_invite_links()
            validation_summary["results"]["invite_links"] = invite_results
            validation_summary["counts"]["invite_links"] = len(invite_results)
            
            if any(not r.is_valid for r in invite_results):
                validation_summary["results"]["overall_valid"] = False
            
            # Validate phone uniqueness
            phone_result = await self.validate_phone_uniqueness()
            validation_summary["results"]["phone_uniqueness"] = phone_result
            
            if not phone_result.is_valid:
                validation_summary["results"]["overall_valid"] = False
            
            # Generate summary statistics
            total_validations = (
                len(validation_summary["results"]["players"]) +
                len(validation_summary["results"]["members"]) +
                len(validation_summary["results"]["invite_links"]) + 1  # +1 for phone uniqueness
            )
            
            failed_validations = sum([
                sum(1 for r in validation_summary["results"]["players"] if not r.is_valid),
                sum(1 for r in validation_summary["results"]["members"] if not r.is_valid),
                sum(1 for r in validation_summary["results"]["invite_links"] if not r.is_valid),
                0 if phone_result.is_valid else 1
            ])
            
            validation_summary["statistics"] = {
                "total_validations": total_validations,
                "passed_validations": total_validations - failed_validations,
                "failed_validations": failed_validations,
                "success_rate": ((total_validations - failed_validations) / total_validations * 100) if total_validations > 0 else 0
            }
            
            if validation_summary["results"]["overall_valid"]:
                logger.info("✅ Data integrity validation passed")
            else:
                logger.warning(f"⚠️ Data integrity validation failed ({failed_validations} issues)")
            
            return validation_summary
            
        except Exception as e:
            logger.error(f"❌ Data integrity validation failed: {e}")
            return {"error": str(e), "timestamp": datetime.now(timezone.utc).isoformat()}

    async def compare_with_baseline(self, collection_type: str) -> Dict[str, Any]:
        """Compare current state with baseline snapshot"""
        try:
            baseline_key = f"baseline_{collection_type}"
            if baseline_key not in self.snapshots:
                return {"error": f"No baseline snapshot for {collection_type}"}
            
            baseline = self.snapshots[baseline_key]
            
            # Get current state
            if collection_type == "players":
                collection = get_team_players_collection(self.team_id)
            elif collection_type == "members":
                collection = get_team_members_collection(self.team_id)
            elif collection_type == "invite_links":
                collection = get_collection_name(COLLECTION_INVITE_LINKS)
            else:
                return {"error": f"Unknown collection type: {collection_type}"}
                
            current_docs = await self.database.query_documents(collection)
            
            comparison = {
                "collection_type": collection_type,
                "baseline_count": baseline.document_count,
                "current_count": len(current_docs),
                "documents_added": len(current_docs) - baseline.document_count,
                "changes": [],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Find new documents (simple comparison by count)
            if comparison["documents_added"] > 0:
                comparison["changes"].append(f"Added {comparison['documents_added']} new documents")
            elif comparison["documents_added"] < 0:
                comparison["changes"].append(f"Removed {abs(comparison['documents_added'])} documents")
                
            return comparison
            
        except Exception as e:
            logger.error(f"❌ Baseline comparison failed: {e}")
            return {"error": str(e)}

    async def generate_validation_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        try:
            logger.info("📊 Generating validation report...")
            
            # Perform full validation
            integrity_results = await self.validate_data_integrity()
            
            # Compare with baselines
            comparisons = {}
            for collection_type in ["players", "members", "invite_links"]:
                comparisons[collection_type] = await self.compare_with_baseline(collection_type)
            
            report = {
                "report_id": f"validation_{self.team_id}_{int(datetime.now().timestamp())}",
                "team_id": self.team_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "integrity_validation": integrity_results,
                "baseline_comparisons": comparisons,
                "summary": {
                    "overall_status": "PASS" if integrity_results.get("results", {}).get("overall_valid", False) else "FAIL",
                    "total_documents": sum([
                        integrity_results.get("counts", {}).get("players", 0),
                        integrity_results.get("counts", {}).get("members", 0),
                        integrity_results.get("counts", {}).get("invite_links", 0)
                    ]),
                    "validation_success_rate": integrity_results.get("statistics", {}).get("success_rate", 0)
                }
            }
            
            logger.info(f"✅ Validation report generated: {report['summary']['overall_status']}")
            return report
            
        except Exception as e:
            logger.error(f"❌ Failed to generate validation report: {e}")
            return {"error": str(e), "timestamp": datetime.now(timezone.utc).isoformat()}

if __name__ == "__main__":
    """Direct script execution for Firestore validation"""
    async def main():
        validator = FirestoreValidator("KTI")
        await validator.initialize()
        
        # Run validation
        report = await validator.generate_validation_report()
        print(json.dumps(report, indent=2, default=str))

    asyncio.run(main())