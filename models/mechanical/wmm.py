from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
from datetime import datetime , timedelta
import math
from decimal import Decimal
import matplotlib.pyplot as plt
import io
import base64

class WmmMechanical(models.Model):
    _name = "mechanical.wmm"
    _inherit = "lerm.eln"
    _rec_name = "name"


    name = fields.Char("Name",default="WMM")
    parameter_id = fields.Many2one('eln.parameters.result', string="Parameter")

    sample_parameters = fields.Many2many('lerm.parameter.master',string="Parameters",compute="_compute_sample_parameters",store=True)
    eln_ref = fields.Many2one('lerm.eln',string="Eln")
    grade = fields.Many2one('lerm.grade.line',string="Grade",compute="_compute_grade_id",store=True)

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
        record = super(WmmMechanical, self).create(vals)
        # record.get_all_fields()
        record.eln_ref.write({'model_id':record.id})
        return record

    @api.depends('eln_ref')
    def _compute_sample_parameters(self):
        for record in self:
            records = record.eln_ref.parameters_result.parameter.ids
            record.sample_parameters = records
            print("Records",records)

    def get_all_fields(self):
        record = self.env['mechanical.wmm'].browse(self.ids[0])
        field_values = {}
        for field_name, field in record._fields.items():
            field_value = record[field_name]
            field_values[field_name] = field_value

        return field_values
    
    # added
    @api.depends('eln_ref')
    def _compute_grade_id(self):
        if self.eln_ref:
            self.grade = self.eln_ref.grade_id.id


    # @api.depends('eln_ref')
    # def _compute_sample_parameters(self):
        
    #     for record in self:
    #         records = record.eln_ref.parameters_result.parameter.ids
    #         record.sample_parameters = records
    #         print("Records",records)

    @api.depends('eln_ref','sample_parameters')
    def _compute_visible(self):
        for record in self:
            record.dry_gradation_visible = False
            record.water_absorbtion_visible  = False  
            record.elongation_visible = False
            record.flakiness_visible = False
            record.abrasion_visible = False
            record.impact_visible = False
            record.plastic_visible = False
            record.liquid_limit_visible = False
            record.plasticity_index_visible = False
            record.density_relation_visible = False
            record.cbr_visible = False
            record.wmm_density_visible = False
            record.specific_gravity_wmm_visible = False
            record.wmm_infra_visible = False


            for sample in record.sample_parameters:
                print("Samples internal id",sample.internal_id)
                if sample.internal_id == '64fecdf5-6741-4817-95f4-5e53a0676c5f':
                    record.dry_gradation_visible = True
                if sample.internal_id == '51e6dcfa-6d14-468e-8488-6d100818e924':
                    record.water_absorbtion_visible  = True  
                if sample.internal_id == 'f1a27ee1-3e7e-4fff-b912-f7b046f5099c':
                    record.elongation_visible = True
                    record.flakiness_visible = True
                if sample.internal_id == 'b8390baa-2d4b-47f4-b9ee-7a4a5b176b97':
                    record.elongation_visible = True
                    record.flakiness_visible = True
                if sample.internal_id == '7edace9a-a4ae-451c-a4cf-36d2c042ed7d':
                    record.abrasion_visible = True
                if sample.internal_id == 'aaea4989-7446-446e-a018-8a5f9dcfd549':
                    record.impact_visible = True
                if sample.internal_id == 'ed625cc1-4295-4d00-977f-205b7a508363':
                    record.plastic_visible  = True  
                if sample.internal_id == '88627a7b-c438-4d13-bfde-330ee0005734':
                    record.liquid_limit_visible = True
                if sample.internal_id == '6fd54acc-61fd-478f-9bcf-6817965312f1':
                    record.liquid_limit_visible = True
                    record.plasticity_index_visible = True
                if sample.internal_id == 'fc19b116-3cb1-448a-8bb0-8f48657ae86b':
                    record.density_relation_visible = True
                if sample.internal_id == '6c0014d9-12d3-45ea-bc23-5b35ec6ffd24':
                    record.cbr_visible = True

                if sample.internal_id == '429h14d9-12d3-45ea-bc23-5b35ec6ffd50':
                    record.wmm_density_visible = True

                if sample.internal_id == '356klu87-12d3-45ea-bc23-5b35ec6ffd50':
                    record.specific_gravity_wmm_visible = True

                if sample.internal_id == '32145ukt1-12d3-45ea-bc23-5b35ec6ff142':
                    record.wmm_infra_visible = True


      # Specific Gravity  
    specific_gravity_wmm_name = fields.Char(default="Specific Gravity ")
    specific_gravity_wmm_visible = fields.Boolean(compute="_compute_visible")

    wt_ssd_wmm = fields.Integer('Weight of saturated surface dry (SSD) sample in air in gms, A')
    wt_saturated_wmm = fields.Float('Weight of saturated sample in water in gms, B')
    oven_dried_wmm = fields.Float('Oven dried weight of sample in gms, C')
    specific_gravity_wmm = fields.Float('Specific Gravity, [C/(A-B)]',compute="_compute_specific_gravity")


    @api.depends('wt_ssd_wmm', 'wt_saturated_wmm', 'oven_dried_wmm')
    def _compute_specific_gravity(self):
        for record in self:
            if record.wt_ssd_wmm and record.wt_saturated_wmm:
                try:
                    record.specific_gravity_wmm = record.oven_dried_wmm / (record.wt_ssd_wmm - record.wt_saturated_wmm)
                except ZeroDivisionError:
                    record.specific_gravity_wmm = 0.0  # Avoid division by zero
            else:
                record.specific_gravity_wmm = 0.0

    specific_gravity_wmm_conformity = fields.Selection([
            ('pass', 'Pass'),
            ('fail', 'Fail')], string="Conformity", compute="_compute_specific_gravity_wmm_conformity", store=True)



    @api.depends('specific_gravity_wmm','eln_ref','grade')
    def _compute_specific_gravity_wmm_conformity(self):
        
        for record in self:
            record.specific_gravity_wmm_conformity = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','356klu87-12d3-45ea-bc23-5b35ec6ffd50')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','356klu87-12d3-45ea-bc23-5b35ec6ffd50')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    req_min = material.req_min
                    req_max = material.req_max
                    mu_value = line.mu_value
                    
                    lower = record.specific_gravity_wmm - record.specific_gravity_wmm*mu_value
                    upper = record.specific_gravity_wmm + record.specific_gravity_wmm*mu_value
                    if lower >= req_min and upper <= req_max:
                        record.specific_gravity_wmm_conformity = 'pass'
                        break
                    else:
                        record.specific_gravity_wmm_conformity = 'fail'

    specific_gravity_wmm_nabl = fields.Selection([
        ('pass', 'NABL'),
        ('fail', 'Non-NABL')], string="NABL", compute="_compute_specific_gravity_wmm_nabl", store=True)

    @api.depends('specific_gravity_wmm','eln_ref','grade')
    def _compute_specific_gravity_wmm_nabl(self):
        
        for record in self:
            record.specific_gravity_wmm_nabl = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','356klu87-12d3-45ea-bc23-5b35ec6ffd50')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','356klu87-12d3-45ea-bc23-5b35ec6ffd50')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    lab_min = line.lab_min_value
                    lab_max = line.lab_max_value
                    mu_value = line.mu_value
                    
                    lower = record.specific_gravity_wmm - record.specific_gravity_wmm*mu_value
                    upper = record.specific_gravity_wmm + record.specific_gravity_wmm*mu_value
                    if lower >= lab_min and upper <= lab_max:
                        record.specific_gravity_wmm_nabl = 'pass'
                        break
                    else:
                        record.specific_gravity_wmm_nabl = 'fail'

                

    # Dry Gradation
    dry_gradation_name = fields.Char(default="Dry Gradation")
    dry_gradation_visible = fields.Boolean(compute="_compute_visible")

    dry_gradation_table = fields.One2many('mech.dry.gradation.line','parent_id',string="Dry Gradation")
    total_sieve_analysis = fields.Integer(string="Total",compute="_compute_total_sieve")
    


    def calculate_sieve(self): 
        for record in self:
            for line in record.dry_gradation_table:
                print("Rows",str(line.percent_retained))
                previous_line = line.serial_no - 1
                if previous_line == 0:
                    if line.percent_retained == 0:
                        # print("Percent retained 0",line.percent_retained)
                        line.write({'cumulative_retained': round(line.percent_retained + line.percent_retained,2)})
                        line.write({'passing_percent': 100 })
                    else:
                        # print("Percent retained else",line.percent_retained)
                        line.write({'cumulative_retained': round(line.percent_retained + line.percent_retained,2)})
                        line.write({'passing_percent': round(100 -line.percent_retained - line.percent_retained,2)})
                else:
                    previous_line_record = self.env['mech.dry.gradation.line'].sudo().search([("serial_no", "=", previous_line),("parent_id","=",self.id)]).cumulative_retained
                    line.write({'cumulative_retained': round(previous_line_record + line.percent_retained,2)})
                    line.write({'passing_percent': round(100-(previous_line_record + line.percent_retained),2)})
                    print("Previous Cumulative",previous_line_record)
                    

    


    @api.depends('dry_gradation_table.wt_retained')
    def _compute_total_sieve(self):
        for record in self:
            print("recordd",record)
            record.total_sieve_analysis = sum(record.dry_gradation_table.mapped('wt_retained'))

    def default_get(self, fields):
        print("From Default Value")
        res = super(WmmMechanical, self).default_get(fields)

        default_dry_sieve_sizes = []
        default_elongated_sieve_sizes = []
        dry_sieve_sizes = ['53 mm', '45 mm','22.4 mm', '11.2 mm', '4.75 mm','2.36 mm','600 micron','75 micron','pan']
        elongation_sieve_sizes = ['63 mm', '50 mm', '40 mm', '31.5 mm', '25 mm','20 mm','16 mm','12.5 mm','10 mm','6.3 mm']


        for i in range(9):  # You can change the number of default lines as needed
            size = {
                'sieve_size': dry_sieve_sizes[i] # Set the default product
                # Set the default quantity
            }
            default_dry_sieve_sizes.append((0, 0, size))
        res['dry_gradation_table'] = default_dry_sieve_sizes
        for i in range(10):  # You can change the number of default lines as needed
            size = {
                'sieve_size': elongation_sieve_sizes[i] # Set the default product
                # Set the default quantity
            }
            default_elongated_sieve_sizes.append((0, 0, size))
        res['dry_gradation_table'] = default_dry_sieve_sizes
        res['elongation_table'] = default_elongated_sieve_sizes

        return res

    # Water Absorbtion 
    water_absorbtion_name = fields.Char(default="Water Absorbtion")
    water_absorbtion_visible = fields.Boolean(compute="_compute_visible")

    wt_ssd_sample = fields.Integer('Weight of saturated surface dry (SSD) sample in air in gms, A')
    oven_dried_wt = fields.Float('Oven dried weight of sample in gms, C')
    water_absorbtion = fields.Float('Water absorption  %',compute="_compute_water_absorbtion")


    @api.depends('wt_ssd_sample','oven_dried_wt')
    def _compute_water_absorbtion(self):
        for record in self:
            if record.oven_dried_wt != 0:
                record.water_absorbtion = round((record.wt_ssd_sample - record.oven_dried_wt)/record.oven_dried_wt * 100,2)
            else:
                record.water_absorbtion = 0


    water_absorbtion_conformity = fields.Selection([
            ('pass', 'Pass'),
            ('fail', 'Fail')], string="Conformity", compute="_compute_water_absorbtion_conformity", store=True)



    @api.depends('water_absorbtion','eln_ref','grade')
    def _compute_water_absorbtion_conformity(self):
        
        for record in self:
            record.water_absorbtion_conformity = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','51e6dcfa-6d14-468e-8488-6d100818e924')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','51e6dcfa-6d14-468e-8488-6d100818e924')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    req_min = material.req_min
                    req_max = material.req_max
                    mu_value = line.mu_value
                    
                    lower = record.water_absorbtion - record.water_absorbtion*mu_value
                    upper = record.water_absorbtion + record.water_absorbtion*mu_value
                    if lower >= req_min and upper <= req_max:
                        record.water_absorbtion_conformity = 'pass'
                        break
                    else:
                        record.water_absorbtion_conformity = 'fail'

    water_absorbtion_nabl = fields.Selection([
        ('pass', 'NABL'),
        ('fail', 'Non-NABL')], string="NABL", compute="_compute_water_absorbtion_nabl", store=True)

    @api.depends('water_absorbtion','eln_ref','grade')
    def _compute_water_absorbtion_nabl(self):
        
        for record in self:
            record.water_absorbtion_nabl = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','51e6dcfa-6d14-468e-8488-6d100818e924')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','51e6dcfa-6d14-468e-8488-6d100818e924')]).parameter_table
            # for material in materials:
            #     if material.grade.id == record.grade.id:
            lab_min = line.lab_min_value
            lab_max = line.lab_max_value
            mu_value = line.mu_value
            
            lower = record.water_absorbtion - record.water_absorbtion*mu_value
            upper = record.water_absorbtion + record.water_absorbtion*mu_value
            if lower >= lab_min and upper <= lab_max:
                record.water_absorbtion_nabl = 'pass'
                break
            else:
                record.water_absorbtion_nabl = 'fail'



    # Flakiness and Elongation 
    elongation_name = fields.Char(default="Elongation and Flakiness Index")
    elongation_visible = fields.Boolean(compute="_compute_visible")

    flakiness_name = fields.Char(default=" Flakiness Index")
    flakiness_visible = fields.Boolean(compute="_compute_visible")

    elongation_table = fields.One2many('mech.elongation.flakiness.line','parent_id',string="Elongation Flakiness Index")

    total_wt_retained_fl_el = fields.Float('Total',compute="_compute_total_el_fl")
    total_elongated_retained = fields.Float('Total Elongation',compute="_compute_total_elongation")
    total_flakiness_retained = fields.Float('Total Flakiness',compute="_compute_total_flakiness")

    aggregate_elongation = fields.Float('Aggregate Elongation Value in %',compute="_compute_aggregate_elongation")
    aggregate_flakiness = fields.Float('Aggregate Flakiness Value in %' ,compute="_compute_aggregate_flakiness")
    aggregate_combine = fields.Float('Aggregate Elongation & Flakiness Value in %',compute="_compute_aggregate_combine")


    @api.depends('elongation_table.wt_retained')
    def _compute_total_el_fl(self):
        for record in self:
            record.total_wt_retained_fl_el = sum(record.elongation_table.mapped('wt_retained'))

    @api.depends('elongation_table.elongated_retained')
    def _compute_total_elongation(self):
        for record in self:
            record.total_elongated_retained = sum(record.elongation_table.mapped('elongated_retained'))

    @api.depends('elongation_table.flakiness_retained')
    def _compute_total_flakiness(self):
        for record in self:
            record.total_flakiness_retained = sum(record.elongation_table.mapped('flakiness_retained'))

    @api.depends('total_wt_retained_fl_el','total_elongated_retained')
    def _compute_aggregate_elongation(self):
        for record in self:
            if record.total_elongated_retained != 0:
                record.aggregate_elongation = record.total_elongated_retained/record.total_wt_retained_fl_el * 100
            else:
                record.aggregate_elongation = 0

    @api.depends('total_wt_retained_fl_el','total_flakiness_retained')
    def _compute_aggregate_flakiness(self):
        for record in self:
            if record.total_flakiness_retained != 0:
                record.aggregate_flakiness = record.total_flakiness_retained/record.total_wt_retained_fl_el * 100
            else:
                record.aggregate_flakiness = 0

    @api.depends('total_wt_retained_fl_el','total_flakiness_retained')
    def _compute_aggregate_combine(self):
        for record in self:
            record.aggregate_combine = record.aggregate_elongation+record.aggregate_flakiness


    aggregate_flakiness_conformity = fields.Selection([
            ('pass', 'Pass'),
            ('fail', 'Fail')], string="Conformity", compute="_compute_aggregate_flakiness_conformity", store=True)



    @api.depends('aggregate_flakiness','eln_ref','grade')
    def _compute_aggregate_flakiness_conformity(self):
        
        for record in self:
            record.aggregate_flakiness_conformity = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','b8390baa-2d4b-47f4-b9ee-7a4a5b176b97')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','b8390baa-2d4b-47f4-b9ee-7a4a5b176b97')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    req_min = material.req_min
                    req_max = material.req_max
                    mu_value = line.mu_value
                    
                    lower = record.aggregate_flakiness - record.aggregate_flakiness*mu_value
                    upper = record.aggregate_flakiness + record.aggregate_flakiness*mu_value
                    if lower >= req_min and upper <= req_max:
                        record.aggregate_flakiness_conformity = 'pass'
                        break
                    else:
                        record.aggregate_flakiness_conformity = 'fail'

    aggregate_flakiness_nabl = fields.Selection([
        ('pass', 'NABL'),
        ('fail', 'Non-NABL')], string="NABL", compute="_compute_aggregate_flakiness_nabl", store=True)

    @api.depends('aggregate_flakiness','eln_ref','grade')
    def _compute_aggregate_flakiness_nabl(self):
        
        for record in self:
            record.aggregate_flakiness_nabl = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','b8390baa-2d4b-47f4-b9ee-7a4a5b176b97')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','b8390baa-2d4b-47f4-b9ee-7a4a5b176b97')]).parameter_table
            # for material in materials:
            #     if material.grade.id == record.grade.id:
            lab_min = line.lab_min_value
            lab_max = line.lab_max_value
            mu_value = line.mu_value
            
            lower = record.aggregate_flakiness - record.aggregate_flakiness*mu_value
            upper = record.aggregate_flakiness + record.aggregate_flakiness*mu_value
            if lower >= lab_min and upper <= lab_max:
                record.aggregate_flakiness_nabl = 'pass'
                break
            else:
                record.aggregate_flakiness_nabl = 'fail'



    aggregate_elongation_conformity = fields.Selection([
            ('pass', 'Pass'),
            ('fail', 'Fail')], string="Conformity", compute="_compute_aggregate_elongation_conformity", store=True)



    @api.depends('aggregate_elongation','eln_ref','grade')
    def _compute_aggregate_elongation_conformity(self):
        
        for record in self:
            record.aggregate_elongation_conformity = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','f1a27ee1-3e7e-4fff-b912-f7b046f5099c')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','f1a27ee1-3e7e-4fff-b912-f7b046f5099c')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    req_min = material.req_min
                    req_max = material.req_max
                    mu_value = line.mu_value
                    
                    lower = record.aggregate_elongation - record.aggregate_elongation*mu_value
                    upper = record.aggregate_elongation + record.aggregate_elongation*mu_value
                    if lower >= req_min and upper <= req_max:
                        record.aggregate_elongation_conformity = 'pass'
                        break
                    else:
                        record.aggregate_elongation_conformity = 'fail'

    aggregate_elongation_nabl = fields.Selection([
        ('pass', 'NABL'),
        ('fail', 'Non-NABL')], string="NABL", compute="_compute_aggregate_elongation_nabl", store=True)

    @api.depends('aggregate_elongation','eln_ref','grade')
    def _compute_aggregate_elongation_nabl(self):
        
        for record in self:
            record.aggregate_elongation_nabl = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','f1a27ee1-3e7e-4fff-b912-f7b046f5099c')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','f1a27ee1-3e7e-4fff-b912-f7b046f5099c')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    lab_min = line.lab_min_value
                    lab_max = line.lab_max_value
                    mu_value = line.mu_value
                    
                    lower = record.aggregate_elongation - record.aggregate_elongation*mu_value
                    upper = record.aggregate_elongation + record.aggregate_elongation*mu_value
                    if lower >= lab_min and upper <= lab_max:
                        record.aggregate_elongation_nabl = 'pass'
                        break
                    else:
                        record.aggregate_elongation_nabl = 'fail'
            


            



    # Abrasion Value
    abrasion_value_name = fields.Char("Name",default="Abrasion Value")
    abrasion_visible = fields.Boolean("Abrasion Visible",compute="_compute_visible")

    total_weight_sample_abrasion = fields.Integer(string="Total weight of Sample in gms")
    weight_passing_sample_abrasion = fields.Integer(string="Weight of Passing sample in 1.70 mm IS sieve in gms")
    weight_retain_sample_abrasion = fields.Integer(string="Weight of Retain sample in 1.70 mm IS sieve in gms",compute="_compute_weight_retain_sample_abrasion")
    abrasion_value_percentage = fields.Float(string="Abrasion Value (%)",compute="_compute_sample_weight")


    @api.depends('total_weight_sample_abrasion', 'weight_passing_sample_abrasion')
    def _compute_weight_retain_sample_abrasion(self):
        for line in self:
            line.weight_retain_sample_abrasion = line.total_weight_sample_abrasion - line.weight_passing_sample_abrasion


    @api.depends('total_weight_sample_abrasion', 'weight_passing_sample_abrasion')
    def _compute_sample_weight(self):
        for line in self:
            if line.total_weight_sample_abrasion != 0:
                line.abrasion_value_percentage = round((line.weight_passing_sample_abrasion / line.total_weight_sample_abrasion) * 100,2)
            else:
                line.abrasion_value_percentage = 0.0


    abrasion_value_percentage_conformity = fields.Selection([
            ('pass', 'Pass'),
            ('fail', 'Fail')], string="Conformity", compute="_compute_abrasion_value_percentage_conformity", store=True)



    @api.depends('abrasion_value_percentage','eln_ref','grade')
    def _compute_abrasion_value_percentage_conformity(self):
        
        for record in self:
            record.abrasion_value_percentage_conformity = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','7edace9a-a4ae-451c-a4cf-36d2c042ed7d')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','7edace9a-a4ae-451c-a4cf-36d2c042ed7d')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    req_min = material.req_min
                    req_max = material.req_max
                    mu_value = line.mu_value
                    
                    lower = record.abrasion_value_percentage - record.abrasion_value_percentage*mu_value
                    upper = record.abrasion_value_percentage + record.abrasion_value_percentage*mu_value
                    if lower >= req_min and upper <= req_max:
                        record.abrasion_value_percentage_conformity = 'pass'
                        break
                    else:
                        record.abrasion_value_percentage_conformity = 'fail'

    abrasion_value_percentage_nabl = fields.Selection([
        ('pass', 'NABL'),
        ('fail', 'Non-NABL')], string="NABL", compute="_compute_abrasion_value_percentage_nabl", store=True)

    @api.depends('abrasion_value_percentage','eln_ref','grade')
    def _compute_abrasion_value_percentage_nabl(self):
        
        for record in self:
            record.abrasion_value_percentage_nabl = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','7edace9a-a4ae-451c-a4cf-36d2c042ed7d')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','7edace9a-a4ae-451c-a4cf-36d2c042ed7d')]).parameter_table
            # for material in materials:
            #     if material.grade.id == record.grade.id:
            lab_min = line.lab_min_value
            lab_max = line.lab_max_value
            mu_value = line.mu_value
            
            lower = record.abrasion_value_percentage - record.abrasion_value_percentage*mu_value
            upper = record.abrasion_value_percentage + record.abrasion_value_percentage*mu_value
            if lower >= lab_min and upper <= lab_max:
                record.abrasion_value_percentage_nabl = 'pass'
                break
            else:
                record.abrasion_value_percentage_nabl = 'fail'

    # Impact Value 
    impact_value_name = fields.Char("Name",default="Impact Value")
    impact_visible = fields.Boolean("Impact Visible",compute="_compute_visible")

    impact_value_child_lines = fields.One2many('mech.wmm.impact.line','parent_id',string="Parameter")

    average_impact_value = fields.Float(string="Average Impact Value", compute="_compute_average_impact_value")

    

    @api.depends('impact_value_child_lines.impact_value')
    def _compute_average_impact_value(self):
        for record in self:
            if record.impact_value_child_lines:
                sum_impact_value = sum(record.impact_value_child_lines.mapped('impact_value'))
                record.average_impact_value = round((sum_impact_value / len(record.impact_value_child_lines)),1)
            else:
                record.average_impact_value = 0.0

    average_impact_value_conformity = fields.Selection([
            ('pass', 'Pass'),
            ('fail', 'Fail')], string="Conformity", compute="_compute_average_impact_value_conformity", store=True)



    @api.depends('average_impact_value','eln_ref','grade')
    def _compute_average_impact_value_conformity(self):
        
        for record in self:
            record.average_impact_value_conformity = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','aaea4989-7446-446e-a018-8a5f9dcfd549')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','aaea4989-7446-446e-a018-8a5f9dcfd549')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    req_min = material.req_min
                    req_max = material.req_max
                    mu_value = line.mu_value
                    
                    lower = record.average_impact_value - record.average_impact_value*mu_value
                    upper = record.average_impact_value + record.average_impact_value*mu_value
                    if lower >= req_min and upper <= req_max:
                        record.average_impact_value_conformity = 'pass'
                        break
                    else:
                        record.average_impact_value_conformity = 'fail'

    average_impact_value_nabl = fields.Selection([
        ('pass', 'NABL'),
        ('fail', 'Non-NABL')], string="NABL", compute="_compute_average_impact_value_nabl", store=True)

    @api.depends('average_impact_value','eln_ref','grade')
    def _compute_average_impact_value_nabl(self):
        
        for record in self:
            record.average_impact_value_nabl = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','aaea4989-7446-446e-a018-8a5f9dcfd549')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','aaea4989-7446-446e-a018-8a5f9dcfd549')]).parameter_table
            # for material in materials:
            #     if material.grade.id == record.grade.id:
            lab_min = line.lab_min_value
            lab_max = line.lab_max_value
            mu_value = line.mu_value
            
            lower = record.average_impact_value - record.average_impact_value*mu_value
            upper = record.average_impact_value + record.average_impact_value*mu_value
            if lower >= lab_min and upper <= lab_max:
                record.average_impact_value_nabl = 'pass'
                break
            else:
                record.average_impact_value_nabl = 'fail'

    # Liquid Limit
    liquid_limit_name = fields.Char("Name",default="Liquid Limit")
    liquid_limit_visible = fields.Boolean("Liquid Limit Visible",compute="_compute_visible")

    liquid_limit_table = fields.One2many('mech.wmm.liquid.limit.line','parent_id',string="Liquid Limit")
    liquid_limit = fields.Float("Liquid Limit")
    remarks_liquid_limit = fields.Selection([
        ('plastic', 'Plastic'),
        ('non-plastic', 'Non-Plastic')],"Remarks",store=True)
    

    liquid_limit_conformity = fields.Selection([
            ('pass', 'Pass'),
            ('fail', 'Fail')], string="Conformity", compute="_compute_liquid_limit_conformity", store=True)
    


      # def calculate_result(self):
    are_child_lines_filled = fields.Boolean(compute='_compute_are_child_lines_filled',string='child lines',store=False)

    @api.depends('liquid_limit_table.moisture_percent', 'liquid_limit_table.mass_dry_sample')  # Replace with actual field names
    def _compute_are_child_lines_filled(self):
        for record in self:
            all_lines_filled = all(line.moisture_percent and line.mass_dry_sample for line in record.liquid_limit_table)
            record.are_child_lines_filled = all_lines_filled

    

    def liquid_calculation(self):
        print('<<<<<<<<<<<<')
        for record in self:
            data = self.liquid_limit_table
           
            result = 0  # Initialize result before the loop
            print(data, 'data')
            container2Moisture = data[1].moisture_percent
            container1Moisture = data[0].moisture_percent
            container3Moisture = data[2].moisture_percent
            cont2blow = data[1].blows
            cont3blow = data[2].blows
            result = (container2Moisture * 100 - ((container2Moisture - container3Moisture) * 100 * (25 - cont2blow)) / (cont3blow - cont2blow)) / 100
            print(result, 'final result')
        self.write({'liquid_limit': result})





    @api.depends('liquid_limit','eln_ref','grade')
    def _compute_liquid_limit_conformity(self):
        
        for record in self:
            record.liquid_limit_conformity = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','88627a7b-c438-4d13-bfde-330ee0005734')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','88627a7b-c438-4d13-bfde-330ee0005734')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    req_min = material.req_min
                    req_max = material.req_max
                    mu_value = line.mu_value
                    
                    lower = record.liquid_limit - record.liquid_limit*mu_value
                    upper = record.liquid_limit + record.liquid_limit*mu_value
                    if lower >= req_min and upper <= req_max:
                        record.liquid_limit_conformity = 'pass'
                        break
                    else:
                        record.liquid_limit_conformity = 'fail'

    liquid_limit_nabl = fields.Selection([
        ('pass', 'NABL'),
        ('fail', 'Non-NABL')], string="NABL", compute="_compute_liquid_limit_value_nabl", store=True)

    @api.depends('liquid_limit','eln_ref','grade')
    def _compute_liquid_limit_value_nabl(self):
        
        for record in self:
            record.liquid_limit_nabl = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','88627a7b-c438-4d13-bfde-330ee0005734')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','88627a7b-c438-4d13-bfde-330ee0005734')]).parameter_table
            # for material in materials:
            #     if material.grade.id == record.grade.id:
            lab_min = line.lab_min_value
            lab_max = line.lab_max_value
            mu_value = line.mu_value
            
            lower = record.liquid_limit - record.liquid_limit*mu_value
            upper = record.liquid_limit + record.liquid_limit*mu_value
            if lower >= lab_min and upper <= lab_max:
                record.liquid_limit_nabl = 'pass'
                break
            else:
                record.liquid_limit_nabl = 'fail'



    # Plastic Limit
    plastic_name = fields.Char("Name",default="Plastic Limit")
    plastic_visible = fields.Boolean("Plastic Limit Visible",compute="_compute_visible")

    plastic_table = fields.One2many('mech.wmm.plastic.limit.line','parent_id',string="Plastic Limit")
    average_plastic_moisture = fields.Float("Average",compute="_compute_plastic_average")
    remarks_plastic = fields.Selection([
        ('plastic', 'Plastic'),
        ('non-plastic', 'Non-Plastic')],"Remarks",store=True)

   

    
    @api.depends('plastic_table.moisture_percent')
    def _compute_plastic_average(self):
        for record in self:
            if record.plastic_table:
                sum_moisture_percent = sum(record.plastic_table.mapped('moisture_percent'))
                record.average_plastic_moisture = round((sum_moisture_percent / len(record.plastic_table)),2)
            else:
                record.average_plastic_moisture = 0.0


    average_plastic_moisture_conformity = fields.Selection([
            ('pass', 'Pass'),
            ('fail', 'Fail')], string="Conformity", compute="_compute_average_plastic_moisture_conformity", store=True)



    @api.depends('average_plastic_moisture','eln_ref','grade')
    def _compute_average_plastic_moisture_conformity(self):
        
        for record in self:
            record.average_plastic_moisture_conformity = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','ed625cc1-4295-4d00-977f-205b7a508363')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','ed625cc1-4295-4d00-977f-205b7a508363')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    req_min = material.req_min
                    req_max = material.req_max
                    mu_value = line.mu_value
                    
                    lower = record.average_plastic_moisture - record.average_plastic_moisture*mu_value
                    upper = record.average_plastic_moisture + record.average_plastic_moisture*mu_value
                    if lower >= req_min and upper <= req_max:
                        record.average_plastic_moisture_conformity = 'pass'
                        break
                    else:
                        record.average_plastic_moisture_conformity = 'fail'

    average_plastic_moisture_nabl = fields.Selection([
        ('pass', 'NABL'),
        ('fail', 'Non-NABL')], string="NABL", compute="_compute_average_plastic_moisture_nabl", store=True)

    @api.depends('average_plastic_moisture','eln_ref','grade')
    def _compute_average_plastic_moisture_nabl(self):
        
        for record in self:
            record.average_plastic_moisture_nabl = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','ed625cc1-4295-4d00-977f-205b7a508363')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','ed625cc1-4295-4d00-977f-205b7a508363')]).parameter_table
            # for material in materials:
            #     if material.grade.id == record.grade.id:
            lab_min = line.lab_min_value
            lab_max = line.lab_max_value
            mu_value = line.mu_value
            
            lower = record.average_plastic_moisture - record.average_plastic_moisture*mu_value
            upper = record.average_plastic_moisture + record.average_plastic_moisture*mu_value
            if lower >= lab_min and upper <= lab_max:
                record.average_plastic_moisture_nabl = 'pass'
                break
            else:
                record.average_plastic_moisture_nabl = 'fail'

    # Plasticity Index
    plasticity_index_visible = fields.Boolean("Plasticity Index Visible",compute="_compute_visible")
    plasticity_index = fields.Float("Plasticity Index",compute="_compute_plasticity_limit")
    remarks_plasticity_index = fields.Selection([
        ('plastic', 'Plastic'),
        ('non-plastic', 'Non-Plastic')],"Remarks",store=True)

    @api.depends('average_plastic_moisture','liquid_limit')
    def _compute_plasticity_limit(self):
        for record in self:
            record.plasticity_index = record.liquid_limit - record.average_plastic_moisture

    plasticity_index_conformity = fields.Selection([
            ('pass', 'Pass'),
            ('fail', 'Fail')], string="Conformity", compute="_compute_plasticity_index_conformity", store=True)



    @api.depends('plasticity_index','eln_ref','grade')
    def _compute_plasticity_index_conformity(self):
        
        for record in self:
            record.plasticity_index_conformity = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','6fd54acc-61fd-478f-9bcf-6817965312f1')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','6fd54acc-61fd-478f-9bcf-6817965312f1')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    req_min = material.req_min
                    req_max = material.req_max
                    mu_value = line.mu_value
                    
                    lower = record.plasticity_index - record.plasticity_index*mu_value
                    upper = record.plasticity_index + record.plasticity_index*mu_value
                    if lower >= req_min and upper <= req_max:
                        record.plasticity_index_conformity = 'pass'
                        break
                    else:
                        record.plasticity_index_conformity = 'fail'

    plasticity_index_nabl = fields.Selection([
        ('pass', 'NABL'),
        ('fail', 'Non-NABL')], string="NABL", compute="_compute_plasticity_index_nabl", store=True)

    @api.depends('plasticity_index','eln_ref','grade')
    def _compute_plasticity_index_nabl(self):
        
        for record in self:
            record.plasticity_index_nabl = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','6fd54acc-61fd-478f-9bcf-6817965312f1')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','6fd54acc-61fd-478f-9bcf-6817965312f1')]).parameter_table
            # for material in materials:
            #     if material.grade.id == record.grade.id:
            lab_min = line.lab_min_value
            lab_max = line.lab_max_value
            mu_value = line.mu_value
            
            lower = record.plasticity_index - record.plasticity_index*mu_value
            upper = record.plasticity_index + record.plasticity_index*mu_value
            if lower >= lab_min and upper <= lab_max:
                record.plasticity_index_nabl = 'pass'
                break
            else:
                record.plasticity_index_nabl = 'fail'

    # Density Relation Heavy Compaction
    density_relation_name = fields.Char("Name",default="Density Relation Using Heavy Compaction")
    density_relation_visible = fields.Boolean("Density Relation Visible",compute="_compute_visible")

    density_relation_table = fields.One2many('mech.wmm.density.relation.line','parent_id',string="Density Relation")
    wt_of_modul = fields.Float('Weight of Mould in gm')
    vl_of_modul = fields.Float('Volume of Mould in cc')
    chart_image_density = fields.Binary("Line Chart", compute="_compute_chart_image_density", store=True)


      # added
    # field Density by Sand Replacement method
    wmm_density_name = fields.Char("Name",default="Field Density by Sand Replacement method")
    wmm_density_visible = fields.Boolean("Field Density by Sand Replacement method Visible",compute="_compute_visible")
    # job_no_dry_density = fields.Char(string="Job No")
    # material_dry_density = fields.Char(String="Material")
    # start_date_dry_density = fields.Date("Start Date")
    # end_date_dry_density = fields.Date("End Date")

    wmm_density_table = fields.One2many('mechanical.wmm.field.dencity.line','parent_id',string="Parameter")
    mmd_wmm = fields.Float(string="MMD gm/cc", store=True)
    omc_wmm = fields.Float(string="OMC %", store=True)
    wmm_degree_of_compaction = fields.Float(string="Degree of Compaction in %",compute="_compute_wmm_degree_of_compaction")

    @api.depends('wmm_density_table.degree_of_compaction')
    def _compute_wmm_degree_of_compaction(self):
        for record in self:
            degree_of_compaction_values = record.wmm_density_table.mapped('degree_of_compaction')
            if degree_of_compaction_values:
                wmm_degree_of_compaction = sum(degree_of_compaction_values) / len(degree_of_compaction_values)
                record.wmm_degree_of_compaction = wmm_degree_of_compaction
            else:
                record.wmm_degree_of_compaction = 0.0

    degree_of_compaction_conformity = fields.Selection([
            ('pass', 'Pass'),
            ('fail', 'Fail')], string="Conformity", compute="_compute_degree_of_compaction_conformity", store=True)

    @api.depends('wmm_degree_of_compaction','eln_ref','grade')
    def _compute_degree_of_compaction_conformity(self):
        
        for record in self:
            record.degree_of_compaction_conformity = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','429h14d9-12d3-45ea-bc23-5b35ec6ffd50')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','429h14d9-12d3-45ea-bc23-5b35ec6ffd50')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    req_min = material.req_min
                    req_max = material.req_max
                    mu_value = line.mu_value
                    
                    lower = record.wmm_degree_of_compaction - record.wmm_degree_of_compaction*mu_value
                    upper = record.wmm_degree_of_compaction + record.wmm_degree_of_compaction*mu_value
                    if lower >= req_min and upper <= req_max:
                        record.degree_of_compaction_conformity = 'pass'
                        break
                    else:
                        record.degree_of_compaction_conformity = 'fail'

    degree_of_compaction_nabl = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail')], string="NABL", compute="_compute_degree_of_compaction_nabl", store=True)

    @api.depends('wmm_degree_of_compaction','eln_ref','grade')
    def _compute_degree_of_compaction_nabl(self):
        
        for record in self:
            record.degree_of_compaction_nabl = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','429h14d9-12d3-45ea-bc23-5b35ec6ffd50')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','429h14d9-12d3-45ea-bc23-5b35ec6ffd50')]).parameter_table
            # for material in materials:
            #     if material.grade.id == record.grade.id:
            lab_min = line.lab_min_value
            lab_max = line.lab_max_value
            mu_value = line.mu_value
            
            lower = record.wmm_degree_of_compaction - record.wmm_degree_of_compaction*mu_value
            upper = record.wmm_degree_of_compaction + record.wmm_degree_of_compaction*mu_value
            if lower >= lab_min and upper <= lab_max:
                record.degree_of_compaction_nabl = 'pass'
                break
            else:
                record.degree_of_compaction_nabl = 'fail'



    def generate_line_chart_density(self):
        # Prepare data for the chart
        x_values = []
        y_values = []
        for line in self.density_relation_table:
            x_values.append(line.moisture)
            y_values.append(line.dry_density)
        
        # Create the line chart
        plt.plot(x_values, y_values, marker='o')
        plt.xlabel('% Moisture')
        plt.ylabel('Dry Density')
        plt.title('Density Relation Using Heavy Compaction')


        plt.ylim(bottom=0, top=max(y_values) + 10)
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        plt.close()  # Close the figure to free up resources
        buffer.seek(0)
    
        # Convert the chart image to base64
        chart_image = base64.b64encode(buffer.read()).decode('utf-8')  
        return chart_image
    
    @api.depends('density_relation_table')
    def _compute_chart_image_density(self):
        try:
            for record in self:
                chart_image = record.generate_line_chart_density()
                record.chart_image_density = chart_image
        except:
            pass 



    # CBR
    cbr_name = fields.Char("Name",default="CBR")
    cbr_visible = fields.Boolean("CBR Visible",compute="_compute_visible")

    cbr_table = fields.One2many('mechanical.wmm.cbr.line','parent_id',string="CBR")
    chart_image_cbr = fields.Binary("Line Chart", compute="_compute_chart_image_cbr", store=True)


    ps_2mm = fields.Float("PS for 2.5mm",compute="_compute_ps_2mm")
    pt_2mm = fields.Float("PT at 2.5mm",default=1370)
    cbr_2mm = fields.Float("CBR at 2.5mm",compute="_compute_cbr_2mm")

    ps_5mm = fields.Float("PS for 5mm",compute="_compute_ps_5mm")
    pt_5mm = fields.Float("PT at 5mm",default=2055)
    cbr_5mm = fields.Float("CBR at 5mm",compute="_compute_cbr_5mm")

    cbr_result = fields.Float("CBR",compute="_compute_final_cbr")

    @api.depends('cbr_table')
    def _compute_ps_2mm(self):
        for record in self:
            if record.cbr_table and len(record.cbr_table) >= 6:
                fifth_row = record.cbr_table[5] 
                record.ps_2mm = fifth_row.load
            else:
                record.ps_2mm = 0


    @api.depends('cbr_table')
    def _compute_ps_5mm(self):
        for record in self:
            if record.cbr_table and len(record.cbr_table) >= 9:
                fifth_row = record.cbr_table[8] 
                record.ps_5mm = fifth_row.load
            else:
                record.ps_5mm = 0

    @api.depends('pt_2mm','ps_2mm')
    def _compute_cbr_2mm(self):
        for record in self:
            if record.pt_2mm != 0:
                record.cbr_2mm = round((record.ps_2mm/record.pt_2mm)*100,2)
            else:
                record.cbr_2mm = 0

    @api.depends('pt_5mm','ps_5mm')
    def _compute_cbr_5mm(self):
        for record in self:
            if record.pt_5mm != 0:
                record.cbr_5mm = round((record.ps_5mm/record.pt_5mm)*100,2)
            else:
                record.cbr_5mm = 0

    @api.depends('cbr_5mm','cbr_2mm')
    def _compute_final_cbr(self):
        for record in self:
            if record.cbr_5mm > record.cbr_2mm:
                record.cbr_result = record.cbr_5mm
            else:
                record.cbr_result = record.cbr_2mm


    def generate_line_chart_cbr(self):
        # Prepare data for the chart
        x_values = []
        y_values = []
        for line in self.cbr_table:
            x_values.append(line.penetration)
            y_values.append(line.load)
        
        # Create the line chart
        plt.plot(x_values, y_values, marker='o')
        plt.xlabel('Penetration')
        plt.ylabel('Load')
        plt.title('CBR')


        plt.ylim(bottom=0, top=max(y_values) + 10)
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        plt.close()  # Close the figure to free up resources
        buffer.seek(0)
    
        # Convert the chart image to base64
        chart_image = base64.b64encode(buffer.read()).decode('utf-8')  
        return chart_image
    
    @api.depends('cbr_table')
    def _compute_chart_image_cbr(self):
        try:
            for record in self:
                chart_image = record.generate_line_chart_cbr()
                record.chart_image_cbr = chart_image
        except:
            pass 



     # CBR Infrastructure

    wmm_infra_name = fields.Char("Name",default="California Bearing Ratio")
    wmm_infra_visible = fields.Boolean("California Bearing Ratio Visible",compute="_compute_visible")
    
    wmm_infra_table = fields.One2many('mechanical.wmm.infra.cbr.line','parent_id',string="CBR")
    chart_image_cbr_infra = fields.Binary("Line Chart", compute="_compute_chart_image_cbr_infra_wmm", store=True)

    wmm_infra_ps_2mm = fields.Float("PS for 2.5mm",compute="_compute_ps_2mm_wmm_infra_ps")
    wmm_infra_pt_2mm = fields.Float("PT at 2.5mm",default=1370)
    wmm_infra_cbr_2mm = fields.Float("CBR at 2.5mm",compute="_compute_cbr_2mm_infra")

    wmm_infra_ps_5mm = fields.Float("PS for 5mm",compute="_compute_ps_5mm_infra")
    wmm_infra_pt_5mm = fields.Float("PT at 5mm",default=2055)
    wmm_infra_cbr_5mm = fields.Float("CBR at 5mm",compute="_compute_cbr_5mm_infra")

    wmm_infra_cbr_result = fields.Float("CBR",compute="_compute_final_cbr_infra")

    @api.depends('wmm_infra_table')
    def _compute_ps_2mm_wmm_infra_ps(self):
        for record in self:
            if record.wmm_infra_table and len(record.wmm_infra_table) >= 6:
                fifth_row1 = record.wmm_infra_table[5] 
                record.wmm_infra_ps_2mm = fifth_row1.load1
            else:
                record.wmm_infra_ps_2mm = 0


    @api.depends('wmm_infra_table')
    def _compute_ps_5mm_infra(self):
        for record in self:
            if record.wmm_infra_table and len(record.wmm_infra_table) >= 9:
                fifth_row = record.wmm_infra_table[8] 
                record.wmm_infra_ps_5mm = fifth_row.load1
            else:
                record.wmm_infra_ps_5mm = 0

    @api.depends('wmm_infra_pt_2mm','wmm_infra_ps_2mm')
    def _compute_cbr_2mm_infra(self):
        for record in self:
            if record.wmm_infra_pt_2mm != 0:
                record.wmm_infra_cbr_2mm = round((record.wmm_infra_ps_2mm/record.wmm_infra_pt_2mm)*100,2)
            else:
                record.wmm_infra_cbr_2mm = 0

    @api.depends('wmm_infra_pt_5mm','wmm_infra_ps_5mm')
    def _compute_cbr_5mm_infra(self):
        for record in self:
            if record.wmm_infra_pt_5mm != 0:
                record.wmm_infra_cbr_5mm = round((record.wmm_infra_ps_5mm/record.wmm_infra_pt_5mm)*100,2)
            else:
                record.wmm_infra_cbr_5mm = 0

    @api.depends('wmm_infra_cbr_5mm','wmm_infra_cbr_2mm')
    def _compute_final_cbr_infra(self):
        for record in self:
            if record.wmm_infra_cbr_5mm > record.wmm_infra_cbr_2mm:
                record.wmm_infra_cbr_result = record.wmm_infra_cbr_5mm
            else:
                record.wmm_infra_cbr_result = record.wmm_infra_cbr_2mm


    def wmm_line_chart_cbr_infra(self):
        # Prepare data for the chart
        x_values = []
        y_values = []
        for line in self.wmm_infra_table:
            x_values.append(line.penetration1)
            y_values.append(line.load1)
        
        # Create the line chart
        plt.plot(x_values, y_values, marker='o')
        plt.xlabel('Penetration')
        plt.ylabel('Load')
        plt.title('CBR')


        plt.ylim(bottom=0, top=max(y_values) + 10)
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        plt.close()  # Close the figure to free up resources
        buffer.seek(0)
    
        # Convert the chart image to base64
        chart_image = base64.b64encode(buffer.read()).decode('utf-8')  
        return chart_image
    
    @api.depends('wmm_infra_table')
    def _compute_chart_image_cbr_infra_wmm(self):
        try:
            for record in self:
                chart_image = record.wmm_line_chart_cbr_infra()
                record.chart_image_cbr_infra = chart_image
        except:
            pass 


