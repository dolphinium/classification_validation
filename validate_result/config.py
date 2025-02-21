# config.py
class Config:
    SYSTEM_OUTPUT_PATH = "data/system_output.csv"
    ANNOTATED_PATH = "data/annotated.csv"
    CLASSIFICATION_CHOICES = [
        ("", "-- None --"),
        ("Potential Customer", "Potential Customer"),
        ("Unnecessary Call", "Unnecessary Call")
    ]
    CATEGORY_CHOICES = [
        ("", "-- None --"),
        ("Guaranteed Product", "Guaranteed Product"),
        ("Irrelevant Sector", "Irrelevant Sector"),
        ("Installation", "Installation"),
        ("Service Fee Rejected", "Service Fee Rejected"),
        ("Customer Asked for Price", "Customer Asked for Price"),
        ("Repeat Customer Call", "Repeat Customer Call")
    ]