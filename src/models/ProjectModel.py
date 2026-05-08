from models.DataBaseModel import DataBaseModel
from models.db_schemes.project import Project


class ProjectModel(DataBaseModel):

    def __init__(self, db_client):
        super().__init__(db_client)
        self.collection = self.db_client["projects"]

    async def create_project(self, project: Project):
        result = await self.collection.insert_one(project.dict())
        project.id = str(result.inserted_id)
        return project

    async def get_project(self, project_id: str):
        result = await self.collection.find_one({"project_id": project_id})

        if result is None:
            return None

        # _id for mongo, project_id for us
        return Project(id=str(result["_id"]), project_id=result["project_id"])

    async def get_project_or_create(self, project_id: str):
        project = await self.get_project(project_id)
        if project is None:
            project = await self.create_project(Project(project_id=project_id))
        return project