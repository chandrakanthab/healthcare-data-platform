import os
import random
from datetime import timedelta

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_SEED = 42

NUM_PRESCRIPTIONS = 160
NUM_DISPENSING = 140

REPO_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        ".."
    )
)

EMR_INPUT_DIR = os.path.join(
    REPO_ROOT,
    "sample-data",
    "emr"
)

OUTPUT_DIR = os.path.join(
    REPO_ROOT,
    "sample-data",
    "pharmacy"
)


# ============================================================
# RANDOM SEED
# ============================================================

random.seed(RANDOM_SEED)


# ============================================================
# HELPER
# ============================================================

def generate_id(prefix, number):
    return f"{prefix}{number:06d}"


# ============================================================
# LOAD EMR
# ============================================================

def load_emr_data():

    encounter_path = os.path.join(
        EMR_INPUT_DIR,
        "encounter.csv"
    )

    if not os.path.exists(encounter_path):
        raise FileNotFoundError(
            f"EMR encounter file not found: "
            f"{encounter_path}"
        )

    encounters = pd.read_csv(
        encounter_path
    )

    return encounters


# ============================================================
# MEDICATION MASTER
# ============================================================

def generate_medication_master():

    medications = [

        {
            "medication_code": "MED001",
            "generic_name": "Paracetamol",
            "brand_name": "Crocin",
            "strength": "500 mg",
            "dosage_form": "Tablet"
        },

        {
            "medication_code": "MED002",
            "generic_name": "Amoxicillin",
            "brand_name": "Mox",
            "strength": "500 mg",
            "dosage_form": "Capsule"
        },

        {
            "medication_code": "MED003",
            "generic_name": "Metformin",
            "brand_name": "Glycomet",
            "strength": "500 mg",
            "dosage_form": "Tablet"
        },

        {
            "medication_code": "MED004",
            "generic_name": "Amlodipine",
            "brand_name": "Amlong",
            "strength": "5 mg",
            "dosage_form": "Tablet"
        },

        {
            "medication_code": "MED005",
            "generic_name": "Azithromycin",
            "brand_name": "Azithral",
            "strength": "500 mg",
            "dosage_form": "Tablet"
        },

        {
            "medication_code": "MED006",
            "generic_name": "Pantoprazole",
            "brand_name": "Pantop",
            "strength": "40 mg",
            "dosage_form": "Tablet"
        },

        {
            "medication_code": "MED007",
            "generic_name": "Atorvastatin",
            "brand_name": "Atorva",
            "strength": "10 mg",
            "dosage_form": "Tablet"
        },

        {
            "medication_code": "MED008",
            "generic_name": "Cetirizine",
            "brand_name": "Cetzine",
            "strength": "10 mg",
            "dosage_form": "Tablet"
        }
    ]

    return pd.DataFrame(
        medications
    )


# ============================================================
# PRESCRIPTION GENERATION
# ============================================================

def generate_prescriptions(
    encounters,
    medication_master
):

    prescriptions = []

    medication_codes = (
        medication_master[
            "medication_code"
        ].tolist()
    )

    encounter_records = (
        encounters
        .to_dict("records")
    )

    for i in range(
        1,
        NUM_PRESCRIPTIONS + 1
    ):

        encounter = random.choice(
            encounter_records
        )

        encounter_id = (
            encounter["encounter_id"]
        )

        prescribed_datetime = (
            pd.to_datetime(
                encounter["admission_datetime"]
            )
            +
            timedelta(
                minutes=random.randint(
                    10,
                    180
                )
            )
        )

        prescriptions.append(
            {
                "prescription_id":
                    generate_id("RX", i),

                "encounter_id":
                    encounter_id,

                "medication_code":
                    random.choice(
                        medication_codes
                    ),

                "dose":
                    random.choice(
                        [
                            "1 tablet",
                            "2 tablets",
                            "5 mL",
                            "1 capsule"
                        ]
                    ),

                "frequency":
                    random.choice(
                        [
                            "OD",
                            "BD",
                            "TID",
                            "QID",
                            "HS"
                        ]
                    ),

                "route":
                    random.choice(
                        [
                            "ORAL",
                            "IV",
                            "IM",
                            "TOPICAL"
                        ]
                    ),

                "duration_days":
                    random.choice(
                        [
                            3,
                            5,
                            7,
                            10,
                            14
                        ]
                    ),

                "prescribed_datetime":
                    prescribed_datetime
            }
        )

    return pd.DataFrame(
        prescriptions
    )


