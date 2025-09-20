from enum import Enum

class QuestionType(Enum):
    INFORMATION_SEARCH = 'information_search'
    FACT_VERIFICATION = 'fact_verification'
    UNKNOWN = 'unknown'