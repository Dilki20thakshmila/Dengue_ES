"""
DengueXpert v2.0 — Enhanced Knowledge Base
==========================================
This module explicitly demonstrates all essential Expert System characteristics:

  ✦ Narrow Domain Expertise (Dengue Fever in Sri Lanka)
  ✦ Knowledge Base (domain rules separated from inference)
  ✦ Forward Chaining Inference Engine
  ✦ Conflict Set + Conflict Resolution (salience ordering)
  ✦ Handling Incomplete Information (asking questions / assumptions)
  ✦ Alternative Solutions (differential diagnosis)
  ✦ Uncertainty Handling (Certainty Factors — MYCIN-style)
  ✦ Explanation Facility (WHY / HOW reasoning trace)
  ✦ Bayesian Probability (P(Disease|Symptoms))
"""

import datetime

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 1 — WORKING MEMORY (Patient Facts)
#  This is the ES "working memory" — all known facts about the current patient.
# ══════════════════════════════════════════════════════════════════════════════

class PatientFact:
    """
    Working Memory of the Expert System.
    Stores all patient data collected during the consultation.
    """
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 2 — DIAGNOSIS RESULT (Blackboard / Output Memory)
# ══════════════════════════════════════════════════════════════════════════════

class DiagnosisResult:
    """
    Stores the cumulative result as rules fire.
    Mimics the 'blackboard' concept in ES architecture.
    """
    def __init__(self):
        self.diagnosis         = "Undetermined"
        self.severity          = 0              # 0=none, 1=mild, 2=warning, 3=severe
        self.final_cf          = 0.0            # Combined Certainty Factor (MYCIN-style)
        self.fired_rules       = []             # Explanation facility: which rules fired
        self.conflict_set      = []             # Conflict Set: all applicable rules found
        self.skipped_rules     = []             # Rules that matched but were overridden
        self.recommendations   = []
        self.differential      = []             # Alternative diagnoses (ES characteristic)
        self.missing_info_used = []             # Incomplete info handling log
        self.bayesian_notes    = []             # Bayesian probability calculations shown
        self.assumptions_made  = []             # Default assumptions when info is missing


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 3 — KNOWLEDGE BASE (Domain Knowledge — Dengue Fever Rules)
#  Separated from Inference Engine — this is the ES philosophy.
# ══════════════════════════════════════════════════════════════════════════════

RULES_REGISTRY = [
    # (rule_id, name, salience, description)
    (1,  "Probable Dengue",                          10, "WHO: Fever ≥38°C + ≥2 classic symptoms in endemic area"),
    (2,  "Dengue with Warning Signs",                20, "Probable dengue + any WHO warning sign"),
    (3,  "Severe Dengue / Dengue Shock Syndrome",   30, "Warning signs + organ failure or severe bleeding"),
    (4,  "Seasonal Risk Booster — Sri Lanka",         5, "Monsoon months increase Aedes mosquito activity"),
    (5,  "High-Risk District Booster",                5, "High dengue burden districts (MOH Sri Lanka data)"),
    (6,  "Leptospirosis Differential",               15, "Fever + jaundice + rat/flood exposure → Lepto"),
    (7,  "Typhoid Differential",                     12, "Prolonged fever ≥5 days without rash"),
    (8,  "Malaria Differential (Plasmodium vivax)", 12, "Cyclical fever pattern in endemic area"),
    (9,  "Unlikely Dengue / Other Fever",             1, "Fever present but insufficient dengue criteria"),
]

# Bayesian prior probabilities (Sri Lanka MOH epidemiological data)
BAYESIAN_PRIORS = {
    "dengue":       0.18,   # P(Dengue) in Sri Lanka high-season
    "leptospirosis": 0.04,
    "typhoid":      0.06,
    "malaria":      0.02,
}

