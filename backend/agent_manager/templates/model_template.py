"""
Database model template for new agent framework.

Add this to your models.py file when implementing a new framework.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Boolean, Text
from sqlalchemy.orm import relationship
from backend.db.session import Base

class NewFrameworkAgentModel(Base):
    """NewFramework specific agent configuration."""
    __tablename__ = "new_framework_agents"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), unique=True)
    field1 = Column(String)
    field2 = Column(JSON, default=lambda: [])
    field3 = Column(Boolean, default=True)
    
    # Relationship back to main agent
    agent = relationship("AgentModel", back_populates="new_framework_config")

    def to_dict(self):
        """Convert the model to a dictionary."""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "field1": self.field1,
            "field2": self.field2,
            "field3": self.field3
        }

    @classmethod
    def from_dict(cls, data, agent_id):
        """Create an instance from a dictionary."""
        return cls(
            agent_id=agent_id,
            field1=data.get("field1", ""),
            field2=data.get("field2", []),
            field3=data.get("field3", True)
        )

# Add this to the AgentModel class in models.py
# new_framework_config = relationship("NewFrameworkAgentModel", back_populates="agent", uselist=False, cascade="all, delete-orphan")

# Then in the AgentModel.to_dict() method, add:
# elif self.framework == "new_framework" and self.new_framework_config:
#     framework_config = {
#         "field1": self.new_framework_config.field1,
#         "field2": self.new_framework_config.field2,
#         "field3": self.new_framework_config.field3
#     }

