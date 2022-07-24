"""Django URLs"""
from django.urls import path
from cloud import views

urlpatterns = [
    path("connections/", views.ConnList.as_view()),
    path("connections/<int:pk>/", views.ConnDetail.as_view()),
    path("tasks/<uuid:uuid>/", views.TaskDetail.as_view()),
    path("buckets/", views.BucketList.as_view()),
    path("buckets/<int:pk>/", views.BucketDetail.as_view()),
    path("migrations/", views.MigrationList.as_view()),
    path("migrations/<int:pk>/", views.MigrationDetail.as_view()),
]
