import json
import urllib.request

from django.shortcuts import render, redirect

from .forms import *

TMDB_API_KEY = "66bbbec74be84702eebab7c21a8e3830"

PROVIDERS = {
    "netflix": 8,
    "prime": 10,
    "apple": 2,
}


# Create your views here.
def index(request):
    tasks = Task.objects.all()
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
                Task.objects.get_or_create(title=title)

            return redirect('/')

        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('/')

    context = {
        "tasks": tasks,
        "form": form,
        "platform": platform,
    }

    return render(request, 'tasks/list.html', context)


def updateTask(request, pk):
    task = Task.objects.get(id=pk)
    form = TaskForm(instance=task)

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('/')

    context = {'form': form}
    return render(request, 'tasks/update_task.html', context)


def deleteTask(request, pk):
    item = Task.objects.get(id=pk)

    if request.method == "POST":
        item.delete()
        return redirect('/')

    context = {'item': item}
    return render(request, 'tasks/delete.html', context)


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
