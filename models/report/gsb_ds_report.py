from odoo import models , fields,api
import json
import base64
import qrcode
from io import BytesIO
from lxml import etree
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import math
from scipy.interpolate import CubicSpline , interp1d , Akima1DInterpolator
from scipy.optimize import minimize_scalar



class GsbReport(models.AbstractModel):
    _name = 'report.lerm_civil.gsb_mec_report'
    _description = 'GSB Report'
    
    @api.model
    def _get_report_values(self, docids, data):
        # eln = self.env['lerm.eln'].sudo().browse(docids)
        inreport_value = data.get('inreport', None)
        nabl = data.get('nabl')
        if 'active_id' in data['context']:
            eln = self.env['lerm.eln'].sudo().search([('sample_id','=',data['context']['active_id'])])
        else:
            eln = self.env['lerm.eln'].sudo().browse(docids) 
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(eln.kes_no)
        qr.make(fit=True)
        qr_image = qr.make_image()

        # Convert the QR code image to base64 string
        buffered = BytesIO()
        qr_image.save(buffered, format="PNG")
        qr_image_base64 = base64.b64encode(buffered.getvalue()).decode()

        # Assign the base64 string to a field in the 'srf' object
        qr_code = qr_image_base64
        model_id = eln.model_id
        # differnt location for product based
        model_name = eln.material.product_based_calculation[0].ir_model.name 
        if model_name:
            general_data = self.env[model_name].sudo().browse(model_id)
        else:
            general_data = self.env['lerm.eln'].sudo().browse(docids)
            
    #     # Prepare data for the chart
    #     plt.figure(figsize=(12, 6))
    #     x_values = []
    #     y_values = []
    #     for line in general_data.density_relation_table:
    #         x_values.append(line.moisture)
    #         y_values.append(line.dry_density)
        
    #    # Find the maximum y value
    #     max_y = max(y_values)
    #     min_y = round(min(y_values),2)
    #     max_x = x_values[y_values.index(max_y)]
    #     min_x = round(min(x_values),2)


    #     # Format max_y and max_x to display 2 digits after the decimal point
    #     max_y = round(max_y , 2)
    #     max_x = round(max_x, 2)
    #     print("Y_MAX",max_y)
    #     print("X_MAX",max_x)

        
    #     # Perform cubic spline interpolation
    #     x_smooth = np.linspace(min(x_values), max(x_values), 100)
    #     # cs = CubicSpline(x_values, y_values,1)
    #     # cs = interp1d(x_values, y_values,kind='cubic')
    #     cs = Akima1DInterpolator(x_values, y_values)

    #     # Create the line chart with a connected smooth line and markers
    #     plt.plot(x_smooth, cs(x_smooth), color='red', label='Smooth Curve')
    #     plt.scatter(x_values, y_values, marker='o', color='blue', s=30, label='Data Points')

        
    #     # Add a horizontal line with a label
    #     plt.axhline(y=max_y, color='green', linestyle='--', label=f'Max Y = {max_y}')

    #     # Add a vertical line with a label
    #     plt.axvline(x=max_x, color='orange', linestyle='--', label=f'Max X = {max_x}')

        
    #     # Set the grid
    #     ax = plt.gca()
    #     ax.grid(which='both', linestyle='--', linewidth=0.5)

    #     # Set the x-axis major and minor tick marks
    #     ax.xaxis.set_major_locator(ticker.MultipleLocator(1))  # Major gridlines every 1 unit
    #     ax.xaxis.set_minor_locator(ticker.MultipleLocator(0.1))  # Minor gridlines every 0.1 unit

    #     # Set the y-axis tick marks
    #     # plt.yticks([1.60, 1.62, 1.64, 1.66, 1.68, 1.70, 1.72, 1.74, 1.76, 1.78, 1.80])

    #     # edit range here
    #     plt.yticks(np.arange(min_y*0.99 , max_y*1.1 , max_y/100))


    #     plt.xticks(np.arange(math.floor(min_x), max_x*1.1, max_x/5))
    #     plt.xlabel('% Moisture')
    #     plt.ylabel('Dry density in gm/cc')
    #     plt.title('% Moisture vs Dry density in gm/cc')
    #     plt.legend()

    #     # Save the Matplotlib plot to a BytesIO object
    #     buffer = BytesIO()
    #     plt.savefig(buffer, format='png')
    #     graph_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

    #     # Close the Matplotlib plot to free up resources
    #     plt.close()
        
        
        
    #     # Prepare data for the chart
    #     plt.figure(figsize=(12, 6))
    #     cbrx_values = []
    #     cbry_values = []
    #     for line in general_data.cbr_table:
    #         cbrx_values.append(line.penetration)
    #         cbry_values.append(line.load)
        
    #     # Perform cubic spline interpolation
    #     cbrx_smooth = np.linspace(min(cbrx_values), max(cbrx_values), 100)
    #     cbrcs = CubicSpline(cbrx_values, cbry_values,1)

    #     # Create the line chart with a connected smooth line and markers
    #     plt.plot(cbrx_smooth, cbrcs(cbrx_smooth), color='red', label='Smooth Curve')
    #     plt.scatter(cbrx_values, cbry_values, marker='o', color='blue', s=30, label='Data Points')

    #     # Add a horizontal line with a label
    #     plt.axhline(y=cbry_values[5], color='green', linestyle='--' , label=f'Load at 2.5 mm = {cbry_values[5]}')
    #     plt.axhline(y=cbry_values[8], color='green', linestyle='--' , label=f'Load at 5 mm = {cbry_values[8]}')

    #     # Add a vertical line with a label
    #     plt.axvline(x=2.5, color='orange', linestyle='--')
    #     plt.axvline(x=5.0, color='orange', linestyle='--')
        
    #     # Set the grid
    #     ax = plt.gca()
    #     ax.grid(which='both', linestyle='--', linewidth=0.5)

    #     # Set the x-axis major and minor tick marks
    #     ax.xaxis.set_major_locator(ticker.MultipleLocator(1))  # Major gridlines every 1 unit
    #     ax.xaxis.set_minor_locator(ticker.MultipleLocator(0.1))  # Minor gridlines every 0.1 unit

    #     # Set the y-axis tick marks
    #     plt.xticks(range(0 , 15 , 1))
    #     plt.yticks(range(0 , 901 , 50))
        
    #     plt.xlabel('Penetration in mm')
    #     plt.ylabel('Load')
    #     plt.title('Penetration in mm vs Load')
    #     plt.legend()

    #     # Save the Matplotlib plot to a BytesIO object
    #     buffer2 = BytesIO()
    #     plt.savefig(buffer2, format='png')
    #     cbr_graph_image = base64.b64encode(buffer2.getvalue()).decode('utf-8')
    #     plt.close()

           # Prepare data for the chart
        plt.figure(figsize=(12, 6))
        x_values = []
        y_values = []
        # import wdb;wdb.set_trace()
        for line in general_data.density_relation_table:
            x_values.append(line.moisture)
            y_values.append(line.dry_density)


        if general_data.density_relation_table:
            try:
                max_y = max(y_values)
            except:
                max_y = 100
            try:
                min_y = round(min(y_values),2)
            except:
                min_y = 0
            try:
                max_x = x_values[y_values.index(max_y)]
            except:
                max_x = 100
            try:
                min_x = round(min(x_values),2)
            except:
                min_x = 0 
            
            


            # Format max_y and max_x to display 2 digits after the decimal point
            max_y = round(max_y , 2)
            max_x = round(max_x, 2)
            print("Y_MAX",max_y)
            print("X_MAX",max_x)