# ============================================================
# DISPENSING GENERATION
# ============================================================

def generate_dispensing(
    prescriptions
):

    dispensing_records = []

    prescription_records = (
        prescriptions
        .to_dict("records")
    )

    # Select prescriptions that are actually dispensed.
    # This intentionally means not every prescription
    # must result in a dispensing transaction.

    selected_prescriptions = random.sample(
        prescription_records,
        min(
            NUM_DISPENSING,
            len(prescription_records)
        )
    )

    for i, prescription in enumerate(
        selected_prescriptions,
        start=1
    ):

        prescribed_datetime = (
            pd.to_datetime(
                prescription[
                    "prescribed_datetime"
                ]
            )
        )

        dispensed_datetime = (
            prescribed_datetime
            +
            timedelta(
                minutes=random.randint(
                    15,
                    720
                )
            )
        )

        dispensing_records.append(
            {
                "dispensing_id":
                    generate_id("DS", i),

                "prescription_id":
                    prescription[
                        "prescription_id"
                    ],

                "dispensed_datetime":
                    dispensed_datetime,

                "dispensed_quantity":
                    random.choice(
                        [
                            5,
                            10,
                            15,
                            20,
                            30
                        ]
                    ),

                "dispensing_status":
                    random.choice(
                        [
                            "DISPENSED",
                            "DISPENSED",
                            "PARTIAL",
                            "CANCELLED"
                        ]
                    )
            }
        )

    return pd.DataFrame(
        dispensing_records
    )


# ============================================================
# PRIMARY KEY VALIDATION
# ============================================================

def validate_primary_keys(
    df,
    column_name,
    table_name
):

    if df[column_name].isnull().any():

        raise ValueError(
            f"NULL primary key found: "
            f"{table_name}.{column_name}"
        )

    if df[column_name].duplicated().any():

        duplicates = (
            df.loc[
                df[column_name].duplicated(),
                column_name
            ]
            .tolist()
        )

        raise ValueError(
            f"Duplicate primary key found in "
            f"{table_name}.{column_name}: "
            f"{duplicates}"
        )

    print(
        f"✓ PK validation passed: "
        f"{table_name}.{column_name}"
    )


# ============================================================
# FOREIGN KEY VALIDATION
# ============================================================

def validate_foreign_key(
    child_df,
    child_column,
    parent_df,
    parent_column,
    relationship
):

    child_values = set(
        child_df[
            child_column
        ].dropna()
    )

    parent_values = set(
        parent_df[
            parent_column
        ].dropna()
    )

    invalid_values = (
        child_values - parent_values
    )

    if invalid_values:

        raise ValueError(
            f"FK validation failed: "
            f"{relationship}. "
            f"Invalid values: "
            f"{list(invalid_values)[:10]}"
        )

    print(
        f"✓ FK validation passed: "
        f"{relationship}"
    )


# ============================================================
# DATE VALIDATION
# ============================================================

def validate_dispensing_dates(
    prescriptions,
    dispensing
):

    merged = dispensing.merge(
        prescriptions[
            [
                "prescription_id",
                "prescribed_datetime"
            ]
        ],
        on="prescription_id",
        how="left"
    )

    invalid = (
        merged["dispensed_datetime"]
        <
        merged["prescribed_datetime"]
    )

    if invalid.any():

        raise ValueError(
            "Dispensing date validation failed"
        )

    print(
        "✓ Dispensing date validation passed"
    )


# ============================================================
# BUSINESS VALIDATION
# ============================================================

