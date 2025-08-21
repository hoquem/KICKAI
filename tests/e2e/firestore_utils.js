/**
 * Firestore Utilities for E2E Testing
 * 
 * Provides specialized functions for validating KICKAI database operations
 * during end-to-end testing with real Firestore integration.
 */

const { getFirestore } = require('firebase-admin/firestore');

class FirestoreTestUtils {
    constructor(db = null) {
        this.db = db || getFirestore();
        this.createdRecords = [];
    }

    /**
     * Track a record for cleanup
     */
    trackRecord(collection, id) {
        this.createdRecords.push({ collection, id });
        console.log(`📝 Tracking record for cleanup: ${collection}/${id}`);
    }

    /**
     * Validate player record creation
     */
    async validatePlayerCreated(phone, expectedData = {}) {
        console.log(`🏃‍♂️ Validating player creation for phone: ${phone}`);
        
        try {
            const snapshot = await this.db
                .collection('kickai_players')
                .where('phone', '==', phone)
                .get();
            
            if (snapshot.empty) {
                console.error(`❌ Player not found with phone: ${phone}`);
                return null;
            }
            
            const doc = snapshot.docs[0];
            const data = doc.data();
            this.trackRecord('kickai_players', doc.id);
            
            // Validate expected fields
            const validations = {
                phone_match: data.phone === phone,
                has_name: !!data.name,
                has_player_id: !!data.player_id,
                has_team_id: !!data.team_id,
                has_status: !!data.status,
                has_created_at: !!data.created_at,
                ...this.validateExpectedFields(data, expectedData)
            };
            
            const allValid = Object.values(validations).every(v => v);
            
            if (allValid) {
                console.log(`✅ Player validated: ${data.name} (${data.player_id})`);
            } else {
                console.error('❌ Player validation failed:', validations);
            }
            
            return {
                id: doc.id,
                data,
                validations,
                valid: allValid
            };
            
        } catch (error) {
            console.error(`❌ Player validation error: ${error.message}`);
            return null;
        }
    }

    /**
     * Validate team member record creation
     */
    async validateTeamMemberCreated(phone, expectedData = {}) {
        console.log(`👔 Validating team member creation for phone: ${phone}`);
        
        try {
            const snapshot = await this.db
                .collection('kickai_team_members')
                .where('phone_number', '==', phone)
                .get();
            
            if (snapshot.empty) {
                console.error(`❌ Team member not found with phone: ${phone}`);
                return null;
            }
            
            const doc = snapshot.docs[0];
            const data = doc.data();
            this.trackRecord('kickai_team_members', doc.id);
            
            // Validate expected fields
            const validations = {
                phone_match: data.phone_number === phone,
                has_name: !!data.name,
                has_member_id: !!data.member_id,
                has_team_id: !!data.team_id,
                has_role: !!data.role,
                has_status: !!data.status,
                has_created_at: !!data.created_at,
                ...this.validateExpectedFields(data, expectedData)
            };
            
            const allValid = Object.values(validations).every(v => v);
            
            if (allValid) {
                console.log(`✅ Team member validated: ${data.name} (${data.member_id})`);
            } else {
                console.error('❌ Team member validation failed:', validations);
            }
            
            return {
                id: doc.id,
                data,
                validations,
                valid: allValid
            };
            
        } catch (error) {
            console.error(`❌ Team member validation error: ${error.message}`);
            return null;
        }
    }

