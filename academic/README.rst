.. |company| replace:: ADHOC SA

.. |company_logo| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-logo.png
   :alt: ADHOC SA
   :target: https://www.adhoc.com.ar

.. |icon| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-icon.png

.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

========
Academic
========

Academic management on top of contacts: it turns ``res.partner`` into students,
relatives, teachers, administrators and families, and adds the academic
structure they belong to (study plans, levels, divisions, subjects and groups),
plus portal access per academic role.

Installation
============

To install this module, you need to:

#. Just install this module.


Configuration
=============

To configure this module, you need to:

#. Go to *Academic / Configuration / General Data* and define the study plans,
   levels, divisions, subjects and roles the institution uses.
#. On each company, set the *Study Plans* available to it, and whether a family
   is required for its students.

Usage
=====

To use this module, you need to:

#. Go to *Academic / Contacts* and register students, relatives, teachers and
   administrators. Each contact has an academic type, and students are grouped
   into families.
#. Go to *Academic / Groups* to create the groups of a year, and use *Create
   next year groups* to carry them over to the following one.
#. To load many contacts at once, use the contact import wizard: it reads an
   xlsx/ods/csv spreadsheet and creates the students, their relatives, the
   links between them and their families. The wizard offers an example file to
   download, available to Academic managers.
#. Grant portal access from the contact itself: the portal wizard assigns the
   portal group that matches the academic type of the contact.
#. Print the *Certificate of Regular Student* from a student, and *Print Basic
   Group Data* from a group.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: http://runbot.adhoc.com.ar/

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/ingadhoc/odoo-academic/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* |company| |icon|

Contributors
------------

Maintainer
----------

|company_logo|

This module is maintained by the |company|.

To contribute to this module, please visit https://www.adhoc.com.ar.
