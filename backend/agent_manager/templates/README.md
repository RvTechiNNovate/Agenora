# Adding a New Agent Framework

This guide walks you through the process of adding a new agent framework to the dashboard.

## Steps to Add a New Framework

1. **Create the Directory Structure**

   Create a new directory under `backend/agent_manager/providers/` with your framework name:

   ```bash
   mkdir -p backend/agent_manager/providers/your_framework_name
   ```

2. **Create the Configuration Class**

   Copy the `config_template.py` to your new directory and customize it:

   ```bash
   cp backend/agent_manager/templates/config_template.py backend/agent_manager/providers/your_framework_name/config.py
   ```

   Edit the file to define the configuration parameters specific to your framework.

3. **Create the Manager Class**

   Copy the `new_framework_template.py` to your new directory and customize it:

   ```bash
   cp backend/agent_manager/templates/new_framework_template.py backend/agent_manager/providers/your_framework_name/your_framework_name_agent.py
   ```

   Implement all the required methods for your framework.

4. **Add Database Models**

   Add your framework-specific model to `backend/models.py`, following the structure in `model_template.py`.
   
   Don't forget to add the relationship to the `AgentModel` class:

   ```python
   your_framework_config = relationship("YourFrameworkAgentModel", back_populates="agent", uselist=False, cascade="all, delete-orphan")
   ```

   Also update the `to_dict` method in `AgentModel` to include your framework's configuration.

5. **Register the Model**

   In `backend/main.py`, make sure your model is imported and registered with the database.

6. **Add Frontend Support**

   Update the frontend to display framework-specific fields:

   - Add your framework to the dropdown in `frontend/index.html`
   - Add field definitions in `frontend/scripts/framework-fields.js`
   - Handle the form submission in `frontend/app.js`

7. **Create __init__.py**

   Create an `__init__.py` file in your framework directory to make it a proper Python package:

   ```bash
   touch backend/agent_manager/providers/your_framework_name/__init__.py
   ```

8. **Test Your Implementation**

   Start the application and test creating, starting, and querying agents with your new framework.

## Framework Implementation Checklist

- [ ] Directory structure created
- [ ] Configuration class implemented
- [ ] Manager class implemented with all required methods
- [ ] Database models added
- [ ] Relationships added to AgentModel
- [ ] Models registered with the database
- [ ] Frontend support added
- [ ] __init__.py file created
- [ ] Test cases created
- [ ] Documentation updated

## Common Issues and Troubleshooting

- **Import errors**: Make sure all imports are correct and dependencies are installed
- **Database errors**: Check that your models are properly defined and relationships are correctly set up
- **Framework-specific errors**: Handle exceptions properly and provide meaningful error messages

## Example Implementation

```python
# Example of a minimal implementation
from backend.agent_manager.base import BaseAgentManager

class MyFrameworkManager(BaseAgentManager):
    @property
    def framework_name(self) -> str:
        return "my_framework"
    
    # Implement all required methods...
    
manager = MyFrameworkManager()
```

Refer to the templates and existing implementations for more details.
