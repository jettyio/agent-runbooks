# Paired-Error Audit — SMASH 2026 Paper #1

**Readers:** Claude Haiku (small-fast) as proxy clinician vs Claude Sonnet (large) as model under audit  
**Dataset:** 36 MedQA-USMLE cases (12 diagnosis, 12 management, 12 mechanism/other); seed 1  

**Offline 2x2:** Clinician proxy 78% accurate, model 92%. Shared errors: 1/36 (double-fault 2.8%; 95% CI 0%–14%).  
Expected if independent: 1.9%. Yule's Q = +0.30 (bootstrap CI –0.52 to +0.91). Rescue potential: 87.5%.  

**Assisted workflows:** When model saw wrong clinician impressions, it copied them 17.6% vs 5.9% blind (2 right→wrong switches).  
When clinician saw wrong AI suggestions, accuracy on those cases dropped from 70% to 50% (20-point drop — comparable to  
the paper's cited 14–18 pp for physicians, though this is an LLM proxy, not clinician evidence).  

**Gates:** Gate 1 (accuracy + low double-fault): PASS. Gate 2 (model-only harm + rescue retained): PASS.  
By stratum: diagnosis and mechanism/other pass Gate 1; management fails (double-fault 8.3%, n=12).  

**Headline finding:** Automation bias was the sharpest signal — wrong AI suggestions reliably degraded clinician-proxy accuracy;  
offline error overlap (Q = +0.30) was modest but estimation precision is very low at n = 36.
