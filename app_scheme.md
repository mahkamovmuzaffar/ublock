# UBlock — App Scheme & API Structure

## 1. Django Apps Architecture

### Core Apps Structure

```
ublock/
├── apps/
│   ├── users/              # User & Authentication Management
│   ├── wallets/            # Token Wallet & Holdings
│   ├── transactions/       # Transaction Records & History
│   ├── blockchain/         # Blockchain Integration & Sync
│   ├── admin_ops/          # Admin Operations & Issuance
│   ├── compliance/         # Compliance & Audit Logs
│   ├── partners/           # Partner Integration Framework
│   └── api/                # API Views & Serializers
├── templates/
├── static/
├── manage.py
└── ublock/ (config)
```

---

## 2. Apps Detailed Specification

### 2.1 `users` App
**Purpose:** User registration, authentication, profiles, and permissions

**Models:**
- `User` (extends Django User)
  - username, email, phone
  - kyc_status, kyc_verified_date
  - risk_level, created_at
  - is_active, is_locked

- `UserProfile`
  - user (FK)
  - full_name, date_of_birth
  - country, address
  - preferred_language

- `UserRole`
  - user (FK)
  - role (ADMIN, USER, PARTNER, AUDITOR)
  - permissions_set

**Key Features:**
- JWT authentication
- KYC status tracking
- Role-based access control (RBAC)
- Account locking/unlocking
- Login audit trail

---

### 2.2 `wallets` App
**Purpose:** Token wallet management and holdings

**Models:**
- `Wallet`
  - user (FK)
  - wallet_address (blockchain address)
  - balance (decimal)
  - locked_balance
  - is_active
  - created_at

- `WalletTransaction`
  - wallet (FK)
  - transaction_hash (blockchain)
  - amount
  - type (DEPOSIT, TRANSFER, WITHDRAWAL)
  - status (PENDING, CONFIRMED, FAILED)
  - timestamp

- `TokenAllocation`
  - user (FK)
  - allocation_amount
  - vesting_schedule
  - release_date
  - released_amount
  - created_date

**Key Features:**
- Multi-wallet support per user
- Balance tracking (available + locked)
- Vesting schedule management
- Wallet activation/deactivation

---

### 2.3 `transactions` App
**Purpose:** Transaction management and history

**Models:**
- `Transaction`
  - transaction_id (unique)
  - from_wallet (FK)
  - to_wallet (FK)
  - amount
  - fee
  - status (INITIATED, PENDING, CONFIRMED, FAILED, REVERSED)
  - transaction_type (TRANSFER, PAYMENT, REWARD, BURN)
  - blockchain_hash
  - timestamp
  - created_at

- `TransactionLog`
  - transaction (FK)
  - status_before, status_after
  - changed_by (user)
  - changed_at
  - notes

**Key Features:**
- Complete transaction history
- Status tracking
- Fee calculation
- Blockchain verification
- Audit trail for all changes

---

### 2.4 `blockchain` App
**Purpose:** Blockchain network interaction and synchronization

**Models:**
- `BlockchainNetwork`
  - network_name (Ethereum, Polygon, etc.)
  - chain_id
  - rpc_url
  - contract_address
  - is_active
  - created_at

- `BlockchainSync`
  - network (FK)
  - last_block_synced
  - last_sync_time
  - status (SYNCED, SYNCING, ERROR)
  - error_message

- `SmartContractEvent`
  - network (FK)
  - event_type (TRANSFER, MINT, BURN)
  - transaction_hash
  - from_address, to_address
  - amount
  - block_number
  - timestamp

**Key Features:**
- Multi-blockchain support
- Real-time event synchronization
- Smart contract interaction layer
- Gas fee tracking
- Network health monitoring

---

### 2.5 `admin_ops` App
**Purpose:** Admin operations and token issuance

**Models:**
- `IssuanceRecord`
  - admin_user (FK)
  - amount
  - recipient_wallet (FK)
  - purpose (ALLOCATION, REWARD, ADJUSTMENT)
  - timestamp
  - blockchain_confirmed
  - notes

