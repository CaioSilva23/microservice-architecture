from shared.database import SessionLocal


def get_db():
    """
    Dependency that provides a database session for each request.
    Yields:
        SessionLocal: A database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