class WmmInfraCBRLine(models.Model):
    _name = "mechanical.wmm.infra.cbr.line"
    parent_id = fields.Many2one('mechanical.wmm',string="Parent Id")

    penetration1 = fields.Float(string="Penetration in mm")
    proving_reading1 = fields.Float(string="Proving Ring Reading 1")

    proving_reading2 = fields.Float(string="Proving Ring Reading 2")
    proving_reading3 = fields.Float(string="Proving Ring Reading 2")

    proving_reading_avg = fields.Integer(string="Proving Ring Reading Avg.",compute="_compute_avg_reading")

    load1 = fields.Float(string="Load in Kg", compute="_compute_load")


    @api.depends('proving_reading1', 'proving_reading2', 'proving_reading3')
    def _compute_avg_reading(self):
        for rec in self:
            readings = [rec.proving_reading1, rec.proving_reading2, rec.proving_reading3]
            if any(readings):
                avg = sum(readings) / 3
                if avg <= 5.5:
                    rec.proving_reading_avg = math.floor(avg)
                else:
                    rec.proving_reading_avg = math.ceil(avg)
            else:
                rec.proving_reading_avg = 0


    @api.depends('proving_reading_avg')
    def _compute_load(self):
        for record in self:
            record.load1 = record.proving_reading_avg * 5.88



