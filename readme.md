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

## 14. Final Note

UBlock should be approached as a **product platform**, not only as a crypto idea.

The team must understand that success depends not only on creating a token, but on building:

- trust
- control
- security
- operational clarity
- documentation
- scalability
- real business use cases