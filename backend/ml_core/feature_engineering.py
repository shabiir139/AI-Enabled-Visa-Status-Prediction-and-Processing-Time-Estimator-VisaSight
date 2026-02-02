"""
Feature Engineering for VisaSight ML Models

Converts VisaCase structured data into features for ML models.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from sklearn.preprocessing import LabelEncoder, StandardScaler
import json

from config import (
    VISA_TYPES, NATIONALITIES, CONSULATES, 
    SPONSOR_TYPES, COMMON_DOCUMENTS, STATUS_MAPPING
)


class CaseTextEncoder:
    """
    Converts VisaCase structured data into text prompts for transformer models.
    """
    
    def __init__(self):
        self.template = """Nationality: {nationality}
Visa Type: {visa_type}
Consulate: {consulate}
Documents Submitted: {documents}
Document Count: {doc_count}
Sponsor Type: {sponsor_type}
Prior US Travel: {prior_travel}
Days Since Submission: {days_since_submission}"""
    
    def encode(self, case: Dict, reference_date: Optional[datetime] = None) -> str:
        """Convert a single case to text prompt."""
        if reference_date is None:
            reference_date = datetime.now()
        
        # Calculate days since submission
        if isinstance(case.get("submission_date"), str):
            sub_date = datetime.strptime(case["submission_date"], "%Y-%m-%d")
        else:
            sub_date = case.get("submission_date", reference_date)
        
        days_since = (reference_date - sub_date).days
        
        # Format documents
        docs = case.get("documents_submitted", [])
        if isinstance(docs, str):
            docs = json.loads(docs) if docs.startswith("[") else docs.split(",")
        docs_str = ", ".join(docs) if docs else "Not specified"
        
        return self.template.format(
            nationality=case.get("nationality", "Unknown"),
            visa_type=case.get("visa_type", "Unknown"),
            consulate=case.get("consulate", "Unknown"),
            documents=docs_str,
            doc_count=len(docs) if isinstance(docs, list) else case.get("document_count", 0),
            sponsor_type=case.get("sponsor_type", "Unknown"),
            prior_travel="Yes" if case.get("prior_travel") else "No",
            days_since_submission=max(0, days_since),
        )
    
    def encode_batch(self, cases: List[Dict], reference_date: Optional[datetime] = None) -> List[str]:
        """Convert multiple cases to text prompts."""
        return [self.encode(case, reference_date) for case in cases]


class TabularFeatureExtractor:
    """
    Extracts and encodes tabular features for baseline ML models.
    """
    
    def __init__(self):
        self.label_encoders: Dict[str, LabelEncoder] = {}
        self.scaler: Optional[StandardScaler] = None
        self.fitted = False
        
        # Categorical columns
        self.cat_columns = ["nationality", "visa_type", "consulate", "sponsor_type"]
        
        # Numeric columns
        self.num_columns = ["document_count", "prior_travel", "days_since_submission"]
    
    def fit(self, df: pd.DataFrame, reference_date: Optional[datetime] = None) -> 'TabularFeatureExtractor':
        """Fit label encoders and scaler on training data."""
        if reference_date is None:
            reference_date = datetime.now()
        
        # Create working copy with engineered features
        df = self._add_engineered_features(df.copy(), reference_date)
        
        # Fit label encoders for categorical columns
        for col in self.cat_columns:
            if col in df.columns:
                le = LabelEncoder()
                # Add 'Unknown' for unseen values during transform
                unique_vals = list(df[col].unique()) + ["Unknown"]
                le.fit(unique_vals)
                self.label_encoders[col] = le
        
        # Fit scaler for numeric columns
        num_data = df[self.num_columns].values.astype(float)
        self.scaler = StandardScaler()
        self.scaler.fit(num_data)
        
        self.fitted = True
        return self
    
    def transform(self, df: pd.DataFrame, reference_date: Optional[datetime] = None) -> np.ndarray:
        """Transform data to feature matrix."""
        if not self.fitted:
            raise ValueError("FeatureExtractor must be fitted before transform")
        
        if reference_date is None:
            reference_date = datetime.now()
        
        df = self._add_engineered_features(df.copy(), reference_date)
        
        features = []
        
        # Encode categorical columns
        for col in self.cat_columns:
            if col in df.columns:
                le = self.label_encoders[col]
                # Handle unseen values
                encoded = []
                for val in df[col]:
                    if val in le.classes_:
                        encoded.append(le.transform([val])[0])
                    else:
                        encoded.append(le.transform(["Unknown"])[0])
                features.append(np.array(encoded).reshape(-1, 1))
        
        # Scale numeric columns
        num_data = df[self.num_columns].values.astype(float)
        scaled_num = self.scaler.transform(num_data)
        features.append(scaled_num)
        
        return np.hstack(features)
    
    def fit_transform(self, df: pd.DataFrame, reference_date: Optional[datetime] = None) -> np.ndarray:
        """Fit and transform in one step."""
        self.fit(df, reference_date)
        return self.transform(df, reference_date)
    
    def _add_engineered_features(self, df: pd.DataFrame, reference_date: datetime) -> pd.DataFrame:
        """Add engineered features to dataframe."""
        # Days since submission
        if "submission_date" in df.columns:
            df["days_since_submission"] = df["submission_date"].apply(
                lambda x: (reference_date - datetime.strptime(str(x)[:10], "%Y-%m-%d")).days
                if pd.notna(x) else 0
            )
        else:
            df["days_since_submission"] = 0
        
        # Document count
        if "document_count" not in df.columns:
            if "documents_submitted" in df.columns:
                df["document_count"] = df["documents_submitted"].apply(
                    lambda x: len(x) if isinstance(x, list) else 0
                )
            else:
                df["document_count"] = 0
        
        # Prior travel as int
        if "prior_travel" in df.columns:
            df["prior_travel"] = df["prior_travel"].astype(int)
        else:
            df["prior_travel"] = 0
        
        return df
    
    def get_feature_names(self) -> List[str]:
        """Get list of feature names."""
        return self.cat_columns + self.num_columns


def encode_labels(df: pd.DataFrame, column: str = "status") -> np.ndarray:
    """Encode status labels to integers."""
    return df[column].map(STATUS_MAPPING).values


def compute_document_completeness(documents: List[str], visa_type: str) -> float:
    """
    Compute document completeness score (0-1).
    """
    required_docs = {
        "F-1": {"Passport", "DS-160", "Photo", "I-20", "Financial Docs"},
        "H-1B": {"Passport", "DS-160", "Photo", "I-797", "Employment Letter"},
        "B1/B2": {"Passport", "DS-160", "Photo"},
        "L-1": {"Passport", "DS-160", "Photo", "I-797"},
        "O-1": {"Passport", "DS-160", "Photo", "I-797"},
        "J-1": {"Passport", "DS-160", "Photo", "I-20"},
    }
    
    required = required_docs.get(visa_type, {"Passport", "DS-160", "Photo"})
    doc_set = set(documents) if isinstance(documents, list) else set()
    
    if not required:
        return 1.0
    
    matched = len(doc_set.intersection(required))
    return matched / len(required)


if __name__ == "__main__":
    # Test the encoders
    test_case = {
        "nationality": "India",
        "visa_type": "H-1B",
        "consulate": "New Delhi",
        "submission_date": "2026-01-15",
        "documents_submitted": ["Passport", "DS-160", "Photo", "I-797", "Employment Letter"],
        "sponsor_type": "employer",
        "prior_travel": True,
    }
    
    # Test text encoder
    text_encoder = CaseTextEncoder()
    prompt = text_encoder.encode(test_case)
    print("📝 Text Prompt:")
    print(prompt)
    print()
    
    # Test completeness
    score = compute_document_completeness(
        test_case["documents_submitted"],
        test_case["visa_type"]
    )
    print(f"📊 Document completeness: {score:.2%}")
