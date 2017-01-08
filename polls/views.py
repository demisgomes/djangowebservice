from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from .models import Choice,Question
from django.urls import reverse
from django.views import generic 
from django.http import Http404
from django.utils.encoding import force_text
from django.core.serializers.json import DjangoJSONEncoder
from django.core.serializers import serialize
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

@csrf_exempt
def api(request):
    if request.method == 'GET':
        question_data=serializers.serialize('json', Question.objects.all())
        choice_data=serializers.serialize('json', Choice.objects.all())
        response={}
        response['questions']=json.loads(question_data)
        response['choices']=json.loads(choice_data)
        return JsonResponse(response, safe=False)

    elif request.method == 'POST':
        json_received=json.loads(request.body)
        question = get_object_or_404(Question, pk=json_received['question_id'])
        selected_choice = question.choice_set.get(pk=json_received['pk'])
        print selected_choice.choice_text
        selected_choice.votes += 1
        selected_choice.save()
        return JsonResponse({'result':'ok'},safe=False)

class LazyEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, YourCustomType):
            return force_text(obj)
        return super(LazyEncoder, self).default(obj)

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
