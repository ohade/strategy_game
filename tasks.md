# Project Tasks

Based on `prd.md`.

- [ ] **1. Define Structured Command Schema:** Finalize the JSON fields and their possible values (`mission`, `primary_goal`, `engagement`, etc.).
- [ ] **2. Build LLM Prompt:** Craft the system prompt for the LLM to ensure it outputs the correct JSON format based on the defined schema.
- [ ] **3. Implement LLM Interaction:**
    - [ ] Take player's free-text input.
    - [ ] Send input and prompt to the LLM API.
    - [ ] Receive and parse the JSON output.
- [ ] **4. Implement Basic AI Engine (MVP):**
    - [ ] Read the structured JSON plan.
    - [ ] Simulate actions via logging/printing based on the plan.
- [ ] **5. Integrate LLM Output with AI Engine:** Connect the LLM output (JSON plan) to the AI engine input.

---

## Future Enhancements

- [ ] **6. Enhance AI Engine:** Implement real game logic (physics, combat, unit control).
- [ ] **7. Expand Command Schema:** Add more fields and complexity.
- [ ] **8. Refine LLM Prompt:** Improve based on testing.
