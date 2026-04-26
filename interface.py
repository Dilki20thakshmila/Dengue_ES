import datetime


def ask_yes_no(question):
    """Ask a yes/no question and keep asking until valid answer."""
    while True:
        ans = input(f"  {question} (yes/no): ").strip().lower()
        if ans in ["yes", "y"]: return True
        if ans in ["no",  "n"]: return False
        print("  Please type yes or no.")


def ask_number(question, min_val, max_val):
    """Ask for a number within a valid range."""
    while True:
        try:
            val = float(input(f"  {question}: "))
            if min_val <= val <= max_val:
                return val
            print(f"  Please enter a value between {min_val} and {max_val}.")
        except ValueError:
            print("  Please enter a valid number.")


def collect_patient_data():
    """
    Runs the consultation — asks all questions
    and returns a dictionary of patient facts.
    """
    data = {}

    print("\n" + "="*55)
    print("  SECTION 1: Basic Information")
    print("="*55)

    data["name"] = input("  Patient name: ").strip()

    districts = [
        "colombo", "gampaha", "kalutara", "kandy",
        "matale", "nuwara eliya", "galle", "matara",
        "hambantota", "jaffna", "ratnapura", "kegalle",
        "kurunegala", "puttalam", "other"
    ]
    print(f"\n  Districts: {', '.join(districts)}")
    while True:
        d = input("  District: ").strip().lower()
        if d in districts:
            data["district"] = d
            break
        print("  Please choose from the list above.")

    # Auto-detect current month for seasonal rule
    data["month"] = datetime.datetime.now().month

    print("\n" + "="*55)
    print("  SECTION 2: Fever")
    print("="*55)

    data["fever"] = ask_number(
        "Body temperature in °C (e.g. 38.5)", 35.0, 42.0
    )
    data["days_of_fever"] = int(ask_number(
        "How many days has the fever lasted?", 0, 30
    ))

    print("\n" + "="*55)
    print("  SECTION 3: Classic Dengue Symptoms")
    print("="*55)

    data["headache"]     = ask_yes_no("Severe headache?")
    data["eye_pain"]     = ask_yes_no("Pain behind the eyes (retro-orbital)?")
    data["muscle_pain"]  = ask_yes_no("Muscle pain (myalgia)?")
    data["joint_pain"]   = ask_yes_no("Joint pain (arthralgia)?")
    data["rash"]         = ask_yes_no("Skin rash appeared?")
    data["nausea"]       = ask_yes_no("Nausea or vomiting?")

    print("\n" + "="*55)
    print("  SECTION 4: Warning Signs (serious symptoms)")
    print("="*55)

    data["abdominal_pain"]      = ask_yes_no("Severe abdominal / stomach pain?")
    data["persistent_vomiting"] = ask_yes_no("Vomiting 3 or more times in the last hour?")
    data["mucosal_bleeding"]    = ask_yes_no("Bleeding from gums or nose?")
    data["rapid_breathing"]     = ask_yes_no("Rapid or difficult breathing?")

    has_platelet = ask_yes_no("Do you have a platelet count result from a blood test?")
    if has_platelet:
        data["platelet"] = ask_number(
            "Platelet count (cells/µL, e.g. 95000)", 1000, 500000
        )
    else:
        data["platelet"] = 150000  # assume normal if unknown

    print("\n" + "="*55)
    print("  SECTION 5: Severe Signs")
    print("="*55)

    data["severe_bleeding"]        = ask_yes_no("Severe bleeding (blood in vomit, stool or urine)?")
    data["organ_failure"]          = ask_yes_no("Signs of organ failure (doctor told you)?")
    data["altered_consciousness"]  = ask_yes_no("Confusion, difficulty waking, or unconsciousness?")

    print("\n" + "="*55)
    print("  SECTION 6: Sri Lanka Local Risk Factors")
    print("="*55)

    data["jaundice"]      = ask_yes_no("Yellowing of eyes or skin (jaundice)?")
    data["rat_exposure"]  = ask_yes_no("Recent contact with flood water or rats?")

    return data