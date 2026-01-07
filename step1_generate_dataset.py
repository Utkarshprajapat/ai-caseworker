"""
STEP 1: DATASET CREATION
========================
Creates a realistic synthetic dataset for welfare cases.

In production, this would be stored in:
- Azure Data Lake Gen2 (for large-scale data)
- Azure SQL Database (for structured queries)
- Azure Synapse Analytics (for analytics workloads)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_synthetic_welfare_dataset(n_samples=1000, seed=42):
    """
    Generate synthetic welfare case data.
    
    Parameters:
    -----------
    n_samples : int
        Number of cases to generate
    seed : int
        Random seed for reproducibility
    
    Returns:
    --------
    pd.DataFrame
        Dataset with welfare case information
    """
    np.random.seed(seed)
    random.seed(seed)
    
    # Generate citizen IDs
    citizen_ids = [f"CIT_{i:06d}" for i in range(1, n_samples + 1)]
    
    # Generate income (somewhat correlated with risk)
    # Higher income might indicate fraud, very low income might indicate exclusion
    base_income = np.random.normal(15000, 5000, n_samples)
    income = np.maximum(5000, base_income)  # Minimum income floor
    
    # Last document update (months ago)
    # Older updates = higher risk
    last_update = np.random.exponential(6, n_samples)
    last_update = np.minimum(last_update, 36)  # Cap at 36 months
    
    # Scheme types
    scheme_types = np.random.choice(
        ['pension', 'subsidy', 'ration'],
        n_samples,
        p=[0.4, 0.35, 0.25]
    )
    
    # Past benefit interruptions (0-5)
    interruptions = np.random.poisson(0.5, n_samples)
    interruptions = np.minimum(interruptions, 5)
    
    # Generate risk level based on features (ground truth for training)
    risk_levels = []
    risk_scores = []
    
    for i in range(n_samples):
        score = 0
        
        # Income-based risk (very high or very low income)
        if income[i] > 30000:
            score += 30  # Potential fraud
        elif income[i] < 8000:
            score += 20  # Potential exclusion
        
        # Document update risk
        if last_update[i] > 12:
            score += 25
        elif last_update[i] > 6:
            score += 15
        
        # Interruption risk
        score += interruptions[i] * 8
        
        # Scheme-specific risk
        if scheme_types[i] == 'pension' and income[i] > 25000:
            score += 15
        
        # Add some randomness
        score += np.random.normal(0, 10)
        score = max(0, min(100, score))  # Clamp to 0-100
        
        risk_scores.append(round(score, 2))
        
        # Categorize risk level
        if score < 30:
            risk_levels.append('low')
        elif score < 60:
            risk_levels.append('medium')
        else:
            risk_levels.append('high')
    
    # Create DataFrame
    df = pd.DataFrame({
        'citizen_id': citizen_ids,
        'income': np.round(income, 2),
        'last_document_update_months': np.round(last_update, 1),
        'scheme_type': scheme_types,
        'past_benefit_interruptions': interruptions,
        'risk_score': risk_scores,
        'risk_level': risk_levels
    })
    
    return df

if __name__ == "__main__":
    print("=" * 60)
    print("STEP 1: GENERATING SYNTHETIC WELFARE DATASET")
    print("=" * 60)
    
    # Generate dataset
    dataset = generate_synthetic_welfare_dataset(n_samples=1000)
    
    # Save to CSV
    # In Azure: This would be saved to Azure Data Lake Gen2 or Azure SQL
    csv_path = "welfare_cases_dataset.csv"
    dataset.to_csv(csv_path, index=False)
    print(f"\n[OK] Dataset saved to: {csv_path}")
    print(f"[OK] Total cases: {len(dataset)}")
    
    # Print sample rows
    print("\n" + "=" * 60)
    print("SAMPLE DATA (First 10 rows):")
    print("=" * 60)
    print(dataset.head(10).to_string())
    
    # Print statistics
    print("\n" + "=" * 60)
    print("DATASET STATISTICS:")
    print("=" * 60)
    print(f"\nRisk Level Distribution:")
    print(dataset['risk_level'].value_counts())
    print(f"\nRisk Score Statistics:")
    print(dataset['risk_score'].describe())
    print(f"\nScheme Type Distribution:")
    print(dataset['scheme_type'].value_counts())
    
    print("\n" + "=" * 60)
    print("[OK] Dataset generation complete!")
    print("=" * 60)
    print("\nNOTE: In production, this data would be stored in:")
    print("  - Azure Data Lake Gen2 (for large-scale storage)")
    print("  - Azure SQL Database (for structured queries)")
    print("  - Azure Synapse Analytics (for analytics)")

