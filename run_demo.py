"""
Quick demo runner script.
Runs all steps in sequence for easy demonstration.
"""

import subprocess
import sys
import os

def run_step(step_number, script_name, description):
    """Run a step and handle errors."""
    print("\n" + "=" * 60)
    print(f"STEP {step_number}: {description}")
    print("=" * 60)
    
    if not os.path.exists(script_name):
        print(f"[ERROR] Script not found: {script_name}")
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            check=True,
            capture_output=False
        )
        print(f"[OK] Step {step_number} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Step {step_number} failed: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Error running step {step_number}: {e}")
        return False

def main():
    """Run all steps in sequence."""
    print("=" * 60)
    print("AI CASEWORKER DEMO - COMPLETE SETUP")
    print("=" * 60)
    
    steps = [
        (1, "step1_generate_dataset.py", "Generate Synthetic Dataset"),
        (2, "step2_ml_risk_model.py", "Train ML Risk Model"),
    ]
    
    for step_num, script, desc in steps:
        success = run_step(step_num, script, desc)
        if not success:
            print(f"\n[ERROR] Demo setup failed at step {step_num}")
            print("Please run steps manually to see detailed error messages.")
            sys.exit(1)
    
    print("\n" + "=" * 60)
    print("[OK] DEMO SETUP COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Start the backend API:")
    print("   python step4_backend_api.py")
    print("\n2. Open the frontend dashboard:")
    print("   Open step6_frontend_dashboard.html in your web browser")
    print("\n3. Start analyzing cases!")
    print("=" * 60)

if __name__ == "__main__":
    main()

