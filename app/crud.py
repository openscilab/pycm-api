from sqlalchemy.orm import Session

from . import models, schemas, utils


def get_user(db: Session, user_id: int) -> models.User:
    """
    Get a user by ID.
    
    :param db: Database connection
    :param user_id: User ID
    :return: User
    """
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> models.User:
    """
    Get a user by email.

    :param db: Database connection
    :param email: User email
    :return: User
    """
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_api_key(db: Session, api_key: str) -> models.User:
    """
    Get a user by API key.

    :param db: Database connection
    :param api_key: API key
    :return: User
    """
    return db.query(models.User).filter(models.User.api_key == api_key).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[models.User]:
    """
    Get all users.

    :param db: Database connection
    :param skip: Number of users to skip from the beginning
    :param limit: Number of users to return
    :return: List of users
    """
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserSignUp) -> models.User:
    """
    Create a new user.

    :param db: Database connection
    :param user: User sign-up information
    :return: New user
    """
    db_user = models.User(
        email=user.email,
        hashed_password=utils.hash_password(user.password),
        api_key=utils.generate_api_key()
        )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_cms(db: Session, skip: int = 0, limit: int = 100) -> list[models.ConfusionMatrix]:
    """
    Get all confusion matrices.

    :param db: Database connection
    :param skip: Number of confusion matrices to skip from the beginning
    :param limit: Number of confusion matrices to return
    :return: List of confusion matrices
    """
    return db.query(models.ConfusionMatrix).offset(skip).limit(limit).all()


def create_cm_for_user(db: Session, cm: schemas.ConfusionMatrixCreate, user: models.User) -> models.ConfusionMatrix:
    """
    Create a new confusion matrix for a user.
    
    :param db: Database connection
    :param cm: Confusion matrix information
    :param user: User
    :return: Created confusion matrix
    """
    cm_uid = utils.generate_cm_uid(user.email)
    utils.save_cm(cm_uid, cm)
    db_cm = models.ConfusionMatrix(uid=cm_uid, owner_id=user.id)
    db.add(db_cm)
    db.commit()
    db.refresh(db_cm)
    return db_cm


def get_cm_by_uid(db: Session, cm_uid: str) -> models.ConfusionMatrix:
    """
    Get a confusion matrix by UID.

    :param db: Database connection
    :param cm_uid: Confusion matrix UID
    :return: Confusion matrix
    """
    return db.query(models.ConfusionMatrix).filter(models.ConfusionMatrix.uid == cm_uid).first()


def delete_cm_by_uid(db: Session, cm_uid: str):
    """
    Delete a confusion matrix by UID.

    :param db: Database connection
    :param cm_uid: Confusion matrix UID
    :return: None
    """
    db_cm = get_cm_by_uid(db, cm_uid)
    db.delete(db_cm)
    db.commit()
