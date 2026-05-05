"""
DengueXpert v2.0 — Main Entry Point
====================================
Includes a DEMO MODE that automatically runs 3 demonstration cases
to show all essential ES characteristics in action.

Usage:
  python main.py          → Interactive mode
  python main.py --demo   → Demonstration mode (for presentation)
"""

import sys
import datetime
from inference_engine import run_diagnosis

SEP = "═" * 65


def interactive_mode():
    """Full interactive consultation."""
    print(f"\n{SEP}")
    print("  DengueXpert v2.0 — Dengue Fever Expert System")
    print("  Developed for Sri Lanka | WHO 2009 Guidelines")
    print("  MSc Artificial Intelligence — Expert Systems")
    print(SEP)

    while True:
        print("\n  This system will guide you through a structured diagnosis.")
        print("  Answer each question carefully.\n")

        pd = {}
        pd['name']          = input("  Patient name       : ").strip() or "Patient"
        pd['age']           = int(input("  Age                : ") or 30)
        pd['district']      = input("  District (e.g. colombo, kandy): ").strip().lower() or "colombo"
        pd['month']         = datetime.datetime.now().month
        pd['fever']         = float(input("  Temperature (°C)   : ") or 38.5)
        pd['days_of_fever'] = int(input("  Days of fever      : ") or 3)

        print("\n  --- Classic Dengue Symptoms (y/n) ---")
        pd['headache']    = input("  Headache?          [y/n]: ").lower().startswith('y')
        pd['eye_pain']    = input("  Eye pain?          [y/n]: ").lower().startswith('y')
        pd['muscle_pain'] = input("  Muscle pain?       [y/n]: ").lower().startswith('y')
        pd['joint_pain']  = input("  Joint pain?        [y/n]: ").lower().startswith('y')
        pd['rash']        = input("  Skin rash?         [y/n]: ").lower().startswith('y')
        pd['nausea']      = input("  Nausea?            [y/n]: ").lower().startswith('y')

        print("\n  --- Warning Signs (y/n) ---")
        pd['abdominal_pain']      = input("  Abdominal pain?    [y/n]: ").lower().startswith('y')
        pd['persistent_vomiting'] = input("  Persistent vomit?  [y/n]: ").lower().startswith('y')
        pd['mucosal_bleeding']    = input("  Mucosal bleeding?  [y/n]: ").lower().startswith('y')
        pd['rapid_breathing']     = input("  Rapid breathing?   [y/n]: ").lower().startswith('y')
        pd['fluid_accumulation']  = input("  Fluid accumulation?[y/n]: ").lower().startswith('y')
        platelet_str              = input("  Platelet count (leave blank if unknown): ").strip()
        pd['platelet']            = float(platelet_str) if platelet_str else None

        print("\n  --- Severe Signs (y/n) ---")
        pd['severe_bleeding']       = input("  Severe bleeding?   [y/n]: ").lower().startswith('y')
        pd['organ_failure']         = input("  Organ failure?     [y/n]: ").lower().startswith('y')
        pd['altered_consciousness'] = input("  Altered conscious? [y/n]: ").lower().startswith('y')

        print("\n  --- Differential Diagnosis Flags (y/n) ---")
        pd['jaundice']      = input("  Jaundice?          [y/n]: ").lower().startswith('y')
        pd['rat_exposure']  = input("  Rat/flood exposure?[y/n]: ").lower().startswith('y')
        pd['cyclical_fever']= input("  Cyclical fever?    [y/n]: ").lower().startswith('y')

        run_diagnosis(pd)

        again = input("  Run another consultation? (yes/no): ").strip().lower()
        if again not in ['yes', 'y']:
            print("\n  Thank you for using DengueXpert. Stay safe!\n")
            break