#    

        
            # Perform cubic spline interpolation
            x_smooth = np.linspace(min(x_values), max(x_values), 100)
            # cs = CubicSpline(x_values, y_values,1)
            # cs = interp1d(x_values, y_values,kind='cubic')
            cs = Akima1DInterpolator(x_values, y_values)

            # Create the line chart with a connected smooth line and markers
            plt.plot(x_smooth, cs(x_smooth), color='red', label='Smooth Curve')
            plt.scatter(x_values, y_values, marker='o', color='blue', s=30, label='Data Points')

            
            # Add a horizontal line with a label
            plt.axhline(y=max_y, color='green', linestyle='--', label=f'Max Y = {max_y}')

            # Add a vertical line with a label
            plt.axvline(x=max_x, color='orange', linestyle='--', label=f'Max X = {max_x}')

            
            # Set the grid
            ax = plt.gca()
            ax.grid(which='both', linestyle='--', linewidth=0.5)

            # Set the x-axis major and minor tick marks
            ax.xaxis.set_major_locator(ticker.MultipleLocator(1))  # Major gridlines every 1 unit
            ax.xaxis.set_minor_locator(ticker.MultipleLocator(0.1))  # Minor gridlines every 0.1 unit

            # Set the y-axis tick marks
            # plt.yticks([1.60, 1.62, 1.64, 1.66, 1.68, 1.70, 1.72, 1.74, 1.76, 1.78, 1.80])

            # edit range here
            plt.yticks(np.arange(min_y*0.99 , max_y*1.1 , max_y/100))


            if max_x != min_x:
                plt.xticks(np.arange(min_x, max_x + 1.0, (max_x - min_x) / 5))
            
        
            plt.xlabel('% Moisture')
            plt.ylabel('Dry density in gm/cc')
            plt.title('% Moisture vs Dry density in gm/cc')
            plt.legend()

            # Save the Matplotlib plot to a BytesIO object
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            graph_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

            # Close the Matplotlib plot to free up resources
            plt.close()
        else:
            graph_image = None
            max_y = 0
            max_x = 0

      
        # Prepare data for the chart
        plt.figure(figsize=(12, 6))
        cbrx_values = []
        cbry_values = []

        if general_data.cbr_table:
            for line in general_data.cbr_table:
                cbrx_values.append(line.penetration)
                cbry_values.append(line.load)
            
            # Perform cubic spline interpolation
            cbrx_smooth = np.linspace(min(cbrx_values), max(cbrx_values), 1000)
            cbrcs = CubicSpline(cbrx_values, cbry_values)

            # Create the line chart with a connected smooth line and markers
            plt.plot(cbrx_smooth, cbrcs(cbrx_smooth), color='red', label='Smooth Curve')
            plt.scatter(cbrx_values, cbry_values, marker='o', color='blue', s=30, label='Data Points')

            # Add a horizontal line with a label
            plt.axhline(y=cbry_values[5], color='green', linestyle='--', label=f'Load at 2.5 mm = {cbry_values[5]}')
            plt.axhline(y=cbry_values[8], color='green', linestyle='--', label=f'Load at 5 mm = {cbry_values[8]}')

            # Add a vertical line with a label
            plt.axvline(x=2.5, color='orange', linestyle='--')
            plt.axvline(x=5.0, color='orange', linestyle='--')
            
            # Set the grid
            ax = plt.gca()
            ax.grid(which='both', linestyle='--', linewidth=0.5)

            # Set the x-axis major and minor tick marks
            ax.xaxis.set_major_locator(ticker.MultipleLocator(1))  # Major gridlines every 1 unit
            ax.xaxis.set_minor_locator(ticker.MultipleLocator(0.1))  # Minor gridlines every 0.1 unit

            # Set the y-axis tick marks
            plt.xticks(range(0, 15, 1))
            plt.yticks(range(0, 481, 50))
            
            plt.xlabel('Penetration in mm')
            plt.ylabel('Load')
            plt.title('Penetration in mm vs Load')
            plt.legend()

            # Save the Matplotlib plot to a BytesIO object
            buffer2 = BytesIO()
            plt.savefig(buffer2, format='png')
            cbr_graph_image = base64.b64encode(buffer2.getvalue()).decode('utf-8')
            plt.close()
        else:
            cbr_graph_image = None
            cbry_values = []  # Set to an empty list instead of 0

        return {
            'eln': eln,
            'data' : general_data,
            'qrcode': qr_code,
            'stamp' : inreport_value,
            'nabl' : nabl,
            'graphHeavy' : graph_image,
            'mdd' : max_y,
            'omc' : max_x,
            'graphCbr' : cbr_graph_image,
            'load2' : cbry_values[5] if cbry_values else 0,  # Access the index if cbry_values is not empty
            'load5' : cbry_values[8] if cbry_values else 0,
        }
        
        # plt.figure(figsize=(12, 6))
        # cbrx_values = []
        # cbry_values = []
        # for line in general_data.cbr_table:
        #     cbrx_values.append(line.penetration)
        #     cbry_values.append(line.load)
        
        # if general_data.cbr_table:
        # # Perform cubic spline interpolation
        #     cbrx_smooth = np.linspace(min(cbrx_values), max(cbrx_values), 1000)
        #     cbrcs = CubicSpline(cbrx_values, cbry_values)

        #     # Create the line chart with a connected smooth line and markers
        #     plt.plot(cbrx_smooth, cbrcs(cbrx_smooth), color='red', label='Smooth Curve')
        #     plt.scatter(cbrx_values, cbry_values, marker='o', color='blue', s=30, label='Data Points')

        #     # Add a horizontal line with a label
        #     plt.axhline(y=cbry_values[5], color='green', linestyle='--' , label=f'Load at 2.5 mm = {cbry_values[5]}')
        #     plt.axhline(y=cbry_values[8], color='green', linestyle='--' , label=f'Load at 5 mm = {cbry_values[8]}')

        #     # Add a vertical line with a label
        #     plt.axvline(x=2.5, color='orange', linestyle='--')
        #     plt.axvline(x=5.0, color='orange', linestyle='--')
            
        #     # Set the grid
        #     ax = plt.gca()
        #     ax.grid(which='both', linestyle='--', linewidth=0.5)

        #     # Set the x-axis major and minor tick marks
        #     ax.xaxis.set_major_locator(ticker.MultipleLocator(1))  # Major gridlines every 1 unit
        #     ax.xaxis.set_minor_locator(ticker.MultipleLocator(0.1))  # Minor gridlines every 0.1 unit

        #     # Set the y-axis tick marks
        #     plt.xticks(range(0 , 15 , 1))
        #     plt.yticks(range(0 , 481 , 50))
            
        #     plt.xlabel('Penetration in mm')
        #     plt.ylabel('Load')
        #     plt.title('Penetration in mm vs Load')
        #     plt.legend()

        #     # Save the Matplotlib plot to a BytesIO object
        #     buffer2 = BytesIO()
        #     plt.savefig(buffer2, format='png')
        #     cbr_graph_image = base64.b64encode(buffer2.getvalue()).decode('utf-8')
        #     plt.close()
        # else:
        #     cbr_graph_image = None
        #     cbrx_values = 0
        #     cbry_values = 0
            
        
        # return {
        #     'eln': eln,
        #     'data' : general_data,
        #     'qrcode': qr_code,
        #     'stamp' : inreport_value,
        #     'nabl' : nabl,
        #     'graphHeavy' : graph_image,
        #     'mdd' : max_y,
        #     'omc' : max_x,
        #     'graphCbr' : cbr_graph_image,
        #     'load2' : cbry_values[5],
        #     'load5' : cbry_values[8],
            
        # }

class GsbDatasheet(models.AbstractModel):
    _name = 'report.lerm_civil.gsb_mech_datasheet'
    _description = 'GSB DataSheet'
    
    @api.model
    def _get_report_values(self, docids, data):
        if 'active_id' in data['context']:
            eln = self.env['lerm.eln'].sudo().search([('sample_id','=',data['context']['active_id'])])
        else:
            eln = self.env['lerm.eln'].sudo().browse(docids) 
        model_id = eln.model_id
        # differnt location for product based
        # model_name = eln.material.product_based_calculation[0].ir_model.name 
        model_name = eln.material.product_based_calculation.filtered(lambda record: record.grade.id == eln.grade_id.id).ir_model.name
        if model_name:
            general_data = self.env[model_name].sudo().browse(model_id)
        else:
            general_data = self.env['lerm.eln'].sudo().browse(docids)
        return {
            'eln': eln,
            'data' : general_data
        }