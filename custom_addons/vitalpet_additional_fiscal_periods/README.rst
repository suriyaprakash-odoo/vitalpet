.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==========
Account Fiscal Period
==========

This module lets you define global Account Fiscal Periods that can be used to filter
your values in tree views.

Usage
=====

To configure this module, you need to:

* Go to Settings > Technical > Account Fiscal Periods > Account Fiscal Period Types where
  you can create types of Account Fiscal Periods.

  .. figure:: static/description/account_fiscal_periods_type_create.png
     :scale: 80 %
     :alt: Create a type of Account Fiscal Period

* Go to Settings > Technical > Account Fiscal Periods >  Account Fiscal Periods where
  you can create Account Fiscal Periods.
  
  .. figure:: static/description/account_fiscal_periods_create.png
     :scale: 80 %
     :alt: Account Fiscal Period creation
  
  It's also possible to launch a wizard from the 'Generate Account Fiscal Periods' menu.

  .. figure:: static/description/account_fiscal_periods_wizard.png
     :scale: 80 %
     :alt: Account Fiscal Period wizard

  The wizard is useful to generate recurring periods.
  
  .. figure:: static/description/account_fiscal_periods_wizard_result.png
     :scale: 80 %
     :alt: Account Fiscal Period wizard result

* Your Account Fiscal Periods are now available in the search filter for any date or datetime fields

  Account Fiscal Period Types are proposed as a filter operator
  
  .. figure:: static/description/account_fiscal_periods_type_as_filter.png
     :scale: 80 %
     :alt: Account Fiscal Period Type available as filter operator

  Once a type is selected, Account Fiscal Periods of this type are porposed as a filter value

  .. figure:: static/description/account_fiscal_periods_as_filter.png
     :scale: 80 %
     :alt: Account Fiscal Period as filter value

  And the dates specified into the Account Fiscal Period are used to filter your result.
  
  .. figure:: static/description/account_fiscal_periods_as_filter_result.png
     :scale: 80 %
     :alt: Account Fiscal Period as filter result


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
    :alt: Try me on Runbot
    :target: https://runbot.odoo-community.org/runbot/149/10.0


Known issues / Roadmap
======================

* The addon use the daterange method from postgres. This method is supported as of postgresql 9.2

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/server-tools/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Laurent Mignon <laurent.mignon@acsone.eu>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
