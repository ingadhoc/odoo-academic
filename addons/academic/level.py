# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class level(models.Model):
    """"""

    _name = 'academic.level'
    _description = 'level'

    name = fields.Char(
        string='Name',
        required=True,
        translate=True
        )
    section_id = fields.Many2one(
        'academic.section',
        string='Section',
        required=True
        )
    group_ids = fields.One2many(
        'academic.group',
        'level_id',
        string='Groups'
        )

    _constraints = [
    ]

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

            name = line.name
            name += ' - ' + line.section_id.name
            res[line.id] = name
        return res 

    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []    
        ids = set()     
        if name:
            ids.update(self.search(cr, user, args + [('name',operator,name)], limit=(limit and (limit-len(ids)) or False) , context=context))
            if not limit or len(ids) < limit:
                ids.update(self.search(cr, user, args + [('section_id.name',operator,name)], limit=limit, context=context))
            ids = list(ids)
        else:
            ids = self.search(cr, user, args, limit=limit, context=context)
        result = self.name_get(cr, user, ids, context=context)
        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
