.. |company| replace:: ADHOC SA

.. |company_logo| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-logo.png
   :alt: ADHOC SA
   :target: https://www.adhoc.com.ar

.. |icon| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-icon.png

.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

==========================================
Academic - Uruguay Accounting Reports UX
==========================================

The uruguayan form 3150 reports, for every payment responsible, how many people it covers. In a school that is
the number of students billed to them during the year, but Academic cannot be a hard dependency of a
localization module: ``l10n_uy_reports_ux`` reports one person and leaves the hook this module extends.

Features:

#. Counts the distinct students billed to the payment responsible during the year, net of credit notes: a
   student whose invoices were all credited, or that only shows up on a credit note, was not billed.
#. Adds the payment responsible without any student billed to the list of problems of the wizard, where it is
   reported that the record goes with one person.

Installation
============

To install this module, you need to:

#. Nothing, it is installed automatically with ``academic_sale_subscription`` and ``l10n_uy_reports_ux``.

Configuration
=============

To configure this module, you need to:

#. Nothing, it has no configuration of its own. The form 3150 is configured in ``l10n_uy_reports_ux``.

Usage
=====

To use this module, you need to:

#. Go to Accounting > Uruguayan Declarations > (UY) Form Declarations.
#. Choose the Form 3150 and the year, and press Get Files.
#. The Persons field of the line E of every record reports the students billed to that payment responsible.

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