class WmmDensityRelationLine(models.Model):
    _name = "mech.wmm.density.relation.line"
    parent_id = fields.Many2one('mechanical.wmm',string="Parent Id")

    determination_no = fields.Float(string="Determination No")
    wt_of_modul_compact = fields.Integer(string="Weight of Mould + Compacted sample in gm")
    wt_of_compact = fields.Integer(string="Weight of compacted sample in gm", compute="_compute_wt_of_compact")
    bulk_density = fields.Float(string="Bulk Density of sample in gm/cc", compute="_compute_bulk_density")
    container_no = fields.Integer(string="Container No")
    wt_of_container = fields.Float(string="Weight of Container in gm")
    wt_of_container_wet = fields.Float(string="Weight of Container + wet sample in gm")
    wt_of_container_dry = fields.Float(string="Weight of Container + dry sample in gm")
    wt_of_dry_sample = fields.Float(string="Weight of dry sample in gm", compute="_compute_wt_of_dry_sample")
    wt_of_moisture = fields.Float(string="Weight of moisture in gm", compute="_compute_wt_of_moisture")
    moisture = fields.Float(string="% Moisture", compute="_compute_moisture")
    dry_density = fields.Float(string="Dry density in gm/cc", compute="_compute_dry_density")


    @api.depends('wt_of_modul_compact', 'parent_id.wt_of_modul')
    def _compute_wt_of_compact(self):
        for line in self:
            line.wt_of_compact = round(line.wt_of_modul_compact - line.parent_id.wt_of_modul,2)



    @api.depends('wt_of_compact', 'parent_id.vl_of_modul')
    def _compute_bulk_density(self):
        for line in self:
            if line.parent_id.vl_of_modul != 0:
                line.bulk_density = round(line.wt_of_compact / line.parent_id.vl_of_modul,2)
            else:
                line.bulk_density = 0.0



    @api.depends('wt_of_container_dry', 'wt_of_container')
    def _compute_wt_of_dry_sample(self):
        for line in self:
            line.wt_of_dry_sample = round(line.wt_of_container_dry - line.wt_of_container,2)


    @api.depends('wt_of_container_wet','wt_of_container_dry')
    def _compute_wt_of_moisture(self):
        for record in self:
            record.wt_of_moisture = round((record.wt_of_container_wet - record.wt_of_container_dry),2)


    @api.depends('wt_of_moisture', 'wt_of_dry_sample')
    def _compute_moisture(self):
        for line in self:
            if line.wt_of_dry_sample != 0:
                line.moisture = round(line.wt_of_moisture / line.wt_of_dry_sample * 100,2)
            else:
                line.moisture = 0.0


    @api.depends('bulk_density', 'moisture')
    def _compute_dry_density(self):
        for line in self:
            line.dry_density = round((100 * line.bulk_density) / (100 + line.moisture),2)


 



