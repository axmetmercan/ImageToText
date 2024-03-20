from django.urls import reverse_lazy
from django.http import HttpResponse
from django.views import View
from django.views.generic.edit import FormView
from core.forms import ImageUploadForm
from io import BytesIO
import pandas as pd
import cv2
import pytesseract
import numpy as np


class FileUploadViewv2(FormView):
    template_name = "fileupload.html"
    form_class = ImageUploadForm
    success_url = reverse_lazy("thanks")



    def read_img(self, img):
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

        cropped_image = np.asarray(bytearray(img.read()), dtype=np.uint8)

        cropped_image = cv2.imdecode(cropped_image, cv2.IMREAD_COLOR)

        # Read the cropped image
        # cropped_image = cv2.imread(img)
        # Check if current image width less then 1000
        prev_res = cropped_image.shape[0]
        # Check if current image width less then 1000
        cropped_image = cv2.resize(cropped_image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        if (prev_res>1000):
            canvas_height = max(cropped_image.shape[0], cropped_image.shape[0] + round(
                cropped_image.shape[0] * 10 / 100))  # Adjust as needed, ensuring it's large enough
            canvas_width = max(cropped_image.shape[1], cropped_image.shape[1] + round(
                cropped_image.shape[1] * 10 / 100))  # Adjust as needed, ensuring it's large enough

        # Otherwise
        else:
            canvas_height = max(cropped_image.shape[0], 3000)  # Adjust as needed, ensuring it's large enough
            canvas_width = max(cropped_image.shape[1], 2700)  # Adjust as needed, ensuring it's large enough


        # Create a white canvas
        canvas = np.ones((canvas_height, canvas_width, 3), dtype=np.uint8) * 255

        # Calculate the offset for placing the cropped image in the center of the canvas
        offset_y = (canvas_height - cropped_image.shape[0]) // 2
        offset_x = (canvas_width - cropped_image.shape[1]) // 2

        # Place the cropped image onto the canvas
        canvas[offset_y:offset_y + cropped_image.shape[0], offset_x:offset_x + cropped_image.shape[1]] = np.copy(cropped_image)


        img = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
        kernel = np.ones((1, 1), np.uint8)
        img = cv2.dilate(img, kernel, iterations=1)
        img = cv2.erode(img, kernel, iterations=1)
        img = cv2.threshold(cv2.medianBlur(img, 3), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        # To see modified image
        # cv2.imwrite("asd.jpg", img)

        text = pytesseract.image_to_string(img)

        return text
    
    def clean_empty_text(self, arr):
        new_arr = []
        for  item in arr:
            if item != "":
                new_arr.append(item)
        return new_arr
    
    def filter_post_codes(self, post_codes, address_list):
        address_dict = dict()
        for post_code in post_codes:

            address_dict[post_code]=[]

            for address in address_list:
                if post_code in address:
                    address = address.replace(post_code, "")
                    address_dict[post_code].append(address)
        return address_dict



    def save_to_excell(self, a_dict):

        columns = ['Address Line 1', 'Address Line 2','City','State','Postal Code','Extra info (Optional)','Add more columns if needed' ]

        # Create an empty DataFrame with the defined columns
        existing_data = pd.DataFrame(columns=columns)

        # Assign new values to the existing columns
        for post_code in a_dict:
            for index, adres in enumerate(a_dict[post_code]):
                try:
                    existing_data.at[index, 'Address Line 1'] = adres  # Replace 'Column1' and new_value1 with your actual data
                    # existing_data.at[index, 'City'] = "Geel"  # Replace 'Column2' and new_value2 with your actual data
                    existing_data.at[index, 'Postal Code'] = int(post_code)  # Replace 'Column2' and new_value2 with your actual data
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


    def form_valid(self, form):
        all_address_list = [1,2]
        requested_files = self.request.FILES.getlist('files_field')
        address_text = ""

        # Accepts an image file and returns it as text

        for file in self.request.FILES.getlist('files_field'):
            # result_file += (self.read_img(file))

            text_file = self.read_img(file)
            address_text += "\n" + text_file

        text_file = address_text.split("\n")
        cleaned_file = self.clean_empty_text(text_file)
        filtered_data = self.filter_post_codes(["2440","2450","4800","4710","4720"], cleaned_file)
     
        # print(filtered_data)       
    
        return self.save_to_excell(filtered_data)





