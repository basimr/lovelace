import base64
import json
import logging
import pprint
import os
import requests
import pprint
import datetime
from urllib.parse import urljoin

from django.http import HttpResponseBadRequest, HttpResponseServerError, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views import generic, View
from django.db.models import F
from django.conf import settings
from django.core.files import File
from django.template.defaulttags import register

from .forms import CodeSubmissionForm
from .models import Problem, Submission
from django.contrib.auth.models import User
from users.models import UserProfile

ENGINE_URL = 'http://engine:14714/submit'
MAX_FILE_SIZE_BYTES = 65536

logger = logging.getLogger('django.' + __name__)


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


class IndexView(generic.ListView):
    template_name = 'problems/index.html'
    context_object_name = 'latest_problem_list'

    def get_queryset(self):
        """Return all problems, sorted by order ID."""
        return Problem.objects.order_by('order_id')

    def get_context_data(self, **kwargs):
        """ Add a list of problems solved by the user, if authenticated. """
        data = super().get_context_data(**kwargs)

        problem_submissions = {}
        for problem in Problem.objects.order_by('order_id'):
            problem_submissions[problem.id] = Submission.objects.filter(problem=problem).count()
        data['problem_submissions'] = problem_submissions

        if self.request.user.is_authenticated:
            current_user_profile = UserProfile.objects.get(user=self.request.user)
            problems_solved = Submission.objects.filter(user=current_user_profile, passed=True).distinct().values_list('problem', flat=True)
            data['problems_solved'] = problems_solved

        return data


