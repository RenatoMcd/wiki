from django.shortcuts import render
from django import forms

from . import util
import markdown
import random

class SearchForm(forms.Form):
    search = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Search Encyclopedia'})
    )

class NewPageForm(forms.Form):
    title = forms.CharField(label="Title")
    mkd_content = forms.CharField(
        label="Content",
        widget=forms.Textarea(attrs={
            'placeholder':'Insert Markdown Content Here'})
        )


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": SearchForm(),
    })

def entry(request, entry):
    md_file = util.get_entry(entry)

    if md_file == None:
        return render(request, "encyclopedia/error.html")
    else:
        file = markdown.markdown(md_file)
        return render(request, "encyclopedia/entry.html", {
            "entry": file,
            "title": entry,
            "form": SearchForm()
    })

def search(request):
    if request.method == "POST":
        form = SearchForm(request.POST)

        if form.is_valid():
            query = form.cleaned_data["search"]
            queried_entries = []

            for item in util.list_entries():
                if query.lower() == item.lower():
                    return entry(request, item)
                
                else:
                    if query.lower() in item.lower():
                        queried_entries.append(item)

                                    
            return render(request, "encyclopedia/index.html", {
                "entries": queried_entries,
                "form": SearchForm()
            })
    
    else:
        return render(request, "encyclopedia/index.html", {
            "form": SearchForm()
        })


def new(request):

    if request.method == "POST":
        np_form = NewPageForm(request.POST)

        if np_form.is_valid():
            title = np_form.cleaned_data["title"]
            content = np_form.cleaned_data["mkd_content"]

            for item in util.list_entries():
                if title.lower() == item.lower():
                   return render(request, "encyclopedia/alreadyExists.html", {
                       "form": SearchForm(),
                       "entry": title
                   })
            
            util.save_entry(title, content)
            return entry(request, title)

    return render(request, "encyclopedia/new.html", {
        "form": SearchForm(),
        "new_page": NewPageForm()
    })

def edit(request, title):

    if request.method == "POST":
        edit_form = NewPageForm(request.POST)

        if edit_form.is_valid():
            title = edit_form.cleaned_data["title"]
            content = edit_form.cleaned_data["mkd_content"]

            util.save_entry(title, content)
            return entry(request, title)

    content = util.get_entry(title)
    data = {
        "mkd_content": content,
        "title": title
    }

    return render(request, "encyclopedia/edit.html", {
        "form": SearchForm(),
        "edit_form": NewPageForm(data),
        "entry": title
    })


def random_page(request):
    return entry(request, random.choice(util.list_entries()))