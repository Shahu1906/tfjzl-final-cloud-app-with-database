from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Course, Enrollment, Question, Choice, Submission


def extract_answers(request):
    submitted_answers = []
    for key in request.POST:
        if key.startswith('choice'):
            submitted_answers.append(int(request.POST[key]))
    return submitted_answers


def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    enrollment = Enrollment.objects.get(user=request.user, course=course)
    submission = Submission.objects.create(enrollment=enrollment)
    submission.choices.set(extract_answers(request))
    return HttpResponseRedirect(
        reverse('onlinecourse:show_exam_result', args=(course.id, submission.id)))


def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    selected_ids = [c.id for c in submission.choices.all()]

    total_score = 0
    possible = 0
    for question in course.question_set.all():
        possible += question.grade
        if question.is_get_score(selected_ids):
            total_score += question.grade

    context = {
        'course': course,
        'selected_ids': selected_ids,
        'grade': int(total_score / possible * 100) if possible else 0,
    }
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)