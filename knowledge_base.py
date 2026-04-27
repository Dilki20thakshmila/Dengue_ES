from experta import *


# ─────────────────────────────────────────────
#  FACT DEFINITION
#  This is the "working memory" of the ES.
#  All patient data is stored as a PatientFact.
# ─────────────────────────────────────────────

class PatientFact:
    """Holds all patient data collected from the form."""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class DiagnosisResult:
    """Stores the final diagnosis after all rules fire."""
    def __init__(self):
        self.diagnosis      = "Undetermined"
        self.severity       = 0          # 0=none, 1=mild, 2=warning, 3=severe
        self.final_cf       = 0.0        # certainty factor 0.0 - 1.0
        self.fired_rules    = []         # list of rules that fired
        self.recommendations = []
        self.differential   = []         # other diagnoses to consider


class DengueExpertSystem:
    """
    Forward-chaining rule engine.
    Rules are evaluated in priority order (salience).
    Each rule that matches fires and updates the diagnosis.
    """

    def __init__(self):
        self.result = DiagnosisResult()

    def _combine_cf(self, cf1, cf2):
        """
        Combine two certainty factors using the standard formula:
        combined = cf1 + cf2 * (1 - cf1)
        """
        return cf1 + cf2 * (1 - cf1)

    def _add_rule(self, rule_num, name, reason, cf):
        """Record a fired rule for the explanation facility."""
        self.result.fired_rules.append({
            "rule":   rule_num,
            "name":   name,
            "reason": reason,
            "cf":     cf
        })

    # ── RULE 1: PROBABLE DENGUE ──────────────────────────────────
    # WHO: Fever + 2 classic symptoms + live/travel in endemic area
    # Salience: 10
    def rule1_probable_dengue(self, p):
        fever_present = getattr(p, 'fever', 0) >= 38.0

        classic_symptoms = sum([
            getattr(p, 'headache',    False),
            getattr(p, 'eye_pain',    False),
            getattr(p, 'muscle_pain', False),
            getattr(p, 'joint_pain',  False),
            getattr(p, 'rash',        False),
        ])

        if fever_present and classic_symptoms >= 1:
            cf = 0.55 + (classic_symptoms * 0.05)  # more symptoms = higher CF
            cf = min(cf, 0.70)
            self._add_rule(1, "Probable Dengue",
                f"Fever {p.fever}°C + {classic_symptoms} classic symptom(s) detected", cf)
            self.result.diagnosis = "Probable Dengue"
            self.result.severity  = 1
            self.result.final_cf  = cf
            self.result.recommendations = [
                "Rest at home and drink plenty of fluids (ORS strongly recommended)",
                "Take paracetamol only for fever — DO NOT take aspirin or ibuprofen",
                "Visit nearest hospital for a Full Blood Count (FBC/CBC) test",
                "Return to hospital immediately if any warning signs appear",
                "Use mosquito nets and repellent to prevent spreading to others"
            ]
            return True
        return False

    # ── RULE 2: DENGUE WITH WARNING SIGNS ────────────────────────
    # WHO: Probable dengue + any warning sign present
    # Salience: 20 (overrides Rule 1)
    def rule2_warning_signs(self, p):
        if self.result.severity < 1:
            return False  # Rule 1 must fire first

        warning_signs = []
        if getattr(p, 'abdominal_pain',      False): warning_signs.append("severe abdominal pain")
        if getattr(p, 'persistent_vomiting', False): warning_signs.append("persistent vomiting")
        if getattr(p, 'mucosal_bleeding',    False): warning_signs.append("mucosal bleeding")
        if getattr(p, 'rapid_breathing',     False): warning_signs.append("rapid breathing")
        if getattr(p, 'platelet', 999999)  < 100000: warning_signs.append(f"low platelet ({int(p.platelet):,})")
        if getattr(p, 'fluid_accumulation', False):  warning_signs.append("fluid accumulation")

        if warning_signs:
            cf = 0.85
            self._add_rule(2, "Dengue with Warning Signs",
                f"Warning signs present: {', '.join(warning_signs)}", cf)
            self.result.diagnosis = "Dengue with Warning Signs"
            self.result.severity  = 2
            self.result.final_cf  = cf
            self.result.recommendations = [
                "⚠ URGENT: Go to hospital immediately — do not wait or delay",
                "IV fluid therapy will likely be required",
                "Continuous monitoring of platelet count every 4–6 hours",
                "Strict bed rest — avoid any physical activity",
                "DO NOT take aspirin, ibuprofen or any NSAID medication",
                "Hospital admission is strongly recommended"
            ]
            return True
        return False

    # ── RULE 3: SEVERE DENGUE / DENGUE SHOCK SYNDROME ────────────
    # WHO: Warning signs + organ impairment or severe bleeding
    # Salience: 30 (highest priority)
    def rule3_severe_dengue(self, p):
        if self.result.severity < 2:
            return False  # Rule 2 must fire first

        severe_signs = []
        if getattr(p, 'severe_bleeding',       False): severe_signs.append("severe bleeding")
        if getattr(p, 'organ_failure',         False): severe_signs.append("organ impairment")
        if getattr(p, 'altered_consciousness', False): severe_signs.append("altered consciousness")
        if getattr(p, 'platelet', 999999) < 20000:     severe_signs.append(f"critically low platelet ({int(p.platelet):,})")

        if severe_signs:
            cf = 0.95
            self._add_rule(3, "Severe Dengue / Dengue Shock Syndrome",
                f"Severe signs: {', '.join(severe_signs)}", cf)
            self.result.diagnosis = "Severe Dengue (DSS)"
            self.result.severity  = 3
            self.result.final_cf  = cf
            self.result.recommendations = [
                "🚨 EMERGENCY: Call 1990 (Suwaseriya Ambulance) immediately",
                "Patient requires ICU admission — do not delay",
                "Aggressive IV fluid resuscitation protocol needed",
                "Continuous vital signs monitoring required",
                "Do NOT move the patient unnecessarily",
                "Inform hospital of suspected Dengue Shock Syndrome on arrival"
            ]
            return True
        return False

    # ── RULE 4: SEASONAL RISK BOOST (Sri Lanka) ──────────────────
    # Monsoon months = higher Aedes mosquito activity
    def rule4_seasonal_risk(self, p):
        month = getattr(p, 'month', 0)
        peak_months = {5: "May", 6: "June", 10: "October", 11: "November"}
        if month in peak_months:
            boost = 0.15
            self._add_rule(4, "Seasonal Risk Factor",
                f"Consultation during peak dengue season ({peak_months[month]}) — monsoon period", boost)
            self.result.final_cf = min(1.0, self._combine_cf(self.result.final_cf, boost))
            return True
        return False

    # ── RULE 5: HIGH-RISK DISTRICT (Sri Lanka) ───────────────────
    # Based on Sri Lanka MOH annual dengue burden data
    def rule5_high_risk_district(self, p):
        district = getattr(p, 'district', '').lower()
        high_risk = ["colombo", "gampaha", "kandy", "kalutara", "galle", "ratnapura"]
        if district in high_risk:
            boost = 0.10
            self._add_rule(5, "High-Risk District",
                f"{district.title()} is a high dengue burden district (MOH Sri Lanka data)", boost)
            self.result.final_cf = min(1.0, self._combine_cf(self.result.final_cf, boost))
            return True
        return False

    # ── RULE 6: LEPTOSPIROSIS DIFFERENTIAL ───────────────────────
    # Common misdiagnosis in Sri Lanka — jaundice + rat/flood exposure
    def rule6_leptospirosis(self, p):
        fever   = getattr(p, 'fever', 0) >= 38.0
        jaundice = getattr(p, 'jaundice',     False)
        rat_exp  = getattr(p, 'rat_exposure', False)
        if fever and jaundice and rat_exp:
            self._add_rule(6, "Leptospirosis Differential",
                "Fever + jaundice + rat/flood water exposure — Leptospirosis must be excluded", 0.70)
            self.result.differential.append(
                "Leptospirosis — request Leptospira serology (MAT test) urgently"
            )
            self.result.recommendations.append(
                "⚠ Also investigate for Leptospirosis — very common co-infection in Sri Lanka"
            )
            return True
        return False

    # ── RULE 7: TYPHOID DIFFERENTIAL ─────────────────────────────
    def rule7_typhoid(self, p):
        fever      = getattr(p, 'fever', 0) >= 38.5
        long_fever = getattr(p, 'days_of_fever', 0) >= 5
        headache   = getattr(p, 'headache', False)
        no_rash    = not getattr(p, 'rash', False)
        if fever and long_fever and headache and no_rash:
            self._add_rule(7, "Typhoid Differential",
                "Prolonged fever (5+ days) without rash — Typhoid fever should be excluded", 0.40)
            self.result.differential.append(
                "Typhoid fever — request Widal test or blood culture"
            )
            return True
        return False

    # ── RULE 8: UNLIKELY DENGUE ──────────────────────────────────
    # Fires only when no dengue diagnosis was established
    def rule8_unlikely_dengue(self, p):
        fever = getattr(p, 'fever', 0) >= 38.0
        if fever and self.result.severity == 0:
            cf = 0.15
            self._add_rule(8, "Unlikely Dengue",
                "Fever present but insufficient criteria for dengue diagnosis", cf)
            self.result.diagnosis = "Unlikely Dengue — Other Cause"
            self.result.severity  = 0
            self.result.final_cf  = cf
            self.result.recommendations = [
                "Visit a doctor to investigate other causes of fever",
                "Consider: influenza, common viral fever, or bacterial infection",
                "Stay well hydrated and monitor temperature every 4 hours",
                "Return if fever persists beyond 3 days or worsens"
            ]
            return True
        return False

    # ── RUN ALL RULES (Forward Chaining) ─────────────────────────
    def run(self, patient_fact):
        """
        Execute rules in salience order.
        Higher salience rules can override lower ones.
        This mimics CLIPS/Experta forward chaining.
        """
        # Base diagnosis rules (in ascending severity order)
        self.rule1_probable_dengue(patient_fact)
        self.rule2_warning_signs(patient_fact)
        self.rule3_severe_dengue(patient_fact)

        # Context/risk modifier rules
        self.rule4_seasonal_risk(patient_fact)
        self.rule5_high_risk_district(patient_fact)

        # Differential diagnosis rules
        self.rule6_leptospirosis(patient_fact)
        self.rule7_typhoid(patient_fact)

        # Fallback rule
        self.rule8_unlikely_dengue(patient_fact)

        return self.result