- `OperationLog`
  - admin_user (FK)
  - operation_type (BURN, FREEZE, UNLOCK, TRANSFER)
  - target_wallet (FK)
  - amount
  - status
  - timestamp
  - approval_status (PENDING, APPROVED, REJECTED)

- `AdminApproval`
  - operation (FK)
  - approver (FK)
  - approval_date
  - notes

**Key Features:**
- Admin-only operations
- Multi-level approval workflow
- Operation auditability
- Token issuance tracking
- Compliance-ready logging

---

### 2.6 `compliance` App
**Purpose:** Compliance, audit, and risk management

**Models:**
- `ComplianceCheck`
  - user (FK)
  - check_type (KYC, AML, SANCTIONS)
  - status (PASSED, FAILED, UNDER_REVIEW)
  - checked_date
  - checked_by (FK)
  - notes

- `AuditLog`
  - action_type
  - user_involved (FK)
  - affected_model
  - affected_id
  - old_value, new_value
  - timestamp
  - ip_address

- `RiskAlert`
  - alert_type (SUSPICIOUS_ACTIVITY, LARGE_TRANSACTION, VELOCITY_CHECK)
  - user (FK)
  - severity (LOW, MEDIUM, HIGH, CRITICAL)
  - description
  - is_resolved
  - created_at
  - resolved_at

**Key Features:**
- Full audit trail
- Compliance check records
- Risk alert system
- Regulatory reporting ready
- Data privacy compliance

---

### 2.7 `partners` App
**Purpose:** Partner integration framework

**Models:**
- `Partner`
  - name
  - api_key
  - api_secret (encrypted)
  - is_active
  - integration_type (WALLET, PAYMENT, ANALYTICS)
  - created_at

- `PartnerIntegration`
  - partner (FK)
  - integration_endpoint
  - webhook_url
  - last_sync
  - is_active

- `PartnerTransaction`
  - partner (FK)
  - partner_reference_id
  - transaction (FK)
  - status

**Key Features:**
- API key management
- Secure credential storage
- Integration webhooks
- Rate limiting per partner
- Access control

---

### 2.8 `api` App
**Purpose:** REST API endpoints and serializers

**Structure:**
```
api/
├── serializers.py       # DRF Serializers
├── views.py             # API Views
├── urls.py              # URL Routing
├── permissions.py       # Custom Permissions
├── throttling.py        # Rate Limiting
└── pagination.py        # Pagination Logic
```

---

## 3. REST API Endpoints Structure

### 3.1 Authentication Endpoints
```
POST   /api/v1/auth/register/           Register new user
POST   /api/v1/auth/login/              Login (JWT token)
POST   /api/v1/auth/refresh/            Refresh token
POST   /api/v1/auth/logout/             Logout
GET    /api/v1/auth/profile/            Get user profile
PUT    /api/v1/auth/profile/            Update profile
POST   /api/v1/auth/change-password/    Change password
```

### 3.2 Wallet Endpoints
```
GET    /api/v1/wallets/                 List user wallets
POST   /api/v1/wallets/                 Create wallet
GET    /api/v1/wallets/{id}/            Get wallet details
GET    /api/v1/wallets/{id}/balance/    Get wallet balance
GET    /api/v1/wallets/{id}/holdings/   Get token holdings
POST   /api/v1/wallets/{id}/activate/   Activate wallet
POST   /api/v1/wallets/{id}/deactivate/ Deactivate wallet
```

### 3.3 Transaction Endpoints
```
GET    /api/v1/transactions/            List user transactions
POST   /api/v1/transactions/transfer/   Create transfer
GET    /api/v1/transactions/{id}/       Get transaction details
GET    /api/v1/transactions/{id}/status/ Get transaction status
POST   /api/v1/transactions/{id}/cancel/ Cancel transaction
GET    /api/v1/transactions/history/    Transaction history (paginated)
```

### 3.4 Allocation & Vesting Endpoints
```
GET    /api/v1/allocations/             List user allocations
GET    /api/v1/allocations/{id}/        Get allocation details
GET    /api/v1/allocations/{id}/vesting/ Get vesting schedule
POST   /api/v1/allocations/{id}/claim/  Claim vested tokens
```

