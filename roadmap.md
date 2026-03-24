# UBlock — Step-by-Step To Do / Self-Research Roadmap

## 1. Purpose of This Document

This document is a detailed self-research and execution roadmap for the UBlock project.

Its purpose is to help the team:

- learn the topic step by step
- understand what must be researched before coding
- organize work from simple to advanced
- avoid jumping into development without product understanding
- build the project with clear structure

This is not only a task list.  
It is also a **learning path**.

Each step should be studied carefully before implementation.

---

## 2. General Working Principle

Before building any crypto product, the team must understand one important rule:

**Do not start with code first.**  
Start with understanding.

The correct order is:

1. understand the product idea
2. understand token basics
3. understand blockchain options
4. understand the role of Django
5. understand system architecture
6. design the structure
7. document the logic
8. only then begin implementation

---

## 3. Phase 1 — Understand What UBlock Actually Is

### Goal
Define the product clearly.

### Questions to research
- What is UBlock in business terms?
- Is it a utility token, payment token, reward token, or something else?
- Who will use it?
- Why do users need it?
- What problem does it solve?
- Why should this exist inside your ecosystem?
- What is the difference between UBlock and a simple balance system in a database?

### Team output
Prepare a short internal note answering:

- product purpose
- target users
- core use case
- expected value
- why tokenization is needed

### What to learn
- difference between token and coin
- difference between blockchain and backend database
- when tokenization makes sense
- when tokenization is unnecessary

---

## 4. Phase 2 — Learn Basic Crypto and Blockchain Concepts

### Goal
Build basic understanding before touching technical architecture.

### Topics to study
- what is blockchain
- what is a smart contract
- what is a token
- what is an address
- what is a wallet
- what is a private key
- what is a public key
- what is gas fee
- what is a transaction hash
- what is block confirmation
- what are token standards
- what is ERC-20
- what is EVM

### Team task
Each team member should explain these concepts in simple language.

### Expected result
The team should be able to speak about the product without using memorized words only.

### Self-check questions
- Can we explain a token to a non-technical manager?
- Can we explain why private key storage is dangerous?
- Can we explain what the blockchain does and what Django does?

---

## 5. Phase 3 — Research Existing Blockchain Options

### Goal
Choose where UBlock will live.

### Main task
Research blockchain networks suitable for token launch.

### Compare at least these areas
- Ethereum
- BNB Smart Chain
- Polygon
- other EVM-compatible options if needed

### What to compare
- ecosystem maturity
- transaction fees
- speed
- wallet support
- developer tools
- stability
- testnet availability
- exchange and ecosystem compatibility
- ease of integration from Python/Django

### Team output
Prepare a comparison table with:
- network name
- pros
- cons
- estimated complexity
- suitability for MVP

### Expected conclusion
Pick one network for MVP research.

### What to learn
- why MVP should use existing chain
- why building own chain is too heavy at first
- why EVM compatibility matters

---

## 6. Phase 4 — Research Token Standards

### Goal
Understand the contract standard before development.

### Main topics
- ERC-20 basics
- total supply
- decimals
- transfer
- approve / allowance
- mint
- burn
- pause
- ownership and access control

### Team task
Research standard token behavior and common extensions.

### Questions to answer
- what functions are mandatory in a standard token?
- should UBlock be mintable?
- should UBlock be burnable?
- should UBlock be pausable?
- should admin have special roles?
- how will supply be managed?

### Expected output
Write a short contract behavior specification.

---

## 7. Phase 5 — Define UBlock Token Logic

### Goal
Define how the token behaves inside the business.

### Research and define
- token name
- symbol
- decimals
- initial supply
- whether supply is fixed or flexible
- whether minting is allowed
- whether burning is allowed
- who controls admin rights
- whether the token is transferable by all users or limited by business rules

### Business questions
- how do users receive UBlock?
- how do users spend UBlock?
- can UBlock be withdrawn externally?
- is it internal-use only?
- can partners receive it?
- are there fees?
- is there any reward or cashback logic?

### Team output
Create a token logic document.

---

## 8. Phase 6 — Learn the Role of Django in Crypto Architecture

### Goal
Understand that Django is not the blockchain.

