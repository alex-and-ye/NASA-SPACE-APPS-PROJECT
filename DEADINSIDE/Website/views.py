from django.shortcuts import render
def home_page_view(request):
    template_name = 'website/home.html'
    context = {
        'user': request.user,
        'chatbot_disabled': request.COOKIES.get('cookie_consent') != 'accepted'
    }
    return render(request, template_name, context)