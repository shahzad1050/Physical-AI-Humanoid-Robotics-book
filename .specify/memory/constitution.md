<!-- Sync Impact Report:
Version change: 0.0.0 -> 1.0.0 (MAJOR: Initial creation)
Modified principles: N/A (new)
Added sections: Core Principles, Book Requirements & Technologies, Mandatory Behavior Rules & Development Guidelines, Governance
Removed sections: N/A
Templates requiring updates:
- .specify/templates/plan-template.md: ✅ updated
- .specify/templates/spec-template.md: ✅ updated
- .specify/templates/tasks-template.md: ✅ updated
- .specify/templates/commands/*.md: ✅ updated
Follow-up TODOs: N/A
-->
# Physical AI & Humanoid Robotics Constitution

## Core Principles

### I. Introduction to Physical AI
Foundations of embodied intelligence; transition from digital AI to robots that understand physical laws; humanoid robotics landscape; sensors: LIDAR, cameras, IMUs, F/T sensors.

### II. ROS 2 Fundamentals
ROS 2 architecture; nodes, topics, services, actions; ROS 2 packages with Python; launch files & parameter management.

### III. Robot Simulation with Gazebo
Environment setup; URDF & SDF formats; physics & sensor simulation; Unity for robot visualization.

### IV. NVIDIA Isaac Platform
Isaac SDK + Isaac Sim; AI perception and manipulation; reinforcement learning for control; sim-to-real transfer techniques.

### V. Humanoid Robot Development
Kinematics & dynamics; bipedal locomotion & balance; manipulation & grasping; human-robot interaction design.

## Book Requirements & Technologies

The system MUST produce a complete Docusaurus textbook with clear module-based chapters, code examples, diagrams (Auto-generated or using Mermaid.js), ROS 2, Gazebo, Unity, and Isaac tutorials. The textbook MUST be structured for deployment on GitHub Pages via Docusaurus.

Technologies covered include: ROS 2, Gazebo, Unity, NVIDIA Isaac SDK & Isaac Sim, and GPT-based conversational robotics.

## Mandatory Behavior Rules & Development Guidelines

Always follow Spec-Kit-Plus format.
Always generate files in correct Docusaurus structure.
Always produce consistent navigation & sidebar configs.
Never omit weekly content.
Never break global theme of “Physical AI & Humanoid Robotics.”
The book MUST be created as a fully working Docusaurus project.

## Governance

This constitution supersedes all other practices. Amendments require documentation, approval, and a migration plan. All PRs/reviews MUST verify compliance. Complexity MUST be justified. The book MUST be created as a fully working Docusaurus project and deployed on GitHub Pages.

**Version**: 1.0.0 | **Ratified**: 2025-12-07 | **Last Amended**: 2025-12-07
