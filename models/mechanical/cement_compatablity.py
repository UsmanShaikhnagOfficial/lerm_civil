from odoo import api, fields, models
from decimal import Decimal
import matplotlib.pyplot as plt
import io
import base64


class CementCompatablity(models.Model):
    _name = "mechanical.cement.compatiblity"
    _inherit = "lerm.eln"
    _rec_name = "name"


    name = fields.Char("Name",default="Compatiblity")
    
    eln_ref = fields.Many2one('lerm.eln',string="Eln")
    temp_percent_normal = fields.Float("Temperature °C")
    humidity_percent_normal = fields.Float("Humidity %")
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    child_lines = fields.One2many('mechanical.cement.compatiblity.lines','parent_id',string="Parameters")
    chart_image = fields.Binary("Line Chart", compute="_compute_chart_image", store=True)
    comment = fields.Char("Comment")
    
    def open_eln_page(self):
        # import wdb; wdb.set_trace()

        return {
                'view_mode': 'form',
                'res_model': "lerm.eln",
                'type': 'ir.actions.act_window',
                'target': 'current',
                'res_id': self.eln_ref.id,
                
            }


    @api.model
    def create(self, vals):
        # import wdb;wdb.set_trace()
        record = super(CementCompatablity, self).create(vals)
        record.eln_ref.write({'model_id':record.id})
        return record
    
    def generate_line_chart(self):
        # Prepare data for the chart
        x_values = []
        y_values = []
        for line in self.child_lines:
            x_values.append(line.admixture_dosage_percent)
            y_values.append(line.flow_60_min)
        
        # Create the line chart
        plt.plot(x_values, y_values, marker='o')
        plt.xlabel('Admixture Dosage %')
        plt.ylabel('Flow at 60 Min Retention (Sec)')
        plt.title('Admixture Dosage % vs Flow 60 Min Retention (Sec)')


        plt.ylim(bottom=0, top=max(y_values) + 10)
        # plt.xlim(left=0, right=max(x_values) + 1.5 )
        
        for i in range(len(x_values)):
            plt.plot([x_values[i], x_values[i]], [0, y_values[i]], color='black', linestyle='--', alpha=0.5)
            if i < len(x_values) - 1:
                plt.plot([x_values[i], x_values[i + 1]], [y_values[i], y_values[i + 1]], color='black', linestyle='-', alpha=0.5)

        # max_y_index = y_values.index(max(y_values))
        
        # plt.axhline(y=y_values[max_y_index], color='red', linestyle='--')

        # plt.axvline(x=x_values[max_y_index], color='red', linestyle='--')
        
        label_space = 1
        
        for i in range(len(x_values)):
            plt.text(x_values[i], y_values[i] + label_space , f'{y_values[i]}', fontsize=10, ha='left', va='bottom', color='black')

        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        plt.close()  # Close the figure to free up resources
        buffer.seek(0)
    
        # Convert the chart image to base64
        chart_image = base64.b64encode(buffer.read()).decode('utf-8')  
        return chart_image
    
    @api.depends('child_lines')
    def _compute_chart_image(self):
        try:
            for record in self:
                chart_image = record.generate_line_chart()
                record.chart_image = chart_image
        except:
            pass        


class CementCompatablityLines(models.Model):
    _name = "mechanical.cement.compatiblity.lines"
    parent_id = fields.Many2one('mechanical.cement.compatiblity',string="Parent Id")
    water_cement_ratio = fields.Float("Water Cement Ratio (w/c)",compute="_compute_water_cement_ratio")
    admixture_dosage_percent = fields.Float("Admixture Dosage %")
    wt_of_cement = fields.Float("Wt. of  Cement (g)")
    wt_of_water = fields.Float("Wt.of water  (g)")
    wt_of_admixture = fields.Float("Wt. of Admixture (g)",compute="_compute_wt_of_admixture")
    flow_sec = fields.Float("Flow 0 Min Retention (Sec)")
    flow_30_min = fields.Float("Flow at 30 Min Retention (Sec)")
    flow_60_min = fields.Float("Flow at 60 Min Retention (Sec)")



    @api.depends('wt_of_water', 'wt_of_cement')
    def _compute_water_cement_ratio(self):
        for record in self:
            if record.wt_of_cement != 0:
                record.water_cement_ratio = Decimal(record.wt_of_water) / Decimal(record.wt_of_cement)
            else:
                record.water_cement_ratio = 0
        

    @api.depends('admixture_dosage_percent', 'wt_of_cement')
    def _compute_wt_of_admixture(self):
        for record in self:
            if record.admixture_dosage_percent != 0:
                record.wt_of_admixture = (Decimal(record.wt_of_cement) * Decimal(record.admixture_dosage_percent)) / 100
            else:
                record.wt_of_admixture = 0
    


