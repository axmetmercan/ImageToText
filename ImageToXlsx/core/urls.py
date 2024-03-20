
from django.urls import path
from core.views import FileUploadViewv2


urlpatterns = [
 
    path("",  FileUploadViewv2.as_view(), name="file-uploadv2"),

]
