
from django.urls import path
from core.views import MyView, FileUploadView,FileUploadViewv2


urlpatterns = [
    path("thanks/", MyView.as_view(), name="thanks"),
    path("",  FileUploadView.as_view(), name="file-upload"),
    path("v1/",  FileUploadViewv2.as_view(), name="file-uploadv2"),

]
