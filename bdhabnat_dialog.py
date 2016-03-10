# -*- coding: utf-8 -*-
"""
/***************************************************************************
 bdhabnatDialog
                                 A QGIS plugin
 Plugin de saisie d'habitats naturels dans QGIS
                             -------------------
        begin                : 2015-08-25
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Conseravtoire d'Espaces Naturels du Nord - Pas-de-Calais
        email                : vincent.damoy@espaces-naturels.fr
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from PyQt4 import QtCore, QtGui, uic, QtSql, Qt
from qgis.core import *
from qgis.gui import *
from ui_bdhabnat_dialog import Ui_bdhabnat_dialog

class bdhabnatDialog(QtGui.QDialog):
    def __init__(self, iface):
        """Constructor."""
        QtGui.QDialog.__init__(self)
        self.ui = Ui_bdhabnat_dialog()
        self.ui.setupUi(self)

        # Référencement de iface dans l'interface (iface = interface de QGIS)
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        
        # Connexion à la base de données. DB type, host, user, password...
        self.db = QtSql.QSqlDatabase.addDatabase("QPSQL") # QPSQL = nom du pilote postgreSQL
        self.db.setHostName("127.0.0.1") 
        self.db.setDatabaseName("sitescsn")
        self.db.setUserName("postgres")
        self.db.setPassword("postgres")
        ok = self.db.open()
        if not ok:
            QtGui.QMessageBox.warning(self, 'Alerte', u'La connexion est échouée'+self.db.hostName())

        # Remplir la combobox "cbx_codesite" avec les codes et noms de sites issus de la table "t_sitescen"
        query_codesite = QtSql.QSqlQuery(self.db)
        if query_codesite.exec_('select idchamp, codesite, nomsite from sites_cen.t_sitescen order by codesite'):
            while query_codesite.next():
                self.ui.cbx_codesite.addItem(query_codesite.value(1) + " " + query_codesite.value(2), query_codesite.value(1) )

        # Remplir la combobox "cbx_auteurs" avec les noms et prénoms issus de la table "t_liste_obsv"
        query_obsv = QtSql.QSqlQuery(self.db)
        if query_obsv.exec_('select id_obsv, nom_obsv, prenom_obsv, initiale_obsv from bd_habnat.t_liste_obsv order by nom_obsv, prenom_obsv'):
            while query_obsv.next():
                self.ui.cbx_auteur.addItem(query_obsv.value(1) + " " + query_obsv.value(2), query_obsv.value(3) )

        # Remplir la combobox "cbx_habref" avec les noms de référentiels issus de la table "t_liste_ref"
        query_ref = QtSql.QSqlQuery(self.db)
        if query_ref.exec_('select id_ref, nom_ref, code_ref from bd_habnat.t_liste_ref order by id_ref'):
            while query_ref.next():
                self.ui.cbx_habref.addItem(query_ref.value(1), query_ref.value(2) )

        # Remplir les combobox "cbx_corine_mep" et "cbx_eur27_mep" avec les champs hab_cod des tables "t_liste_ref_cirone" et "t_loiste_ref_eur27"
        query_corine = QtSql.QSqlQuery(self.db)
        if query_corine.exec_('select hab_cod from bd_habnat.t_liste_ref_corine order by hab_cod'):
            while query_corine.next():
                self.ui.cbx_corine_mep.addItem(query_corine.value(0), query_corine.value(0) )
        print query_corine

        query_eur27 = QtSql.QSqlQuery(self.db)
        if query_eur27.exec_('select hab_cod from bd_habnat.t_liste_ref_eur27 order by hab_cod'):
            while query_eur27.next():
                self.ui.cbx_eur27_mep.addItem(query_eur27.value(0), query_eur27.value(0) )
        print query_eur27

        # Connexions signaux - slots
        self.ui.cbx_habref.currentIndexChanged.connect(self.listesref)
        self.ui.cbx_habfr.currentIndexChanged.connect(self.coreur27)
        self.ui.buttonBox.accepted.connect(self.sauvSaisie)
        self.ui.buttonBox.rejected.connect(self.close)
        self.ui.chx_peupleraie.stateChanged.connect(self.peupleraie)



    def listesref(self):
        # Réinitialisations
        self.ui.cbx_hablat.clear()
        self.ui.cbx_habfr.clear()
        self.ui.txt_codeeur27.clear()
        self.ui.txt_codecorine.clear()
        self.habref = self.ui.cbx_habref.itemData(self.ui.cbx_habref.currentIndex())
        if self.habref == 'cbnbl':
        # Si le référentiel "Digitale" du CBNBL est sélectionné, alors remplir la combobox "cbx_hablat"
            print 'cbnbl'
            query_cbnbl = QtSql.QSqlQuery(self.db)
            qcbnbl = u'select hab_cod, hab_lat from bd_habnat.t_liste_ref_cbnbl order by hab_lat'
            ok = query_cbnbl.exec_(qcbnbl)
            while query_cbnbl.next():
                self.ui.cbx_hablat.addItem(query_cbnbl.value(1), query_cbnbl.value(0))
            if not ok:
                QtGui.QMessageBox.warning(self, 'Alerte', u'Requête CBNBL ratée')
                print unicode(qcbnbl)
        else :
        # Si un autre référentiel est sélectionné, alors remplir la combobox "cbx_habfr" avec les valeurs de la table correspondant au référentiel.
            print str(self.habref)
            query_autrref = QtSql.QSqlQuery(self.db)
            qautrref = u"""select hab_cod, hab_fr from bd_habnat.t_liste_ref_{zr_table} order by hab_fr""".format(zr_table = str(self.habref))
            ok = query_autrref.exec_(qautrref)
            while query_autrref.next():
                self.ui.cbx_habfr.addItem(query_autrref.value(1), query_autrref.value(0))
            if not ok:
                QtGui.QMessageBox.warning(self, 'Alerte', u'Requête Autre ref ratée')
                print unicode(qautrref)



    def coreur27(self):
        # Remplissage éventuel des zones de texte "txt_codeeur27" et "txt_codecorine"
        self.ui.txt_codeeur27.clear()
        self.ui.txt_codecorine.clear()
        self.codecoreu27 = self.ui.cbx_habfr.itemData(self.ui.cbx_habfr.currentIndex())
        if self.habref == 'eur27':
            self.ui.txt_codeeur27.setText(unicode(self.codecoreu27))
        if self.habref == 'corine':
            self.ui.txt_codecorine.setText(unicode(self.codecoreu27))



    def peupleraie(self):
        if self.ui.chx_peupleraie.isChecked() == True:
            self.ui.cbx_pourcent.setEnabled(0)
            self.ui.cbx_pourcent.setCurrentIndex(self.ui.cbx_pourcent.findText('100', QtCore.Qt.MatchStartsWith))
        else :
            self.ui.cbx_pourcent.setEnabled(1)



    def sauvSaisie(self):
        self.erreurSaisieBase = '0'
        print 'sauv_saisie'
        #copie des entités sélectionnées dans une couche "memory". Evite les problèmes avec les types de couches "non éditables" (comme les GPX).
        coucheactive=self.iface.activeLayer()

        # On vérifie que les entités sélectionnées dans la couche active sont bien des polygones (et non des lignes ou des points)
        entselect=[QgsGeometry(feature.geometry()) for feature in coucheactive.selectedFeatures()]
        if entselect[0].type() == QGis.Polygon:
            typegeom='Polygon'
#            geom = self.transfoPoly(entselect)
#            print "geom=" + str(geom.exportToWkt())
            print "polygones"
        else: 
            QtGui.QMessageBox.warning(self, 'Alerte', u'Les entités sélectionnées ne sont pas des polygones')
            self.close
            return

        # Création de la couche en mémoire "memlayer" et début de la session d'édition
        if coucheactive.crs().authid() == u'EPSG:4326':
            memlayer=QgsVectorLayer("{zr_typegeom}?crs=epsg:4326".format(zr_typegeom = typegeom), "memlayer", "memory")
        if coucheactive.crs().authid() == u'EPSG:2154':
            memlayer=QgsVectorLayer("{zr_typegeom}?crs=epsg:2154".format(zr_typegeom = typegeom), "memlayer", "memory")
            print "memlayer="+str(memlayer)
        QgsMapLayerRegistry.instance().addMapLayer(memlayer, False)
        root = QgsProject.instance().layerTreeRoot()
        memlayerNode = QgsLayerTreeLayer(memlayer)
        root.insertChildNode(0, memlayerNode)
        self.iface.setActiveLayer(memlayer)
        memlayer.startEditing()


# Pour chaque entité sélectionnée, si elle est multipartie, on ajoute chacune de ses parties individuellement à la couche memlayer. Sinon, on l'ajoute directement à "memlayer". Puis, on clot la session d'édition.
        for feature in coucheactive.selectedFeatures() :
            geom = feature.geometry()
            temp_feature = QgsFeature(feature)
            # check if feature geometry is multipart
            if geom.isMultipart():
                # if feature is multipart creates a new feature using the geometry of each part
                for part in geom.asGeometryCollection ():
                    temp_feature.setGeometry(part)
                    memlayer.dataProvider().addFeatures([temp_feature])
                    memlayer.updateExtents()
                # if feature is singlepart, simply adds it to the layer memory
            else :
                temp_feature.setGeometry(geom)
                memlayer.dataProvider().addFeatures([temp_feature])
                memlayer.updateExtents()
        memlayer.commitChanges()
        print "memlayercount="+str(memlayer.featureCount())

        #on sélectionne toutes les entités de memlayer pour en faire une liste de géométries, qui sera saisie en base.
        memlayer.selectAll()
        geomlis = [QgsGeometry(feature.geometry()) for feature in memlayer.selectedFeatures()]
        print "geomlis="+str(geomlis)
        geomlist = QgsGeometry.fromMultiPolygon([poly.asPolygon() for poly in geomlis])


        #export de la géométrie en WKT et transformation de la projection si les données ne sont pas saisies en Lambert 93
        if memlayer.crs().authid() == u'EPSG:2154':
            thegeom='st_setsrid(st_geometryfromtext (\'{zr_geom}\'), 2154)'.format(zr_geom=geomlist.exportToWkt())
        elif memlayer.crs().authid() == u'EPSG:4326':
            thegeom='st_transform(st_setsrid(st_geometryfromtext (\'{zr_geom}\'),4326), 2154)'.format(zr_geom=geomlist.exportToWkt())
        else :
            print u'La projection de la couche active n\'est pas supportée'


        #gestion de l'identifiant id_mosaik, servant à regrouper les enregistrements appartenant à une même mosaïque d'habitats
        pourcent = int(self.ui.cbx_pourcent.itemText(self.ui.cbx_pourcent.currentIndex()))
        if pourcent > 99 :
            print ">99"
            id_mosaik = 0
        else :
            querymosaik = QtSql.QSqlQuery(self.db)
            qmosaik = u"""SELECT id_hab_ce, date_fin, pourcent,the_geom, peupleraie, id_mosaik FROM bd_habnat.t_ce_habnat_surf WHERE the_geom = {zr_thegeom} AND date_fin = '{zr_datefin}' AND peupleraie = 'f' """.format (\
            zr_thegeom = thegeom,\
            zr_datefin = self.ui.dat_datefin.date().toPyDate().strftime("%Y-%m-%d"))
            print qmosaik
            ok = querymosaik.exec_(qmosaik)
            if not ok:
                QtGui.QMessageBox.warning(self, 'Alerte', u'Requête Mosaik ratée')
            if querymosaik.size() > 0 :
                print "on est deja dans la mosaique"
                sumprct = 0
                while querymosaik.next() :
                    sumprct += int(querymosaik.value(2))
                sumprct += pourcent
                if sumprct > 100 :
                    QtGui.QMessageBox.warning(self, 'Alerte', u'La somme des pourcentages d'u'habitats dépasse 100 % dans la mosaïque')
                    return
                print "sumprct = " + str(sumprct)
                querymosaik.first()
                id_mosaik = querymosaik.value(5)
                print "id_mosaik="+str(id_mosaik)
            else :
                querybiggestid = QtSql.QSqlQuery(self.db)
                qbiggestid = u"""SELECT id_mosaik FROM bd_habnat.t_ce_habnat_surf ORDER BY id_mosaik DESC LIMIT 1"""
                ok = querybiggestid.exec_(qbiggestid)
                if not ok:
                    QtGui.QMessageBox.warning(self, 'Alerte', u'Requête PlusGrandIdMosaik ratée')
                querybiggestid.next()
                print "debut de la mosaique"
                if self.ui.chx_peupleraie.isChecked == True :
                    id_mosaik = 0
                else :
                    id_mosaik = int(querybiggestid.value(0))+1
                print "id_mosaik="+str(id_mosaik)



        #lancement de la requête SQL qui introduit les données géographiques et du formulaire dans la base de données.

        self.habref = self.ui.cbx_habref.itemData(self.ui.cbx_habref.currentIndex())
        if self.habref == 'cbnbl':
            print 'liste cbnbl'
            queryrarmen = QtSql.QSqlQuery(self.db)
            qrarmen = u"""SELECT rarete, menace, interetpatr FROM bd_habnat.t_liste_ref_cbnbl WHERE hab_lat = '{zr_hablat}'""".format (\
            zr_hablat= self.ui.cbx_hablat.itemText(self.ui.cbx_hablat.currentIndex()).replace("\'","\'\'"))
            okrarmen=queryrarmen.exec_(qrarmen)
            if not okrarmen :
                QtGui.QMessageBox.warning(self, 'Alerte', u'Requête RarMen ratée')
            queryrarmen.next()
            self.rarete = queryrarmen.value(0)
            self.menace = queryrarmen.value(1)
#            self.patrimonialite = queryrarmen.value(2)
#            print str(self.rarete)+" "+str(self.menace)+" "+str(self.patrimonialite)
        else :
            self.rarete = 'ND'
            self.menace = 'ND'
        self.patrimonialite = str(self.ui.chx_patrimoine.isChecked()).lower()

        querysauvhab = QtSql.QSqlQuery(self.db)
        query = u"""INSERT INTO bd_habnat.t_ce_habnat_surf(codesite, auteur, date_deb, date_fin, hab_ref, hab_cod, hab_lat, hab_fr, code_eur27, code_corine, pourcent, rarete, menace, patrimoine, surf_tot, the_geom, peupleraie, id_mosaik) values ('{zr_codesite}', '{zr_auteur}', '{zr_datedeb}', '{zr_datefin}', '{zr_habref}', '{zr_habcod}', '{zr_hablat}', '{zr_habfr}', '{zr_codeeur27}', '{zr_codecorine}', '{zr_pourcent}', '{zr_rarete}', '{zr_menace}', '{zr_patrimoine}', st_area({zr_thegeom}), {zr_thegeom}, {zr_peupleraie}, {zr_idmosaik})""".format (\
        zr_codesite = self.ui.cbx_codesite.itemData(self.ui.cbx_codesite.currentIndex()),\
        zr_auteur = self.ui.cbx_auteur.itemData(self.ui.cbx_auteur.currentIndex()),\
        zr_datedeb = self.ui.dat_datedeb.date().toPyDate().strftime("%Y-%m-%d"),\
        zr_datefin = self.ui.dat_datefin.date().toPyDate().strftime("%Y-%m-%d"),\
        zr_habref = self.ui.cbx_habref.itemData(self.ui.cbx_habref.currentIndex()),\
        zr_habcod = '',\
        zr_hablat = self.ui.cbx_hablat.itemText(self.ui.cbx_hablat.currentIndex()).replace("\'","\'\'"),\
        zr_habfr = self.ui.cbx_habfr.itemText(self.ui.cbx_habfr.currentIndex()).replace("\'","\'\'"),\
        zr_codeeur27 = self.ui.cbx_eur27_mep.itemText(self.ui.cbx_eur27_mep.currentIndex()),\
        zr_codecorine = self.ui.cbx_corine_mep.itemText(self.ui.cbx_corine_mep.currentIndex()),\
        zr_pourcent = self.ui.cbx_pourcent.itemText(self.ui.cbx_pourcent.currentIndex()),\
        zr_rarete = self.rarete,\
        zr_menace = self.menace,\
        zr_patrimoine = self.patrimonialite,\
        zr_thegeom = thegeom,\
        zr_peupleraie = str(self.ui.chx_peupleraie.isChecked()).lower(),\
        zr_idmosaik = id_mosaik)
        ok = querysauvhab.exec_(query)
        if not ok:
            QtGui.QMessageBox.warning(self, 'Alerte', u'Requête sauver Ope ratée')
            self.erreurSaisieBase = '1'
        self.iface.setActiveLayer(coucheactive)
        QgsMapLayerRegistry.instance().removeMapLayer(memlayer.id())

        if self.erreurSaisieBase == '0':
            QtGui.QMessageBox.information(self, 'Information', u'Données correctement saisies dans la base')
        else : 
            QtGui.QMessageBox.warning(self, 'Alerte', u'Il y a eu une erreur lors de la saisie. Données non saisies en base.')
        print "bonjour"
        self.close()


