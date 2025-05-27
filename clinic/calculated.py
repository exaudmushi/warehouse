class VLPercentageCalculator:
    """
    A class to handle JSON data for VL results and calculate percentages.
    """
    
    def __init__(self, json_data):
        """
        Initialize the calculator with JSON data.
        
        Args:
            json_data (dict): JSON data containing rows with VL results
        """
        self.json_data = json_data
        self.vl_below_1000_id = "IM8BcMFo1Qg"  # ART clients VL results <1,000 copies/ml
        self.total_vl_results_id = "Uqs0gTxgKoN"  # Documented VL results

    def get_rows(self):
        """
        Retrieve the rows object from the JSON data.
        
        Returns:
            list: List of rows from the JSON data, or None if not found
        """
        try:
            rows = self.json_data.get('rows', None)
            if rows is None:
                print("No 'rows' key found in JSON data")
            return rows
        except Exception as e:
            print(f"Error retrieving rows: {e}")
            return None

    def calculate_percentage(self):
        """
        Calculate the percentage of ART clients with VL <1,000 copies/ml.
        
        Returns:
            float: Percentage rounded to 2 decimal places, or None if data is invalid
        """
        try:
            rows = self.get_rows()
            if not rows:
                return None
            
            # Initialize variables
            vl_below_1000 = None
            total_vl_results = None
            
            # Iterate through rows to find relevant values
            for row in rows:
                data_id = row[0]  # First column is dx (data ID)
                value = float(row[3])  # Fourth column is value
                
                if data_id == self.vl_below_1000_id:
                    vl_below_1000 = value
                elif data_id == self.total_vl_results_id:
                    total_vl_results = value
            
            # Check if both values were found
            if vl_below_1000 is None or total_vl_results is None:
                print("Required data IDs not found in rows")
                return None
                
            # Avoid division by zero
            if total_vl_results == 0:
                print("Total VL results is zero, cannot calculate percentage")
                return 0.0
                
            # Calculate percentage
            percentage = (vl_below_1000 / total_vl_results) * 100
            return round(percentage, 2)
            
        except (KeyError, IndexError, ValueError) as e:
            print(f"Error processing JSON data: {e}")
            return None
