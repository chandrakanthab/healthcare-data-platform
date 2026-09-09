"""
CityCare Hospital Network
Synthetic EMR Data Generator

Generates:
    - Department
    - Provider
    - Patient
    - Appointment
    - Encounter

Purpose:
    Create reproducible synthetic healthcare source-system data
    for the Healthcare Data Platform project.
"""

from __future__ import annotations

import os
import random
from datetime import datetime, timedelta
from decimal import Decimal

import pandas as pd
from faker import Faker


# ============================================================
# CONFIGURATION
# ============================================================

SEED = 42

NUM_PATIENTS = 100
NUM_PROVIDERS = 15
NUM_APPOINTMENTS = 150
NUM_ENCOUNTERS = 120


#OUTPUT_DIR = "sample-data/emr"
REPO_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        ".."
    )
)

OUTPUT_DIR = os.path.join(
    REPO_ROOT,
    "sample-data",
    "emr"
)
# ============================================================
# INITIALIZATION
# ============================================================

random.seed(SEED)
fake = Faker("en_IN")
Faker.seed(SEED)


# ============================================================
# CONSTANTS / REFERENCE DATA
# ============================================================

GENDERS = [
    "Male",
    "Female",
    "Other",
]

BLOOD_GROUPS = [
    "A+",
    "A-",
    "B+",
    "B-",
    "AB+",
    "AB-",
    "O+",
    "O-",
]

SPECIALTIES = [
    "General Medicine",
    "Cardiology",
    "Emergency Medicine",
    "Endocrinology",
    "Neurology",
    "Orthopedics",
    "Pediatrics",
    "Dermatology",
]

ENCOUNTER_TYPES = [
    "OP",
    "IP",
    "ER",
]

ENCOUNTER_STATUSES = [
    "COMPLETED",
    "DISCHARGED",
]

APPOINTMENT_TYPES = [
    "CONSULTATION",
    "FOLLOW_UP",
    "ROUTINE_CHECKUP",
]

APPOINTMENT_STATUSES = [
    "SCHEDULED",
    "COMPLETED",
    "CANCELLED",
    "NO_SHOW",
]

DEPARTMENTS = [
    {
        "department_id": "D001",
        "department_name": "Emergency",
        "department_type": "Clinical",
        "active_flag": True,
    },
    {
        "department_id": "D002",
        "department_name": "Cardiology",
        "department_type": "Clinical",
        "active_flag": True,
    },
    {
        "department_id": "D003",
        "department_name": "General Medicine",
        "department_type": "Clinical",
        "active_flag": True,
    },
    {
        "department_id": "D004",
        "department_name": "Neurology",
        "department_type": "Clinical",
        "active_flag": True,
    },
    {
        "department_id": "D005",
        "department_name": "Orthopedics",
        "department_type": "Clinical",
        "active_flag": True,
    },
    {
        "department_id": "D006",
        "department_name": "Pediatrics",
        "department_type": "Clinical",
        "active_flag": True,
    },
]


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def random_datetime(start_date: datetime, end_date: datetime) -> datetime:
    """
    Generate a random datetime between start_date and end_date.
    """

    delta = end_date - start_date

    random_seconds = random.randint(
        0,
        int(delta.total_seconds())
    )

    return start_date + timedelta(seconds=random_seconds)


def generate_id(prefix: str, number: int, width: int = 6) -> str:
    """
    Generate standardized source-system identifiers.

    Example:
        P000001
        PR000001
        E000001
    """

    return f"{prefix}{number:0{width}d}"


# ============================================================
# DEPARTMENT GENERATION
# ============================================================

def generate_departments() -> pd.DataFrame:
    """
    Generate EMR department master data.
    """

    df = pd.DataFrame(DEPARTMENTS)

    return df


# ============================================================
# PROVIDER GENERATION
# ============================================================

def generate_providers(
    departments_df: pd.DataFrame,
) -> pd.DataFrame:

    providers = []

    clinical_department_ids = departments_df[
        departments_df["department_type"] == "Clinical"
    ]["department_id"].tolist()

    for i in range(1, NUM_PROVIDERS + 1):

        specialty = random.choice(SPECIALTIES)

        provider = {
            "provider_id": generate_id("PR", i),
            "provider_name": f"Dr. {fake.first_name()} {fake.last_name()}",
            "specialty": specialty,
            "qualification": random.choice(
                ["MBBS", "MD", "MS", "DM"]
            ),
            "years_experience": random.randint(2, 30),
            "active_flag": True,
        }

        providers.append(provider)

    return pd.DataFrame(providers)


# ============================================================
# PATIENT GENERATION
# ============================================================

