from datetime import datetime
from aptamer_api.extensions import oidc
from flask import request
from aptamer_api.extensions import db, ma
from aptamer_api.providers.base_provider import BaseProvider
from aptamer_api.models.role import Role, RoleSchema
from aptamer_api.models.user import User, UserSchema
from aptamer_api.models.temp_article import TempArticle, TempArticleSchema
from aptamer_api.models.user_field import UserField, UserFieldSchema
from aptamer_api.models.user_field_category import UserFieldCategory, UserFieldCategorySchema
from aptamer_api.models.user_field_type import UserFieldType, UserFieldTypeSchema
from aptamer_api.models.user_field import UserField


class TempArticleProvider(BaseProvider):
    def add(self, data):
        data['id'] = self.generate_id(field=TempArticle.id)
        temp_article = TempArticle(data)
        db.session.add(temp_article)
        db.session.commit()
        return temp_article

    def update(self, data, temp_article):
        temp_article.name = data.get('name')

        temp_article.pubmedid = data.get('pubmedid')
        temp_article.doinumber = data.get('doinumber')
        temp_article.aptamertargettype = data.get('aptamertargettype')
        temp_article.aptamertargetname = data.get('aptamertargetname')
        temp_article.aptamersequence = data.get('aptamersequence')
        temp_article.lengthofrandomregion = data.get('lengthofrandomregion')
        temp_article.templatesequence = data.get('templatesequence')
        temp_article.yearofpublication = data.get('yearofpublication')
        temp_article.templatebias = data.get('templatebias')
        temp_article.selexmethod = data.get('selexmethod')
        temp_article.numberofselectionrounds = data.get('numberofselectionrounds')
        temp_article.separationpartitioningmethod = data.get('separationpartitioningmethod')
        temp_article.elutionrecoverymethod = data.get('elutionrecoverymethod')
        temp_article.selectionsolutionbufferingagent = data.get('selectionsolutionbufferingagent')
        temp_article.selectionsolutionph = data.get('selectionsolutionph')
        temp_article.selectionsolutiontemperature = data.get('selectionsolutiontemperature')
        temp_article.concentrationkm = data.get('concentrationkm')
        temp_article.concentrationmgm = data.get('concentrationmgm')
        temp_article.concentrationnam = data.get('concentrationnam')
        temp_article.concentrationznm = data.get('concentrationznm')
        temp_article.concentrationcam = data.get('concentrationcam')
        temp_article.concentrationotherm = data.get('concentrationotherm')
        temp_article.affinitymethod = data.get('affinitymethod')
        temp_article.affinitymethodconditions = data.get('affinitymethodconditions')
        temp_article.aptamertype = data.get('aptamertype')
        temp_article.othermodification = data.get('othermodification')
        temp_article.kdvalueinmolar = data.get('kdvalueinmolar')
        temp_article.kderror = data.get('kderror')
        temp_article.testedapplicationpurpose = data.get('testedapplicationpurpose')
        temp_article.mutationalanalysis = data.get('mutationalanalysis')
        temp_article.minamersyesno = data.get('minamersyesno')
        temp_article.minimeronesequence = data.get('minimeronesequence')
        temp_article.minimeronekd = data.get('minimeronekd')
        temp_article.minimertwosequence = data.get('minimertwosequence')
        temp_article.minimertwokd = data.get('minimertwokd')
        temp_article.minimerthreesequence = data.get('minimerthreesequence')
        temp_article.minimerthreekd = data.get('minimerthreekd')
        temp_article.notes = data.get('notes')

        return temp_article
