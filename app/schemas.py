import enum
from typing import List, Dict, Set
from pydantic import BaseModel
import pycm


class CurveTypes(enum.Enum):
    ROC = "ROC"
    PR = "PR"


class UserAuthenticatedBaseModel(BaseModel):
    """Base scheme class for authenticated user"""
    api_key: str


class ConfusionMatrixCreate(UserAuthenticatedBaseModel):
    """Scheme class for creating a confusion matrix"""
    actual_vector: List[float]
    predicted_vector: List[float]


class ConfusionMatrixDataBase(BaseModel):
    """Base scheme class for confusion matrix data"""
    accuracy: float | str | None = None
    precision: float | str | None = None
    recall: float | str | None = None
    f1: float | str | None = None
    confusion_matrix: List[List[int]] | None = None

    def __init__(self, cm: pycm.ConfusionMatrix, **data):
        super().__init__(**data)
        self.accuracy = cm.Overall_ACC
        self.precision = cm.PPV_Macro
        self.recall = cm.TPR_Macro
        self.f1 = cm.F1_Macro
        self.confusion_matrix = cm.to_array().tolist()


class ConfusionMatrix(BaseModel):
    """Scheme class for confusion matrix"""
    uid: str

    class Config:
        from_attributes = True


class ConfusionMatrixResponseBase(ConfusionMatrix, ConfusionMatrixDataBase):
    """Base scheme class for confusion matrix responses"""
    pass


class ConfusionMatrixCompareRequestBase(UserAuthenticatedBaseModel):
    """Base scheme class for confusion matrix comparison requests"""
    cm_uids: List[str]


class ConfusionMatrixCompareResponseBase(BaseModel):
    """Base scheme class for confusion matrix comparison responses"""
    cm_uids: List[str]
    best_name: str | None = None
    cm_scores: Dict[str, Dict[str, float]] | None = None
    cm_orders: List[str] | None = None


class MultiLabelConfusionMatrixCreate(UserAuthenticatedBaseModel):
    """Scheme class for creating a multi-label confusion matrix"""
    actual_vector: List[Set[str]]
    predicted_vector: List[Set[str]]
    classes: List[str] | None = None


class MultiLabelConfusionMatrixResponseBase(BaseModel):
    """Base scheme class for multi-label confusion matrix responses"""
    multihot_actual: List[List[int]]
    multihot_predicted: List[List[int]]
    classes: List[str]
    cm_by_classes: Dict[str, ConfusionMatrixDataBase]
    cm_by_samples: Dict[int, ConfusionMatrixDataBase]


class CurveCreate(UserAuthenticatedBaseModel):
    """Scheme class for creating a curve"""
    type: CurveTypes
    actual_vector: List[float] | List[str] | List[int]
    probability_vector: List[List[float]]
    classes: List[str] | List[int] | None = None


class CurveDataBase(BaseModel):
    """Base scheme class for curve data"""
    thresholds: List[float] | None = None
    auc_trp: Dict[str, float] | None = None

    def __init__(self, curve: pycm.Curve, **data):
        super().__init__(**data)
        self.thresholds = list(map(float, curve.thresholds))
        self.auc_trp = {x: float(y) for x, y in curve.area().items()}


class CurveResponseBase(CurveDataBase):
    """Base scheme class for curve responses"""
    pass


class UserBase(BaseModel):
    """Base scheme class for user"""
    email: str


class UserSingIn(UserBase):
    """Scheme class for user sign in"""
    password: str


class UserSignUp(UserSingIn):
    """Scheme class for user sign up"""
    pass


class User(UserBase):
    """Scheme class for user"""
    id: int
    api_key: str
    credit: float
    is_active: bool
    cms: list[ConfusionMatrix] = []

    class Config:
        from_attributes = True

