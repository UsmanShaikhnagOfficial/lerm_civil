from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
import math
from datetime import datetime , timedelta


class MechanicalConcreteCube(models.Model):
    _name = "concrete.cube.water.absorption"
    _inherit = "lerm.eln"
    _rec_name = "name"

    name = fields.Char("Name",default="Concrete Cube Water Absorption")
    parameter_id = fields.Many2one('eln.parameters.result',string="Parameter")
    sample_parameters = fields.Many2many('lerm.parameter.master',string="Parameters",compute="_compute_sample_parameters",store=True)
    child_lines = fields.One2many('concrete.cube.water.absorption.line','parent_id',string="Parameter")
    average_concrete_cube_water = fields.Float(string="Average Water Absorption %", compute="_compute_average_concrete_cube_water",digits=(12,2))
    correction_factor = fields.Float(string="Correction Factor = Volume (mm3) / (Surface Area (mm2) * 12.5)")
    water_correction_factor = fields.Float(string="Water Absorption after correction Factor",compute="_compute_water_correction_factor")
    grade = fields.Many2one('lerm.grade.line',string="Grade",compute="_compute_grade_id",store=True)
    eln_ref = fields.Many2one('lerm.eln',string="ELN")
    
    age_of_days = fields.Selection([
        ('3days', '3 Days'),
        ('7days', '7 Days'),
        ('14days', '14 Days'),
        ('21days', '21 Days'),
        ('28days', '28 Days'),
        ('56days', '56 Days'),
        ('112days', '112 Days'),
    ], string='Age', default='28days',required=True,compute="_compute_age_of_days")
    date_of_casting = fields.Date(string="Date of Casting",compute="compute_date_of_casting")
    date_of_testing = fields.Date(string="Date of Testing")
    confirmity = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('not_applicable', 'Not Applicable'),

    ], string='Confirmity', default='fail',compute="_compute_confirmity")
    age_of_test = fields.Integer("Age of Test, days",compute="compute_age_of_test")
    difference = fields.Integer("Difference",compute="compute_difference")

    # grade = fields.Many2one('lerm.grade.line',string="Grade",compute="_compute_grade_id",store=True)
    nabl = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail'),

    ], string='NABL', default='fail',compute="_compute_nabl")


    @api.depends('age_of_test','age_of_days')
    def compute_difference(self):
        for record in self:
            age_of_days = 0
            if record.age_of_days == '3days':
                age_of_days = 3
            elif record.age_of_days == '7days':
                age_of_days = 7
            elif record.age_of_days == '14days':
                age_of_days = 14
            elif record.age_of_days == '21days':
                age_of_days = 21
            elif record.age_of_days == '28days':
                age_of_days = 28
            elif record.age_of_days == '56days':
                age_of_days = 56
            elif record.age_of_days == '112days':
                age_of_days = 112
            else:
                age_of_days = 0
            record.difference = record.age_of_test - age_of_days

        


    @api.depends('date_of_testing','date_of_casting')
    def compute_age_of_test(self):
        for record in self:
            if record.date_of_casting and record.date_of_testing:
                date1 = fields.Date.from_string(record.date_of_casting)
                date2 = fields.Date.from_string(record.date_of_testing)
                date_difference = (date2 - date1).days
                record.age_of_test = date_difference
            else:
                record.age_of_test = 0

    @api.onchange('eln_ref')
    def compute_date_of_casting(self):
        for record in self:
            if record.eln_ref.sample_id:
                sample_record = self.env['lerm.srf.sample'].sudo().search([('id','=', record.eln_ref.sample_id.id)]).date_casting
                record.date_of_casting = sample_record
            else:
                record.date_of_casting = None



    @api.onchange('eln_ref')
    def _compute_age_of_days(self):
        for record in self:
            if record.eln_ref.sample_id:
                sample_record = self.env['lerm.srf.sample'].sudo().search([('id','=', record.eln_ref.sample_id.id)]).days_casting
                if sample_record == '3':
                    record.age_of_days = '3days'
                elif sample_record == '7':
                    record.age_of_days = '7days'
                elif sample_record == '14':
                    record.age_of_days = '14days'
                elif sample_record == '21':
                    record.age_of_days = '21days'
                elif sample_record == '28':
                    record.age_of_days = '28days'
                elif sample_record == '56':
                    record.age_of_days = '56days'
                elif sample_record == '112':
                    record.age_of_days = '112days'
                else:
                    record.age_of_days = None
            else:
                record.age_of_days = None

    def open_eln_page(self):
        # import wdb; wdb.set_trace()

        return {
                'view_mode': 'form',
                'res_model': "lerm.eln",
                'type': 'ir.actions.act_window',
                'target': 'current',
                'res_id': self.eln_ref.id,
                
            }
        # return {'type': 'ir.actions.client', 'tag': 'history_back'}

    # @api.depends('date_of_casting','age_of_days')
    # def _compute_testing_date(self):
    #     for record in self:
    #         if record.date_of_casting:
    #             if record.age_of_days == "3days":
    #                 cast_date = fields.Datetime.from_string(record.date_of_casting)
    #                 testing_date = cast_date + timedelta(days=3)
    #                 record.date_of_testing = fields.Datetime.to_string(testing_date)
    #             elif record.age_of_days == "7days":
    #                 cast_date = fields.Datetime.from_string(record.date_of_casting)
    #                 testing_date = cast_date + timedelta(days=7)
    #                 record.date_of_testing = fields.Datetime.to_string(testing_date)
    #             elif record.age_of_days == "14days":
    #                 cast_date = fields.Datetime.from_string(record.date_of_casting)
    #                 testing_date = cast_date + timedelta(days=14)
    #                 record.date_of_testing = fields.Datetime.to_string(testing_date)
    #             elif record.age_of_days == "28days":
    #                 cast_date = fields.Datetime.from_string(record.date_of_casting)
    #                 testing_date = cast_date + timedelta(days=28)
    #                 record.date_of_testing = fields.Datetime.to_string(testing_date)
    #             else:
    #                 record.date_of_testing = False
    #         else:
    #             record.date_of_testing = False
            

    @api.depends('eln_ref')
    def _compute_grade_id(self):
        if self.eln_ref:
            self.grade = self.eln_ref.grade_id.id


    @api.depends('average_concrete_cube_water','eln_ref','grade')
    def _compute_nabl(self):
        
        for record in self:
            record.nabl = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','2002fc5d-b01c-47c1-a37c-332e37a412a7')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','2002fc5d-b01c-47c1-a37c-332e37a412a7')]).parameter_table
            # for material in materials:
            #     if material.grade.id == record.grade.id:
            lab_min = line.lab_min_value
            lab_max = line.lab_max_value
            mu_value = line.mu_value
            
            lower = record.average_concrete_cube_water - record.average_concrete_cube_water*mu_value
            upper = record.average_concrete_cube_water + record.average_concrete_cube_water*mu_value
            if lower >= lab_min and upper <= lab_max:
                record.nabl = 'pass'
                break
            else:
                record.nabl = 'fail'


    @api.depends('average_concrete_cube_water','eln_ref','grade','age_of_days','difference')
    def _compute_confirmity(self):
        for record in self:
            record.confirmity = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','2002fc5d-b01c-47c1-a37c-332e37a412a7')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','2002fc5d-b01c-47c1-a37c-332e37a412a7')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    req_min = material.req_min
                    req_max = material.req_max
                    mu_value = line.mu_value
                    if record.age_of_days == "3days":
                        req_min = req_min * 0.5
                        req_max = req_max* 0.5
                    if record.age_of_days == "7days":
                        req_min = req_min * 0.7
                        req_max = req_max* 0.7
                    if record.age_of_days == "14days":
                        req_min = req_min * 0.9
                        req_max = req_max* 0.9
                    if record.age_of_days == "28days":
                        req_min = req_min
                        req_max = req_max
                    lower = record.average_concrete_cube_water - record.average_concrete_cube_water*mu_value
                    upper = record.average_concrete_cube_water + record.average_concrete_cube_water*mu_value
                    
                    if record.difference == 0:
                        if lower >= req_min and upper <= req_max :
                            record.confirmity = 'pass'
                            break
                        else:
                            record.confirmity = 'fail'
                    else:
                        record.confirmity = 'not_applicable'


    @api.depends('child_lines.water_absorption_percent')
    def _compute_average_concrete_cube_water(self):
        for record in self:
            total_strength = sum(line.water_absorption_percent for line in record.child_lines)
            record.average_concrete_cube_water = total_strength / len(record.child_lines) if len(record.child_lines) > 0 else 0.0

    @api.depends('average_concrete_cube_water', 'correction_factor')
    def _compute_water_correction_factor(self):
        for record in self:
            record.water_correction_factor = record.average_concrete_cube_water * record.correction_factor


    @api.depends('eln_ref')
    def _compute_grade_id(self):
        if self.eln_ref:
            self.grade = self.eln_ref.grade_id.id


    
    @api.model
    def create(self, vals):
        # import wdb;wdb.set_trace()
        record = super(MechanicalConcreteCube, self).create(vals)
        # record.get_all_fields()
        record.eln_ref.write({'model_id':record.id})
        return record
    

    @api.depends('eln_ref')
    def _compute_sample_parameters(self):
        # records = self.env['lerm.eln'].sudo().search([('id','=', record.eln_id.id)]).parameters_result
        # print("records",records)
        # self.sample_parameters = records
        for record in self:
            records = record.eln_ref.parameters_result.parameter.ids
            record.sample_parameters = records
            print("Records",records)

    def get_all_fields(self):
        record = self.env['concrete.cube.water.absorption'].browse(self.ids[0])
        field_values = {}
        for field_name, field in record._fields.items():
            field_value = record[field_name]
            field_values[field_name] = field_value

        return field_values



