from interface import collect_patient_data
from inference_engine import run_diagnosis


def main():
    print("\n" + "═"*55)
    print("  DengueXpert — Dengue Fever Expert System")
    print("  Developed for Sri Lanka | WHO Guidelines 2009")
    print("  MSc Artificial Intelligence — Expert Systems")
    print("═"*55)
    print("\n  This system will ask you a series of questions")
    print("  and provide a dengue fever risk assessment.")
    print("  Answer each question carefully.\n")

    while True:
        # Collect all answers from user
        patient_data = collect_patient_data()

        # Run the expert system engine
        run_diagnosis(patient_data)

        # Ask if they want to run another case
        again = input("  Run another consultation? (yes/no): ").strip().lower()
        if again not in ["yes", "y"]:
            print("\n  Thank you for using DengueXpert. Stay safe!\n")
            break


if __name__ == "__main__":
    main()