class DetailView(View):
    @staticmethod
    def get(request, problem_name):
        problem = get_object_or_404(Problem, name=problem_name)
        template = 'problems/{}.html'.format(str(problem_name))
        form = CodeSubmissionForm()

        logger.info("Adding list of previous submissions to context data...")

        previous_submissions = []
        if request.user.is_authenticated:
            current_user_profile = UserProfile.objects.get(user=request.user)
            previous_submissions_queryset = Submission.objects.filter(user=current_user_profile, problem__name=problem_name)
            for s in previous_submissions_queryset:
                logger.info("Found previous submission ID#{:d}".format(s.id))

                if s.runtime_sum < 1e-6:
                    runtime_sum = "{:.3g} ns".format(s.runtime_sum * 1e9)
                elif 1e-6 <= s.runtime_sum < 1e-3:
                    runtime_sum = "{:.3g} μs".format(s.runtime_sum * 1e6)
                elif 1e-3 < s.runtime_sum < 1:
                    runtime_sum = "{:.3g} ms".format(s.runtime_sum * 1e3)
                else:
                    runtime_sum = "{:.3g} s".format(s.runtime_sum)

                max_mem_usage = "{:d} kB".format(round(s.max_mem_usage))

                previous_submissions.append({
                    'id': s.id,
                    'passed': s.passed,
                    'date': s.date,
                    'language': s.language,
                    'file': s.file,
                    'filename': s.file.name.split('/')[-1],
                    'test_cases_passed': s.test_cases_passed,
                    'test_cases_total': s.test_cases_total,
                    'runtime_sum': runtime_sum,
                    'max_mem_usage': max_mem_usage,
                    })


            n_submissions_passed = Submission.objects.filter(user=current_user_profile, problem__name=problem_name, passed=True).count()
            solved_by_user = True if n_submissions_passed > 0 else False
        else:
            solved_by_user = False

        context = {
            'problem': problem,
            'form': form,
            'previous_submissions': previous_submissions,
            'solved_by_user': solved_by_user,
        }

        return render(request, template, context)

    @staticmethod
    def post(request, problem_name):
        problem = get_object_or_404(Problem, name=problem_name)
        form = CodeSubmissionForm(request.POST, request.FILES)

        if not form.is_valid():
            return HttpResponseBadRequest('Unknown problem with the submitted file')

        logger.info("Received submission for problem={:}. Request:\n{:}"
                .format(problem_name, pprint.pformat(request.__dict__)))

        if request.is_ajax():
            logger.debug("AJAX request received.")
        else:
            logger.debug("Received request NOT AJAX.")

        button_clicked = request.POST['button-clicked']
        logger.info("Button clicked: {:}".format(button_clicked))

        logger.debug("Anon user looks like: {}".format(request.user))

        if request.user.username:
            username = request.user.username
            user = request.user
            user_profile = UserProfile.objects.get(user=user)
        else:
            username = 'anonymous'
            user = User.objects.get(username=username)
            user_profile = UserProfile.objects.get(user=user)

        logger.info("Submission from user: {}".format(user))
        logger.info("Submission from user_profile: {}".format(user_profile))

        if button_clicked == 'submit-code-button':
            language = request.POST['language']
            logger.info("Language selected: {:s}".format(language))

            extension = {'python': 'py', 'javascript': 'js', 'julia': 'jl', 'c': 'c'}.get(language)

            editor_code = request.POST['raw-code']
            logger.info("User code:\n{:}".format(editor_code))
            raw_code = str(base64.b64encode(bytes(editor_code, 'utf-8')), 'utf-8')

            datetime_now = datetime.datetime.now()
            year = datetime_now.strftime("%Y")
            month = datetime_now.strftime("%m")
            day = datetime_now.strftime("%d")
            timestamp = datetime_now.strftime("%Y%m%d%H%M%S")

            user_code_filename = f"{problem_name}_{username}_{timestamp}.{extension}"
            user_code_filepath = os.path.join(settings.MEDIA_ROOT, "uploads", year, month, day, user_code_filename)

            user_code_dir = os.path.dirname(user_code_filepath)
            if not os.path.exists(user_code_dir):
                logger.info(f"Creating directory: {user_code_dir}")
                os.makedirs(user_code_dir)

            logger.info(f"Writing user code to file: {user_code_filepath}")

            # Not sure if there's a simpler way to do this but we first create a Python File
            # and write the code into it. We then create a Django File from the Python File
            # so we can pass it to Django when creating the `Submission` below.
            # We then delete the Python File at the end lol.

            pfile = open(user_code_filepath, 'w+')  # Python File
            pfile.write(editor_code)

            file = File(pfile)  # Creating Django File from Python file

            # Apparently this will use the user_timestamped_filepath function to determine the filepath
            # so we give it a generic filename like "chaos.py" and Django figures out the rest.
            file.name = problem_name + "." + extension

            logger.debug("user_code_filepath = {}".format(user_code_filepath))
            logger.debug("user_code_filename = {}".format(user_code_filename))
            logger.debug("user_code_dir = {}".format(user_code_dir))
            logger.debug("django file.name = {}".format(file.name))

        elif button_clicked == 'submit-file-button':
            try:
                file = form.files['file']
            except KeyError:
                return JsonResponse({'error': 'Please choose and attach your file before submitting.'})

            if file.size > MAX_FILE_SIZE_BYTES:
                return JsonResponse({'error': f'File must be smaller than {MAX_FILE_SIZE_BYTES} bytes.'})

            base_filename, extension = os.path.splitext(file.name)
            ext2language = {'.py': 'python', '.js': 'javascript', '.jl': 'julia', '.c': 'c'}
            language = ext2language.get(extension)

            if language is None:
                supported_extensions = "".join([lang + " -> " + ext + "\n" for ext, lang in ext2language.items()])
                return JsonResponse({'error': f'Invalid file extension: {extension}. Supported languages and extensions are\n' + supported_extensions})

            raw_code = str(base64.b64encode(file.read()), 'utf-8')

        else:
            return JsonResponse({'error': 'Invalid value for button-clicked in POST form.'})

        submission = {
            'problem': problem_name,
            'language': language,
            'code': raw_code
        }

        engine_resp = requests.post(ENGINE_URL, data=json.dumps(submission), timeout=9999)
        status = engine_resp.status_code

        if status == 400:
            error_resp = engine_resp.json()
            error_msg = error_resp['error']
            logging.warning("Engine returned HTTP 400. Probably due to bad user code. Error: {:}".format(error_msg))
            return JsonResponse({'error': error_msg})
        elif status == 500:
            error_resp = engine_resp.json()
            error_msg = error_resp['error']
            logging.warning("Engine returned HTTP 500. Probably due to bad file push or pull. Error: {:}".format(error_msg))
            return JsonResponse({'error': error_msg})

        results = engine_resp.json()

        test_cases_passed = 0
        test_cases_total = 0
        runtime_sum = 0.0
        max_mem_usage = 0.0

        for tc in results['testCaseDetails']:
            test_cases_total += 1
            if tc['passed']:
                test_cases_passed += 1
            runtime_sum += tc['processInfo']['runtime']
            max_mem_usage = max(max_mem_usage, tc['processInfo']['max_mem_usage'])

        submission = Submission(
            user=user_profile,
            problem=problem,
            passed=results['success'],
            language=language,
            file=file,
            test_cases_passed=test_cases_passed,
            test_cases_total=test_cases_total,
            runtime_sum=runtime_sum,
            max_mem_usage=max_mem_usage,
        )
        submission.save()

        if button_clicked == "submit-code-button":
            pfile.close()
            os.remove(pfile.name)

        # Increment user's submission count by 1.
        UserProfile.objects.filter(user=user).update(submissions_made=F('submissions_made') + 1)  # this can be simplified

        # If successful and is user's first successful submission, increment problem's solved_by by 1 and user's problems_solved by 1.
        if results['success']:
            num_previous_successful_submissions = Submission.objects.filter(user=user_profile, passed=True, problem__name=problem_name).count()
            logger.info("# previous successful submissions: {:}".format(num_previous_successful_submissions))
            if num_previous_successful_submissions == 1:
                logger.info("User {:} successfully solved {:}. Incrementing problem's solved_by 1.".format(user_profile, problem_name))
                Problem.objects.filter(name=problem_name).update(solved_by=F('solved_by') + 1)
                UserProfile.objects.filter(user=user).update(problems_solved=F('problems_solved') + 1)  # this can be simplified

        return JsonResponse({'results': results})
