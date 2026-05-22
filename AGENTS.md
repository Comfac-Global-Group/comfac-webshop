# Comfac Webshop Agent Instructions

> **For:** Kimi, Claude, DeepSeek, OpenCode, or any AI assistant  
> **Repo:** `comfac-webshop` — web shop setup, product listings, pricing, and e-commerce configuration  
> **Last Updated:** 2026-05-15

---

## Your Job as the Webshop Agent

You work in the webshop repo. Your job is to:
1. **Build and maintain** the web shop product catalog, pricing, and checkout flow.
2. **Report progress** after every session so the comfac-ops agent can monitor webshop development.
3. **Preserve** configuration guides, pricing rules, and integration notes.

---

## Progress Reporting (Required)

After **every session**, append a dated entry to `SESSION_LOG.md` (create it if it doesn't exist). Use this format:

```markdown
## YYYY-MM-DD — <One-line summary>

**Owner:** <Name>  
**Status:** 🟢/🟡/🔴  

### What Was Done
- <Bullet 1>
- <Bullet 2>

### Blockers / Risks
- <None | description>

### Next Actions
- <Action 1> — due <date> — owner <name>
```

**Status colors:**
- 🟢 **Green** — on track, no blockers
- 🟡 **Yellow** — minor delays or dependencies
- 🔴 **Red** — blocked, needs escalation

### Weekly Summary

Every **Friday**:

```markdown
## Week of YYYY-MM-DD

**Focus:** <Theme>
**Overall Status:** 🟢/🟡/🔴

### Completed
- <Item>

### In Progress
- <Item>

### Blockers
- <None | description>

### Next Week
- <Planned work>
```

> **These files are read by the comfac-ops agent.** Keep them factual and concise. The ops agent synthesizes across all repos — your job is to feed it accurate signal.

---

*Agents: The webshop is a revenue channel. Blockers here directly impact sales. Log them.*