### 3.5 Admin Endpoints
```
GET    /api/v1/admin/users/             List all users
GET    /api/v1/admin/users/{id}/        Get user details
POST   /api/v1/admin/issuance/          Issue tokens
GET    /api/v1/admin/issuance/          View issuance records
POST   /api/v1/admin/operations/        Create operation
GET    /api/v1/admin/operations/        List operations
POST   /api/v1/admin/operations/{id}/approve/   Approve operation
POST   /api/v1/admin/operations/{id}/reject/    Reject operation
```

### 3.6 Compliance & Audit Endpoints
```
GET    /api/v1/compliance/checks/       List compliance checks
POST   /api/v1/compliance/kyc/          Initiate KYC check
GET    /api/v1/compliance/kyc/{id}/     Get KYC status
GET    /api/v1/audit/logs/              View audit logs (admin only)
GET    /api/v1/compliance/alerts/       Get risk alerts (admin only)
```

### 3.7 Blockchain Endpoints
```
GET    /api/v1/blockchain/status/       Get network status
GET    /api/v1/blockchain/networks/     List supported networks
GET    /api/v1/blockchain/sync/         Get sync status
GET    /api/v1/blockchain/events/       Get blockchain events
```

### 3.8 Partner Endpoints
```
POST   /api/v1/partners/register/       Register partner
GET    /api/v1/partners/me/             Get partner info
POST   /api/v1/partners/webhook/test/   Test webhook
GET    /api/v1/partners/transactions/   View partner transactions
```

---

## 4. API Response Format

### Success Response (200, 201)
```json
{
  "success": true,
  "code": "SUCCESS",
  "message": "Operation completed successfully",
  "data": {
    "id": 1,
    "name": "John Doe"
  },
  "timestamp": "2026-04-01T10:30:00Z"
}
```

### Paginated Response
```json
{
  "success": true,
  "code": "SUCCESS",
  "data": [
    { "id": 1, "amount": 100 }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 50,
    "total_pages": 3
  },
  "timestamp": "2026-04-01T10:30:00Z"
}
```

### Error Response (400, 401, 403, 500)
```json
{
  "success": false,
  "code": "INVALID_REQUEST",
  "message": "User validation failed",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ],
  "timestamp": "2026-04-01T10:30:00Z"
}
```

---

## 5. Authentication & Authorization

### Token Strategy
- **JWT Tokens** for stateless authentication
- **Access Token**: 15 minutes validity
- **Refresh Token**: 30 days validity
- **API Keys**: For partner/third-party integrations

### Permission Levels
```
- PUBLIC:        No authentication required
- USER:          Authenticated user required
- ADMIN:         Admin role required
- AUDITOR:       Auditor role required
- PARTNER:       Partner API key required
- MULTI_APPROVE: Multiple admin approval required
```

---

## 6. Implementation Order

1. **Phase 1** (Foundation):
   - `users` app (authentication)
   - `wallets` app (wallet model)
   - Basic JWT endpoints

2. **Phase 2** (Transactions):
   - `transactions` app
   - Internal transfer logic
   - Transaction endpoints

3. **Phase 3** (Blockchain):
   - `blockchain` app
   - Smart contract integration
   - Event syncing

4. **Phase 4** (Admin & Compliance):
   - `admin_ops` app
   - `compliance` app
   - Audit logging

5. **Phase 5** (Partners):
   - `partners` app
   - Webhook integration
   - API key management

---

## 7. Database & Indexing Strategy

### Critical Indexes
```python
# Users
- email (unique)
- username (unique)

# Wallets
- user_id
- wallet_address (unique)
- is_active

# Transactions
- from_wallet_id
- to_wallet_id
- blockchain_hash (unique)
- created_at
- status

# Blockchain Events
- network_id
- transaction_hash (unique)
- block_number
```

---

## 8. Security Considerations

- ✓ JWT secret in environment variables
- ✓ Rate limiting per endpoint
- ✓ CORS configuration
- ✓ SQL injection prevention (ORM)
- ✓ Encrypted sensitive data (passwords, API secrets)
- ✓ Audit logging for all operations
- ✓ IP whitelisting for admin
- ✓ 2FA for admin users
- ✓ Input validation on all endpoints