    /**
     * Validate invite link record creation
     */
    async validateInviteLinkCreated(inviteId, expectedData = {}) {
        console.log(`🔗 Validating invite link creation for ID: ${inviteId}`);
        
        try {
            const snapshot = await this.db
                .collection('kickai_invite_links')
                .where('invite_id', '==', inviteId)
                .get();
            
            if (snapshot.empty) {
                console.error(`❌ Invite link not found with ID: ${inviteId}`);
                return null;
            }
            
            const doc = snapshot.docs[0];
            const data = doc.data();
            this.trackRecord('kickai_invite_links', doc.id);
            
            // Validate expected fields
            const validations = {
                invite_id_match: data.invite_id === inviteId,
                has_invite_link: !!data.invite_link,
                has_team_id: !!data.team_id,
                has_invite_type: !!data.invite_type,
                has_created_at: !!data.created_at,
                has_expires_at: !!data.expires_at,
                not_used: !data.used_at, // Should be unused initially
                ...this.validateExpectedFields(data, expectedData)
            };
            
            const allValid = Object.values(validations).every(v => v);
            
            if (allValid) {
                console.log(`✅ Invite link validated: ${data.invite_type} for ${data.team_id}`);
            } else {
                console.error('❌ Invite link validation failed:', validations);
            }
            
            return {
                id: doc.id,
                data,
                validations,
                valid: allValid
            };
            
        } catch (error) {
            console.error(`❌ Invite link validation error: ${error.message}`);
            return null;
        }
    }

    /**
     * Validate field update in any collection
     */
    async validateFieldUpdate(collection, conditions, field, expectedValue) {
        console.log(`🔄 Validating field update: ${collection}.${field} = ${expectedValue}`);
        
        try {
            let query = this.db.collection(collection);
            
            // Apply conditions
            for (const [condField, condValue] of Object.entries(conditions)) {
                query = query.where(condField, '==', condValue);
            }
            
            const snapshot = await query.get();
            
            if (snapshot.empty) {
                console.error(`❌ No records found in ${collection} matching conditions:`, conditions);
                return null;
            }
            
            const doc = snapshot.docs[0];
            const data = doc.data();
            const actualValue = data[field];
            
            const isMatch = actualValue === expectedValue;
            
            if (isMatch) {
                console.log(`✅ Field update validated: ${field} = ${actualValue}`);
            } else {
                console.error(`❌ Field update mismatch: expected ${expectedValue}, got ${actualValue}`);
            }
            
            return {
                id: doc.id,
                data,
                field,
                expectedValue,
                actualValue,
                valid: isMatch
            };
            
        } catch (error) {
            console.error(`❌ Field update validation error: ${error.message}`);
            return null;
        }
    }

    /**
     * Validate record status change
     */
    async validateStatusChange(collection, conditions, expectedStatus) {
        console.log(`📊 Validating status change to: ${expectedStatus}`);
        
        return await this.validateFieldUpdate(collection, conditions, 'status', expectedStatus);
    }

    /**
     * Validate invite link usage
     */
    async validateInviteLinkUsed(inviteId) {
        console.log(`🔗 Validating invite link usage: ${inviteId}`);
        
        try {
            const snapshot = await this.db
                .collection('kickai_invite_links')
                .where('invite_id', '==', inviteId)
                .get();
            
            if (snapshot.empty) {
                console.error(`❌ Invite link not found: ${inviteId}`);
                return null;
            }
            
            const doc = snapshot.docs[0];
            const data = doc.data();
            
            const validations = {
                has_used_at: !!data.used_at,
                has_used_by: !!data.used_by,
                used_timestamp_valid: data.used_at ? new Date(data.used_at.toDate()) <= new Date() : false
            };
            
            const allValid = Object.values(validations).every(v => v);
            
            if (allValid) {
                console.log(`✅ Invite link usage validated: used by ${data.used_by} at ${data.used_at?.toDate()}`);
            } else {
                console.error('❌ Invite link usage validation failed:', validations);
            }
            
            return {
                id: doc.id,
                data,
                validations,
                valid: allValid
            };
            
        } catch (error) {
            console.error(`❌ Invite link usage validation error: ${error.message}`);
            return null;
        }
    }

