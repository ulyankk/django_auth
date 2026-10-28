from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Count
import json

from .forms import AcademicGroupForm, CourseForm, DepartmentForm
from .models import AcademicGroup, Course, Department, StudentProfile


def is_methodist(user):
    return user.groups.filter(name='Методист').exists()


@login_required
def profile(request):
    return render(request, 'profile.html', {
        'is_methodist': is_methodist(request.user),
    })


# ---------- ДАШБОРД ----------

@login_required
def dashboard(request):
    """Страница дашбордов с данными из БД и фильтром по факультету."""

    dept_filter = request.GET.get('department', '')

    # Список всех факультетов для выпадающего фильтра
    all_departments = Department.objects.all()

    # Дашборд 1: количество курсов по факультетам
    dept_stats = Department.objects.annotate(
        course_count=Count('courses')
    ).order_by('name')

    if dept_filter:
        dept_stats = dept_stats.filter(id=dept_filter)

    dept_labels = [d.name for d in dept_stats]
    dept_counts = [d.course_count for d in dept_stats]

    # KPI-карточки
    total_courses = Course.objects.count()
    total_departments = Department.objects.count()
    total_groups = AcademicGroup.objects.count()
    total_students = StudentProfile.objects.count()

    # Дашборд 3: студенты по учебным группам
    group_stats = AcademicGroup.objects.annotate(
        student_count=Count('students')
    ).order_by('name')

    if dept_filter:
        group_stats = group_stats.filter(department_id=dept_filter)

    group_labels = [g.name for g in group_stats]
    group_counts = [g.student_count for g in group_stats]

    context = {
        'all_departments': all_departments,
        'dept_filter': dept_filter,
        'dept_labels': json.dumps(dept_labels),
        'dept_counts': json.dumps(dept_counts),
        'group_labels': json.dumps(group_labels),
        'group_counts': json.dumps(group_counts),
        'total_courses': total_courses,
        'total_departments': total_departments,
        'total_groups': total_groups,
        'total_students': total_students,
    }
    return render(request, 'dashboard.html', context)


# ---------- КУРСЫ ----------

@login_required
def course_list(request):
    courses = Course.objects.select_related('department').all()
    return render(request, 'course_list.html', {
        'courses': courses,
        'is_methodist': is_methodist(request.user),
    })


@login_required
@user_passes_test(is_methodist)
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('course_list')
    else:
        form = CourseForm()
    return render(request, 'object_form.html', {
        'form': form,
        'title': 'Добавление курса',
    })


@login_required
@user_passes_test(is_methodist)
def course_update(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'object_form.html', {
        'form': form,
        'title': 'Изменение курса',
    })


@login_required
@user_passes_test(is_methodist)
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course.delete()
        return redirect('course_list')
    return render(request, 'object_confirm_delete.html', {
        'object': course,
        'title': 'Удаление курса',
    })


# ---------- ФАКУЛЬТЕТЫ ----------

@login_required
def department_list(request):
    departments = Department.objects.all()
    return render(request, 'department_list.html', {
        'departments': departments,
        'is_methodist': is_methodist(request.user),
    })


@login_required
@user_passes_test(is_methodist)
def department_create(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('department_list')
    else:
        form = DepartmentForm()
    return render(request, 'object_form.html', {
        'form': form,
        'title': 'Добавление факультета',
    })


@login_required
@user_passes_test(is_methodist)
def department_update(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            return redirect('department_list')
    else:
        form = DepartmentForm(instance=department)
    return render(request, 'object_form.html', {
        'form': form,
        'title': 'Изменение факультета',
    })


@login_required
@user_passes_test(is_methodist)
def department_delete(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        department.delete()
        return redirect('department_list')
    return render(request, 'object_confirm_delete.html', {
        'object': department,
        'title': 'Удаление факультета',
    })


# ---------- УЧЕБНЫЕ ГРУППЫ ----------

@login_required
def academic_group_list(request):
    groups = AcademicGroup.objects.select_related('department').all()
    return render(request, 'academic_group_list.html', {
        'groups': groups,
        'is_methodist': is_methodist(request.user),
    })


@login_required
@user_passes_test(is_methodist)
def academic_group_create(request):
    if request.method == 'POST':
        form = AcademicGroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('academic_group_list')
    else:
        form = AcademicGroupForm()
    return render(request, 'object_form.html', {
        'form': form,
        'title': 'Добавление учебной группы',
    })


@login_required
@user_passes_test(is_methodist)
def academic_group_update(request, pk):
    group = get_object_or_404(AcademicGroup, pk=pk)
    if request.method == 'POST':
        form = AcademicGroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect('academic_group_list')
    else:
        form = AcademicGroupForm(instance=group)
    return render(request, 'object_form.html', {
        'form': form,
        'title': 'Изменение учебной группы',
    })


@login_required
@user_passes_test(is_methodist)
def academic_group_delete(request, pk):
    group = get_object_or_404(AcademicGroup, pk=pk)
    if request.method == 'POST':
        group.delete()
        return redirect('academic_group_list')
    return render(request, 'object_confirm_delete.html', {
        'object': group,
        'title': 'Удаление учебной группы',
    })