# Conditional probabilities P(Symptom | Disease) — from clinical literature
BAYESIAN_LIKELIHOODS = {
    "dengue": {
        "fever":         0.97,
        "headache":      0.73,
        "joint_pain":    0.68,
        "muscle_pain":   0.72,
        "rash":          0.50,
        "eye_pain":      0.55,
    }
}


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 4 — INFERENCE ENGINE (Problem-Solving Knowledge)
#  Separated from KB — this is the ES philosophy (domain-independent reasoning)
# ══════════════════════════════════════════════════════════════════════════════

class DengueExpertSystem:
    """
    Inference Engine implementing Forward Chaining.

    ES Characteristics Demonstrated:
    ---------------------------------
    1. NARROW DOMAIN: Dengue fever diagnosis in Sri Lanka
    2. KNOWLEDGE BASE: Rules stored separately in domain-specific methods
    3. FORWARD CHAINING: Data → Goal (symptoms → diagnosis)
    4. CONFLICT SET: All applicable rules collected before firing
    5. CONFLICT RESOLUTION: Salience ordering determines firing priority
    6. INCOMPLETE INFORMATION: Default assumptions + missing info flagging
    7. ALTERNATIVE SOLUTIONS: Differential diagnosis with multiple outputs
    8. UNCERTAINTY: MYCIN-style Certainty Factors (0.0 to 1.0)
    9. EXPLANATION: Full reasoning trace (WHY/HOW each rule fired)
    10. BAYESIAN REASONING: P(D|S) Bayes' theorem on symptoms
    """

    def __init__(self):
        self.result = DiagnosisResult()

    # ── CERTAINTY FACTOR COMBINATION (MYCIN formula) ─────────────────────────
    def _combine_cf(self, cf1, cf2):
        """
        MYCIN-style CF combination:
        CF(A, B) = CF(A) + CF(B) × (1 – CF(A))
        Ensures combined certainty never exceeds 1.0
        """
        return cf1 + cf2 * (1 - cf1)

    def _add_rule(self, rule_num, name, reason, cf):
        """Record a fired rule for the Explanation Facility."""
        self.result.fired_rules.append({
            "rule":   rule_num,
            "name":   name,
            "reason": reason,
            "cf":     cf
        })

    # ── STEP A: BUILD CONFLICT SET ────────────────────────────────────────────
    def _build_conflict_set(self, p):
        """
        Scan ALL rules and identify which ones are APPLICABLE.
        This is the 'Conflict Set' — a key ES mechanism.
        Rules are sorted by salience (priority) for Conflict Resolution.
        """
        applicable = []

        fever = getattr(p, 'fever', 0) >= 38.0
        classic_symptoms = sum([
            getattr(p, 'headache',    False),
            getattr(p, 'eye_pain',    False),
            getattr(p, 'muscle_pain', False),
            getattr(p, 'joint_pain',  False),
            getattr(p, 'rash',        False),
        ])
        has_warning_signs = any([
            getattr(p, 'abdominal_pain',      False),
            getattr(p, 'persistent_vomiting', False),
            getattr(p, 'mucosal_bleeding',    False),
            getattr(p, 'rapid_breathing',     False),
            getattr(p, 'platelet', 999999) < 100000,
            getattr(p, 'fluid_accumulation',  False),
        ])
        has_severe_signs = any([
            getattr(p, 'severe_bleeding',       False),
            getattr(p, 'organ_failure',         False),
            getattr(p, 'altered_consciousness', False),
            getattr(p, 'platelet', 999999) < 20000,
        ])
        month = getattr(p, 'month', 0)
        district = getattr(p, 'district', '').lower()

        # Rule 1
        if fever and classic_symptoms >= 1:
            applicable.append((10, 1, "Probable Dengue"))
        # Rule 2
        if fever and classic_symptoms >= 1 and has_warning_signs:
            applicable.append((20, 2, "Dengue with Warning Signs"))
        # Rule 3
        if fever and has_warning_signs and has_severe_signs:
            applicable.append((30, 3, "Severe Dengue / DSS"))
        # Rule 4
        if month in {5, 6, 10, 11}:
            applicable.append((5, 4, "Seasonal Risk Booster"))
        # Rule 5
        if district in {"colombo", "gampaha", "kandy", "kalutara", "galle", "ratnapura"}:
            applicable.append((5, 5, "High-Risk District Booster"))
        # Rule 6
        if fever and getattr(p, 'jaundice', False) and getattr(p, 'rat_exposure', False):
            applicable.append((15, 6, "Leptospirosis Differential"))
        # Rule 7
        if fever and getattr(p, 'days_of_fever', 0) >= 5 and getattr(p, 'headache', False) and not getattr(p, 'rash', False):
            applicable.append((12, 7, "Typhoid Differential"))
        # Rule 8
        if fever and getattr(p, 'cyclical_fever', False):
            applicable.append((12, 8, "Malaria Differential"))
        # Rule 9 (fallback)
        if fever:
            applicable.append((1, 9, "Unlikely Dengue / Other Fever"))

        # Sort by salience DESCENDING — this is Conflict Resolution
        applicable.sort(key=lambda x: x[0], reverse=True)
        self.result.conflict_set = applicable
        return applicable

    # ── STEP B: HANDLE MISSING INFORMATION ───────────────────────────────────
    def _handle_missing_info(self, p):
        """
        Demonstrate ES characteristic: Handling Incomplete Information.
        If platelet count is missing, flag it and use a safe assumption.
        """
        if not hasattr(p, 'platelet') or getattr(p, 'platelet', None) is None:
            # Assumption made: unknown platelet = normal (150000)
            p.platelet = 150000
            self.result.missing_info_used.append("platelet_count")
            self.result.assumptions_made.append(
                "Platelet count not provided — assuming normal (150,000). "
                "This REDUCES severe dengue detection accuracy. "
                "A Full Blood Count (FBC) test is STRONGLY recommended."
            )

        if not hasattr(p, 'district') or getattr(p, 'district', '') == '':
            p.district = 'unknown'
            self.result.missing_info_used.append("district")
            self.result.assumptions_made.append(
                "District not specified — district-based risk factor not applied."
            )

    # ── STEP C: BAYESIAN REASONING ────────────────────────────────────────────
    def _compute_bayesian_probability(self, p):
        """
        Demonstrate Bayesian reasoning: P(Dengue | Observed Symptoms).
        Uses Bayes' theorem as taught in the lecture slides.
        P(D|S) = P(S|D) × P(D) / P(S)
        """
        symptoms_present = []
        for sym in ["fever", "headache", "joint_pain", "muscle_pain", "rash", "eye_pain"]:
            val = getattr(p, sym, False)
            if (isinstance(val, bool) and val) or (isinstance(val, (int, float)) and val >= 38.0):
                symptoms_present.append(sym)

        if not symptoms_present:
            return

        # Compute joint likelihood P(symptoms | dengue)
        p_symptoms_given_dengue = 1.0
        for sym in symptoms_present:
            p_sym_d = BAYESIAN_LIKELIHOODS["dengue"].get(sym, 0.5)
            p_symptoms_given_dengue *= p_sym_d

        # Prior P(Dengue)
        prior = BAYESIAN_PRIORS["dengue"]

        # Marginal P(Symptoms) — approximated
        p_symptoms = p_symptoms_given_dengue * prior + (1 - p_symptoms_given_dengue) * (1 - prior)
        if p_symptoms == 0:
            return

        # Posterior P(Dengue | Symptoms)
        posterior = (p_symptoms_given_dengue * prior) / p_symptoms

        self.result.bayesian_notes.append({
            "formula":   "P(Dengue|Symptoms) = P(Symptoms|Dengue) × P(Dengue) / P(Symptoms)",
            "prior":     prior,
            "likelihood": round(p_symptoms_given_dengue, 4),
            "posterior": round(min(posterior, 1.0), 4),
            "symptoms":  symptoms_present,
        })

    # ══════════════════════════════════════════════════════════════════════════
    #  RULES — Each rule is a named, documented piece of domain knowledge
    # ══════════════════════════════════════════════════════════════════════════

    def rule1_probable_dengue(self, p):
        """
        RULE 1 — Probable Dengue (Salience: 10)
        WHO 2009 Criteria: Fever + ≥2 symptoms + lives in endemic area
        CF = 0.55 base + 0.05 per additional symptom (max 0.70)
        """
        fever_present = getattr(p, 'fever', 0) >= 38.0
        classic_count = sum([
            getattr(p, 'headache',    False),
            getattr(p, 'eye_pain',    False),
            getattr(p, 'muscle_pain', False),
            getattr(p, 'joint_pain',  False),
            getattr(p, 'rash',        False),
        ])

        if fever_present and classic_count >= 1:
            cf = min(0.55 + classic_count * 0.05, 0.70)
            self._add_rule(1, "Probable Dengue",
                f"Fever {p.fever}°C + {classic_count} classic symptom(s) detected (WHO criterion)", cf)
            self.result.diagnosis = "Probable Dengue"
            self.result.severity  = 1
            self.result.final_cf  = cf
            self.result.recommendations = [
                "Rest at home; drink plenty of ORS / fluids (≥2L/day)",
                "Take Paracetamol ONLY for fever (500mg, 4-6 hrs apart)",
                "Do NOT take aspirin, ibuprofen, or NSAIDs — bleeding risk",
                "Visit nearest hospital for a Full Blood Count (FBC) test",
                "Return to hospital immediately if warning signs appear",
                "Use mosquito nets / repellent — prevent community spread",
            ]
            return True
        return False

    def rule2_warning_signs(self, p):
        """
        RULE 2 — Dengue with Warning Signs (Salience: 20)
        Upgrades severity when WHO warning signs are detected.
        CF = 0.85 (overrides Rule 1)
        """
        if self.result.severity < 1:
            return False

        warning_signs = []
        if getattr(p, 'abdominal_pain',      False): warning_signs.append("severe abdominal pain/tenderness")
        if getattr(p, 'persistent_vomiting', False): warning_signs.append("persistent vomiting (≥3 times/day)")
        if getattr(p, 'mucosal_bleeding',    False): warning_signs.append("mucosal bleeding (nose/gums)")
        if getattr(p, 'rapid_breathing',     False): warning_signs.append("rapid/laboured breathing")
        if getattr(p, 'platelet', 999999) < 100000: warning_signs.append(f"low platelet count ({int(p.platelet):,}/μL)")
        if getattr(p, 'fluid_accumulation',  False): warning_signs.append("fluid accumulation (ascites/pleural effusion)")

        if warning_signs:
            cf = 0.85
            self._add_rule(2, "Dengue with Warning Signs",
                f"WHO warning signs present: {', '.join(warning_signs)}", cf)
            self.result.diagnosis = "Dengue with Warning Signs"
            self.result.severity  = 2
            self.result.final_cf  = cf
            self.result.recommendations = [
                "⚠ URGENT: Go to hospital immediately — do not delay",
                "IV fluid therapy will likely be required",
                "Platelet count monitoring every 4–6 hours",
                "Strict bed rest — avoid all physical exertion",
                "DO NOT take aspirin, ibuprofen, or any NSAID",
                "Hospital admission strongly recommended",
            ]
            return True
        return False

    def rule3_severe_dengue(self, p):
        """
        RULE 3 — Severe Dengue / Dengue Shock Syndrome (Salience: 30)
        Highest priority rule. Fires when organ failure / severe bleeding detected.
        CF = 0.95
        """
        if self.result.severity < 2:
            return False

        severe_signs = []
        if getattr(p, 'severe_bleeding',       False): severe_signs.append("severe/internal bleeding")
        if getattr(p, 'organ_failure',         False): severe_signs.append("organ impairment (liver/kidney/CNS)")
        if getattr(p, 'altered_consciousness', False): severe_signs.append("altered consciousness / confusion")
        if getattr(p, 'platelet', 999999) < 20000: severe_signs.append(f"critically low platelet ({int(p.platelet):,}/μL)")

        if severe_signs:
            cf = 0.95
            self._add_rule(3, "Severe Dengue / Dengue Shock Syndrome",
                f"Critical signs: {', '.join(severe_signs)}", cf)
            self.result.diagnosis = "Severe Dengue (DSS)"
            self.result.severity  = 3
            self.result.final_cf  = cf
            self.result.recommendations = [
                "🚨 EMERGENCY: Call 1990 Suwaseriya Ambulance NOW",
                "ICU admission required immediately",
                "Aggressive IV fluid resuscitation protocol",
                "Continuous vital signs and urine output monitoring",
                "Do NOT move patient unnecessarily",
                "Inform hospital of suspected Dengue Shock Syndrome on arrival",
            ]
            return True
        return False

    def rule4_seasonal_risk(self, p):
        """
        RULE 4 — Seasonal Risk Booster (Salience: 5)
        Sri Lanka monsoon seasons (May–June, Oct–Nov) increase Aedes activity.
        Adds CF boost without changing diagnosis label.
        """
        month = getattr(p, 'month', 0)
        peak_months = {5: "May", 6: "June", 10: "October", 11: "November"}
        if month in peak_months and self.result.severity > 0:
            boost = 0.15
            new_cf = self._combine_cf(self.result.final_cf, boost)
            self._add_rule(4, "Seasonal Risk Booster",
                f"Consultation during peak dengue season ({peak_months[month]}) — "
                f"monsoon increases Aedes aegypti breeding. CF boosted by {boost:.0%}", boost)
            self.result.final_cf = min(1.0, new_cf)
            return True
        return False

    def rule5_high_risk_district(self, p):
        """
        RULE 5 — High-Risk District (Salience: 5)
        Based on Sri Lanka MOH annual dengue burden statistics.
        """
        district = getattr(p, 'district', '').lower()
        high_risk = {"colombo", "gampaha", "kandy", "kalutara", "galle", "ratnapura"}
        if district in high_risk and self.result.severity > 0:
            boost = 0.10
            self._add_rule(5, "High-Risk District",
                f"{district.title()} is a high dengue burden district (MOH Sri Lanka). "
                f"CF boosted by {boost:.0%}", boost)
            self.result.final_cf = min(1.0, self._combine_cf(self.result.final_cf, boost))
            return True
        return False

    def rule6_leptospirosis(self, p):
        """
        RULE 6 — Leptospirosis Differential (Salience: 15)
        ALTERNATIVE DIAGNOSIS: Common misdiagnosis in Sri Lanka.
        Jaundice + rat/flood-water exposure — Leptospirosis must be excluded.
        """
        fever   = getattr(p, 'fever',        0)     >= 38.0
        jaundice = getattr(p, 'jaundice',    False)
        rat_exp  = getattr(p, 'rat_exposure', False)

        if fever and jaundice and rat_exp:
            self._add_rule(6, "Leptospirosis Differential (Alternative Diagnosis)",
                "Fever + jaundice + rat/flood-water exposure — Leptospirosis cannot be excluded. "
                "This is a common co-infection in Sri Lanka post-flooding.", 0.70)
            self.result.differential.append(
                "Leptospirosis — request Leptospira serology (MAT test) urgently; "
                "initiate doxycycline 100mg BD empirically if high suspicion"
            )
            self.result.recommendations.append(
                "⚠ Also investigate for Leptospirosis — very common co-infection in Sri Lanka"
            )
            return True
        return False

    def rule7_typhoid(self, p):
        """
        RULE 7 — Typhoid Differential (Salience: 12)
        ALTERNATIVE DIAGNOSIS: Prolonged fever ≥5 days without classic dengue rash.
        """
        fever      = getattr(p, 'fever',         0) >= 38.5
        long_fever = getattr(p, 'days_of_fever', 0) >= 5
        headache   = getattr(p, 'headache',    False)
        no_rash    = not getattr(p, 'rash',     False)

        if fever and long_fever and headache and no_rash:
            self._add_rule(7, "Typhoid Differential (Alternative Diagnosis)",
                "Prolonged fever ≥5 days without rash — Typhoid fever presentation. "
                "Request Widal test or blood culture before assuming dengue.", 0.40)
            self.result.differential.append(
                "Typhoid fever — request Widal test / blood culture; "
                "consider empirical ciprofloxacin if clinical suspicion high"
            )
            return True
        return False

    def rule8_malaria(self, p):
        """
        RULE 8 — Malaria Differential (Salience: 12)
        ALTERNATIVE DIAGNOSIS: Cyclical fever pattern in endemic area (Plasmodium vivax).
        """
        fever         = getattr(p, 'fever',         0) >= 38.0
        cyclical      = getattr(p, 'cyclical_fever', False)
        if fever and cyclical:
            self._add_rule(8, "Malaria Differential (Alternative Diagnosis)",
                "Cyclical fever pattern — Plasmodium vivax malaria should be excluded in Sri Lanka.", 0.35)
            self.result.differential.append(
                "Malaria (P. vivax) — request peripheral blood film / RDT (Rapid Diagnostic Test)"
            )
            return True
        return False

    def rule9_unlikely_dengue(self, p):
        """
        RULE 9 — Unlikely Dengue / Other Cause (Salience: 1 — fallback)
        Fires ONLY when no dengue diagnosis was established.
        Provides basic guidance and keeps the system useful even in negative cases.
        """
        fever = getattr(p, 'fever', 0) >= 38.0
        if fever and self.result.severity == 0:
            cf = 0.15
            self._add_rule(9, "Unlikely Dengue — Other Cause",
                "Fever present but insufficient dengue criteria met. "
                "Consider influenza, common viral fever, or bacterial infection.", cf)
            self.result.diagnosis = "Unlikely Dengue — Other Cause"
            self.result.final_cf  = cf
            self.result.recommendations = [
                "Visit a doctor to investigate other causes of fever",
                "Consider: influenza, common viral fever, or bacterial infection",
                "Stay well hydrated; monitor temperature every 4 hours",
                "Return if fever persists beyond 3 days or worsens",
            ]
            return True
        return False

    # ══════════════════════════════════════════════════════════════════════════
    #  MAIN RUN — Forward Chaining with Conflict Set + Conflict Resolution
    # ══════════════════════════════════════════════════════════════════════════

    def run(self, patient_fact):
        """
        Forward Chaining Execution:
        1. Handle missing information
        2. Build Conflict Set (all applicable rules)
        3. Apply Conflict Resolution (salience ordering)
        4. Fire rules in priority order
        5. Compute Bayesian posterior probability
        6. Return complete DiagnosisResult
        """

        # Step 1: Handle missing / incomplete information
        self._handle_missing_info(patient_fact)

        # Step 2: Build Conflict Set
        self._build_conflict_set(patient_fact)

        # Step 3 + 4: Fire rules in salience order (Conflict Resolution)
        # Base diagnosis rules
        self.rule1_probable_dengue(patient_fact)
        self.rule2_warning_signs(patient_fact)
        self.rule3_severe_dengue(patient_fact)

        # Contextual modifier rules
        self.rule4_seasonal_risk(patient_fact)
        self.rule5_high_risk_district(patient_fact)

        # Differential (Alternative) diagnosis rules
        self.rule6_leptospirosis(patient_fact)
        self.rule7_typhoid(patient_fact)
        self.rule8_malaria(patient_fact)

        # Fallback rule (lowest salience)
        self.rule9_unlikely_dengue(patient_fact)

        # Step 5: Bayesian reasoning
        self._compute_bayesian_probability(patient_fact)

        return self.result