    /**
     * Validate cross-entity synchronization
     */
    async validateCrossEntitySync(playerPhone, teamMemberPhone, syncField) {
        console.log(`🔄 Validating cross-entity sync for field: ${syncField}`);
        
        try {
            // Get player record
            const playerSnapshot = await this.db
                .collection('kickai_players')
                .where('phone', '==', playerPhone)
                .get();
            
            // Get team member record
            const memberSnapshot = await this.db
                .collection('kickai_team_members')
                .where('phone_number', '==', teamMemberPhone)
                .get();
            
            if (playerSnapshot.empty || memberSnapshot.empty) {
                console.error('❌ One or both records not found for cross-entity sync validation');
                return null;
            }
            
            const playerData = playerSnapshot.docs[0].data();
            const memberData = memberSnapshot.docs[0].data();
            
            // Map fields between entities (some fields have different names)
            const fieldMapping = {
                phone: 'phone_number',
                email: 'email',
                emergency_contact_name: 'emergency_contact_name',
                emergency_contact_phone: 'emergency_contact_phone'
            };
            
            const playerField = syncField;
            const memberField = fieldMapping[syncField] || syncField;
            
            const playerValue = playerData[playerField];
            const memberValue = memberData[memberField];
            
            const isSynced = playerValue === memberValue;
            
            if (isSynced) {
                console.log(`✅ Cross-entity sync validated: ${syncField} = ${playerValue}`);
            } else {
                console.error(`❌ Cross-entity sync mismatch: player.${playerField}=${playerValue}, member.${memberField}=${memberValue}`);
            }
            
            return {
                playerData,
                memberData,
                syncField,
                playerValue,
                memberValue,
                synced: isSynced
            };
            
        } catch (error) {
            console.error(`❌ Cross-entity sync validation error: ${error.message}`);
            return null;
        }
    }

    /**
     * Check for duplicate records
     */
    async checkDuplicatesPrevented(collection, field, value) {
        console.log(`🔍 Checking duplicate prevention in ${collection}.${field} = ${value}`);
        
        try {
            const snapshot = await this.db
                .collection(collection)
                .where(field, '==', value)
                .get();
            
            const count = snapshot.size;
            const noDuplicates = count <= 1;
            
            if (noDuplicates) {
                console.log(`✅ No duplicates found: ${count} record(s) with ${field} = ${value}`);
            } else {
                console.error(`❌ Duplicates detected: ${count} records with ${field} = ${value}`);
            }
            
            return {
                collection,
                field,
                value,
                count,
                noDuplicates
            };
            
        } catch (error) {
            console.error(`❌ Duplicate check error: ${error.message}`);
            return null;
        }
    }

    /**
     * Validate expected fields against actual data
     */
    validateExpectedFields(actualData, expectedData) {
        const validations = {};
        
        for (const [field, expectedValue] of Object.entries(expectedData)) {
            const actualValue = actualData[field];
            const key = `${field}_match`;
            validations[key] = actualValue === expectedValue;
            
            if (validations[key]) {
                console.log(`   ✓ ${field}: ${actualValue}`);
            } else {
                console.log(`   ✗ ${field}: expected ${expectedValue}, got ${actualValue}`);
            }
        }
        
        return validations;
    }

    /**
     * Clean up all tracked records
     */
    async cleanup() {
        if (this.createdRecords.length === 0) {
            console.log('ℹ️ No records to clean up');
            return;
        }
        
        console.log(`🧹 Cleaning up ${this.createdRecords.length} test records...`);
        
        try {
            const batch = this.db.batch();
            
            for (const record of this.createdRecords) {
                const docRef = this.db.collection(record.collection).doc(record.id);
                batch.delete(docRef);
                console.log(`   🗑️ Queuing deletion: ${record.collection}/${record.id}`);
            }
            
            await batch.commit();
            console.log(`✅ Successfully cleaned up ${this.createdRecords.length} records`);
            
            this.createdRecords = [];
            
        } catch (error) {
            console.error('❌ Cleanup failed:', error);
            throw error;
        }
    }

    /**
     * Get cleanup summary
     */
    getCleanupSummary() {
        const summary = {
            totalRecords: this.createdRecords.length,
            collections: {}
        };
        
        for (const record of this.createdRecords) {
            if (!summary.collections[record.collection]) {
                summary.collections[record.collection] = 0;
            }
            summary.collections[record.collection]++;
        }
        
        return summary;
    }
}

module.exports = FirestoreTestUtils;