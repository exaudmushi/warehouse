class DataTransformer:
    def transformer(self,transformed_rows, metadata, response):
    # EID Transform rows to include names
        
        for row in response['rows']:
            
            data_element_id, category_option_combo_id, period_id, org_unit_id, value = row
            transformed_row = [
                metadata[data_element_id]['name'],
                metadata[category_option_combo_id]['name'],
                metadata[period_id]['name'],
                metadata[org_unit_id]['name'],
                value
            ]
            # Sum the values from rows
            
            transformed_rows.append(transformed_row)
        return transformed_rows
    
