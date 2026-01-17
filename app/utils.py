"""Utility functions for the application."""

import hashlib
import secrets
import os
import pycm
import io
import matplotlib.pyplot as plt
from typing import List

from .schemas import ConfusionMatrix, ConfusionMatrixResponseBase
from .schemas import ConfusionMatrixCreate, ConfusionMatrixCompareResponseBase
from .schemas import ConfusionMatrixDataBase
from .schemas import MultiLabelConfusionMatrixCreate
from .schemas import MultiLabelConfusionMatrixResponseBase
from .schemas import CurveCreate, CurveResponseBase
from .params import PATH2CMS, PATH2REPORTS, PATH2PLOTS
from .params import PASSWORD_SALT
from .params import API_KEY_LENGTH, USER_UID_LENGHT
from .params import CM_OBJECT_NAME_MAIN_LENGTH
from .params import PYCM_ADMIN, PYCM_ADMIN_PASSWORD
from .errors import PyCMAPISaveFileError


def hash_password(password: str) -> str:
    """
    Hash a password using MD5 and a salt.
    
    :param password: Password to hash
    :return: Hashed password
    """
    salted_password = password + PASSWORD_SALT
    return hashlib.md5(salted_password.encode()).hexdigest()


def generate_api_key() -> str:
    """
    Generate an API key.
    
    :return: API key
    """
    return secrets.token_urlsafe(API_KEY_LENGTH)


def generate_cm_uid(user_email: str) -> str:
    """
    Generate a confusion matrix UID.
    
    :param user_email: User email
    :return: Confusion matrix UID
    """
    generated_key = secrets.token_urlsafe(CM_OBJECT_NAME_MAIN_LENGTH)
    user_key = hashlib.md5(user_email.encode()).hexdigest()[:USER_UID_LENGHT]
    return f"{user_key}:{generated_key}"


def authorize_admin(username: str, password: str) -> bool:
    """
    Authorize an admin.
    
    :param username: Admin username
    :param password: Admin password
    :return: True if the admin is authorized, False otherwise
    """
    return username == PYCM_ADMIN and password == PYCM_ADMIN_PASSWORD


def save_cm(uid: str, cm: ConfusionMatrixCreate) -> None:
    """
    Save a confusion matrix.

    :param uid: UID of the confusion matrix
    :param cm: Confusion matrix information
    :return: None
    """
    cm = pycm.ConfusionMatrix(actual_vector=cm.actual_vector,
                              predict_vector=cm.predicted_vector)
    result = cm.save_obj(os.path.join(PATH2CMS, uid))
    if not result['Status']:
        raise PyCMAPISaveFileError()


def load_cm(cm_db: ConfusionMatrix) -> ConfusionMatrixResponseBase:
    """
    Load a confusion matrix.

    :param cm_db: Confusion matrix database object
    :return: Confusion matrix
    """
    with open(os.path.join(PATH2CMS, cm_db.uid) + '.obj', "r") as file:
        cm = pycm.ConfusionMatrix(file=file)
        return ConfusionMatrixResponseBase(uid=cm_db.uid, cm=cm)


def get_plot(cm_db: ConfusionMatrix) -> str:
    """
    Get the plot of the confusion matrix.

    :param cm_db: Confusion matrix database object
    :return: Plot path
    """
    with open(os.path.join(PATH2CMS, cm_db.uid) + '.obj', "r") as file:
        cm = pycm.ConfusionMatrix(file=file)
        img_path = os.path.join(PATH2PLOTS, cm_db.uid) + '.png'
        if os.path.exists(img_path):
            return img_path
        else:
            cm.plot()
            plt.savefig(img_path)
            return img_path


def get_curve(curve_create: CurveCreate) -> CurveResponseBase:
    """
    Create a curve and return it.

    :param curve_create: Curve create information
    :return: Curve object
    """
    CurveModule = pycm.Curve
    if curve_create.type == "ROC":
        CurveModule = pycm.ROCCurve
    elif curve_create.type == "PR":
        CurveModule = pycm.PRCurve
    curve = CurveModule(actual_vector=curve_create.actual_vector,
                        probs=curve_create.probability_vector,
                        classes=curve_create.classes)
    return CurveResponseBase(curve=curve)


def get_html_report(cm_db: ConfusionMatrix) -> str:
    """
    Get the HTML report of the confusion matrix.

    :param cm_db: Confusion matrix database object
    :return: HTML report
    """
    with open(os.path.join(PATH2CMS, cm_db.uid) + '.obj', "r") as file:
        cm = pycm.ConfusionMatrix(file=file)
        html_path = os.path.join(PATH2REPORTS, cm_db.uid) + '.html'
        if os.path.exists(html_path):
            with open(html_path, "r") as html_file:
                return html_file.read()
        else:
            cm.save_html(os.path.join(PATH2REPORTS, cm_db.uid))
            with open(html_path, "r") as html_file:
                return html_file.read()


def compare_cm(cms_db: List[ConfusionMatrix]) -> ConfusionMatrixCompareResponseBase:
    """
    Compare given confusion matrices.

    :param cms_db: List of confusion matrices
    :return: Comparison result
    """
    cms_dict = {}
    for cm_db in cms_db:
        with open(os.path.join(PATH2CMS, cm_db.uid) + '.obj', "r") as file:
            cm = pycm.ConfusionMatrix(file=file)
            cms_dict[cm_db.uid] = cm
    compare = pycm.Compare(cms_dict)
    return ConfusionMatrixCompareResponseBase(cm_uids=[cm_db.uid for cm_db in cms_db],
                                              best_name=compare.best_name,
                                              cm_scores=compare.scores,
                                              cm_orders=compare.sorted)


def get_multi_label_cm(mlcm_req: MultiLabelConfusionMatrixCreate) -> MultiLabelConfusionMatrixResponseBase:
    """
    Get a multi-label confusion matrix.

    :param mlcm_req: Multi-label confusion matrix information
    :return: Multi-label confusion matrix
    """
    mlcm = pycm.MultiLabelCM(actual_vector=mlcm_req.actual_vector,
                             predict_vector=mlcm_req.predicted_vector,
                             classes=mlcm_req.classes)
    return MultiLabelConfusionMatrixResponseBase(multihot_actual=mlcm.actual_vector_multihot,
                                                 multihot_predicted=mlcm.predict_vector_multihot,
                                                 classes=mlcm.classes,
                                                 cm_by_classes={class_name: ConfusionMatrixDataBase(cm=mlcm.get_cm_by_class(class_name)) for class_name in mlcm.classes},
                                                 cm_by_samples={sample: ConfusionMatrixDataBase(cm=mlcm.get_cm_by_sample(sample)) for sample in range(len(mlcm.actual_vector))})
