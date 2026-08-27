from datetime import datetime
from typing import Optional

import strawberry
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.types import Info

from app.models import Task, TaskPriority, TaskStatus


TaskStatusGQL = strawberry.enum(TaskStatus)
TaskPriorityGQL = strawberry.enum(TaskPriority)

# Defines the TaskType for the GraphQL schema
@strawberry.type #@strawberry.type is a decorator that defines a GraphQL type
class TaskType:
    id: int
    title: str
    description: Optional[str]
    status: TaskStatusGQL
    priority: TaskPriorityGQL
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, task: Task) -> "TaskType":
        return cls(
            id=task.id,
            title=task.title,
            description=task.description,
            status=TaskStatusGQL(task.status.value),
            priority=TaskPriorityGQL(task.priority.value),
            due_date=task.due_date,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )


@strawberry.input
class CreateTaskInput:
    title: str
    description: Optional[str] = None
    status: TaskStatusGQL = TaskStatusGQL.TODO
    priority: TaskPriorityGQL = TaskPriorityGQL.MEDIUM
    due_date: Optional[datetime] = None


@strawberry.input
class UpdateTaskInput:
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatusGQL] = None
    priority: Optional[TaskPriorityGQL] = None
    due_date: Optional[datetime] = None


async def get_db(info: Info) -> AsyncSession:
    return info.context["session"]


@strawberry.type
class Query:
    @strawberry.field
    async def tasks(self, info: Info) -> list[TaskType]:
        db = await get_db(info)
        result = await db.execute(select(Task).order_by(Task.created_at.desc()))
        return [TaskType.from_model(t) for t in result.scalars().all()]

    @strawberry.field
    async def task(self, info: Info, id: int) -> Optional[TaskType]:
        db = await get_db(info)
        result = await db.execute(select(Task).where(Task.id == id))
        task = result.scalar_one_or_none()
        return TaskType.from_model(task) if task else None


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_task(self, info: Info, input: CreateTaskInput) -> TaskType:
        db = await get_db(info)
        task = Task(
            title=input.title,
            description=input.description,
            status=TaskStatus(input.status.value),
            priority=TaskPriority(input.priority.value),
            due_date=input.due_date,
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return TaskType.from_model(task)

    @strawberry.mutation
    async def update_task(
        self, info: Info, id: int, input: UpdateTaskInput
    ) -> Optional[TaskType]:
        db = await get_db(info)
        result = await db.execute(select(Task).where(Task.id == id))
        task = result.scalar_one_or_none()
        if not task:
            return None

        if input.title is not None:
            task.title = input.title
        if input.description is not None:
            task.description = input.description
        if input.status is not None:
            task.status = TaskStatus(input.status.value)
        if input.priority is not None:
            task.priority = TaskPriority(input.priority.value)
        if input.due_date is not None:
            task.due_date = input.due_date

        await db.commit()
        await db.refresh(task)
        return TaskType.from_model(task)

    @strawberry.mutation
    async def delete_task(self, info: Info, id: int) -> bool:
        db = await get_db(info)
        result = await db.execute(select(Task).where(Task.id == id))
        task = result.scalar_one_or_none()
        if not task:
            return False
        await db.delete(task)
        await db.commit()
        return True


schema = strawberry.Schema(query=Query, mutation=Mutation)
