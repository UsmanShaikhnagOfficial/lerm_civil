{'name':'LERM_CIVIL',
 'summary': "LERM_CIVIL",
 'author': "Usman Shaikhnag", 
 'website': "http://www.esehat.org", 
 'category': 'Uncategorized', 
 'version': '13.0.1', 
 'depends':['base' , 'contacts','stock','product' , 'mail','documents','documents_spreadsheet','lerm_civil_inv'],
 'data': [
    'data/sequence.xml',
    'views/lerm.xml',
    'views/groups.xml',
    'views/res_company.xml',
    'views/material.xml',
    'views/srf.xml',
    'views/parameter_master.xml',
    'views/datasheet_master.xml',
    'views/sample.xml',
    'views/sample_range.xml',
    'views/eln.xml',
    'views/contractor.xml',
    'views/mechanical/sieve_analysis.xml',
    'views/mechanical/pavel_block.xml',
    'views/mechanical/free_swell_index.xml',
    'views/mechanical/soil_cbr.xml',
    'views/mechanical/heavy_ligth_compaction.xml',
    'views/mechanical/plastic_limit.xml',
    'views/mechanical/liquid_limit.xml',
    'views/mechanical/compressive_strength_solid.xml',
    'views/mechanical/block_density.xml',
    'views/mechanical/split_tensile_strength.xml',
    'views/mechanical/water_absorption_solid.xml',
    'views/mechanical/drying_shrinkage_solid.xml',
    'views/mechanical/moisture_movement_solid.xml',
    'views/mechanical/flexural_strength_concrete_beam.xml',
    'views/mechanical/compressive_strength_concrete_cube.xml',
    'views/mechanical/splitting_tensile_strength_concrete.xml',
    'views/mechanical/act_compressive_concrete_cube.xml',
    'views/mechanical/crushing_value_coarse_aggregate.xml',
    'views/mechanical/impact_value_coarse_aggregate.xml',
    'views/mechanical/loose_bulk_density.xml',
    'views/mechanical/rodded_bulk_density.xml',
    'views/mechanical/abration_value_coarse_aggregate.xml',
    'views/mechanical/specific_gravity_and_water_absorption_coarce_aggregate.xml',
    'views/mechanical/compressive_strength_concrete_man_hole.xml',
    'views/mechanical/moisture_content_concrete_man_hole.xml',
    'views/mechanical/drying_shrinkage_concrete_man_hole.xml',
    'views/mechanical/dimentions_concrete_man_hole.xml',
    'views/mechanical/water_and_gravity_fine_aggregate.xml',
    'views/mechanical/steel_tmt_bar.xml',
    'views/mechanical/flakiness_elongated_index.xml',
    'views/mechanical/rock.xml',
    'views/mechanical/structural_steel.xml',
    'views/mechanical/bricks.xml',
    'views/mechanical/compressive_strength_brick.xml',
    'views/mechanical/dry_density_sand_replacement.xml',
    'views/mechanical/cement_compatablity.xml',
    'views/ndt/crack_width.xml',
    'views/ndt/concrete_core.xml',
    'views/ndt/crack_depth.xml',
    'views/ndt/acil_crack_depth.xml',
    'views/ndt/cover_meter.xml',
    'views/ndt/carbonation_test.xml',
    'views/ndt/rebound_hammer.xml',
    'views/ndt/acil_upv.xml', 
    'views/ndt/upv.xml',
    'views/ndt/half_cell.xml',
    'views/mechanical/cement_normal_consistency.xml',
    'views/mechanical/cement_psc.xml',
    'views/mechanical/cement_ppc.xml',
    'views/mechanical/cement_setting_time.xml',
    'views/mechanical/ggbs.xml',
    'views/mechanical/wpt.xml',
    'views/mechanical/gypsum.xml',
    'views/mechanical/fly_ash.xml',
    'views/mechanical/microsilica.xml',
    'reports/eln_report_action.xml',
    'reports/eln_report_template.xml',
    'reports/sample_report_template.xml',
    'reports/srf_report_action.xml',
    'reports/srf_report_template.xml',
    'reports/report_cement.xml',
    'reports/microsilica_datasheet.xml',
    'reports/gypsum_report.xml',
    'reports/wpt_report.xml',
    'reports/microsilica_report.xml',
    'reports/ggbs_report.xml',
    'security/security.xml',
    # 'security/dump.sql',
    'security/ir.model.access.csv',
    'reports/sample_report_action.xml',
    'reports/datasheet_templates.xml',
    'reports/compatiblity_datasheet.xml',
    'reports/compatiblity_report.xml',
    'reports/general_template.xml',
    'reports/ggbs_datasheet.xml',
    'reports/gypsum_datasheet.xml',
    'reports/wpt_datasheet.xml',
    'reports/general_report_template.xml',
    
    ],
        'assets': {
    'web.assets_backend':[
        '/lerm_civil/static/src/js/spreadsheet.js'
    ],
    'web.report_assets_common': [
            '/lerm_civil/static/src/css/eln_report.scss',
            '/lerm_civil/static/src/css/data_sheet_styles.scss',
        ],
    'web.assets_qweb': [
        '/lerm_civil/static/src/xml/spreadsheet.xml'

    ],
        }
}