class WmmCBRLine(models.Model):
    _name = "mechanical.wmm.cbr.line"
    parent_id = fields.Many2one('mechanical.wmm',string="Parent Id")

    penetration = fields.Float(string="Penetration in mm")
    proving_reading = fields.Float(string="Proving Ring Reading")
    load = fields.Float(string="Load in Kg", compute="_compute_load")


    @api.depends('proving_reading')
    def _compute_load(self):
        for record in self:
            record.load = record.proving_reading * 6.96



class WmmLiquidLimitLine(models.Model):
    _name = "mech.wmm.liquid.limit.line"
    parent_id = fields.Many2one('mechanical.wmm', string="Parent Id")
    
    container_no = fields.Char("Container No.")
    blows = fields.Integer(string="No of Blows")
    mass_wet_sample_container = fields.Float(string="Mass of wet sample+container, (M1) in gms")
    mass_dry_sample_container = fields.Float(string="Mass of dry sample+container, (M2) in gms")
    mass_container = fields.Float(string="Mass of container, (M3) in gms")
    mass_moisture = fields.Float(string="Mass of Moisture, (M1-M2) in gms",compute="_compute_mass_moisture")
    mass_dry_sample = fields.Float(string="Mass of dry sample, (M2-M3) in gms",compute="_compute_mass_dry_sample")
    moisture_percent = fields.Float(string="% Moisture",compute="_compute_moisture_percent")


    @api.depends('mass_dry_sample_container','mass_wet_sample_container')
    def _compute_mass_moisture(self):
        for record in self:
            record.mass_moisture = record.mass_wet_sample_container - record.mass_dry_sample_container


    @api.depends('mass_dry_sample_container','mass_container')
    def _compute_mass_dry_sample(self):
        for record in self:
            record.mass_dry_sample = record.mass_dry_sample_container - record.mass_container

    @api.depends('mass_moisture','mass_dry_sample')
    def _compute_moisture_percent(self):
        for record in self:
            if record.mass_dry_sample != 0:
                record.moisture_percent = round((record.mass_moisture /record.mass_dry_sample) *100,2)
            else:
                record.moisture_percent = 0



