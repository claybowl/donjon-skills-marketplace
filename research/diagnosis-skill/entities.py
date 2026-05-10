from typing_extensions import TypedDict, Annotated, List, Sequence
from enum import Enum

class Category(Enum):
    anatomy: "ANATOMY"
    behavioral_environmental_social: "BEHAVIORAL_ENVIRONMENTAL_SOCIAL"
    medical_condition: "MEDICAL_CONDITION"
    medication: "MEDICATION"
    protected_health_information: "PROTECTED_HEALTH_INFORMATION"
    test_treatment_procedure: "TEST_TREATMENT_PROCEDURE"
    time_expression: "TIME_EXPRESSION"


class AttributeType(Enum):
    dosage: "DOSAGE"
    duration: "DURATION"
    form: "FORM"
    frequency: "FREQUENCY"
    rate: "RATE"
    route_or_mode: "ROUTE_OR_MODE"
    strenght: "STRENGTH"


class Attribute(TypedDict):
    begin_offset: int 
    end_offset: int 
    text: str
    traits: List[], 
    score: float 
    type: AttributeType
    id: int
    relationship_score: float


class DetectionEntity(TypedDict):
    category: Category
    begin_offset: int
    end_offset: int
    traits: List[]
    text: str
    score: float
    attributes


class SymptomsOutputState(TypedDict):
    high_confidence: List[DetectionEntity]
    confidence_below_treshold: List[DetectionEntity]


class PatientBrief(TypedDict):
    patient_id: str
    timestamp: datetime

    conversation: List[Message]
    detections: List[DetectionEntity]

    medication: List[Medication]
    medical_record: MedicalRecord
    substance_use: SubstanceUse


class Message(TypedDict):
    timestamp: datetime
    actor: 'PATIENT' | 'SYSTEM'
    message: str


class SubstanceUse(TypedDict, total=False):
    tobacco: str
    alcohol: str
    other: str


class Medication(TypedDict, total=False):
    name: str
    dosage: str
    frequency: str
    prescribedBy: str
    startDate: date
    recentChanges: List[MedicationChange]


class MedicationChange(TypedDict):
    date: date
    change: str
    reason: str
