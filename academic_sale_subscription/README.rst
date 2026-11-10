.. |company| replace:: ADHOC SA

.. |company_logo| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-logo.png
   :alt: ADHOC SA
   :target: https://www.adhoc.com.ar

.. |icon| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-icon.png

.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

==========================
Academic Sale Subscription
==========================

This module extends the standard Odoo subscription management capabilities to cater specifically to academic institutions

Installation
============

To install this module, you need to:

#. Only need to install the module

Configuration
=============

To configure this module, you need to:

#. Nothing to configure for the standard behaviour.
#. To group the invoice notice by payment responsible, go to Settings / Sales / Subscriptions and enable
   "Group invoice notice by payment responsible", choosing the mail template of the notice. With it enabled,
   academic invoices stop using the subscription plan mail template: they stay posted and unsent, and the
   "Grouped Invoice Notice by Payment Responsible" scheduled action sends each payment responsible a single
   mail, once a day, with the pending invoices of their students, the detail per student, the total of the
   notice, the total due, a link to the portal and the invoices attached. Set the hour of that scheduled
   action after the recurring invoicing one.

Usage
=====

To use this module, you need to:

#. Just use

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: http://runbot.adhoc.com.ar/

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/ingadhoc/{project_repo}/issues>`_. In case of trouble, please
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
