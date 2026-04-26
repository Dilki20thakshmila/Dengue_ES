from knowledge_base import DengueExpertSystem, PatientFact


SEVERITY_LABELS = {
    0: "LOW",
    1: "MODERATE",
    2: "HIGH",
    3: "CRITICAL"
}

SEVERITY_COLORS = {
    0: "✅",
    1: "🟡",
    2: "🟠",
    3: "🔴"
}


def run_diagnosis(patient_data: dict):
    """
    Takes patient data dict, runs the expert system,
    and prints a full diagnosis report with explanation.
    """
    # 1. Create and reset the engine
    engine = DengueExpertSystem()
    engine.reset()

    # 2. Load all patient data as a single fact
    engine.declare(PatientFact(**patient_data))

    # 3. Run — this fires all matching rules
    engine.run()

    # 4. Print the diagnosis report
    print_report(engine, patient_data)


def print_report(engine, patient_data):
    icon  = SEVERITY_COLORS[engine.severity]
    level = SEVERITY_LABELS[engine.severity]

    print("\n" + "═"*55)
    print("  DENGUE EXPERT SYSTEM — DIAGNOSIS REPORT")
    print("  DengueXpert v1.0 | Sri Lanka MOH Guidelines")
    print("═"*55)

    print(f"\n  Patient : {patient_data.get('name', 'Unknown')}")
    print(f"  District: {patient_data.get('district','').title()}")
    print(f"  Fever   : {patient_data.get('fever')}°C")

    print(f"\n  {icon} DIAGNOSIS : {engine.diagnosis}")
    print(f"  SEVERITY  : {level}")
    print(f"  CERTAINTY : {engine.final_cf:.0%}")

    print("\n" + "─"*55)
    print("  RECOMMENDATIONS")
    print("─"*55)
    for rec in engine.recommendations:
        print(f"  • {rec}")

    print("\n" + "─"*55)
    print("  REASONING TRACE (Explanation Facility)")
    print("─"*55)
    if not engine.fired_rules:
        print("  No rules fired — no fever detected.")
    else:
        for r in engine.fired_rules:
            print(f"\n  [{r['rule']}] {r['name']}")
            print(f"  Reason : {r['reason']}")
            print(f"  CF     : {r['cf']:.0%}")

    print("\n" + "─"*55)
    print("  COMBINED CERTAINTY FACTOR")
    print("─"*55)
    print(f"  Final CF = {engine.final_cf:.2f} ({engine.final_cf:.0%} confidence)")
    print("\n  DISCLAIMER: This system is a decision-support")
    print("  tool only. Always consult a qualified doctor.")
    print("═"*55 + "\n")