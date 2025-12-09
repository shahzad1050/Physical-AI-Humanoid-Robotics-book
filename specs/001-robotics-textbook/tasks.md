# Tasks: Physical AI & Humanoid Robotics

**Input**: Design documents from `/specs/001-robotics-textbook/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify the existing project structure.

- [ ] T001 Verify Docusaurus project is correctly set up in `physical-ai-humanoid-robotics/`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Configure the core Docusaurus site structure.

- [ ] T002 Configure `docusaurus.config.ts` with project title, `baseUrl`, `organizationName`, and `projectName`.
- [ ] T003 Configure the navbar in `docusaurus.config.ts` for the 4 main modules.
- [ ] T004 Configure the sidebars in `sidebars.ts` for the 4 main modules.
- [ ] T005 Create placeholder markdown files for Introduction, Glossary, References, and Summary in `physical-ai-humanoid-robotics/docs/`.

---

## Phase 3: User Story 1 - Student reads a chapter (Priority: P1) 🎯 MVP

**Goal**: A student can read the content of the textbook.

**Independent Test**: Navigate to a chapter and verify the content is displayed correctly.

### Implementation for User Story 1

- [ ] T006 [P] [US1] Generate content for Module 1 chapters in `physical-ai-humanoid-robotics/docs/module1/`.
- [ ] T007 [P] [US1] Generate content for Module 2 chapters in `physical-ai-humanoid-robotics/docs/module2/`.
- [ ] T008 [P] [US1] Generate content for Module 3 chapters in `physical-ai-humanoid-robotics/docs/module3/`.
- [ ] T009 [P] [US1] Generate content for Module 4 chapters in `physical-ai-humanoid-robotics/docs/module4/`.
- [ ] T010 [P] [US1] Create diagrams for all modules using Mermaid.js.

---

## Phase 4: User Story 2 - Student completes a lab exercise (Priority: P2)

**Goal**: A student can complete the lab exercises in the textbook.

**Independent Test**: Follow a lab exercise and verify the expected outcome.

### Implementation for User Story 2

- [ ] T011 [P] [US2] Create practical labs for Module 1 in `physical-ai-humanoid-robotics/docs/module1/labs/`.
- [ ] T012 [P] [US2] Create practical labs for Module 2 in `physical-ai-humanoid-robotics/docs/module2/labs/`.
- [ ] T013 [P] [US2] Create practical labs for Module 3 in `physical-ai-humanoid-robotics/docs/module3/labs/`.
- [ ] T014 [P] [US2] Create practical labs for Module 4 in `physical-ai-humanoid-robotics/docs/module4/labs/`.
- [ ] T015 [P] [US2] Create quizzes and exercises for all modules.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final touches and deployment.

- [ ] T016 Add a GitHub Pages deployment workflow in `.github/workflows/deploy.yml`.
- [ ] T017 Run a local Docusaurus build to test for errors.
- [ ] T018 Review the entire textbook for consistency and clarity.

---

## Dependencies & Execution Order

- **Phase 1 (Setup)** must be completed first.
- **Phase 2 (Foundational)** depends on Phase 1.
- **Phase 3 (US1)** and **Phase 4 (US2)** depend on Phase 2. They can be worked on in parallel.
- **Phase 5 (Polish)** depends on the completion of all other phases.
