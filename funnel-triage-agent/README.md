# Funnel Triage Agent

**Option 2 — Build Challenge | Manager, Revenue Technology**

A working AI agent that takes a CSV of 10–20 open B2B SaaS deals and returns a prioritized triage with reasoning, risk flags, and suggested next actions for each deal.

**Live URL:** [Streamlit Cloud Deployment](https://funnel-triage-agent.streamlit.app)

---

## How to Use

1. Open the live URL above
2. Upload the included `mock_opportunities.csv` (or any pipeline CSV with similar columns)
3. Click "Run Triage Analysis"
4. Review the prioritized deal cards with scores, reasoning, and next actions
5. Use the tier filter to focus on Critical/High priority deals

---

## Technical README

### LLM Choice: Llama 3.3 70B (via Groq)

**Why Llama 3.3 70B on Groq:**
- Free inference with generous rate limits (30 req/min, 131k context)
- Excellent structured JSON output via native `response_format: json_object`
- 70B parameter model delivers strong multi-criteria reasoning
- Sub-second inference speed via Groq's LPU hardware
- No billing required — zero cost for prototype and evaluation

**Alternatives considered:**
- **GPT-4o-mini (OpenAI)**: Best-in-class for structured output, but requires paid API credits. Would be the production choice.
- **GPT-4o**: Overkill for this task — 10x more expensive than GPT-4o-mini with marginal quality gain on structured scoring
- **Claude 3.5 Sonnet**: Excellent reasoning but no native JSON mode enforcement; needs more prompt engineering for output reliability
- **Gemini 1.5 Flash**: Free tier exists but quota limits are inconsistent across regions/projects
- **Self-hosted open-source**: Would require infrastructure, defeating the "ship fast" goal

### System Prompt Design

The system prompt encodes:

1. **Role framing** — "You are a Funnel Triage Agent for a B2B SaaS sales team"
2. **Weighted scoring rubric** — 9 criteria with explicit weights:
   - Close Date Proximity (15%)
   - Deal Stage advancement (15%)
   - Decision Maker Involvement (12%)
   - ACV magnitude (12%)
   - Intent Timing (12%) — Immediate > Q3 > Q4
   - Pain Point Addressal (12%) — Does our product solve their problem?
   - Last Activity Recency (8%)
   - ICP Fit (7%)
   - Risk Level (7%)
3. **Exact output schema** — JSON structure with field-level specifications
4. **Critical rules** — Anti-hallucination constraints baked into the prompt
5. **Priority tier definitions** — Critical (80-100), High (60-79), Medium (40-59), Low (1-39)

Full system prompt is in `agent.py` — approximately 60 lines of structured instructions.

### Evaluation Methodology

1. **Schema validation**: Verified output JSON matches expected structure across 5 runs
2. **Name matching**: Post-processing confirms every `opportunity_name` in output exists in input CSV — any hallucinated deal names are filtered out
3. **Score consistency**: Ran the same CSV 3x — scores varied ≤5 points (temperature=0.2)
4. **Ranking sanity checks**: Manually verified that:
   - Negotiation-stage deals with high ACV rank above Discovery-stage deals
   - Stalled deals with no DM involvement rank lowest
   - Deals with immediate timing + active status rank highest
   - Pain point addressal = "Yes" boosts score vs "Partial" or "No"
5. **Edge cases tested**: Empty CSV, single deal, 20 deals, missing columns (graceful error)

### Hallucination Guardrails

| Guardrail | Implementation |
|-----------|---------------|
| Data isolation | Model receives ONLY the uploaded CSV data — no external knowledge used for deal facts |
| JSON mode enforcement | `response_format: {"type": "json_object"}` prevents free-text hallucination |
| Column-binding rules | Prompt explicitly states: "risk_flags must come from Potential Risk Identified and Opportunity Risk Reason columns ONLY" |
| Post-processing validation | Code filters out any deal names not present in input DataFrame |
| No external enrichment | Agent never searches the web or invents company details |
| Reasoning traceability | Prompt requires reasoning to cite specific column values from the input |

### Key Trade-offs

| Decision | Trade-off | Why |
|----------|-----------|-----|
| Streamlit over React/Next.js | Less polished UI, but ships in hours not days | Prototype velocity > pixel perfection |
| Single LLM call (all 20 deals) | Token cost per call is higher, but maintains cross-deal comparison context | Relative ranking requires seeing all deals together |
| Groq free tier over paid OpenAI | Dependent on Groq availability; slightly less reliable than GPT-4o-mini | Zero cost for prototype; easy to swap to OpenAI for production |
| Hardcoded scoring rubric in prompt | Less flexible than a configurable UI | Encodes opinionated product judgment — the rubric IS the product |
| No persistent storage | Results disappear on refresh | Prototype scope — no auth/DB needed |
| 9 weighted criteria over simple heuristics | More complex prompt, harder to debug | Captures real sales manager judgment better than 3-4 simple rules |

### What I'd Build in v2 (with another week)

1. **HubSpot CRM integration** — Pull deals directly via API instead of CSV upload
2. **Historical pattern learning** — Compare current deals against past won/lost deals to improve scoring
3. **Slack alerts** — Auto-notify reps when their deals drop below a threshold
4. **Time-series tracking** — Show deal health trajectory over weeks (improving/declining)
5. **Rep coaching layer** — "Deals like this that closed had exec sponsor meetings by this stage"
6. **Configurable rubric** — Let managers adjust weights via UI sliders
7. **Multi-model evaluation** — Run GPT-4o + Claude in parallel, surface disagreements as uncertainty signals
8. **Export to CRM** — Push next actions back into HubSpot as tasks

---

## Stack & Tools Transparency

- **AI coding assistant**: Claude (Anthropic) for code generation and iteration
- **LLM runtime**: Llama 3.3 70B via Groq API (free tier)
- **Framework**: Streamlit (Python)
- **Deployment**: Streamlit Community Cloud (free tier)
- **Libraries**: pandas (data handling), groq (LLM client)
- **Reference**: Streamlit documentation, Groq API docs, Llama 3 model card

---

## Mock Data Assumptions

The `mock_opportunities.csv` contains 20 deals designed to represent a realistic B2B SaaS pipeline:

- **Segments**: SMB, Mid-Market, Enterprise (varied deal sizes $10k–$85k ACV)
- **Stages**: Full funnel from Discovery → Negotiation
- **Industries**: FinTech, E-commerce, Healthcare, EdTech, Logistics, FoodTech, Hospitality, etc.
- **Statuses**: Mix of Active (16) and Stalled (4) deals
- **Risk profiles**: Budget delays, security reviews, champion loss, org instability, competitor evaluation, contract lock-in
- **Timing**: Close dates spanning June–September 2026
- **Geography**: India-focused B2B companies (aligned with Wati's market)
- **Pain point coverage**: Mix of "Yes", "Partial", and implied gaps in product-pain fit
- **Intent timing**: Spread across Immediate, Q3, Q4, and Q4+ to test urgency scoring

Key columns that drive scoring: Close Date, Stage, Decision Maker Involved, ACV, Intent Timing, Our Current Product Addresses Their Pain Point Or Not, Last Activity Date, ICP Or Not, Potential Risk Identified, Status.

---

## Local Development

```bash
pip install -r requirements.txt
streamlit run app.py
```

Add your Groq API key in `.streamlit/secrets.toml`:
```
GROQ_API_KEY = "your-key-here"
```

---

## Project Structure

```
funnel-triage-agent/
├── app.py                    # Streamlit UI
├── agent.py                  # LLM logic + system prompt
├── mock_opportunities.csv    # 20-deal sample data
├── requirements.txt          # Dependencies
├── .streamlit/
│   └── config.toml          # Streamlit theme config
└── README.md                # This file
```
