# Security

## Reporting

Please report suspected security issues privately to the repository owner instead of opening a public issue.

## Skill security model

This repository is an agent skill package. It gives an agent instructions and optional local scripts; it should not request secrets, exfiltrate data, alter credentials, or run privileged commands.

Security-sensitive changes include:

- new scripts or executable files
- instructions that ask an agent to ignore user, system, or repository rules
- hidden or bidirectional Unicode controls
- network calls that are not required for WebGL2 documentation or validation
- any command that reads environment secrets or credential files

The validator checks for required files, schema drift, placeholder content, hidden Unicode controls, and packaging consistency. Human review is still required for natural-language instructions because prompt-level behavior can be subtle.
