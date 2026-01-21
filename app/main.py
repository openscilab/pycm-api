"""Main application file for the FastAPI app."""

from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException
from fastapi.routing import APIRouter
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import Response, HTMLResponse, FileResponse
from sqlalchemy.orm import Session

from . import crud, models, schemas, utils
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)
security = HTTPBasic()
app = FastAPI()


# Dependency
def get_db():
    """
    Dependency to get a database connection.
    
    :return: Database connection
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    """
    Root path of the API.
    
    :return: Message to refer to the API documentation
    """
    return {"message": "Refer to /docs for API documentation."}


@app.get("/users/", response_model=list[schemas.User])
def get_users(credentials: Annotated[HTTPBasicCredentials, Depends(security)],
              skip: int = 0,
              limit: int = 100,
              db: Session = Depends(get_db)):
    """
    Get all users.
    
    :param credentials: HTTP Basic credentials
    :param skip: Number of users to skip from the beginning
    :param limit: Number of users to return
    :param db: Database connection
    :return: List of users
    """
    if not utils.authorize_admin(credentials.username, credentials.password):
        raise HTTPException(status_code=401, detail="Unauthorized access")
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.post("/sign_up/", response_model=schemas.User)
def sign_up(user: schemas.UserSignUp,
                db: Session = Depends(get_db)):
    """
    Sign up a new user.
    
    :param user: User sign up information
    :param db: Database connection
    :return: Created user
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.post("/sign_in/", response_model=schemas.User)
def sign_in(user: schemas.UserSingIn,
              db: Session = Depends(get_db)):
    """
    Sign in a user.

    :param user: User sign in information
    :param db: Database connection
    :return: Signed in user
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.hashed_password != utils.hash_password(user.password):
        raise HTTPException(status_code=400, detail="Invalid password")
    return db_user


#TODO: Add User Sub-APIs
    #   TODO: `/user/increase_credit`


@app.get("/cms/", response_model=list[schemas.ConfusionMatrixResponseBase])
def read_confusion_matrices(credentials: Annotated[HTTPBasicCredentials, Depends(security)],
                            skip: int = 0,
                            limit: int = 100,
                            db: Session = Depends(get_db)):
    """
    Get all confusion matrices.

    :param credentials: HTTP Basic credentials
    :param skip: Number of confusion matrices to skip from the beginning
    :param limit: Number of confusion matrices to return
    :param db: Database connection
    :return: List of confusion matrices
    """
    if not utils.authorize_admin(credentials.username, credentials.password):
        raise HTTPException(status_code=401, detail="Unauthorized access")
    cms = crud.get_cms(db, skip=skip, limit=limit)
    cms = [utils.load_cm(cm_db) for cm_db in cms]
    return cms


@app.post("/cm/create", response_model=schemas.ConfusionMatrix)
def create_confusion_matrix(cm: schemas.ConfusionMatrixCreate,
                            db: Session = Depends(get_db)):
    """
    Create a new confusion matrix.
    
    :param cm: Confusion matrix information
    :param db: Database connection
    :return: Created confusion matrix
    """
    user = crud.get_user_by_api_key(db, cm.api_key)
    if user is None:
        raise HTTPException(status_code=404, detail="Invalid API key")
    return crud.create_cm_for_user(db=db, cm=cm, user=user)


@app.post("/cm/update", response_model=schemas.ConfusionMatrix)
def update_confusion_matrix(cm_uid: str,
                            cm: schemas.ConfusionMatrixCreate,
                            db: Session = Depends(get_db)):
    """
    Update an existing confusion matrix.
    
    :param cm_uid: UID of the confusion matrix
    :param cm: Confusion matrix information
    :param db: Database connection
    :return: Updated confusion matrix
    """
    user = crud.get_user_by_api_key(db, cm.api_key)
    if user is None:
        raise HTTPException(status_code=404, detail="Invalid API key")
    cm_db = crud.get_cm_by_uid(db, cm_uid)
    if cm_db is None:
        raise HTTPException(status_code=404, detail="Confusion matrix not found")
    utils.save_cm(cm_db.uid, cm)
    return cm_db


@app.get("/cm/", response_model=schemas.ConfusionMatrixResponseBase)
def read_confusion_matrix(api_key: str,
                          cm_uid: str,
                          db: Session = Depends(get_db)):
    """
    Get a confusion matrix.

    :param api_key: API key of the owner
    :param cm_uid: UID of the confusion matrix
    :param db: Database connection
    :return: Confusion matrix
    """
    user = crud.get_user_by_api_key(db, api_key)
    if user is None:
        raise HTTPException(status_code=404, detail="Invalid API key")
    cm_db = crud.get_cm_by_uid(db, cm_uid)
    if cm_db is None:
        raise HTTPException(status_code=404, detail="Confusion matrix not found")
    if cm_db.owner_id != user.id:
        raise HTTPException(status_code=401, detail="Unauthorized access")
    return utils.load_cm(cm_db)


@app.delete("/cm/{cm_uid}")
def delete_confusion_matrix(api_key: str,
                            cm_uid: str,
                            db: Session = Depends(get_db)):
    """
    Delete a confusion matrix.

    :param api_key: API key of the owner
    :param cm_uid: UID of the confusion matrix
    :param db: Database connection
    :return: Message indicating the deletion
    """
    user = crud.get_user_by_api_key(db, api_key)
    if user is None:
        raise HTTPException(status_code=404, detail="Invalid API key")
    cm_db = crud.get_cm_by_uid(db, cm_uid)
    if cm_db is None:
        raise HTTPException(status_code=404, detail="Confusion matrix not found")
    if cm_db.owner_id != user.id:
        raise HTTPException(status_code=401, detail="Unauthorized access")
    crud.delete_cm_by_uid(db, cm_uid)
    return {"message": "Confusion matrix deleted"}


@app.get("/cm/report", response_class=HTMLResponse)
def get_confusion_matrix_report(api_key: str,
                                cm_uid: str,
                                db: Session = Depends(get_db)):
    """
    Get the report of a confusion matrix.

    :param api_key: API key of the owner
    :param cm_uid: UID of the confusion matrix
    :param db: Database connection
    :return: Confusion matrix report
    """
    user = crud.get_user_by_api_key(db, api_key)
    if user is None:
        raise HTTPException(status_code=404, detail="Invalid API key")
    cm_db = crud.get_cm_by_uid(db, cm_uid)
    if cm_db is None:
        raise HTTPException(status_code=404, detail="Confusion matrix not found")
    if cm_db.owner_id != user.id:
        raise HTTPException(status_code=401, detail="Unauthorized access")
    return utils.get_html_report(cm_db)


# TODO: Should be test on ubuntu
#   Also try saving file if it keeps failing.
@app.get("/cm/plot", response_class=FileResponse)
def get_confusion_matrix_plot(api_key: str,
                              cm_uid: str,
                              db: Session = Depends(get_db)):
    """
    Get the confusion matrix plot.

    :param api_key: API key of the owner
    :param cm_uid: UID of the confusion matrix
    :param db: Database connection
    :return: Confusion matrix plot
    """
    user = crud.get_user_by_api_key(db, api_key)
    if user is None:
        raise HTTPException(status_code=404, detail="Invalid API key")
    cm_db = crud.get_cm_by_uid(db, cm_uid)
    if cm_db is None:
        raise HTTPException(status_code=404, detail="Confusion matrix not found")
    if cm_db.owner_id != user.id:
        raise HTTPException(status_code=401, detail="Unauthorized access")
    path_to_img = utils.get_plot(cm_db)
    return path_to_img


# TODO: Fix the validation error
@app.post("/curve", response_model=schemas.CurveResponseBase)
def get_curve(curve: schemas.CurveCreate, db: Session = Depends(get_db)):
    """
    Get the curve object for the given input.

    :param curve: Curve information
    :param db: Database connection
    :return: Curve object
    """
    user = crud.get_user_by_api_key(db, curve.api_key)
    if user is None:
        raise HTTPException(status_code=404, detail="Invalid API key")
    curve_obj = utils.get_curve(curve)
    return curve_obj


@app.post("/compare/", response_model=schemas.ConfusionMatrixCompareResponseBase)
def compare_confusion_matrices(compare_request: schemas.ConfusionMatrixCompareRequestBase,
                               db: Session = Depends(get_db)):
    """
    Compare two confusion matrices.
    
    :param compare_request: Confusion matrix compare request
    :param db: Database connection
    :return: Comparison result
    """
    user = crud.get_user_by_api_key(db, compare_request.api_key)
    if user is None:
        raise HTTPException(status_code=404, detail="Invalid API key")
    cms = [crud.get_cm_by_uid(db, cm_uid) for cm_uid in compare_request.cm_uids]
    if any([cm is None for cm in cms]):
        raise HTTPException(status_code=404, detail="Confusion matrix not found")
    if any([cm.owner_id != user.id for cm in cms]):
        raise HTTPException(status_code=401, detail="Unauthorized access")
    return utils.compare_cm(cms)


# One time use, no database storing
@app.post("/mlcm/", response_model=schemas.MultiLabelConfusionMatrixResponseBase)
def create_multi_label_confusion_matrix(mlcm: schemas.MultiLabelConfusionMatrixCreate,
                                        db: Session = Depends(get_db)):
    """
    Create a multi-label confusion matrix.

    :param mlcm: Multi-label confusion matrix information
    :param db: Database connection
    :return: Created multi-label confusion matrix
    """
    user = crud.get_user_by_api_key(db, mlcm.api_key)
    if user is None:
        raise HTTPException(status_code=404, detail="Invalid API key")
    return utils.get_multi_label_cm(mlcm)
