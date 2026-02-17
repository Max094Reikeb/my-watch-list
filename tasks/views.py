import json
import urllib.request

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404

from .forms import TaskForm
from .models import Task

TMDB_API_KEY = "66bbbec74be84702eebab7c21a8e3830"

PROVIDERS = {
    "netflix": 8,
    "prime": 10,
    "apple": 2,
}


# Create your views here.
@login_required
def index(request):
    tasks = Task.objects.filter(user=request.user)
    form = TaskForm()
    platform = request.GET.get("platform") or request.POST.get("platform")

    if request.method == 'POST':
        if request.POST.get("Import") == "import":
            if platform not in PROVIDERS:
                return redirect('/')

            shows = fetch_top_tv_shows(PROVIDERS[platform])

            for show in shows[:10]:
                title = show.get("name") or show.get("original_name")
                if not title:
                    continue
                Task.objects.get_or_create(user=request.user, title=title)

            return redirect('/')

        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            form.save()
        return redirect('/')

    context = {
        "tasks": tasks,
        "form": form,
        "platform": platform,
    }

    return render(request, 'tasks/list.html', context)


@login_required
def updateTask(request, pk):
    task = get_object_or_404(Task, id=pk, user=request.user)
    form = TaskForm(instance=task)

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect("list")

    context = {"form": form}
    return render(request, "tasks/update_task.html", context)


@login_required
def deleteTask(request, pk):
    item = get_object_or_404(Task, id=pk, user=request.user)

    if request.method == "POST":
        item.delete()
        return redirect("list")

    context = {"item": item}
    return render(request, "tasks/delete.html", context)


def fetch_top_tv_shows(provider_id):
    url = (
        "https://api.themoviedb.org/3/discover/tv"
        f"?api_key={TMDB_API_KEY}"
        "&with_genres=10759"
        "&watch_region=FR"
        f"&with_watch_providers={provider_id}"
        "&sort_by=vote_average.desc"
        "&page=1"
    )

    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())

    # TMDB always returns 20 → keep only 10
    return data.get("results", [])[:10]


def signup(request):
    if request.user.is_authenticated:
        return redirect("list")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("list")
    else:
        form = UserCreationForm()

    return render(request, "registration/signup.html", {"form": form})
