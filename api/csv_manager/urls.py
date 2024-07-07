from django.urls import path
from api.csv_manager.views import UploadCSVView, SearchView
urlpatterns = [
    path("upload_csv/", UploadCSVView.as_view(), name="upload_csv"),
    path("search/", SearchView.as_view(), name="search"),
]
