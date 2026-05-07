# UBlock — Project Scope

## 1. Project Overview

**UBlock** is a crypto-based digital asset project built around a tokenized ecosystem, with Django as the main backend platform for business logic, user management, transaction monitoring, admin operations, and integrations.

At the first stage, UBlock is not intended to become a fully independent blockchain.  
Instead, it should be launched as a **token on an existing blockchain network**, while Django manages the operational, financial, and product-side infrastructure around it.

The project should be designed as a foundation for future expansion into:

- wallet services
- internal transfers
- partner integrations
- token utility scenarios
- rewards and loyalty logic
- payment scenarios
- admin monitoring and compliance tools

---

## 2. Main Goal

The main goal of UBlock is to create a controlled and scalable token ecosystem where:

- users can interact with the token through web/mobile products
- the business can track all token-related activity
- admin users can manage issuance and operations
- partners can later integrate token-related functionality
- compliance, audit, and operational visibility exist from the beginning

---

## 3. Product Vision

UBlock should become a structured token platform, not only a smart contract.

The smart contract is only one part of the system.  
The full product includes:

- token smart contract
- backend platform in Django
- admin dashboard
- user and wallet relations
- blockchain interaction service
- transaction synchronization
- compliance and risk controls
- documentation and operational processes

---

## 4. First Version Philosophy

The first version should focus on practicality and controlled launch.

That means:

- do not create your own blockchain from scratch
- do not start with mining, validators, or custom consensus
- do not overcomplicate tokenomics in phase 1
- do not build an exchange first
- do not store sensitive secrets unsafely

The first version should instead focus on:

- a standard token contract
- a Django backend
- clean architecture
- transaction traceability
- admin control
- operational readiness
- documentation

---

## 5. Suggested Initial Product Type

For MVP, UBlock should be treated as one of the following:

### Option A — Utility Token
Used inside your ecosystem for access, fees, discounts, rewards, or internal usage.

### Option B — Loyalty / Reward Token
Used to reward users, partners, or ecosystem participants.

### Option C — Payment Token Inside Ecosystem
Used as a controlled payment instrument within your own services.

The easiest and safest starting point is:

**Utility + Reward + Internal Ecosystem Usage**

This is more realistic than trying to launch a public unrestricted crypto model from day one.

---

## 6. Technical Scope

### Backend
Main backend should be built in **Django**.

Backend responsibilities:

- user management
- authentication and authorization
- wallet linking and ownership records
- token metadata storage
- transaction history mirror
- admin actions
- blockchain integration
- background jobs
- notification flows
- audit logging
- compliance support

### API Layer
The project should expose APIs for:

- frontend web app
- mobile app
- admin dashboard
- future partner integrations

### Blockchain Layer
The blockchain layer should handle:

- token smart contract deployment
- balance reading
- transfer monitoring
- mint/burn operations if needed
- transaction confirmation tracking
- event listening

### Database Layer
The database should serve as the operational source of truth for product logic, even though blockchain remains the final settlement layer.

---

## 7. Functional Scope

### 7.1 User Management
The system should support:

- registration
- login
- profile
- roles
- permissions
- 2FA later
- account status management

### 7.2 Wallet Management
The system should support:

- linking blockchain wallet addresses
- storing public wallet metadata
- marking verified wallets
- assigning wallets to users
- tracking supported networks

### 7.3 Token Management
The system should support:

- token information
- symbol
- decimals
- contract address
- network information
- token status
- supply-related metadata

### 7.4 Transaction Monitoring
The system should support:

- incoming transaction sync
- outgoing transaction sync
- status tracking
- transaction type classification
- block number tracking
- transaction hash storage
- confirmations count
- failure handling

### 7.5 Internal Ledger
Even though transactions exist on-chain, the project should also maintain an internal business ledger for:

- reporting
- analytics
- operational tracing
- fee calculation
- admin review
- dispute handling

### 7.6 Admin Operations
The admin side should support:

- token overview
- user overview
- transaction monitoring
- manual review tools
- mint request approval if applicable
- burn request approval if applicable
- pause/emergency controls if business model requires them
- logs and audit trail

### 7.7 Compliance and Risk
The project should be designed with future compliance in mind.

This includes:

- KYC/KYB status fields
- sanctions/risk flags
- suspicious activity review
- transaction thresholds
- address blacklisting internally
- audit history

### 7.8 Notifications
The system should later support:

- email notifications
- push notifications
- Telegram/admin alerts
- webhook callbacks for integrations

---

## 8. Non-Functional Scope

The project should also include attention to the following:

### Security
- secure authentication
- environment variable protection
- safe signing architecture
- no plain private key storage
- permission control
- admin action logging

### Scalability
- modular Django apps
- reusable service layer
- background workers
- structured models
- API versioning strategy later if needed

