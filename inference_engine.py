from knowledge_base import DengueExpertSystem, PatientFact

SEVERITY_LABELS = {0: "LOW", 1: "MODERATE", 2: "HIGH", 3: "CRITICAL"}
SEVERITY_ICONS  = {0: "✅", 1: "🟡", 2: "🟠", 3: "🔴"}
SEP_DOUBLE = "═" * 65
SEP_SINGLE = "─" * 65


def run_diagnosis(patient_data: dict):
    engine = DengueExpertSystem()
    result = engine.run(PatientFact(**patient_data))
    print_report(result, patient_data)
    return result


def print_report(result, pd):
    icon  = SEVERITY_ICONS[result.severity]
    level = SEVERITY_LABELS[result.severity]

    print(f"\n{SEP_DOUBLE}")
    print("  DengueXpert v2.0 — EXPERT SYSTEM DIAGNOSIS REPORT")
    print("  Dengue Fever Assessment | Sri Lanka MOH / WHO 2009 Guidelines")
    print(SEP_DOUBLE)

    # Patient Summary
    print(f"\n  👤 Patient  : {pd.get('name','Patient')}, Age {pd.get('age','?')}")
    print(f"  📍 District : {pd.get('district','N/A').title()}")
    print(f"  🌡  Fever    : {pd.get('fever','?')}°C   |   Days of Fever: {pd.get('days_of_fever','?')}")

    # ── ES CHARACTERISTIC 1: NARROW DOMAIN ───────────────────────────────────
    print(f"\n{SEP_SINGLE}")
    print("  [ES FEATURE 1] NARROW DOMAIN OPERATION")
    print(SEP_SINGLE)
    print("  This system operates ONLY on Dengue Fever and closely related")
    print("  febrile illnesses in the Sri Lankan epidemiological context.")
    print("  Domain knowledge encoded: WHO 2009 Dengue Classification,")
    print("  Sri Lanka MOH guidelines, local district risk data.")

    # ── ES CHARACTERISTIC 2: CONFLICT SET ────────────────────────────────────
    print(f"\n{SEP_SINGLE}")
    print("  [ES FEATURE 2] CONFLICT SET (All Applicable Rules Identified)")
    print(SEP_SINGLE)
    if result.conflict_set:
        print(f"  {'Salience':>10}  {'Rule ID':>8}  Name")
        print(f"  {'--------':>10}  {'-------':>8}  ----")
        for salience, rule_id, name in result.conflict_set:
            print(f"  {salience:>10}  R{rule_id:<8}  {name}")
    else:
        print("  No rules applicable — no fever detected.")

    # ── ES CHARACTERISTIC 3: CONFLICT RESOLUTION ─────────────────────────────
    print(f"\n{SEP_SINGLE}")
    print("  [ES FEATURE 3] CONFLICT RESOLUTION (Salience-Based Ordering)")
    print(SEP_SINGLE)
    print("  Rules are fired in DESCENDING SALIENCE order.")
    print("  Higher-salience rules (severe cases) override lower ones.")
    print("  This mimics how a doctor prioritises the worst-case scenario first.")
    fired_ids = [r['rule'] for r in result.fired_rules]
    print(f"  Rules fired (in order): {' → '.join(f'R{i}' for i in fired_ids) or 'None'}")

    # ── ES CHARACTERISTIC 4: INCOMPLETE INFORMATION ───────────────────────────
    print(f"\n{SEP_SINGLE}")
    print("  [ES FEATURE 4] HANDLING INCOMPLETE INFORMATION")
    print(SEP_SINGLE)
    if result.missing_info_used:
        for field in result.missing_info_used:
            print(f"  ⚠ Missing field: '{field}'")
        for assumption in result.assumptions_made:
            print(f"  → Assumption made: {assumption}")
    else:
        print("  All required fields provided — no assumptions needed.")

    # ── ES CHARACTERISTIC 5: UNCERTAINTY / CERTAINTY FACTOR ──────────────────
    print(f"\n{SEP_SINGLE}")
    print("  [ES FEATURE 5] UNCERTAINTY HANDLING — CERTAINTY FACTORS (MYCIN-style)")
    print(SEP_SINGLE)
    print("  CF combination formula: CF(A+B) = CF(A) + CF(B) × (1 – CF(A))")
    if result.fired_rules:
        running_cf = 0.0
        for r in result.fired_rules:
            if r['rule'] in {1, 2, 3, 9}:  # Primary diagnosis rules
                running_cf = r['cf']
                print(f"  R{r['rule']:<2} ({r['name']:<38}) → CF = {r['cf']:.2f}")
            elif r['cf'] > 0.01:
                new_cf = running_cf + r['cf'] * (1 - running_cf)
                print(f"  R{r['rule']:<2} ({r['name']:<38}) → CF boost +{r['cf']:.2f}  (combined: {new_cf:.2f})")
                running_cf = new_cf
    print(f"\n  ▶ FINAL COMBINED CF = {result.final_cf:.2f}  ({result.final_cf:.0%} confidence)")

    # ── ES CHARACTERISTIC 6: BAYESIAN PROBABILITY ────────────────────────────
    print(f"\n{SEP_SINGLE}")
    print("  [ES FEATURE 6] BAYESIAN PROBABILITY — P(Dengue | Symptoms)")
    print(SEP_SINGLE)
    if result.bayesian_notes:
        b = result.bayesian_notes[0]
        print(f"  Symptoms observed      : {', '.join(b['symptoms'])}")
        print(f"  Formula                : {b['formula']}")
        print(f"  Prior P(Dengue)        : {b['prior']:.2f}  (Sri Lanka MOH seasonal rate)")
        print(f"  Likelihood P(S|Dengue) : {b['likelihood']:.4f}")
        print(f"  Posterior P(D|S)       : {b['posterior']:.4f}  ({b['posterior']*100:.1f}%)")
    else:
        print("  No symptoms provided for Bayesian computation.")

    # ── MAIN DIAGNOSIS ────────────────────────────────────────────────────────
    print(f"\n{SEP_DOUBLE}")
    print(f"  {icon}  DIAGNOSIS  : {result.diagnosis}")
    print(f"     SEVERITY   : {level}")
    print(f"     CERTAINTY  : {result.final_cf:.0%}")
    print(SEP_DOUBLE)

    # ── ES CHARACTERISTIC 7: EXPLANATION FACILITY (WHY/HOW) ──────────────────
    print(f"\n{SEP_SINGLE}")
    print("  [ES FEATURE 7] EXPLANATION FACILITY — WHY was this diagnosis reached?")
    print(SEP_SINGLE)
    if not result.fired_rules:
        print("  No rules fired.")
    else:
        for r in result.fired_rules:
            print(f"\n  ▶ Rule R{r['rule']}: {r['name']}")
            print(f"    Reason : {r['reason']}")
            print(f"    CF     : {r['cf']:.0%}")

    # ── ES CHARACTERISTIC 8: ALTERNATIVE SOLUTIONS ───────────────────────────
    print(f"\n{SEP_SINGLE}")
    print("  [ES FEATURE 8] ALTERNATIVE SOLUTIONS — Differential Diagnoses")
    print(SEP_SINGLE)
    if result.differential:
        for i, d in enumerate(result.differential, 1):
            print(f"  {i}. {d}")
    else:
        print("  No significant differential diagnoses identified for this case.")

    # ── RECOMMENDATIONS ───────────────────────────────────────────────────────
    print(f"\n{SEP_SINGLE}")
    print("  RECOMMENDATIONS")
    print(SEP_SINGLE)
    for rec in result.recommendations:
        print(f"  • {rec}")

    print(f"\n  ⚠ DISCLAIMER: DengueXpert is a clinical decision-support tool.")
    print(f"    Always confirm with a qualified medical professional.")
    print(f"{SEP_DOUBLE}\n")
