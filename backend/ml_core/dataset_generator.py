"""
Synthetic VisaCase Dataset Generator

Generates realistic visa application data for model training and testing.
Uses deterministic seeding for reproducibility.
"""

import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional
import json

from config import (
    DATASET_CONFIG, VISA_TYPES, VISA_TYPE_WEIGHTS,
    NATIONALITIES, CONSULATES, SPONSOR_TYPES, 
    COMMON_DOCUMENTS, STATUS_LABELS, DATA_DIR
)


def set_seed(seed: int = 42):
    """Set random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)


def generate_processing_time(visa_type: str, status: str, consulate: str) -> int:
    """Generate realistic processing time based on visa type and outcome."""
    # Base processing times by visa type (in days)
    base_times = {
        "F-1": (30, 60),
        "H-1B": (60, 180),
        "B1/B2": (14, 45),
        "L-1": (45, 120),
        "O-1": (30, 90),
        "J-1": (21, 50),
    }
    
    min_days, max_days = base_times.get(visa_type, (30, 90))
    
    # Adjust based on status
    if status == "approved":
        processing_time = random.randint(min_days, int(max_days * 0.8))
    elif status == "rfe":
        processing_time = random.randint(int(max_days * 0.7), int(max_days * 1.3))
    else:  # denied
        processing_time = random.randint(min_days, int(max_days * 0.6))
    
    # Add consulate-specific variance
    consulate_factor = hash(consulate) % 20 - 10  # -10 to +10 days
    processing_time += consulate_factor
    
    return max(7, processing_time)


def generate_status(
    visa_type: str,
    nationality: str,
    prior_travel: bool,
    doc_count: int,
    sponsor_type: str
) -> str:
    """Generate visa status with realistic probability distribution."""
    # Base approval rates by visa type
    base_approval = {
        "F-1": 0.85,
        "H-1B": 0.70,
        "B1/B2": 0.80,
        "L-1": 0.75,
        "O-1": 0.65,
        "J-1": 0.88,
    }
    
    approval_prob = base_approval.get(visa_type, 0.75)
    
    # Adjust based on factors
    if prior_travel:
        approval_prob += 0.05
    
    if doc_count >= 8:
        approval_prob += 0.05
    elif doc_count <= 4:
        approval_prob -= 0.10
    
    if sponsor_type in ["employer", "university"]:
        approval_prob += 0.03
    
    # Nationality adjustments (simplified)
    high_approval_countries = ["Canada", "United Kingdom", "Germany", "Japan"]
    if nationality in high_approval_countries:
        approval_prob += 0.05
    
    approval_prob = min(0.95, max(0.40, approval_prob))
    
    # Generate status
    rand = random.random()
    if rand < approval_prob:
        return "approved"
    elif rand < approval_prob + 0.15:
        return "rfe"
    else:
        return "denied"


def generate_documents(visa_type: str) -> list:
    """Generate list of submitted documents based on visa type."""
    # Required documents by type
    required = {
        "F-1": ["Passport", "DS-160", "Photo", "Fee Receipt", "I-20", "Financial Docs", "Transcripts"],
        "H-1B": ["Passport", "DS-160", "Photo", "Fee Receipt", "I-797", "Employment Letter", "Resume"],
        "B1/B2": ["Passport", "DS-160", "Photo", "Fee Receipt", "Invitation Letter"],
        "L-1": ["Passport", "DS-160", "Photo", "Fee Receipt", "I-797", "Employment Letter"],
        "O-1": ["Passport", "DS-160", "Photo", "Fee Receipt", "I-797", "Resume"],
        "J-1": ["Passport", "DS-160", "Photo", "Fee Receipt", "I-20"],
    }
    
    base_docs = required.get(visa_type, ["Passport", "DS-160", "Photo", "Fee Receipt"])
    
    # Randomly add or remove some docs
    if random.random() < 0.2:  # 20% chance of missing a doc
        if len(base_docs) > 4:
            base_docs = base_docs[:-1]
    
    # Maybe add extra docs
    extra_docs = ["Travel Itinerary", "Bank Statement", "Tax Returns", "Property Docs"]
    for doc in extra_docs:
        if random.random() < 0.3:
            base_docs.append(doc)
    
    return list(set(base_docs))


def generate_visa_case(case_id: int, base_date: datetime) -> dict:
    """Generate a single visa case."""
    # Random visa type with weights
    visa_type = random.choices(VISA_TYPES, weights=VISA_TYPE_WEIGHTS)[0]
    
    # Random attributes
    nationality = random.choice(NATIONALITIES)
    consulate = random.choice(CONSULATES)
    sponsor_type = random.choice(SPONSOR_TYPES)
    prior_travel = random.random() < 0.35
    
    # Generate documents
    documents = generate_documents(visa_type)
    
    # Generate status
    status = generate_status(visa_type, nationality, prior_travel, len(documents), sponsor_type)
    
    # Dates
    days_offset = random.randint(0, 365)
    submission_date = base_date - timedelta(days=days_offset + 90)
    processing_time = generate_processing_time(visa_type, status, consulate)
    decision_date = submission_date + timedelta(days=processing_time)
    
    return {
        "id": f"case_{case_id:06d}",
        "nationality": nationality,
        "visa_type": visa_type,
        "consulate": consulate,
        "submission_date": submission_date.strftime("%Y-%m-%d"),
        "decision_date": decision_date.strftime("%Y-%m-%d"),
        "processing_days": processing_time,
        "documents_submitted": documents,
        "document_count": len(documents),
        "sponsor_type": sponsor_type,
        "prior_travel": prior_travel,
        "status": status,
    }


def generate_dataset(
    n_samples: int = 10000,
    seed: int = 42,
    save: bool = True
) -> pd.DataFrame:
    """
    Generate synthetic visa case dataset.
    
    Args:
        n_samples: Number of cases to generate
        seed: Random seed for reproducibility
        save: Whether to save to CSV
        
    Returns:
        DataFrame with generated cases
    """
    set_seed(seed)
    
    base_date = datetime(2026, 1, 29)
    
    cases = []
    for i in range(n_samples):
        case = generate_visa_case(i, base_date)
        cases.append(case)
    
    df = pd.DataFrame(cases)
    
    # Sort by submission date for time-based splitting
    df = df.sort_values("submission_date").reset_index(drop=True)
    
    if save:
        # Save CSV
        csv_path = DATA_DIR / "synthetic_visa_cases.csv"
        df.to_csv(csv_path, index=False)
        print(f"✅ Saved {n_samples} cases to {csv_path}")
        
        # Save metadata
        metadata = {
            "n_samples": n_samples,
            "seed": seed,
            "generated_at": datetime.now().isoformat(),
            "columns": list(df.columns),
            "status_distribution": df["status"].value_counts().to_dict(),
            "visa_type_distribution": df["visa_type"].value_counts().to_dict(),
        }
        
        meta_path = DATA_DIR / "dataset_metadata.json"
        with open(meta_path, "w") as f:
            json.dump(metadata, f, indent=2)
        print(f"✅ Saved metadata to {meta_path}")
    
    return df


def split_dataset(df: pd.DataFrame) -> tuple:
    """
    Split dataset using time-based strategy.
    
    Returns:
        (train_df, val_df, test_df)
    """
    n = len(df)
    train_end = int(n * DATASET_CONFIG["train_ratio"])
    val_end = train_end + int(n * DATASET_CONFIG["val_ratio"])
    
    train_df = df.iloc[:train_end].copy()
    val_df = df.iloc[train_end:val_end].copy()
    test_df = df.iloc[val_end:].copy()
    
    print(f"📊 Dataset split: Train={len(train_df)}, Val={len(val_df)}, Test={len(test_df)}")
    
    return train_df, val_df, test_df


if __name__ == "__main__":
    print("🚀 Generating synthetic visa case dataset...")
    df = generate_dataset(n_samples=DATASET_CONFIG["synthetic_size"])
    
    print("\n📊 Dataset Statistics:")
    print(f"Total samples: {len(df)}")
    print(f"\nStatus distribution:\n{df['status'].value_counts()}")
    print(f"\nVisa type distribution:\n{df['visa_type'].value_counts()}")
    print(f"\nProcessing time stats:\n{df['processing_days'].describe()}")
    
    train, val, test = split_dataset(df)
