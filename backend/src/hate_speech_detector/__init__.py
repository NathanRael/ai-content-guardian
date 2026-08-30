"""Hate speech detector with dialectal bias audit."""


def main() -> None:
    """Entry point for the CLI script."""
    print("Use the pipeline scripts in src/hate_speech_detector/:")
    print("  python -m hate_speech_detector.data")
    print("  python -m hate_speech_detector.train")
    print("  python -m hate_speech_detector.evaluate")
    print("  python -m hate_speech_detector.audit")
    print("  python -m hate_speech_detector.explain")
    print("Dashboard: streamlit run src/hate_speech_detector/dashboard.py")
