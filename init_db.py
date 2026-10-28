
from app.database import Base, engine
from app.models.debug_history import DebugHistory

Base.metadata.create_all(bind=engine)

print("TraceIQ database tables created successfully.")
