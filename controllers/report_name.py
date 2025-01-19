import base64
import copy
import datetime
import functools
import hashlib
import io
import itertools
import json
import logging
import operator
import os
import re
import sys
import tempfile
import unicodedata
from collections import OrderedDict, defaultdict

import babel.messages.pofile
import werkzeug
import werkzeug.exceptions
import werkzeug.utils
import werkzeug.wrappers
import werkzeug.wsgi
from lxml import etree, html
from markupsafe import Markup
from werkzeug.urls import url_encode, url_decode, iri_to_uri

import odoo
import odoo.modules.registry
from odoo.api import call_kw
from odoo.addons.base.models.ir_qweb import render as qweb_render
from odoo.modules import get_resource_path, module
from odoo.tools import html_escape, pycompat, ustr, apply_inheritance_specs, lazy_property, osutil
from odoo.tools.mimetypes import guess_mimetype
from odoo.tools.translate import _
from odoo.tools.misc import str2bool, xlsxwriter, file_open, file_path
from odoo.tools.safe_eval import safe_eval, time
from odoo import http
from odoo.http import content_disposition, dispatch_rpc, request, serialize_exception as _serialize_exception
from odoo.exceptions import AccessError, UserError, AccessDenied
from odoo.models import check_method_name
from odoo.service import db, security  
from odoo.addons.web.controllers.main import ReportController 
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request

class MyReportName(ReportController):
    @http.route(['/report/download'], type='http', auth="user")
    def report_download(self, data, context=None):
        """This function is used by 'action_manager_report.js' in order to trigger the download of
        a pdf/controller report.

        :param data: a javascript array JSON.stringified containg report internal url ([0]) and
        type [1]
        :returns: Response with an attachment header

        """
        requestcontent = json.loads(data)
        url, type = requestcontent[0], requestcontent[1]
        reportname = '???'
        
        try:
            if type in ['qweb-pdf', 'qweb-text']:
                
                converter = 'pdf' if type == 'qweb-pdf' else 'text'
                extension = 'pdf' if type == 'qweb-pdf' else 'txt'

                pattern = '/report/pdf/' if type == 'qweb-pdf' else '/report/text/'
                reportname = url.split(pattern)[1].split('?')[0]

                print("REPORTNAME",reportname)
                

                docids = None
                if '/' in reportname:
                    reportname, docids = reportname.split('/')

                if docids:
                    # import wdb; wdb.set_trace()
                    # Generic report:
                   

                    response = self.report_routes(reportname, docids=docids, converter=converter, context=context)

                    print("Response",response)
                else:
                    # Particular report:
                    data = dict(url_decode(url.split('?')[1]).items())  # decoding the args represented in JSON
                    if 'context' in data:
                        context, data_context = json.loads(context or '{}'), json.loads(data.pop('context'))
                        context = json.dumps({**context, **data_context})
                    response = self.report_routes(reportname, converter=converter, context=context, **data)

                report = request.env['ir.actions.report']._get_report_from_name(reportname)
                filename = "%s.%s" % (report.name, extension)
                
                print("FILENAME",filename)

                if docids:
                    ids = [int(x) for x in docids.split(",")]
                    obj = request.env[report.model].browse(ids)
                    
                    if report.print_report_name and not len(obj) > 1:
                        report_name = safe_eval(report.print_report_name, {'object': obj, 'time': time})
                        filename = "%s.%s" % (report_name, extension)

                if reportname == 'lerm_civil.eln_report_template':
                    pattern = r'active_model%22%3A%22([^%]+)%22.*?active_id%22%3A(\d+)'
                    match = re.search(pattern, url)

                    if match:
                        active_model = match.group(1)
                        active_id = match.group(2)
                        kes_no = request.env[active_model].browse(int(active_id)).kes_no
                        filename = kes_no
                    else:
                        print("Active Model not found in the URL.")
                
                if reportname == 'lerm_civil.general_report_template':
                    pattern = r'active_model%22%3A%22([^%]+)%22.*?active_id%22%3A(\d+)'
                    match = re.search(pattern, url)

                    if match:
                        active_model = match.group(1)
                        active_id = match.group(2)
                        kes_no = request.env[active_model].browse(int(active_id)).kes_no
                        filename = kes_no
                    else:
                        print("Active Model not found in the URL.")
                
                response.headers.add('Content-Disposition', content_disposition(filename))

                return response
                
            else:
                return
        except Exception as e:
            # _logger.exception("Error while generating report %s", reportname)
            se = _serialize_exception(e)
            error = {
                'code': 200,
                'message': "Odoo Server Error",
                'data': se
            }
            res = werkzeug.wrappers.Response(
                json.dumps(error),
                status=500,
                headers=[("Content-Type", "application/json")]
            )
            raise werkzeug.exceptions.InternalServerError(response=res) from e

