# Session Logging Contract

## Goal
Keep a detailed, current-session-only log from application startup until application exit.

## Retention Rule
- On every fresh app launch, `log.txt` and `logs/app.log` are recreated in write mode.
- Previous-session logs are discarded.
- The active session log remains available until the app closes.

## Required Coverage
The log should reveal:
- startup sequence
- settings snapshot
- resolved paths
- dependency and browser/tool resolution
- analyze request flow
- download request flow
- progress updates
- fallback attempts
- empty responses / failures / exceptions
- shutdown marker

## Core Files
- `log.txt` -> concise session summary log
- `logs/app.log` -> detailed trace log

## Logging Principles
- Prefer structured trace payloads over vague text.
- Record function flow, action intent, response shape, and failure point.
- Redact obviously sensitive fields such as cookies, passwords, authorization tokens.
- Keep logging focused on diagnosis, not on raw data dumping.

## EXE Relevance
This contract is a prerequisite for portable EXE work because frozen-runtime failures are usually path-, dependency-, or response-contract-related.