def generate_patients() -> pd.DataFrame:

    patients = []

    start_registration = datetime(2020, 1, 1)
    end_registration = datetime(2026, 8, 1)

    for i in range(1, NUM_PATIENTS + 1):

        date_of_birth = fake.date_of_birth(
            minimum_age=1,
            maximum_age=90,
        )

        registration_date = random_datetime(
            start_registration,
            end_registration,
        ).date()

        patient = {
            "patient_id": generate_id("P", i),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "date_of_birth": date_of_birth,
            "gender": random.choice(GENDERS),
            "phone_number": fake.phone_number(),
            "email": fake.email(),
            "address": fake.street_address(),
            "city": fake.city(),
            "state": fake.state(),
            "postal_code": fake.postcode(),
            "blood_group": random.choice(BLOOD_GROUPS),
            "registration_date": registration_date,
        }

        patients.append(patient)

    return pd.DataFrame(patients)


# ============================================================
# APPOINTMENT GENERATION
# ============================================================

def generate_appointments(
    patients_df: pd.DataFrame,
    providers_df: pd.DataFrame,
    departments_df: pd.DataFrame,
) -> pd.DataFrame:

    appointments = []

    patient_ids = patients_df["patient_id"].tolist()
    provider_ids = providers_df["provider_id"].tolist()
    department_ids = departments_df["department_id"].tolist()

    start_datetime = datetime(2026, 1, 1)
    end_datetime = datetime(2026, 8, 18)

    for i in range(1, NUM_APPOINTMENTS + 1):

        appointment_datetime = random_datetime(
            start_datetime,
            end_datetime,
        )

        appointment = {
            "appointment_id": generate_id("A", i),
            "patient_id": random.choice(patient_ids),
            "provider_id": random.choice(provider_ids),
            "department_id": random.choice(department_ids),
            "appointment_datetime": appointment_datetime,
            "appointment_type": random.choice(APPOINTMENT_TYPES),
            "status": random.choice(APPOINTMENT_STATUSES),
        }

        appointments.append(appointment)

    return pd.DataFrame(appointments)


# ============================================================
# ENCOUNTER GENERATION
# ============================================================

def generate_encounters(
    patients_df: pd.DataFrame,
    providers_df: pd.DataFrame,
    departments_df: pd.DataFrame,
) -> pd.DataFrame:

    encounters = []

    patient_ids = patients_df["patient_id"].tolist()
    provider_ids = providers_df["provider_id"].tolist()
    department_ids = departments_df["department_id"].tolist()

    start_datetime = datetime(2026, 1, 1)
    end_datetime = datetime(2026, 8, 18)

    complaints = [
        "Chest pain",
        "Fever",
        "Headache",
        "Abdominal pain",
        "Back pain",
        "Routine follow-up",
        "Shortness of breath",
        "Joint pain",
        "Cough",
        "Diabetes follow-up",
    ]

    for i in range(1, NUM_ENCOUNTERS + 1):

        encounter_type = random.choice(ENCOUNTER_TYPES)

        admission_datetime = random_datetime(
            start_datetime,
            end_datetime,
        )

        # OP/ER usually have shorter encounter duration.
        # IP encounters can span multiple days.

        if encounter_type == "IP":

            duration_hours = random.randint(24, 120)

        else:

            duration_hours = random.randint(1, 8)

        discharge_datetime = (
            admission_datetime
            + timedelta(hours=duration_hours)
        )

        if encounter_type == "IP":
            status = "DISCHARGED"
        else:
            status = "COMPLETED"

        encounter = {
            "encounter_id": generate_id("E", i),
            "patient_id": random.choice(patient_ids),
            "provider_id": random.choice(provider_ids),
            "department_id": random.choice(department_ids),
            "encounter_type": encounter_type,
            "admission_datetime": admission_datetime,
            "discharge_datetime": discharge_datetime,
            "encounter_status": status,
            "chief_complaint": random.choice(complaints),
        }

        encounters.append(encounter)

    return pd.DataFrame(encounters)


# ============================================================
# VALIDATION FUNCTIONS
# ============================================================

def validate_foreign_key(
    child_df: pd.DataFrame,
    child_column: str,
    parent_df: pd.DataFrame,
    parent_column: str,
    relationship_name: str,
) -> None:

    parent_values = set(
        parent_df[parent_column].astype(str)
    )

    child_values = set(
        child_df[child_column].astype(str)
    )

    invalid_values = child_values - parent_values

    if invalid_values:

        raise ValueError(
            f"Foreign key validation failed for "
            f"{relationship_name}. "
            f"Invalid values: {sorted(invalid_values)}"
        )

    print(
        f"✓ FK validation passed: {relationship_name}"
    )


def validate_primary_key(
    df: pd.DataFrame,
    column: str,
    table_name: str,
) -> None:

    if df[column].isna().any():

        raise ValueError(
            f"{table_name}.{column} contains NULL values."
        )

    duplicate_count = df[column].duplicated().sum()

    if duplicate_count > 0:

        raise ValueError(
            f"{table_name}.{column} contains "
            f"{duplicate_count} duplicate values."
        )

    print(
        f"✓ PK validation passed: {table_name}.{column}"
    )


