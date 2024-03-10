from django.urls import reverse_lazy
from django.http import HttpResponse
from django.views import View
from django.views.generic.edit import FormView
from core.forms import ImageUploadForm
from io import BytesIO
import requests
import pandas as pd
import cv2
import pytesseract
import numpy as np
import os



class MyView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse("Dosyanız Hazırlanıyor...")

class FileUploadViewv2(FormView):
    template_name = "fileupload.html"
    form_class = ImageUploadForm
    success_url = reverse_lazy("thanks")

    


    def form_valid(self, form):
        result_file = []


        def image_to_text(image_file):
            img_data = image_file.read()
            pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

            # Use OpenCV to read the image
            # replace 'test.png' with your image file
            nparr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if (img is None):
                print('hatra var')

            # Convert the image to gray scale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Use pytesseract to convert the image data to text
            text = pytesseract.image_to_string(gray)

            # Print the text
            text = text.split("\n")
            for index, item in enumerate(text):
                if len(item) <= 4:
                    text.pop(index)
            return text


        for file in self.request.FILES.getlist('files_field'):
            result_file += (image_to_text(file))
        

        all_address_list = []
        for index, item in enumerate(result_file):
            item = item.split(" ")
            # print(item[-1], type(item[:-1]))

            #Deletes the city names
            try :
                item[-1] = int(item[-1])
                item = item
                
            except:
               
                item= item[:-1]
            try:
                address = ""
                for i in item[:-1]:
                    address += " "+i
                item = [address.lstrip(),item[-1] ]
            except:
                pass

            all_address_list.append(item)

        #Deletes unreaded elements and table head
        for index, i in enumerate( all_address_list):
            if len(i) <=0:
                all_address_list.pop(index)
            
            if str("street").upper() in str(i).upper():
                all_address_list.pop(index)

            # try:
            #     all_address_list[i][-1] = int( all_address_list[i][-1])
            # except:
            #     pass
        

        # for index, i in enumerate( all_address_list):
        #     if (type(i[-1]) != int):

        #         all_address_list.pop(index)

        def save_to_excell(list):

            columns = ['Address Line 1', 'Address Line 2','City','State','Postal Code','Extra info (Optional)','Add more columns if needed' ]

            # Create an empty DataFrame with the defined columns
            existing_data = pd.DataFrame(columns=columns)

            # Assign new values to the existing columns
            for index, adres in enumerate(list):
                try:
                    existing_data.at[index, 'Address Line 1'] = adres[0]  # Replace 'Column1' and new_value1 with your actual data
                    # existing_data.at[index, 'City'] = "Geel"  # Replace 'Column2' and new_value2 with your actual data
                    existing_data.at[index, 'Postal Code'] = int(adres[1])  # Replace 'Column2' and new_value2 with your actual data
                except:
                    pass


            excel_buffer = BytesIO()
            existing_data.to_excel(excel_buffer, index=False)
            excel_buffer.seek(0)
             #  Create an HTTP response with the Excel file as content
            response = HttpResponse(excel_buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

            # Set the content disposition to force the browser to download the fil
            # Set the content disposition to force the browser to download the file
            response['Content-Disposition'] = 'attachment; filename="processed_excel.xlsx"'
            return response
        
        return save_to_excell(all_address_list)

class FileUploadView(FormView):
    template_name = "fileupload.html"
    form_class = ImageUploadForm
    success_url = reverse_lazy("thanks")

    def form_valid(self, form):
        api_url = 'https://api.api-ninjas.com/v1/imagetotext'
        headers = {'X-Api-Key': os.environ.get("API_KEY")}
        
        result_file = []
        for file in self.request.FILES.getlist('files_field'):
            print(file.name)
            uploaded_file = file

            image_file_descriptor = uploaded_file
            files = {'image': image_file_descriptor}
            r = requests.post(api_url, files=files, headers=headers)
            result_file = result_file + r.json()
        
        obj = AddressList(result_file)
        obj.add_post_code("2440")
        obj.CombineAdresses(obj.jsonData)
        res_file = obj.save_to_excell()

    

        #  Create an HTTP response with the Excel file as content
        response = HttpResponse(res_file, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

        # Set the content disposition to force the browser to download the file
        response['Content-Disposition'] = 'attachment; filename="processed_excel.xlsx"'

        return response

    

class AddressList(object):

    def __init__(self, jsonData):
        self.jsonData = jsonData
        self.city_names = []
        self.post_codes = []

    def addCity(self, city):
        self.city_names.append(str(city))
        return self.city_names

    def add_post_code(self, post_code):
        self.post_codes.append(str(post_code))
        return self.post_codes

    def CombineAdresses(self, jsonList):
        adresler = []

        """
        hepsini birleştir
        şehir adlarını listeden sil
        posta koduna göre split et elemanları
        """
        full_text = ""
        for index, text in enumerate(jsonList):
            if str(text['text']).upper() != "STREET".upper() and str(text['text']).upper() != "TOWN".upper():
                full_text += text['text'] + " "

        full_text = full_text.upper()
        for city in self.city_names:
            if str(city).upper() in full_text:
                full_text = full_text.replace(city.upper(), "")

        full_text = full_text.split(" ")

        """
        ikili array yap 
        posta koduna ulaşana kadar iç araye ekle 
        sonra yeni iç eray oluştur
        """
        for post in self.post_codes:
            a = ""
            for item in full_text:
                if item != post:
                    a = a + " " + item
                if item == post:
                    a = a.lstrip()
                    adresler.append([a, post])
                    a = ""

     

        return adresler

    def save_to_excell(self):

        columns = ['Address Line 1', 'Address Line 2','City','State','Postal Code','Extra info (Optional)','Add more columns if needed' ]

        # Create an empty DataFrame with the defined columns
        existing_data = pd.DataFrame(columns=columns)

        # Assign new values to the existing columns
        for index, adres in enumerate(self.CombineAdresses(self.jsonData)):
            existing_data.at[index, 'Address Line 1'] = adres[0]  # Replace 'Column1' and new_value1 with your actual data
            # existing_data.at[index, 'City'] = "Geel"  # Replace 'Column2' and new_value2 with your actual data
            existing_data.at[index, 'Postal Code'] = int(adres[1])  # Replace 'Column2' and new_value2 with your actual data


        excel_buffer = BytesIO()
        existing_data.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        return excel_buffer
