# -*- coding: utf-8 -*-
##############################################################################
#
#    Academic
#    Copyright (C) 2014 Sistemas ADHOC
#    contacto@ingenieriaadhoc.com.ar
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more detaicreate_students_usersls.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


import re
from openerp import netsvc
from openerp.osv import osv, fields
from openerp.tools.translate import _
from datetime import date
from openerp import SUPERUSER_ID

class group(osv.osv):
    """"""
    
    _inherit = 'academic.group'

    def name_get(self, cr, uid, ids, context=None):
        # always return the full hierarchical name
        res = self._complete_name(cr, uid, ids, 'complete_name', None, context=context)
        return res.items()

    def _complete_name(self, cr, uid, ids, name, args, context=None):
        """ Forms complete name of location from parent location to child location.
        @return: Dictionary of values
        """
        res = {}
        for line in self.browse(cr, uid, ids):

            name = line.subject_id.name 
            name += ' - ' + line.company_id.name
            name += ', ' + line.level_id.name
            if line.division_id:
                name += ' ' + line.division_id.name
            name += ' - ' + line.level_id.section_id.name
            name +=  ' - ' + _('Year: ') + str(line.year)
            res[line.id] = name
        return res 

    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []    
        ids = set()     
        if name:
            ids.update(self.search(cr, user, args + [('subject_id.name',operator,name)], limit=(limit and (limit-len(ids)) or False) , context=context))
            if not limit or len(ids) < limit:
                ids.update(self.search(cr, user, args + [('company_id.name',operator,name)], limit=limit, context=context))
            if not limit or len(ids) < limit:
                ids.update(self.search(cr, user, args + [('level_id.name',operator,name)], limit=limit, context=context))
            if not limit or len(ids) < limit:
                try:
                    year = int(name)
                    ids.update(self.search(cr, user, args + [('year',operator,year)], limit=limit, context=context))
                except:
                    print 'not convertable to integer'
            ids = list(ids)
        else:
            ids = self.search(cr, user, args, limit=limit, context=context)
        result = self.name_get(cr, user, ids, context=context)
        return result

    _columns = {
        'complete_name': fields.function(_complete_name,type='char',string='Complete Name',),
    }

    _defaults = {
        'year': date.today().year,
    }


    _constraints = [
    ]

    _sql_constraints = [('group_unique', 'unique(subject_id, company_id, level_id, year, division_id)', 'Group should be unique per Institution, Subject, Course-Division and Year')]

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        # record = self.browse(cr, uid, id, context=context)
        default['division_id'] = False
        default['group_evaluation_ids'] = []
        return super(group, self).copy(cr, uid, id, default, context)

    def create_students_users(self, cr, uid, ids, context=None):
        '''
        This function create users if they don't exist for students related to this group.
        '''
        for group in self.browse(cr, uid, ids, context=context):
            partners = group.student_ids
            partner_ids = [x.id for x in partners]
            print 'partner_ids', partner_ids
            # Create users, if they already exists it will update grupos and activate them
            self.pool.get('res.partner').quickly_create_user(cr, uid, partner_ids, context=context)
        return False

    def print_users(self, cr, uid, ids, context=None):
        '''
        This function prints a report with users login and password. 
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time'
        self.create_students_users(cr, uid, ids, context=context)
        return self.pool['report'].get_action(cr, uid, ids, 'academic_x.template_report_users', context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