def validate_business_rules(
    prescriptions,
    dispensing
):

    # Prescription duration must be positive
    invalid_duration = (
        prescriptions["duration_days"]
        <= 0
    )

    if invalid_duration.any():

        raise ValueError(
            "Invalid prescription duration found"
        )

    print(
        "✓ Prescription duration validation passed"
    )

    # Dispensed quantity must be positive
    invalid_quantity = (
        dispensing["dispensed_quantity"]
        <= 0
    )

    if invalid_quantity.any():

        raise ValueError(
            "Invalid dispensing quantity found"
        )

    print(
        "✓ Dispensing quantity validation passed"
    )


# ============================================================
# COMPLETE LIS VALIDATION
# ============================================================

def validate_pharmacy_data(
    encounters,
    medication_master,
    prescriptions,
    dispensing
):

    print()
    print("=" * 60)
    print("PHARMACY DATA VALIDATION")
    print("=" * 60)

    # --------------------------------------------------------
    # Primary Keys
    # --------------------------------------------------------

    validate_primary_keys(
        medication_master,
        "medication_code",
        "medication_master"
    )

    validate_primary_keys(
        prescriptions,
        "prescription_id",
        "prescription"
    )

    validate_primary_keys(
        dispensing,
        "dispensing_id",
        "dispensing"
    )

    # --------------------------------------------------------
    # Foreign Keys
    # --------------------------------------------------------

    validate_foreign_key(
        prescriptions,
        "encounter_id",
        encounters,
        "encounter_id",
        "prescription → encounter"
    )

    validate_foreign_key(
        prescriptions,
        "medication_code",
        medication_master,
        "medication_code",
        "prescription → medication_master"
    )

    validate_foreign_key(
        dispensing,
        "prescription_id",
        prescriptions,
        "prescription_id",
        "dispensing → prescription"
    )

    # --------------------------------------------------------
    # Date validation
    # --------------------------------------------------------

    validate_dispensing_dates(
        prescriptions,
        dispensing
    )

    # --------------------------------------------------------
    # Business validation
    # --------------------------------------------------------

    validate_business_rules(
        prescriptions,
        dispensing
    )

    print()
    print("✓ ALL PHARMACY VALIDATIONS PASSED")


# ============================================================
# WRITE CSV
# ============================================================

def write_csv(
    df,
    filename
):

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    output_path = os.path.join(
        OUTPUT_DIR,
        filename
    )

    df.to_csv(
        output_path,
        index=False
    )

    print(
        f"✓ Written {filename}: "
        f"{len(df)} records"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("CITYCARE HOSPITAL - PHARMACY DATA GENERATOR")
    print("=" * 60)

    print()
    print(
        f"Random seed: {RANDOM_SEED}"
    )

    # --------------------------------------------------------
    # Load EMR
    # --------------------------------------------------------

    encounters = load_emr_data()

    # --------------------------------------------------------
    # Generate master data
    # --------------------------------------------------------

    medication_master = (
        generate_medication_master()
    )

    # --------------------------------------------------------
    # Generate prescriptions
    # --------------------------------------------------------

    prescriptions = (
        generate_prescriptions(
            encounters,
            medication_master
        )
    )

    # --------------------------------------------------------
    # Generate dispensing
    # --------------------------------------------------------

    dispensing = (
        generate_dispensing(
            prescriptions
        )
    )

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    validate_pharmacy_data(
        encounters,
        medication_master,
        prescriptions,
        dispensing
    )

    # --------------------------------------------------------
    # Write files
    # --------------------------------------------------------

    print()

    write_csv(
        medication_master,
        "medication_master.csv"
    )

    write_csv(
        prescriptions,
        "prescription.csv"
    )

    write_csv(
        dispensing,
        "dispensing.csv"
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("PHARMACY GENERATION COMPLETE")
    print("=" * 60)

    print()
    print(
        f"Medication Master : "
        f"{len(medication_master)} records"
    )

    print(
        f"Prescriptions     : "
        f"{len(prescriptions)} records"
    )

    print(
        f"Dispensing        : "
        f"{len(dispensing)} records"
    )

    print()
    print("Output directory:")
    print(OUTPUT_DIR)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()