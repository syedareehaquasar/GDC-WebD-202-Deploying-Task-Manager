from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.forms import ModelForm, ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from django import forms

from tasks.models import Task, Report


class TaskCreateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].widget.attrs[
            "class"
        ] = "p-2 mb-2 bg-gray-200/75 rounded-lg w-full"
        self.fields["description"].widget.attrs[
            "class"
        ] = "p-2 mb-2 bg-gray-200/75 rounded-lg w-full"
        self.fields["priority"].widget.attrs[
            "class"
        ] = "p-2 mb-2 bg-gray-200/75 rounded-lg"
        self.fields["status"].widget.attrs["class"] = "p-1 mb-2 bg-gray-200/75"
        self.fields["completed"].widget.attrs[
            "class"
        ] = "p-5 mb-2 bg-gray-200/75 rounded-lg"

    def clean_title(self):
        title = self.cleaned_data["title"]
        if len(title) < 5:
            raise ValidationError("Title too short.")
        return title

    class Meta:
        model = Task
        fields = ["title", "description", "priority", "status", "completed"]


class AuthorizedTaskManager(LoginRequiredMixin):
    login_url = "/user/login"
    success_url = "/tasks"
    model = Task
    def get_queryset(self):
        return Task.objects.filter(deleted=False, user=self.request.user)


class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs[
            "class"
        ] = "p-1 mb-2 bg-gray-200/75 rounded-lg w-full"
        self.fields["password1"].widget.attrs[
            "class"
        ] = "p-1 mb-2 bg-gray-200/75 rounded-lg w-full"
        self.fields["password2"].widget.attrs[
            "class"
        ] = "p-1 mb-2 bg-gray-200/75 rounded-lg w-full"


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs[
            "class"
        ] = "p-1 mb-2 bg-gray-200/75 rounded-lg w-full"
        self.fields["password"].widget.attrs[
            "class"
        ] = "p-1 mb-2 bg-gray-200/75 rounded-lg w-full"


class UserLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = "user_login.html"
    success_url = "/user/login/"


class UserCreateView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "user_signup.html"
    success_url = "/user/login/"


def session_storage_view(request):
    total_views = request.session.get("total_views", 0)
    request.session["total_views"] = total_views + 1
    return HttpResponse(
        f"total views is {total_views} and the user is {request.user} and the user is {request.user.is_authenticated}"
    )


def count_tasks(self, request):
    completed_tasks = Task.objects.filter(
        status__in=["COMPLETED"], deleted=False, user=self.request.user
    ).count()
    total_tasks = Task.objects.filter(
        deleted=False, user=self.request.user).count()
    context = {"completed_tasks": completed_tasks, "total_tasks": total_tasks}
    return render(request, "base_tabs.html", context)


class GenericTaskCompleteView(AuthorizedTaskManager, UpdateView):
    model = Task
    success_url = "/all-tasks"


class GenericTaskDeleteView(AuthorizedTaskManager, DeleteView):
    model = Task
    template_name = "task_delete.html"
    success_url = "/all-tasks"


class GenericTaskDetailView(AuthorizedTaskManager, DetailView):
    model = Task
    template_name = "task_details.html"


def handle_priority(form, user):
    priority_to_add = form.cleaned_data["priority"]
    tasks_present = Task.objects.filter(
        user=user, priority__gte=priority_to_add, completed=False, deleted=False
    ).order_by("priority")
    for task in tasks_present:
        if task.priority == priority_to_add:
            task.priority += 1
            priority_to_add += 1
        else:
            break
    Task.objects.bulk_update(tasks_present, ["priority"])


class GenericTaskUpdateView(AuthorizedTaskManager, UpdateView):
    model = Task
    form_class = TaskCreateForm
    template_name = "task_update.html"
    success_url = "/all-tasks"

    def form_valid(self, form):
        if "priority" in form.changed_data:
            handle_priority(form, self.request.user)
        self.object = form.save()
        self.object.user = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class GenericTaskCreateView(LoginRequiredMixin, CreateView):
    form_class = TaskCreateForm
    template_name = "add_task.html"
    success_url = "/all-tasks"

    def form_valid(self, form):
        handle_priority(form, self.request.user)
        self.object = form.save()
        self.object.user = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("/tasks")
    else:
        return HttpResponseRedirect("/user/login")


class GenericTaskView(ListView, LoginRequiredMixin):

    queryset = Task.objects.filter(completed=False, deleted=False)
    template_name = "tasks.html"
    context_object_name = "tasks"
    paginate_by = 5

    def get_queryset(self):
        search_term = self.request.GET.get("search")
        tasks = Task.objects.filter(
            status__in=["PENDING", "IN_PROGRESS"], deleted=False, user=self.request.user
        ).order_by("priority")
        if search_term:
            tasks = tasks.filter(title__icontains=search_term)
        return tasks


class GenericAllTaskView(LoginRequiredMixin, ListView):
    queryset = Task.objects.filter(deleted=False)
    template_name = "all.html"
    context_object_name = "tasks"
    paginate_by = 5

    def get_queryset(self):
        return Task.objects.filter(deleted=False, user=self.request.user).order_by(
            "priority"
        )


class GenericCompletedTaskView(LoginRequiredMixin, ListView):
    queryset = Task.objects.filter(status=("COMPLETED"), deleted=False)
    template_name = "completed_tasks.html"
    context_object_name = "tasks"
    paginate_by = 5

    def get_queryset(self):
        res = Task.objects.filter(
            status__in=["COMPLETED"], deleted=False, user=self.request.user
        )
        return res.order_by("priority")

class ReportForm(forms.ModelForm):

    error_css_class = "is-invalid"
    required_css_class = "is-required"

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("label_suffix", "")
        super().__init__(*args, **kwargs)

    class Meta:
        model = Report
        fields = ("time", "is_disabled")
        widgets = {
            "time": forms.TimeInput(
                attrs={"class": "form-control", "type": "time"}
            ),
            "is_disabled": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

class reportSettings(LoginRequiredMixin, UpdateView):
    model = Report
    form_class = ReportForm
    template_name = "report.html"
    success_url = "/tasks/"

    def get_object(self):
        return Report.objects.get_or_create(user=self.request.user)[0]
