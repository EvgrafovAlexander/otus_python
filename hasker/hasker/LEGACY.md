def add_question(request):
    """Добавление нового вопроса"""
    if request.method == "POST":
        form = AddQuestionForm(request.POST)
        if form.is_valid():
            try:
                question = form.save(commit=False)
                question.author = request.user
                question.save()
                tags = parse_tags(request.POST.get("tags"))
                if len(tags) > 3:
                    messages.info(request, "Only three tags can be set.")
                for tag in tags[:3]:
                    tag = Tag(name=tag)
                    tag.save()
                    question.tags.add(tag)
                return redirect("posts:detail", pk=question.id)
            except Exception:
                form.add_error(None, "Failed to add question")
    else:
        form = AddQuestionForm()
    return render(request, "posts/add_question.html", {"form": form})