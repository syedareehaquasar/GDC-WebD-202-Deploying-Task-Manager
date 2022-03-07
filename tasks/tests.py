from django.test import TestCase

from tasks.models import Task, User

class TestTaskManager(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test", email="test@test.com", password="test123"
        )

    def test_add_task(self):
        task = Task.objects.create(
            title="create task test",
            description="abc description",
            priority=1,
            user=self.user,
        )
        self.assertTrue(
            Task.objects.filter(user=self.user, title="create task test").exists()
        )
        self.assertEqual(str(task), "create task test")

    def test_task_priority_does_not_increment(self):
        task1 = Task.objects.create(
            title="test title",
            description="test description",
            priority=1,
            user=self.user,
        )
        Task.objects.create(
            title="test title",
            description="test description",
            priority=1,
            status="COMPLETED",
            user=self.user,
        )
        task1 = Task.objects.get(pk=task1.pk)
        self.assertEqual(task1.priority, 1)


