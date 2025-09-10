.. |company| replace:: ADHOC SA

.. |company_logo| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-logo.png
   :alt: ADHOC SA
   :target: https://www.adhoc.com.ar

.. |icon| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-icon.png

.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

===========
Academic HR
===========

This module extends Odoo's HR functionality to support academic institutions with specific requirements:

* **Multiple Employees per User**: Allows a single user to manage multiple employee records across different companies
* **Parent-Child Employee Relationships**: Enables hierarchical employee structures with main and child employees
* **Enhanced Leave Management**: Supports leave requests and allocations for users with multiple employee records
* **Timesheet Integration**: Provides better timesheet management for academic staff with multiple roles

Installation
============

To install this module, you need to:

#. Just install.

Configuration
=============

To configure users with multiple employees:

#. Go to *Employees > Employees*
#. Create or edit a main employee record
#. In the "Child Employees" tab, add additional employee records for the same user
#. The system will automatically link them and propagate user/company information


Usage
=====

Managing Multiple Employees
---------------------------

When a user has multiple employee records:

#. Leave requests will show a combined view with employee names
#. Timesheet entries can be created for any of the user's employees
#. The system automatically selects the first employee as default


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