### Team must understand
Django should manage the platform around the token.

### Research topics
- user accounts
- API creation
- admin panel
- database design
- transaction history mirror
- blockchain service integration
- background jobs
- audit logs
- permissions
- notifications

### Critical understanding
The token contract lives on-chain.  
Django manages:
- product logic
- business operations
- admin controls
- monitoring
- integrations
- reporting

### Expected output
A written explanation:  
“What is handled by blockchain, and what is handled by Django?”

---

## 9. Phase 7 — Define System Architecture

### Goal
Create the first architecture picture.

### Research and plan
Identify the major project components.

### Suggested components
- frontend
- Django API
- PostgreSQL
- Redis
- Celery workers
- blockchain RPC connection
- smart contract
- admin dashboard
- notification service
- logging/monitoring

### Team output
Prepare:
- simple architecture diagram
- module interaction description
- data flow summary

### Key questions
- how does a user connect wallet?
- how does backend read balance?
- how are transactions synced?
- how are admin actions executed?
- how are failed transactions handled?

---

## 10. Phase 8 — Define Django App Structure

### Goal
Break the project into modules.

### Research task
Think in Django apps, not in one huge codebase.

### Suggested app structure
- `users`
- `wallets`
- `tokens`
- `ledger`
- `transactions`
- `blockchain`
- `compliance`
- `notifications`
- `audit`

### What to learn
- why modular architecture matters
- how to separate responsibilities
- how service layers help maintainability

### Team output
Create a proposed app/module map with descriptions.

---

## 11. Phase 9 — Design Database Models

### Goal
Create the first data structure draft.

### Research task
List all business entities needed.

### Minimum entities to research
- user
- wallet
- blockchain network
- token contract
- transaction
- ledger entry
- admin action
- risk flag
- notification log
- audit log

### Questions to answer
- what should be stored on-chain only?
- what should be mirrored in DB?
- what should be business-only data?
- what statuses are needed?
- what relationships exist between models?

### Expected output
Prepare model draft with fields and descriptions.

---

## 12. Phase 10 — Research Wallet Connection and Address Ownership

### Goal
Understand how user wallets are connected.

### Topics to study
- wallet address format
- wallet ownership verification
- signature-based verification
- custodial vs non-custodial model
- risks of storing private keys

### Important rule
For early stage, prefer:
- store public address
- verify ownership
- avoid unsafe private key storage in core backend

### Team output
Prepare a short note on:
- how users will connect wallets
- whether the product is custodial or non-custodial in MVP
- what security assumptions exist

---

## 13. Phase 11 — Research Smart Contract Development Flow

### Goal
Understand how a contract is built, tested, and deployed.

### Topics to learn
- Solidity basics
- contract compilation
- deployment process
- constructor parameters
- ownership
- access control
- contract verification
- testnet deployment

### Team task
Learn standard smart contract lifecycle:

1. write contract
2. test contract
3. deploy to testnet
4. verify contract
5. interact with it
6. monitor events

### Expected output
A short contract deployment flow document.

---

## 14. Phase 12 — Research Django to Blockchain Integration

### Goal
Understand how backend talks to blockchain.

### Topics to study
- RPC endpoints
- reading contract methods
- sending transactions
- event listening
- nonce handling
- transaction status tracking

### Questions
- how will Django read balances?
- how will Django send admin-triggered token operations?
- how will event logs be processed?
- how will failed chain interactions be retried?

### Team output
Prepare a blockchain integration design note.

---

## 15. Phase 13 — Background Tasks and Workers

### Goal
Understand asynchronous processes.

### Topics to study
- why background workers are needed
- Celery basics
- retries
- periodic jobs
- transaction sync jobs
- event polling
- notification tasks

### Use cases to research
- sync blockchain transactions every interval
- refresh confirmations
- send notifications after confirmed transfer
- retry failed sync operations

### Output
Prepare a list of jobs and why each one is needed.

---

## 16. Phase 14 — Internal Ledger and Reporting Logic

### Goal
Understand why on-chain data is not enough for business operations.

### Topics to research
- internal ledger purpose
- business statuses vs blockchain statuses
- reporting needs
- admin search and filtering
- reconciliation principles

