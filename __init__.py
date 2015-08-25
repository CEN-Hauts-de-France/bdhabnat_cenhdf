# -*- coding: utf-8 -*-
"""
/***************************************************************************
 bdhabnat
                                 A QGIS plugin
 Plugin de saisie d'habitats naturels dans QGIS
                             -------------------
        begin                : 2015-08-25
        copyright            : (C) 2015 by Conseravtoire d'Espaces Naturels du Nord - Pas-de-Calais
        email                : vincent.damoy@espaces-naturels.fr
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load bdhabnat class from file bdhabnat.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .bdhabnat import bdhabnat
    return bdhabnat(iface)
