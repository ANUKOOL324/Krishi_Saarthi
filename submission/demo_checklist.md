# KrishiSaarthi AI: Live Demo & Final Submission Checklist

This file contains the validation checklists to ensure a smooth, error-free demonstration and final submission for the Kaggle AI Agents Capstone Project.

---

## Live Demo Execution Steps

Prepare your environment before recording the presentation video or demonstrating to judges:

1.  **Environment Preparation**:
    - (Optional) Verify your `.env` contains a valid `GEMINI_API_KEY` and/or `OPENROUTER_API_KEY` (for online modes).
    - If running offline, no API keys are required.
2.  **Start the MCP Server**:
    - Open a terminal and run:
      ```bash
      python src/mcp_server.py
      ```
3.  **Start the Streamlit App**:
    - Open a second terminal and run:
      ```bash
      streamlit run app.py
      ```
4.  **Demonstrate the Flow**:
    - **Recommended for Video/Screenshots**: In the Streamlit sidebar, set **Run Mode** to `Offline Demo Mode` to guarantee absolute reliability and speed.
    - Set soil NPK dials (e.g. N=90, P=45, K=45, pH=6.2) to simulate local conditions.
    - Enter farm location (e.g. *Amritsar*, *Karnal*, or *Chikmagalur*).
    - Set primary crop of interest (e.g., *rice*, *wheat*, or *cotton*).
    - Click **Generate Plan** and watch the coordinator compile the plan.
    - Walk through the output tabs: **Weekly Farm Plan**, **Weather Risk**, **Crop Suitability**, **Market Note**, and **Safety Note**.

---

## Final Kaggle Submission Checklist

Review and check off these items before submitting your capstone entry:

- [ ] **GitHub Repository Public?**
  - Ensure the repository `ANUKOOL324/krishi-saarthi-ai` is set to **Public** so judges can view the codebase.
- [ ] **README Complete?**
  - Verify `README.md` includes the problem statement, track declaration, system flows, security checks, and future improvements.
- [ ] **API Keys & `.env` Sanitized?**
  - Verify `.env` is **NOT** committed to GitHub (listed in `.gitignore`).
  - Verify no raw API keys are hardcoded in any script files.
- [ ] **Tests Passing?**
  - Run `python -m pytest` and confirm all 8 test assertions pass cleanly with zero failures.
- [ ] **Screenshots Captured?**
  - Confirm `home_ui.png`, `agent_trace.png`, `final_report.png`, and `test_results.png` are saved inside `docs/screenshots/`.
- [ ] **Video Uploaded to YouTube?**
  - Confirm your 3-minute project walkthrough video is uploaded (can be unlisted or public) and the link is active.
- [ ] **Kaggle Writeup Submitted?**
  - Copy and format the contents of `kaggle_writeup_draft.md` into the Kaggle discussion forum or submission portal.