class MechanicalConcreteCubeLine(models.Model):
    _name = "concrete.cube.water.absorption.line"
    parent_id = fields.Many2one('concrete.cube.water.absorption',string="Parent Id")

    sr_no = fields.Integer(string="Sr.No.",readonly=True, copy=False, default=1)
    sample_id = fields.Char(string="Sample ID")
    oven_dry_weight = fields.Float(string="Oven Dry Weight After 72 Hrs.(kg)" ,digits=(12,3))
    weight_immersion = fields.Float(string="Weight of Immersion in water after 30 Minutes (kg)" ,digits=(12,3))
    water_absorption_percent = fields.Float(string="Water Absorption %",compute="_compute_water_absorption_percent" ,digits=(12,2))
   


    # @api.depends('parent_id')
    # def _compute_id_mark(self):
    #     for record in self:
    #         sample_id = record.parent_id.eln_ref.sample_id.client_sample_id
    #         record.id_mark = sample_id


    # @api.onchange('parent_id')
    # def _onchange_parent_id(self):
    #     for record in self:
    #         sample_id = record.parent_id.eln_ref.sample_id.client_sample_id
    #         if sample_id:
    #             record.id_mark = sample_id
    #         else:
    #             record.id_mark = ""

    # @api.onchange('id_mark')
    # def _onchange_id_mark(self):
    #     for record in self:
    #         if record.id_mark and not record.parent_id.eln_ref.sample_id.client_sample_id:
    #             record.parent_id.eln_ref.sample_id.client_sample_id = record.id_mark





   

    @api.depends('weight_immersion', 'oven_dry_weight')
    def _compute_water_absorption_percent(self):
        for record in self:
            if record.oven_dry_weight != 0:
                record.water_absorption_percent = ((record.weight_immersion - record.oven_dry_weight)/ record.oven_dry_weight) * 100
            else:
                record.water_absorption_percent = 0.0


    @api.model
    def create(self, vals):
        # Set the serial_no based on the existing records for the same parent
        if vals.get('parent_id'):
            existing_records = self.search([('parent_id', '=', vals['parent_id'])])
            if existing_records:
                max_serial_no = max(existing_records.mapped('sr_no'))
                vals['sr_no'] = max_serial_no + 1

        return super(MechanicalConcreteCubeLine, self).create(vals)

    def _reorder_serial_numbers(self):
        # Reorder the serial numbers based on the positions of the records in child_lines
        records = self.sorted('id')
        for index, record in enumerate(records):
            record.sr_no = index + 1