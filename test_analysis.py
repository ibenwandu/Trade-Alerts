"""Manual test script to trigger a full analysis cycle"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import TradeAlertSystem

def main():
    print("=" * 60)
    print("Manual Analysis Test")
    print("=" * 60)
    print("\nInitializing Trade Alert System...")
    
    try:
        system = TradeAlertSystem()
        print("\n✅ System initialized")
        print("\nRunning full analysis cycle...")
        print("-" * 60)
        
        # Run full analysis
        system._run_full_analysis()
        
        print("-" * 60)
        print("\n✅ Analysis complete!")
        print("Check your email for recommendations.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

