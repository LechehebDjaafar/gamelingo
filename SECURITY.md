# Security Policy

GameLingo runs local scripts on files the user points it at. Please report vulnerabilities (path traversal, unsafe file writes, command execution) **privately** via GitHub Security Advisories ("Report a vulnerability" in the Security tab) rather than a public issue.

Design principles: scripts never overwrite sources, reject `..`/absolute paths in backup manifests, and never download or execute binaries. Skills must never instruct bypassing DRM, anti-cheat or licensing.
