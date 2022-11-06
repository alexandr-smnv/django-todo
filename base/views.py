from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import redirect

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy

from base.models import Task


class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    fields = '__all__'
    # редирект при авторизации
    redirect_authenticated_user = True

    # url редиректа
    def get_success_url(self):
        return reverse_lazy('tasks')


class RegisterPage(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        # сохранение пользователя в базе
        user = form.save()
        if user is not None:
            # авторизация пользователя
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)

    # если пользователь авторизован, он не может зайти на страницу регистрации
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage, self).get(*args, **kwargs)


# LoginRequiredMixin - для проверки авторизации

class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'

    # Изменение контекста
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user)
        context['count'] = context['tasks'].filter(complete=False).count()

        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            context['tasks'] = context['tasks'].filter(title__startswith=search_input)

        context['search_input'] = search_input
        return context


class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task'
    template_name = 'base/task_detail.html'


class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    # поля редактирования в форме из модели Task
    fields = ['title', 'description', 'complete']
    # при успешном заполнении формы - редирект на список задач
    success_url = reverse_lazy('tasks')

    # если форма валидна, добавить в поле user авторизованного пользователя
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)


class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')


class TaskDelete(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')

