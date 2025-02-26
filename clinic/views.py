from django.views.generic import FormView, TemplateView
from django.shortcuts import redirect
from django.urls import reverse_lazy
import os
import json
import datetime
from .dataservices import file_converter, servicefacility
import zipfile
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from .forms import MDBFileUploadForm

def datetime_serializer(obj):
    """
    Custom serializer for datetime and date objects.
    Converts datetime and date objects to ISO 8601 format strings.
    """
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()  # Convert datetime or date to string in ISO 8601 format
    raise TypeError(f"Type {type(obj)} not serializable")

# Create your views here.
class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add your custom context variables here
        return context

class DataUplodResponse(TemplateView):
    template_name = "successsful.html"
    
    def get_context_data(self, **kwargs):
        """Add verification results to the context."""
        context = super().get_context_data(**kwargs)
        #context['results'] = self.verify_all_files()
        return context
    
    
class MDBFileUploadAndVerifyView(FormView,TemplateView):
    template_name = 'upload.html'
    success_url = reverse_lazy('dashboard')  # Redirect after successful upload
    form_class = MDBFileUploadForm
    def get_context_data(self, **kwargs):
        """Add verification results to the context."""
        context = super().get_context_data(**kwargs)
       
        return context

    def form_valid(self, form):
        """Handle valid file uploads."""
        uploaded_file = self.request.FILES['file']
        directory = 'uploaded_files'
        os.makedirs(directory, exist_ok=True)
        file_path = os.path.join(directory, uploaded_file.name)

        uploaded_file_name = uploaded_file.name
        format_name = servicefacility.HighlevelFunction
        data_file = format_name.format_filename(uploaded_file_name)

        # Save uploaded ZIP file
        fs = FileSystemStorage(location=settings.MEDIA_ROOT)
        filename = fs.save(directory, uploaded_file) 
        file_path = os.path.join(settings.MEDIA_ROOT, filename)
     
        # Define the extraction path
        extract_path = os.path.join(settings.MEDIA_ROOT, 'extracted_files')

        # Ensure the extraction folder exists
        os.makedirs(extract_path, exist_ok=True)

        # Extract the ZIP file
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)


        all_tables_data = {}
            # Process MDB files
        json_data_process = file_converter.JsonConverter(all_tables_data,output_folder="converted_json",weekly_file=data_file)
        absolute_path = os.path.abspath(extract_path)
        clear_temp = servicefacility.HighlevelFunction
        clear_temp.clear_temp_files()
        json_data_process.convert_mdb_to_json(absolute_path + "\\" + data_file )

        
        return redirect('successful') # Return file path or response




































            #return JsonResponse({'message': 'File uploaded and extracted successfully!'})
       
            # #Read the content of the uploaded file
            # for data_file in os.listdir(extreacted_file):
            #     single_file_path = os.path.join(extreacted_file, data_file)
            #     print(single_file_path)
            #     #initiate the pydoc connector
            #     #Try to connect to the database and close the connection
            #     try:
            #         # print(pyodbc.drivers())

            #         conn = pyodbc.connect(f'Driver={{Microsoft Access Driver (*.mdb, *.accdb)}};Dbq={single_file_path};')

            #         cursor = conn.cursor()


                 
            #        # Step 1: Retrieve all table names using cursor.tables()
            #         cursor.tables()
            #         tables = cursor.fetchall()
                

            #         # Filter out system tables (those whose names start with 'MSys')
            #         user_tables = [table for table in tables if table.table_type == 'TABLE' and not table.table_name.startswith('MSys')]
                    
                    
            #         # Print the number of tables and list the table names
            #         print(f"table found {len(user_tables)} user tables:")
            #         for table in user_tables:
            #             print(table.table_name)  # This will print the name of each user table

            #         # Initialize a dictionary to hold the data of all tables
            #         all_tables_data = {}

            #         # Step 2: Loop through each user table and fetch its data
            #         for table in user_tables:
            #             table_name = table.table_name
                        
                                           
            #              # Query to get column names for the table
            #             cursor.execute(f"SELECT * FROM [{table_name}]")
            #             columns = [column[0] for column in cursor.description]  # Get column names

            #             # Query to get data from each table
            #             cursor.execute(f"SELECT * FROM [{table_name}]")
            #             rows = cursor.fetchall()

            #             # Convert the rows to a list of dictionaries (column names as keys)
            #             table_data = [dict(zip(columns, row)) for row in rows]

            #             # Store the table data in the dictionary
            #             all_tables_data[table_name] = table_data
                        
        
            #         #Adding HRFCode fr the facility
            #         hrfCode = servicefacility.FacilityInfo.HRFCode(self,directory)
            #         print(hrfCode)
            #         # Create the writer instance and call the method to write to DB and JSON
            #         writter = file_converter.JsonConverter(all_tables_data)

            #         writter.convert_to_json()
                  
            #         #encryption_service.process_table_data(json_data, facility_code, facility_biom)


                #     return redirect('successful')
                #     # return HttpResponseRedirect({'valid': True, 'message': 'Data retrieved successfully'})
                # except pyodbc.Error as e:
                #     return JsonResponse({'valid': False, 'message': str(e)})

                # finally:
                #     if 'conn' in locals() and conn:
                #         conn.close()
                
        # # Save file information to the database
        # DataFileUpload.objects.create(
        #     facility_name=uploaded_file.name.split('.')[0],
        #     size=uploaded_file.size,
        #     status=False
        # )

        # return super().form_valid(form)


