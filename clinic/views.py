from django.views.generic import FormView, TemplateView
from django.shortcuts import redirect
from django.urls import reverse_lazy
import os
import pyodbc
from .models import HRFCodeFacility, DataFileUpload, FacilityEncryptedData
from .forms import MDBFileUploadForm
from django.http import JsonResponse
import pyodbc
import json
import datetime
from .dataservices import file_converter
from django.conf import settings as setup


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
    
    
class MDBFileUploadAndVerifyView(FormView, TemplateView):
    template_name = 'upload.html'
    form_class = MDBFileUploadForm
    success_url = reverse_lazy('dashboard')  # Redirect after successful upload

    def get_context_data(self, **kwargs):
        """Add verification results to the context."""
        context = super().get_context_data(**kwargs)
        #context['results'] = self.verify_all_files()
        return context

    def form_valid(self, form):
        """Handle valid file uploads."""
        uploaded_file = self.request.FILES['file']
        directory = 'uploaded_files'
        os.makedirs(directory, exist_ok=True)
        file_path = os.path.join(directory, uploaded_file.name)
        
        # Save the uploaded file
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
       
            #Read the content of the uploaded file
            for data_file in os.listdir(directory):
                single_file_path = os.path.join(directory, data_file)
                print(single_file_path)
                #initiate the pydoc connector
                #Try to connect to the database and close the connection
                try:
                    # print(pyodbc.drivers())

                    conn = pyodbc.connect(f'Driver={{Microsoft Access Driver (*.mdb, *.accdb)}};Dbq={single_file_path};')

                    cursor = conn.cursor()
                 
                   # Step 1: Retrieve all table names using cursor.tables()
                    cursor.tables()
                    tables = cursor.fetchall()
                

                    # Filter out system tables (those whose names start with 'MSys')
                    user_tables = [table for table in tables if table.table_type == 'TABLE' and not table.table_name.startswith('MSys')]
                    
                    
                    # Print the number of tables and list the table names
                    print(f"Found to procss{len(user_tables)} user tables:")
                    for table in user_tables:
                        print(table.table_name)  # This will print the name of each user table

                    # Initialize a dictionary to hold the data of all tables
                    all_tables_data = {}

                    # Step 2: Loop through each user table and fetch its data
                    for table in user_tables:
                        table_name = table.table_name
                        
                                           
                         # Query to get column names for the table
                        cursor.execute(f"SELECT * FROM [{table_name}]")
                        columns = [column[0] for column in cursor.description]  # Get column names

                        # Query to get data from each table
                        cursor.execute(f"SELECT * FROM [{table_name}]")
                        rows = cursor.fetchall()

                        # Convert the rows to a list of dictionaries (column names as keys)
                        table_data = [dict(zip(columns, row)) for row in rows]

                        # Store the table data in the dictionary
                        all_tables_data[table_name] = table_data

        

                    # Create the writer instance and call the method to write to DB and JSON
                    writer = file_converter.JSONDataWriter(all_tables_data)
                    writer.write_all_tables(setupDB=setup.DATABASES_VARIABLE)


                    #encryption_service.process_table_data(json_data, facility_code, facility_biom)


                    return redirect('successful')
                    # return HttpResponseRedirect({'valid': True, 'message': 'Data retrieved successfully'})
                except pyodbc.Error as e:
                    return JsonResponse({'valid': False, 'message': str(e)})

                finally:
                    if 'conn' in locals() and conn:
                        conn.close()
                
        # Save file information to the database
        DataFileUpload.objects.create(
            facility_name=uploaded_file.name.split('.')[0],
            size=uploaded_file.size,
            status=False
        )

        return super().form_valid(form)


