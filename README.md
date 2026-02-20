# FirstSelect QuickMatch - 4 Agent Python SDK

Production-oriented Python implementation of a **4-agent architecture** aligned with your Claude/Supabase workflow:

1. **RequirementFinalizationAgent** — gathers and summarizes requirements.
2. **TimekeeperAgent** — enforces <6 minute / question-budget policy.
3. **SearchRetrievalAgent** — runs deterministic 3-tier facility scoring.
4. **SupplierMatchingAgent** — formats ranked results + emits `present_matching_suppliers` payload.

## Professional folder structure

```text
src/first_select_quickmatch/
  agents/
    base.py
    requirement_agent.py
    timekeeper_agent.py
    retrieval_agent.py
    matching_agent.py
  core/
    models.py
    prompts.py
    rules.py
  db/
    matching.py
  llm.py
  orchestrator.py
migrations/
  20260220_001_supplier_facility_refactor.sql
tests/
  test_orchestrator.py
  test_rules.py
four_agent_system.py (compatibility entrypoint)
```

## Run tests

```bash
pytest -q
```

## Notes

- The matching agent **does not recompute model-generated score text**; it uses pre-scored deterministic outputs from retrieval.
- Tool payload contract emitted by matching agent:
  - `{"name": "present_matching_suppliers", "input": {"suppliers": [...]}}`
- SQL migration script includes creation/migration of `suppliers`, `facilities`, `vehicles`, `agents`, and `loads` with RLS policies and triggers.