### Questions
- why keep internal history if blockchain already stores transfers?
- how do we show business-friendly transaction history?
- how do we calculate product metrics?

### Output
Write a note on internal ledger necessity.

---

## 17. Phase 15 — Compliance and Risk Research

### Goal
Prepare project structure for future real-world use.

### Topics to study
- KYC
- KYB
- AML awareness
- sanctions flags
- suspicious transaction review
- transaction limits
- auditability

### Important note
Even if compliance is not fully implemented in MVP, the architecture should reserve place for it.

### Team output
Prepare a compliance-ready entity list and field list.

---

## 18. Phase 16 — Admin Panel Research

### Goal
Understand internal operational needs.

### Research questions
- what should admin see first?
- what tables are needed?
- what actions require approval?
- what filters are needed?
- what should be logged?
- what should be restricted by roles?

### Suggested admin sections
- dashboard
- users
- wallets
- token info
- transactions
- mint requests
- burn requests
- risk flags
- audit logs
- system settings

### Output
Prepare an admin dashboard feature list.

---

## 19. Phase 17 — API Design Research

### Goal
Understand what APIs will exist before coding.

### Research and define
- user APIs
- wallet APIs
- token info APIs
- balance APIs
- transaction APIs
- admin APIs

### Example API groups
- auth
- wallets
- balances
- transactions
- admin operations
- notifications

### Team output
Prepare initial API endpoint map.

---

## 20. Phase 18 — Security Research

### Goal
Identify critical security areas early.

### Topics to study
- secret management
- environment variables
- role permissions
- 2FA
- transaction signing safety
- hot wallet risks
- admin action protection
- audit trails
- secure deployment basics

### Key principle
Security is not an afterthought in crypto-related systems.

### Output
Prepare security checklist v1.

---

## 21. Phase 19 — Documentation Preparation

### Goal
Make the team document as they learn.

### Documents to prepare
- project scope
- glossary
- token logic
- architecture draft
- model draft
- API draft
- security notes
- deployment notes
- open questions register

### Rule
Every researched topic should end with a short written conclusion.

---

## 22. Phase 20 — Define MVP

### Goal
Cut the project into realistic first release scope.

### MVP should likely include
- chosen network
- chosen token model
- base smart contract
- Django project structure
- user auth
- wallet address linking
- token metadata
- balance reading
- transaction sync draft
- admin monitoring basics
- documentation package

### MVP should likely exclude
- public trading
- large tokenomics complexity
- cross-chain mechanics
- exchange integration
- advanced DeFi
- complex staking

### Output
Prepare MVP boundary document.

---

## 23. Final Research Deliverables

Before coding starts, the team should ideally finish these deliverables:

### Product
- product purpose note
- target user note
- token use case note

### Technical
- blockchain comparison
- token standard research
- architecture draft
- Django module draft
- data model draft
- API map draft

### Operational
- compliance note
- security note
- admin operations note
- background task note

### Planning
- MVP scope
- phased roadmap
- open questions list

---

## 24. Recommended Working Style for Team

Each topic should be worked in this format:

### Step 1
Read basic materials

### Step 2
Write short summary in your own words

### Step 3
Explain it to the team simply

### Step 4
Document final conclusion

### Step 5
Only then move to implementation planning

This project should not be approached as copy-paste development.  
It should be approached as a structured product build.

---

## 25. Suggested Final Execution Sequence

Recommended order of work:

1. define product purpose
2. learn blockchain basics
3. compare networks
4. study token standards
5. define token logic
6. define Django role
7. prepare architecture draft
8. define modules
9. design models
10. design APIs
11. study wallet connection flow
12. study smart contract flow
13. study backend-chain integration
14. define background jobs
15. define admin logic
16. define compliance placeholders
17. prepare documentation
18. define MVP
19. assign development tasks
20. start implementation

---

## 26. Final Note

The main objective of this roadmap is not only to “finish tasks”.

It is to ensure the team truly understands:

- what they are building
- why they are building it
- how the system should work
- what risks exist
- what must be researched before development

A strong crypto project starts from:
- clarity
- documentation
- architecture thinking
- controlled implementation

Not from writing code too early.