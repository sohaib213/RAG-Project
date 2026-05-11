from models.DataBaseModel import DataBaseModel
from models.db_schemes.project import Project


class ProjectModel(DataBaseModel):

    def __init__(self, db_client):
        super().__init__(db_client)
        self.collection = self.db_client["projects"]

    async def create_project(self, project: Project):
        # Insert the project into MongoDB and return it with its new id
        result = await self.collection.insert_one(project.dict())
        project.id = str(result.inserted_id)
        return project

    async def get_project(self, project_id: str):
        # Find a project by its project_id field
        result = await self.collection.find_one({"project_id": project_id})

        if result is None:
            return None

        # Convert MongoDB's _id to a plain string and return a Project object
        return Project(id=str(result["_id"]), project_id=result["project_id"])

    async def get_project_or_create(self, project_id: str):
        # Try to find the project first
        project = await self.get_project(project_id)

        # If it doesn't exist yet, create it
        if project is None:
            project = await self.create_project(Project(project_id=project_id))

        return project