from Authentification.models import Notification

def notifications_non_lues_processor(request):
    if request.user.is_authenticated:
        notifications_non_lues_count = Notification.objects.filter(
            utilisateur=request.user,
            est_lu=False
        ).count()
    else:
        notifications_non_lues_count = 0
    return {
        'notifications_non_lues_count': notifications_non_lues_count
    }