### Auditability
- every critical action should be traceable
- admin actions should be logged
- important financial operations should be reviewable

### Reliability
- retry mechanisms
- background task monitoring
- error logging
- status tracking
- chain sync monitoring

### Documentation
The project must be documented from day one:
- technical documentation
- API documentation
- operational documentation
- deployment notes
- research notes

---

## 9. Suggested Architecture Modules

Recommended Django apps/modules:

- `users`
- `wallets`
- `tokens`
- `ledger`
- `blockchain`
- `transactions`
- `compliance`
- `notifications`
- `audit`
- `admin_ops`

This structure can be adjusted later, but modular separation is important from the beginning.

---

## 10. Out of Scope for MVP

The following should be considered out of scope for version 1:

- building an independent blockchain
- mining infrastructure
- validator nodes
- public exchange platform
- advanced DeFi features
- cross-chain bridges
- staking system
- complex tokenomics engine
- NFT integration
- large-scale public token sale mechanics

These can be considered only after core platform maturity.

---

## 11. Expected Deliverables

At minimum, the project should produce:

- smart contract concept
- Django backend architecture
- database model draft
- API endpoint draft
- admin workflow description
- background job plan
- compliance-ready model structure
- README and documentation files
- phased implementation plan

---

## 12. Success Criteria for Phase 1

Phase 1 can be considered successful if the team can demonstrate:

- clear understanding of token architecture
- selected blockchain/network approach
- documented backend structure
- draft data models
- draft API map
- smart contract research completion
- operational flow understanding
- risk and compliance awareness
- development roadmap readiness

---

## 13. Long-Term Expansion Possibilities

After MVP, UBlock may expand into:

- ecosystem wallet integration
- internal merchant payments
- partner distribution
- cashback/reward engine
- cross-border utility
- B2B tokenized settlement use cases
- treasury tools
- business dashboard for token analytics
- mobile wallet app
- token-powered loyalty system
- limited stable-value scenarios if legally and operationally justified

---

## 14. Wallet API Reference

All endpoints require authentication (session or token). Base path: `/api/wallet/`

---

### 14.1 Wallet Management

#### List Wallets
```
GET /api/wallet/
```
Returns all active wallets for the authenticated user.

**Response**
```json
{
  "success": true,
  "count": 2,
  "wallets": [
    {
      "id": 1,
      "wallet_address": "0xAbC...",
      "network": "ethereum",
      "label": "Main wallet",
      "description": null,
      "balance": "1.234500000000000000",
      "available_balance": "1.234500000000000000",
      "locked_balance": "0",
      "is_verified": true,
      "is_active": true,
      "created_at": "2026-05-01T10:00:00Z"
    }
  ]
}
```

---

#### Create Wallet
```
POST /api/wallet/create/
```

**Body**
```json
{
  "wallet_address": "0xAbC...",
  "network": "ethereum",
  "label": "My Wallet",
  "description": "Optional description"
}
```

**Response** `201`
```json
{
  "success": true,
  "wallet": { "id": 1, "wallet_address": "0xAbC...", "..." }
}
```

---

#### Get Wallet
```
GET /api/wallet/<wallet_id>/
```

---

#### Update Wallet
```
PUT /api/wallet/<wallet_id>/update/
```

**Body** — only `label` and `description` are updatable.
```json
{
  "label": "New label",
  "description": "Updated description"
}
```

---

#### Delete Wallet
```
DELETE /api/wallet/<wallet_id>/delete/
```
Soft-deletes the wallet (`is_active = false`).

---

### 14.2 Wallet Verification

Proves ownership of a wallet address via message signing (two-step).

#### Step 1 — Request challenge
```
POST /api/wallet/<wallet_id>/verify/
```
```json
{ "action": "request_challenge", "wallet_address": "0xAbC..." }
```
**Response**
```json
{ "success": true, "challenge": "Verify wallet ownership - a3f9...", "expires_in": 900 }
```

#### Step 2 — Submit signature
```
POST /api/wallet/<wallet_id>/verify/
```
```json
{
  "action": "verify_signature",
  "wallet_address": "0xAbC...",
  "signature": "0x..."
}
```
**Response**
```json
{ "success": true, "message": "Wallet verified successfully", "wallet": { "..." } }
```

---

### 14.3 Wallet Balance

Fetches the native coin balance live from the blockchain and updates the cached value.

```
GET /api/wallet/<wallet_id>/balance/
```

**Response**
```json
{
  "success": true,
  "wallet_address": "0xAbC...",
  "network": "ethereum",
  "balance": "1.234500000000000000",
  "balance_wei": "1234500000000000000",
  "symbol": "ETH",
  "last_updated": "2026-05-07T12:00:00Z"
}
```

---

### 14.4 Transaction History

Returns paginated transaction history fetched from the block explorer API.

```
GET /api/wallet/<wallet_id>/transactions/?page=1&page_size=10
```

