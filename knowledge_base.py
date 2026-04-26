from experta import *


# ─────────────────────────────────────────────
#  FACT DEFINITION
#  This is the "working memory" of the ES.
#  All patient data is stored as a PatientFact.
# ─────────────────────────────────────────────

class PatientFact(Fact):
    """Holds all patient data collected from the user."""
    pass


class DiagnosisFact(Fact):
    """Stores the diagnosis result after rules fire."""
    pass


# ─────────────────────────────────────────────
#  EXPERT SYSTEM ENGINE
#  All @Rule methods = your IF-THEN rules
# ─────────────────────────────────────────────

class DengueExpertSystem(KnowledgeEngine):

    # Track which rules fired (for explanation facility)
    def __init__(self):
        super().__init__()
        self.fired_rules = []
        self.final_cf = 0.0
        self.diagnosis = "Undetermined"
        self.severity = 0
        self.recommendations = []

    # ── RULE 1: PROBABLE DENGUE ──────────────────
    # WHO criteria: fever + 2 of the classic symptoms
    # CF = 0.60 (moderate confidence)
    @Rule(
        PatientFact(fever=P(lambda x: x >= 38.0)),
        OR(
            PatientFact(headache=True),
            PatientFact(eye_pain=True),
            PatientFact(muscle_pain=True),
            PatientFact(joint_pain=True),
            PatientFact(rash=True)
        )
    )
    def rule1_probable_dengue(self):
        cf = 0.60
        self.fired_rules.append({
            "rule": "Rule 1",
            "name": "Probable Dengue",
            "reason": "Fever ≥ 38°C + classic dengue symptoms detected",
            "cf": cf
        })
        self.diagnosis = "Probable Dengue"
        self.severity = 1
        self.final_cf = cf
        self.recommendations = [
            "Rest and drink plenty of fluids (ORS recommended)",
            "Take paracetamol for fever — DO NOT take aspirin or ibuprofen",
            "Visit nearest hospital for blood test (CBC)",
            "Monitor for warning signs — return to hospital if they appear"
        ]
        self.declare(DiagnosisFact(level=1, cf=cf))

    # ── RULE 2: DENGUE WITH WARNING SIGNS ────────
    # WHO criteria: probable dengue + any warning sign
    # CF = 0.85 (high confidence — needs hospital NOW)
    @Rule(
        DiagnosisFact(level=1),
        OR(
            PatientFact(abdominal_pain=True),
            PatientFact(persistent_vomiting=True),
            PatientFact(mucosal_bleeding=True),
            PatientFact(rapid_breathing=True),
            PatientFact(platelet=P(lambda x: x < 100000))
        )
    )
    def rule2_warning_signs(self):
        cf = 0.85
        self.fired_rules.append({
            "rule": "Rule 2",
            "name": "Dengue with Warning Signs",
            "reason": "Warning signs present — risk of plasma leakage",
            "cf": cf
        })
        self.diagnosis = "Dengue with Warning Signs"
        self.severity = 2
        self.final_cf = cf
        self.recommendations = [
            "URGENT: Go to hospital immediately — do not wait",
            "IV fluid therapy will likely be needed",
            "Continuous monitoring of platelet count required",
            "Do NOT take aspirin, ibuprofen or any NSAID"
        ]
        self.declare(DiagnosisFact(level=2, cf=cf))

    # ── RULE 3: SEVERE DENGUE (DSS) ───────────────
    # WHO criteria: warning signs + organ involvement
    # CF = 0.95 (very high — life threatening)
    @Rule(
        DiagnosisFact(level=2),
        OR(
            PatientFact(severe_bleeding=True),
            PatientFact(organ_failure=True),
            PatientFact(altered_consciousness=True),
            PatientFact(platelet=P(lambda x: x < 20000))
        )
    )
    def rule3_severe_dengue(self):
        cf = 0.95
        self.fired_rules.append({
            "rule": "Rule 3",
            "name": "Severe Dengue (DSS)",
            "reason": "Severe plasma leakage / organ failure / severe bleeding",
            "cf": cf
        })
        self.diagnosis = "Severe Dengue / Dengue Shock Syndrome"
        self.severity = 3
        self.final_cf = cf
        self.recommendations = [
            "EMERGENCY: Call 1990 (Suwaseriya) immediately",
            "Patient requires ICU admission",
            "Aggressive IV fluid resuscitation needed",
            "Do NOT move patient unnecessarily"
        ]
        self.declare(DiagnosisFact(level=3, cf=cf))

    # ── RULE 4: SEASONAL RISK BOOST (Sri Lanka) ──
    # Monsoon seasons = higher dengue transmission
    @Rule(
        PatientFact(month=P(lambda m: m in [5,6,10,11]))
    )
    def rule4_seasonal_risk(self):
        self.fired_rules.append({
            "rule": "Rule 4",
            "name": "Seasonal Risk Factor",
            "reason": "Patient presents during peak dengue season (May/Jun or Oct/Nov)",
            "cf": 0.15
        })
        self.final_cf = min(1.0, self.final_cf + 0.15)

    # ── RULE 5: HIGH-RISK DISTRICT (Sri Lanka) ───
    # Highest dengue burden districts from MOH Sri Lanka data
    @Rule(
        PatientFact(district=P(lambda d: d in [
            "colombo", "gampaha", "kandy",
            "kalutara", "galle", "ratnapura"
        ]))
    )
    def rule5_high_risk_district(self):
        self.fired_rules.append({
            "rule": "Rule 5",
            "name": "High-Risk District",
            "reason": f"District is a high-burden dengue zone per MOH Sri Lanka",
            "cf": 0.10
        })
        self.final_cf = min(1.0, self.final_cf + 0.10)

    # ── RULE 6: LEPTOSPIROSIS DIFFERENTIAL ───────
    # Common misdiagnosis in Sri Lanka — flag if jaundice + rat exposure
    @Rule(
        PatientFact(fever=P(lambda x: x >= 38.0)),
        PatientFact(jaundice=True),
        PatientFact(rat_exposure=True)
    )
    def rule6_lepto_differential(self):
        self.fired_rules.append({
            "rule": "Rule 6",
            "name": "Leptospirosis Differential",
            "reason": "Jaundice + rat/flood exposure — consider Leptospirosis",
            "cf": 0.70
        })
        self.recommendations.append(
            "⚠ Also consider Leptospirosis — request Leptospira serology test"
        )

    # ── RULE 7: UNLIKELY DENGUE ──────────────────
    # Fires only if no dengue diagnosis was made
    @Rule(
        PatientFact(fever=P(lambda x: x >= 38.0)),
        NOT(DiagnosisFact())
    )
    def rule7_unlikely_dengue(self):
        self.fired_rules.append({
            "rule": "Rule 7",
            "name": "Unlikely Dengue",
            "reason": "Fever present but insufficient dengue criteria met",
            "cf": 0.20
        })
        self.diagnosis = "Unlikely Dengue — Other Cause"
        self.severity = 0
        self.final_cf = 0.20
        self.recommendations = [
            "Visit a doctor to investigate other causes of fever",
            "Consider: Flu, Typhoid, Malaria, or other viral fever",
            "Stay hydrated and monitor temperature"
        ]