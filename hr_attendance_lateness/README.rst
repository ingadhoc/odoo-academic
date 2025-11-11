.. |company| replace:: ADHOC SA

.. |company_logo| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-logo.png
   :alt: ADHOC SA
   :target: https://www.adhoc.com.ar

.. |icon| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-icon.png

.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

======================
HR Attendance Lateness
======================

This module extends the HR Attendance module to automatically calculate and track employee lateness by comparing actual check-in times against their expected schedule from their working hours.

Features:

#. Adds three new fields to attendance records: **Expected Check-in**, **Late Minutes**, and **Is Late**.
#. Automatically calculates lateness based on the employee's working hours (resource calendar).
#. Configurable tolerance threshold via system parameter ``hr_attendance.lateness_threshold`` (default: 0 minutes).
#. Visual indicator: Late attendances appear in **red** in the list view.
#. New filter "Late Check-ins" to quickly view only late attendances.
#. New grouping option "Late Status" to group attendances by lateness.

Installation
============

To install this module, you need to:

#. Install this module from the Apps menu

Configuration
=============

To configure this module, you need to:

#. Ensure employees have working hours defined (Employee > Work Information > Working Hours)
#. Configure the lateness tolerance threshold:

   - Go to Settings > Attendances
   - In the "Lateness Control" section, set the "Attendance Lateness Threshold"
   - Set the value in minutes (e.g., ``5`` for 5-minute grace period)
   - Default is ``0`` (no tolerance)
   - This setting is company-specific

Usage
=====

To use this module, you need to:

#. Go to Attendances > Attendances
#. View the new columns: Expected Check-in, Late (min), and Is Late
#. Use the "Late Check-ins" filter to view only late attendances
#. Late attendances appear in bold for easy identification
#. Group by "Late Status" to separate late from on-time attendances

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