**Response**
```json
{
  "success": true,
  "wallet_address": "0xAbC...",
  "network": "ethereum",
  "page": 1,
  "page_size": 10,
  "count": 10,
  "transactions": [
    {
      "hash": "0x...",
      "block_number": "19000000",
      "timestamp": "2026-05-07T11:00:00Z",
      "from": "0x...",
      "to": "0xAbC...",
      "value": "0.5",
      "value_wei": "500000000000000000",
      "gas": "21000",
      "gas_used": "21000",
      "gas_price": "20000000000",
      "is_error": false,
      "direction": "incoming",
      "confirmations": "120"
    }
  ]
}
```

---

### 14.5 Supported Networks

```
GET /api/wallet/networks/
```
No authentication required.

**Response**
```json
{
  "success": true,
  "count": 5,
  "networks": [
    { "id": "ethereum", "name": "Ethereum", "symbol": "ETH", "chain_id": 1,
      "explorer_url": "https://etherscan.io", "rpc_url": "https://mainnet.infura.io/v3/" },
    { "id": "polygon",  "name": "Polygon",  "symbol": "MATIC", "chain_id": 137, "..." },
    { "id": "bsc",      "name": "BNB Smart Chain", "symbol": "BNB", "chain_id": 56, "..." },
    { "id": "arbitrum", "name": "Arbitrum One", "symbol": "ETH", "chain_id": 42161, "..." },
    { "id": "optimism", "name": "Optimism", "symbol": "ETH", "chain_id": 10, "..." }
  ]
}
```

---

### 14.6 Token Registry

Shared registry of known ERC-20 tokens across all users.

#### List Tokens
```
GET /api/wallet/tokens/
GET /api/wallet/tokens/?network=ethereum
```

**Response**
```json
{
  "success": true,
  "count": 1,
  "tokens": [
    {
      "id": 1,
      "contract_address": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
      "symbol": "USDT",
      "name": "Tether USD",
      "decimals": 6,
      "network": "ethereum",
      "logo_url": null,
      "coingecko_id": "tether",
      "is_verified": true,
      "created_at": "2026-05-01T10:00:00Z"
    }
  ]
}
```

#### Get Token
```
GET /api/wallet/tokens/<token_id>/
```

---

### 14.7 Wallet Token Management

Each wallet independently tracks a set of ERC-20 tokens with cached balances.

#### List Tracked Tokens
```
GET /api/wallet/<wallet_id>/tokens/
```
Returns all tokens tracked by the wallet, including cached balance and USD value.

**Response**
```json
{
  "success": true,
  "count": 1,
  "tokens": [
    {
      "id": 1,
      "contract_address": "0xdAC17...",
      "symbol": "USDT",
      "name": "Tether USD",
      "decimals": 6,
      "network": "ethereum",
      "logo_url": null,
      "coingecko_id": "tether",
      "is_verified": true,
      "created_at": "2026-05-01T10:00:00Z",
      "balance": "250.000000",
      "balance_usd": "250.00",
      "last_synced_at": "2026-05-07T12:00:00Z"
    }
  ]
}
```

---

#### Add Token to Wallet
```
POST /api/wallet/<wallet_id>/tokens/add/
```
If the token is not yet in the registry, its symbol and decimals are read directly from the smart contract on-chain.

**Body**
```json
{
  "contract_address": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
  "network": "ethereum",
  "name": "Tether USD"
}
```
`network` defaults to the wallet's network. `name` is optional — falls back to on-chain symbol.

**Response** `201`
```json
{
  "success": true,
  "message": "Token added to wallet",
  "token": { "id": 1, "symbol": "USDT", "decimals": 6, "..." }
}
```

**Error cases**

| Status | Reason |
|--------|--------|
| 400 | Missing or invalid `contract_address` |
| 400 | Token already tracked for this wallet |
| 400 | Unsupported network |
| 502 | Failed to read metadata from chain |

---

#### Remove Token from Wallet
```
DELETE /api/wallet/<wallet_id>/tokens/<token_id>/remove/
```
Removes the tracking record. The token entry in the registry is kept.

**Response**
```json
{ "success": true, "message": "Token removed from wallet" }
```

---

#### Sync Token Balance
```
POST /api/wallet/<wallet_id>/tokens/<token_id>/sync/
```
Fetches the live on-chain balance and current USD price from CoinGecko, then updates the cached values.

**Response**
```json
{
  "success": true,
  "token_id": 1,
  "balance": "250.000000",
  "balance_usd": "250.00",
  "last_synced_at": "2026-05-07T12:05:00Z"
}
```

---

## 15. Final Note

UBlock should be approached as a **product platform**, not only as a crypto idea.

The team must understand that success depends not only on creating a token, but on building:

- trust
- control
- security
- operational clarity
- documentation
- scalability
- real business use cases