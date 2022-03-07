from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView

from tasks.views import (
    session_storage_view,
    GenericTaskView,
    GenericTaskCreateView,
    GenericTaskUpdateView,
    GenericTaskDeleteView,
    GenericTaskDetailView,
    UserCreateView,
    UserLoginView,
    GenericAllTaskView,
    GenericCompletedTaskView,
    GenericTaskCompleteView,
    index,
    reportSettings
)

from tasks.apiviews import TaskListAPI, TaskViewSet, TaskHistoryViewSet

from rest_framework_nested import routers

router = routers.SimpleRouter()
router.register(r"api/v1/task", TaskViewSet)

task_router = routers.NestedSimpleRouter(router, r"api/v1/task", lookup="task")
task_router.register(r"history", TaskHistoryViewSet, basename="history")

urlpatterns = [
    path("", index),
    path("admin/", admin.site.urls),
    path(r"", include(router.urls)),
    path(r"", include(task_router.urls)),
    path("tasksapi/", TaskListAPI.as_view()),
    path("tasks/", GenericTaskView.as_view(), name="Tasks"),
    path("all-tasks/", GenericAllTaskView.as_view(), name="All Tasks"),
    path("completed-tasks/", GenericCompletedTaskView.as_view(),
         name="Completed Tasks"),
    path("create-task/", GenericTaskCreateView.as_view(), name="Add Task"),
    path("update-task/<pk>/", GenericTaskUpdateView.as_view(), name="Update Task"),
    path("delete-task/<pk>/", GenericTaskDeleteView.as_view(), name="Delete Task"),
    path("details-task/<pk>/", GenericTaskDetailView.as_view(), name="View Task"),
    path("complete-task/<pk>/", GenericTaskCompleteView.as_view(),
         name="Mark a task as completed"),
    path("user/signup/", UserCreateView.as_view()),
    path("user/login/", UserLoginView.as_view()),
    path("user/logout/", LogoutView.as_view()),
    path("sessiontest/", session_storage_view),
    path("reportSettings/", reportSettings.as_view())
]
