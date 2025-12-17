import os

class Config:
    EMAIL = os.getenv("NAUKRI_EMAIL")
    PASSWORD = os.getenv("NAUKRI_PASSWORD")
    KEYWORDS = ["DevOps Engineer"]
    LOCATION = "Bangalore"
    APPLY_LIMIT = 10