class WmmPlasticLimitLine(models.Model):
    _name = "mech.wmm.plastic.limit.line"
    parent_id = fields.Many2one('mechanical.wmm', string="Parent Id")
    
    container_no = fields.Char("Container No.")
    mass_wet_sample_container = fields.Float(string="Mass of wet sample+container, (M1) in gms")
    mass_dry_sample_container = fields.Float(string="Mass of dry sample+container, (M2) in gms")
    mass_container = fields.Float(string="Mass of container, (M3) in gms")
    mass_moisture = fields.Float(string="Mass of Moisture, (M1-M2) in gms",compute="_compute_mass_moisture")
    mass_dry_sample = fields.Float(string="Mass of dry sample, (M2-M3) in gms",compute="_compute_mass_dry_sample")
    moisture_percent = fields.Float(string="% Moisture",compute="_compute_moisture_percent")


    @api.depends('mass_dry_sample_container','mass_wet_sample_container')
    def _compute_mass_moisture(self):
        for record in self:
            record.mass_moisture = record.mass_wet_sample_container - record.mass_dry_sample_container


    @api.depends('mass_dry_sample_container','mass_container')
    def _compute_mass_dry_sample(self):
        for record in self:
            record.mass_dry_sample = record.mass_dry_sample_container - record.mass_container

    @api.depends('mass_moisture','mass_dry_sample')
    def _compute_moisture_percent(self):
        for record in self:
            if record.mass_dry_sample != 0:
                record.moisture_percent = round((record.mass_moisture /record.mass_dry_sample) *100,2)
            else:
                record.moisture_percent = 0