def validate_emr(
    patients_df: pd.DataFrame,
    providers_df: pd.DataFrame,
    departments_df: pd.DataFrame,
    appointments_df: pd.DataFrame,
    encounters_df: pd.DataFrame,
) -> None:

    print("\n" + "=" * 60)
    print("EMR DATA VALIDATION")
    print("=" * 60)

    # Primary keys

    validate_primary_key(
        patients_df,
        "patient_id",
        "patient",
    )

    validate_primary_key(
        providers_df,
        "provider_id",
        "provider",
    )

    validate_primary_key(
        departments_df,
        "department_id",
        "department",
    )

    validate_primary_key(
        appointments_df,
        "appointment_id",
        "appointment",
    )

    validate_primary_key(
        encounters_df,
        "encounter_id",
        "encounter",
    )

    # Appointment foreign keys

    validate_foreign_key(
        appointments_df,
        "patient_id",
        patients_df,
        "patient_id",
        "appointment → patient",
    )

    validate_foreign_key(
        appointments_df,
        "provider_id",
        providers_df,
        "provider_id",
        "appointment → provider",
    )

    validate_foreign_key(
        appointments_df,
        "department_id",
        departments_df,
        "department_id",
        "appointment → department",
    )

    # Encounter foreign keys

    validate_foreign_key(
        encounters_df,
        "patient_id",
        patients_df,
        "patient_id",
        "encounter → patient",
    )

    validate_foreign_key(
        encounters_df,
        "provider_id",
        providers_df,
        "provider_id",
        "encounter → provider",
    )

    validate_foreign_key(
        encounters_df,
        "department_id",
        departments_df,
        "department_id",
        "encounter → department",
    )

    # Date validation

    invalid_encounters = encounters_df[
        encounters_df["discharge_datetime"]
        < encounters_df["admission_datetime"]
    ]

    if len(invalid_encounters) > 0:

        raise ValueError(
            "Encounter date validation failed."
        )

    print(
        "✓ Encounter date validation passed"
    )

    print("\n✓ ALL EMR VALIDATIONS PASSED")


# ============================================================
# WRITE CSV FILES
# ============================================================

def write_emr_data(
    departments_df: pd.DataFrame,
    providers_df: pd.DataFrame,
    patients_df: pd.DataFrame,
    appointments_df: pd.DataFrame,
    encounters_df: pd.DataFrame,
) -> None:

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True,
    )

    datasets = {
        "department.csv": departments_df,
        "provider.csv": providers_df,
        "patient.csv": patients_df,
        "appointment.csv": appointments_df,
        "encounter.csv": encounters_df,
    }

    for filename, df in datasets.items():

        output_path = os.path.join(
            OUTPUT_DIR,
            filename,
        )

        df.to_csv(
            output_path,
            index=False,
        )

        print(
            f"✓ Written {filename}: "
            f"{len(df):,} records"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("CITYCARE HOSPITAL - EMR DATA GENERATOR")
    print("=" * 60)

    print(f"\nRandom seed: {SEED}")

    # --------------------------------------------------------
    # 1. Generate master/reference data
    # --------------------------------------------------------

    departments_df = generate_departments()

    providers_df = generate_providers(
        departments_df
    )

    # --------------------------------------------------------
    # 2. Generate patients
    # --------------------------------------------------------

    patients_df = generate_patients()

    # --------------------------------------------------------
    # 3. Generate transactional data
    # --------------------------------------------------------

    appointments_df = generate_appointments(
        patients_df,
        providers_df,
        departments_df,
    )

    encounters_df = generate_encounters(
        patients_df,
        providers_df,
        departments_df,
    )

    # --------------------------------------------------------
    # 4. Validate
    # --------------------------------------------------------

    validate_emr(
        patients_df,
        providers_df,
        departments_df,
        appointments_df,
        encounters_df,
    )

    # --------------------------------------------------------
    # 5. Write files
    # --------------------------------------------------------

    write_emr_data(
        departments_df,
        providers_df,
        patients_df,
        appointments_df,
        encounters_df,
    )

    # --------------------------------------------------------
    # 6. Summary
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("EMR GENERATION COMPLETE")
    print("=" * 60)

    print(f"Patients      : {len(patients_df):,}")
    print(f"Providers     : {len(providers_df):,}")
    print(f"Departments   : {len(departments_df):,}")
    print(f"Appointments  : {len(appointments_df):,}")
    print(f"Encounters    : {len(encounters_df):,}")

    print(f"\nOutput directory:")
    print(OUTPUT_DIR)


if __name__ == "__main__":
    main()