def demo_mode():
    """
    DEMONSTRATION MODE — For academic presentation.
    Runs 3 pre-configured cases to show all ES characteristics:
      Case 1: Mild Dengue — CF, Bayesian, Conflict Set
      Case 2: Warning Signs — Conflict Resolution, Incomplete Info
      Case 3: Severe + Differentials — Alternative Solutions, Explanation
    """
    cases = [
        {
            "_title": "DEMO CASE 1 — Probable Dengue (Mild)",
            "_note":  "Shows: Conflict Set, CF Calculation, Bayesian Probability",
            "name":   "Nimal Perera",
            "age":    28,
            "district": "colombo",
            "month":  11,       # November = peak season
            "fever":  38.8,
            "days_of_fever": 2,
            "headache":    True,
            "eye_pain":    True,
            "muscle_pain": True,
            "joint_pain":  False,
            "rash":        False,
            "nausea":      True,
            "abdominal_pain":      False,
            "persistent_vomiting": False,
            "mucosal_bleeding":    False,
            "rapid_breathing":     False,
            "fluid_accumulation":  False,
            "platelet":            None,    # MISSING — demonstrates incomplete info
            "severe_bleeding":     False,
            "organ_failure":       False,
            "altered_consciousness": False,
            "jaundice":     False,
            "rat_exposure": False,
            "cyclical_fever": False,
        },
        {
            "_title": "DEMO CASE 2 — Dengue with Warning Signs",
            "_note":  "Shows: Conflict Resolution (Rule override), High Severity",
            "name":   "Kumari Silva",
            "age":    42,
            "district": "kandy",
            "month":  6,        # June = peak season
            "fever":  39.5,
            "days_of_fever": 4,
            "headache":    True,
            "eye_pain":    True,
            "muscle_pain": True,
            "joint_pain":  True,
            "rash":        True,
            "nausea":      True,
            "abdominal_pain":      True,   # WARNING SIGN
            "persistent_vomiting": True,   # WARNING SIGN
            "mucosal_bleeding":    False,
            "rapid_breathing":     False,
            "fluid_accumulation":  False,
            "platelet":            85000,  # WARNING: Low platelet
            "severe_bleeding":     False,
            "organ_failure":       False,
            "altered_consciousness": False,
            "jaundice":     False,
            "rat_exposure": False,
            "cyclical_fever": False,
        },
        {
            "_title": "DEMO CASE 3 — Severe Dengue + Leptospirosis Differential",
            "_note":  "Shows: Alternative Solutions, Highest Severity, Full Explanation",
            "name":   "Saman Fernando",
            "age":    55,
            "district": "gampaha",
            "month":  10,
            "fever":  40.1,
            "days_of_fever": 6,
            "headache":    True,
            "eye_pain":    True,
            "muscle_pain": True,
            "joint_pain":  True,
            "rash":        False,
            "nausea":      True,
            "abdominal_pain":      True,
            "persistent_vomiting": True,
            "mucosal_bleeding":    True,
            "rapid_breathing":     True,
            "fluid_accumulation":  True,
            "platelet":            15000,  # CRITICAL
            "severe_bleeding":     True,
            "organ_failure":       True,
            "altered_consciousness": True,
            "jaundice":     True,          # → Triggers Leptospirosis differential
            "rat_exposure": True,          # → Triggers Leptospirosis differential
            "cyclical_fever": False,
        },
    ]

    print(f"\n{'█'*65}")
    print("  DengueXpert v2.0 — ACADEMIC DEMONSTRATION MODE")
    print("  Showing all 8 Essential Expert System Characteristics")
    print(f"{'█'*65}")

    for i, case in enumerate(cases, 1):
        title = case.pop('_title')
        note  = case.pop('_note')
        print(f"\n\n{'▓'*65}")
        print(f"  DEMONSTRATION {i}/3: {title}")
        print(f"  Focus: {note}")
        print(f"{'▓'*65}")
        input("  [Press ENTER to run this case...]\n")
        run_diagnosis(case)
        if i < len(cases):
            input("  [Press ENTER to continue to next case...]\n")

    print(f"\n{'█'*65}")
    print("  DEMONSTRATION COMPLETE")
    print("  All 8 ES Characteristics have been demonstrated:")
    print("   1. Narrow Domain Expertise")
    print("   2. Knowledge Base (separate from Inference Engine)")
    print("   3. Forward Chaining (Data → Goal)")
    print("   4. Conflict Set + Conflict Resolution (Salience)")
    print("   5. Handling Incomplete Information (Assumptions)")
    print("   6. Alternative Solutions (Differential Diagnosis)")
    print("   7. Uncertainty Handling (MYCIN Certainty Factors)")
    print("   8. Explanation Facility (WHY / HOW reasoning trace)")
    print("  + Bayesian Probability P(Disease | Symptoms)")
    print(f"{'█'*65}\n")


if __name__ == "__main__":
    if "--demo" in sys.argv:
        demo_mode()
    else:
        interactive_mode()