class DryGradationLine(models.Model):
    _name = "mech.dry.gradation.line"
    parent_id = fields.Many2one('mechanical.wmm', string="Parent Id")
    
    serial_no = fields.Integer(string="Sr. No", readonly=True, copy=False, default=1)
    sieve_size = fields.Char(string="IS Sieve Size" )
    wt_retained = fields.Float(string="Wt. Retained in gms")
    percent_retained = fields.Float(string='% Retained', compute="_compute_percent_retained")
    cumulative_retained = fields.Float(string="Cum. Retained %", store=True)
    passing_percent = fields.Float(string="Passing %")



    @api.model
    def create(self, vals):
        # Set the serial_no based on the existing records for the same parent
        if vals.get('parent_id'):
            existing_records = self.search([('parent_id', '=', vals['parent_id'])])
            if existing_records:
                max_serial_no = max(existing_records.mapped('serial_no'))
                vals['serial_no'] = max_serial_no + 1

        return super(DryGradationLine, self).create(vals)

    def _reorder_serial_numbers(self):
        # Reorder the serial numbers based on the positions of the records in child_lines
        records = self.sorted('id')
        for index, record in enumerate(records):
            record.serial_no = index + 1

    def write(self, vals):
        # Handle row deletions and adjust serial numbers
        if 'parent_id' in vals or 'wt_retained' in vals:
            for record in self:
                if record.parent_id and record.parent_id == vals.get('parent_id') and 'wt_retained' in vals:
                    record.percent_retained = round((vals['wt_retained'] / record.parent_id.total * 100),2) if record.parent_id.total else 0

            new_self = super(DryGradationLine, self).write(vals)

            if 'wt_retained' in vals:
                for record in self:
                    record.parent_id._compute_total_sieve()

            return new_self

        return super(DryGradationLine, self).write(vals)

    def unlink(self):
        # Get the parent_id before the deletion
        parent_id = self[0].parent_id

        res = super(DryGradationLine, self).unlink()

        

        return res


    @api.depends('wt_retained', 'parent_id.total_sieve_analysis')
    def _compute_percent_retained(self):
        for record in self:
            try:
                record.percent_retained = record.wt_retained / self.parent_id.total_sieve_analysis * 100
            except ZeroDivisionError:
                record.percent_retained = 0


