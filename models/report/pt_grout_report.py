from odoo import models , fields,api
import json
import base64
import qrcode
from io import BytesIO
from lxml import etree




class PtGroutReport(models.AbstractModel):
    _name = 'report.lerm_civil.lerm_ptgrout_report'
    _description = 'PtGrout Report'
    
    
    @api.model
    def _get_report_values(self, docids, data):
        # eln = self.env['lerm.eln'].sudo().browse(docids)
        # if 'active_id' in data['context']:
        #     eln = self.env['lerm.eln'].sudo().search([('sample_id','=',data['context']['active_id'])])
        # else:
        #     eln = self.env['lerm.eln'].sudo().browse(docids)
        fromEln = data.get('fromEln')
        if data.get('report_wizard') == True:
            eln = self.env['lerm.eln'].sudo().search([('sample_id','=',data['sample'])])
        elif fromEln == False:
            if 'active_id' in data['context']:
                eln = self.env['lerm.eln'].sudo().search([('sample_id','=',data['context']['active_id'])])
            else:
                eln = self.env['lerm.eln'].sudo().browse(docids)
        else:
            if 'active_id' in data['context']:
                eln = self.env['lerm.eln'].sudo().search([('id','=',data['context']['active_id'])])
            else:
                eln = self.env['lerm.eln'].sudo().browse(docids)
        
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        # qr.add_data(eln.kes_no)
        url = self.env['ir.config_parameter'].sudo().search([('key','=','web.base.url')]).value
        url = url +'/download_report/'+ str(eln.id)
        qr.add_data(url)
        qr.make(fit=True)
        qr_image = qr.make_image()

        # Convert the QR code image to base64 string
        buffered = BytesIO()
        qr_image.save(buffered, format="PNG")
        qr_image_base64 = base64.b64encode(buffered.getvalue()).decode()

        # Assign the base64 string to a field in the 'srf' object
        qr_code = qr_image_base64
            
        data = {
            "material_id":eln.material.id,
            "grade_id":eln.grade_id.id
        }
        model = eln.get_product_base_calc_line(data).ir_model.model
        ptgrout_data = self.env[model].search([("id","=",eln.model_id)])
        return {
            'eln': eln,
            'ptgrout': ptgrout_data,
            'qrcode': qr_code,
            # 'nabl':nabl,
            'fromEln':fromEln
        }





# class PtGroutReport(models.AbstractModel):
#     _name = 'report.lerm_civil.lerm_ptgrout_report'
#     _description = 'PtGrout Report'
    
#     @api.model
#     def _get_report_values(self, docids, data):
#         # eln = self.env['lerm.eln'].sudo().browse(docids)
#         fromEln = data.get('fromEln')
#         if fromEln == False:
#             if 'active_id' in data['context']:
#                 eln = self.env['lerm.eln'].sudo().search([('sample_id','=',data['context']['active_id'])])
#             else:
#                 eln = self.env['lerm.eln'].sudo().browse(docids)
#         else:
#             if 'active_id' in data['context']:
#                 eln = self.env['lerm.eln'].sudo().search([('id','=',data['context']['active_id'])])
#             else:
#                 eln = self.env['lerm.eln'].sudo().browse(docids)
        
#         qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
#         qr.add_data(eln.kes_no)
#         qr.make(fit=True)
#         qr_image = qr.make_image()

#         # Convert the QR code image to base64 string
#         buffered = BytesIO()
#         qr_image.save(buffered, format="PNG")
#         qr_image_base64 = base64.b64encode(buffered.getvalue()).decode()

#         # Assign the base64 string to a field in the 'srf' object
#         qr_code = qr_image_base64
            
#         data = {
#             "material_id":eln.material.id,
#             "grade_id":eln.grade_id.id
#         }
#         model = eln.get_product_base_calc_line(data).ir_model.model
#         ptgrout_data = self.env[model].search([("id","=",eln.model_id)])
#         return {
#             'eln': eln,
#             'ptgrout': ptgrout_data,
#             'qrcode': qr_code,
#             'fromEln':fromEln
#         }
