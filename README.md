# fde-agent

A terminal-based Forward Deployed Engineer agent that does the analysis an FDE does on a client engagement. It takes a stakeholder survey, maps the workflow as it actually runs, finds bottlenecks (time per step, handoffs, rework), checks data quality across ERP/CRM/DB systems, and tracks outcome metrics (call-handling time, NPS, first-contact resolution) against a baseline. It's local-first: a small local model through Ollama, a human approval step before any decision with real consequences, and every step logged. The example domain is residential HVAC service calls. **Status:** early. The repo currently has a Python skeleton and CI; the agent is built in phases.

## License

[MIT](LICENSE)