class ElongationLine(models.Model):
    _name = "mech.elongation.flakiness.line"
    parent_id = fields.Many2one('mechanical.wmm', string="Parent Id")

    sieve_size = fields.Char(string="IS Sieve Size")
    wt_retained = fields.Float(string="Wt. Retained in gms")
    elongated_retained = fields.Float(string="Elongated Retained in gms")
    flakiness_retained = fields.Float(string="Flakiness Retained in gms")



# class FlakinessLine(models.Model):
#     _name = "mech.flakiness.line"
#     parent_id = fields.Many2one('mechanical.wmm', string="Parent Id")

#     sieve_size = fields.Char(string="IS Sieve Size")
#     wt_retained = fields.Float(string="Wt. Retained in gms")
#     flakiness_retained = fields.Float(string="Flakiness Retained in gms")


class ImpactValueLine(models.Model):
    _name = "mech.wmm.impact.line"
    parent_id = fields.Many2one('mechanical.wmm',string="Parent Id")

    sample_no = fields.Integer(string="Sample", readonly=True, copy=False, default=1)
    wt_of_cylinder = fields.Integer(string="Weight of cylindrical measure in gms")
    total_wt_of_dried = fields.Integer(string="Total Wt. of Oven dried (4 hrs) aggregate sample + cylindrical measure in gms")
    total_wt_aggregate = fields.Float(string="Total Wt. of Oven dried (4 hrs) aggregate sample filling the cylindrical measure in gms", compute="_compute_total_wt_aggregate")
    wt_of_aggregate_passing = fields.Float(string="Wt. of aggregate passing 2.36 mm sieve after the test in gms")
    wt_of_aggregate_retained = fields.Float(string="Wt. of aggregate retained on 2.36 mm sieve after the test in gms", compute="_compute_wt_of_aggregate_retained")
    impact_value = fields.Float(string="Impact value", compute="_compute_impact_value")


    @api.depends('total_wt_of_dried', 'wt_of_cylinder')
    def _compute_total_wt_aggregate(self):
        for rec in self:
            rec.total_wt_aggregate = rec.total_wt_of_dried - rec.wt_of_cylinder


    @api.depends('total_wt_aggregate', 'wt_of_aggregate_passing')
    def _compute_wt_of_aggregate_retained(self):
        for rec in self:
            rec.wt_of_aggregate_retained = rec.total_wt_aggregate - rec.wt_of_aggregate_passing


    @api.depends('wt_of_aggregate_passing', 'total_wt_aggregate')
    def _compute_impact_value(self):
        for rec in self:
            if rec.total_wt_aggregate != 0:
                rec.impact_value = (rec.wt_of_aggregate_passing / rec.total_wt_aggregate) * 100
            else:
                rec.impact_value = 0.0


