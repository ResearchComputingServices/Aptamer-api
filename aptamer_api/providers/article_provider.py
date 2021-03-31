from datetime import datetime
from aptamer_api.extensions import oidc
from flask import request
from aptamer_api.extensions import db, ma
from aptamer_api.providers.base_provider import BaseProvider
from aptamer_api.models.role import Role, RoleSchema
from aptamer_api.models.user import User, UserSchema
from aptamer_api.models.article import Article, ArticleSchema
from aptamer_api.models.user_field import UserField, UserFieldSchema
from aptamer_api.models.user_field_category import UserFieldCategory, UserFieldCategorySchema
from aptamer_api.models.user_field_type import UserFieldType, UserFieldTypeSchema
from aptamer_api.models.user_field import UserField


class ArticleProvider(BaseProvider):
    def add(self, data):
        data['id'] = self.generate_id(field=Article.id)
        article = Article(data)
        db.session.add(article)
        db.session.commit()
        return article

    def update(self, data, article):
        article.name = data.get('name')
        article.pubmedid = data.get('pubmedid')
        article.doinumber = data.get('doinumber')
        article.aptamertargettype = data.get('aptamertargettype')
        article.aptamertargetname = data.get('aptamertargetname')
        article.aptamersequence = data.get('aptamersequence')
        article.lengthofrandomregion = data.get('lengthofrandomregion')
        article.templatesequence = data.get('templatesequence')
        article.yearofpublication = data.get('yearofpublication')
        article.templatebias = data.get('templatebias')
        article.selexmethod = data.get('selexmethod')
        article.numberofselectionrounds = data.get('numberofselectionrounds')
        article.separationpartitioningmethod = data.get('separationpartitioningmethod')
        article.elutionrecoverymethod = data.get('elutionrecoverymethod')
        article.selectionsolutionbufferingagent = data.get('selectionsolutionbufferingagent')
        article.selectionsolutionph = data.get('selectionsolutionph')
        article.selectionsolutiontemperature = data.get('selectionsolutiontemperature')
        article.concentrationkm = data.get('concentrationkm')
        article.concentrationmgm = data.get('concentrationmgm')
        article.concentrationnam = data.get('concentrationnam')
        article.concentrationznm = data.get('concentrationznm')
        article.concentrationcam = data.get('concentrationcam')
        article.concentrationotherm = data.get('concentrationotherm')
        article.affinitymethod = data.get('affinitymethod')
        article.affinitymethodconditions = data.get('affinitymethodconditions')
        article.aptamertype = data.get('aptamertype')
        article.othermodification = data.get('othermodification')
        article.kdvalueinmolar = data.get('kdvalueinmolar')
        article.kderror = data.get('kderror')
        article.testedapplicationpurpose = data.get('testedapplicationpurpose')
        article.mutationalanalysis = data.get('mutationalanalysis')
        article.minamersyesno = data.get('minamersyesno')
        article.minimeronesequence = data.get('minimeronesequence')
        article.minimeronekd = data.get('minimeronekd')
        article.minimertwosequence = data.get('minimertwosequence')
        article.minimertwokd = data.get('minimertwokd')
        article.minimerthreesequence = data.get('minimerthreesequence')
        article.minimerthreekd = data.get('minimerthreekd')
        article.notes = data.get('notes')


        article.status = data.get('status')
        article.operator = data.get('operator')

        return article
