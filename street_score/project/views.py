import csv
import datetime
import logging
from django.contrib.sessions.models import Session
from django.db import connections
from django.http import HttpResponse
from django.views import generic as views

from .models import Rating, UserInfo

log = logging.getLogger(__name__)

def csv_data(request):
    now = datetime.datetime.utcnow()

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=beautifulst_data_%s.csv' % (now.strftime('%Y%m%d%H%M%S'), )

    # Get the data
    ratings = Rating.objects.all().select_related()

    # Init the csv writer
    writer = csv.writer(response)

    # Write the header row
    writer.writerow(['lat1','lon1','lat2','lon2','score'])

    # Write the contents
    for rating in ratings:
        writer.writerow([
            rating.place1.lat, rating.place1.lon,
            rating.place2.lat, rating.place2.lon,
            rating.score])

    return response


class MainUIView (views.TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(MainUIView, self).get_context_data(**kwargs)

        # Using the browser session, get the current user info (or create it if
        # none exists for the current session).
        session_key = self.request.session.session_key
        session = Session.objects.get(session_key=session_key)
        user_info = UserInfo.objects.get_or_create(session=session)[0]

        context.update({
            'user_info': user_info,
            'initial_vote_count': user_info.ratings.count()
        })
        return context