#added
class WmmFieldDencityLine(models.Model):
    _name = "mechanical.wmm.field.dencity.line"
    parent_id = fields.Many2one('mechanical.wmm',string="Parent Id")
   
    determination_no = fields.Integer(string="Determination No",readonly=True, copy=False, default=1)
    wt_of_sample = fields.Integer(string="Weight of sample gm")
    water_of_sample = fields.Integer(string="Water content of sample RMM")
    wt_of_before_cylinder = fields.Integer(string="Weight of sand + Cylinder before pouring gm")
    wt_of_after_cylinder = fields.Integer(string="Weight of sand + Cylinder after pouring gm")
    wt_of_sand_cone = fields.Integer(string="Weight of sand in cone gm")
    wt_of_sand_hole = fields.Integer(string="Weight of sand in hole gm", compute="_compute_sand_hole")
    density_of_sand = fields.Float(string="Density of sand gm/cc")
    volume_of_hole = fields.Float(string="Volume of hole cc",compute="_compute_volume_of_hole")
    bulk_density_of_sample = fields.Float(string="Bulk Density of sample gm/cc",compute="_compute_bulk_density")
    dry_density_of_sample = fields.Float(string="Dry Density of sample",compute="_compute_dry_density")
    degree_of_compaction = fields.Float(string="Degree of Compaction %",compute="_compute_degree_of_compaction")

    


    @api.depends('wt_of_before_cylinder','wt_of_after_cylinder','wt_of_sand_cone')
    def _compute_sand_hole(self):
        for record in self:
            record.wt_of_sand_hole = record.wt_of_before_cylinder - record.wt_of_after_cylinder - record.wt_of_sand_cone


    @api.depends('wt_of_sand_hole', 'density_of_sand')
    def _compute_volume_of_hole(self):
        for record in self:
            if record.density_of_sand != 0:
                record.volume_of_hole = record.wt_of_sand_hole / record.density_of_sand
            else:
                record.volume_of_hole = 0.0

 


    @api.depends('wt_of_sample', 'volume_of_hole')
    def _compute_bulk_density(self):
        for record in self:
            if record.volume_of_hole != 0:  # Avoid division by zero
                record.bulk_density_of_sample = record.wt_of_sample / record.volume_of_hole
            else:
                record.bulk_density_of_sample = 0.0

    @api.depends('bulk_density_of_sample', 'water_of_sample')
    def _compute_dry_density(self):
        for record in self:
            if record.water_of_sample + 100 != 0:  # Avoid division by zero
                record.dry_density_of_sample = (100 * record.bulk_density_of_sample) / (record.water_of_sample + 100)
            else:
                record.dry_density_of_sample = 0.0

    @api.depends('dry_density_of_sample', 'parent_id.mmd_wmm')
    def _compute_degree_of_compaction(self):
        for record in self:
            if record.parent_id.mmd_wmm != 0:  # Access mmd_wmm from parent_id
                record.degree_of_compaction = (record.dry_density_of_sample / record.parent_id.mmd_wmm) * 100
            else:
                record.degree_of_compaction = 0.0


    @api.model
    def create(self, vals):
        # Set the serial_no based on the existing records for the same parent
        if vals.get('parent_id'):
            existing_records = self.search([('parent_id', '=', vals['parent_id'])])
            if existing_records:
                max_serial_no = max(existing_records.mapped('determination_no'))
                vals['determination_no'] = max_serial_no + 1

        return super(WmmFieldDencityLine, self).create(vals)

    def _reorder_serial_numbers(self):
        # Reorder the serial numbers based on the positions of the records in child_lines
        records = self.sorted('id')
        for index, record in enumerate(records):
            record.determination_no = index + 1