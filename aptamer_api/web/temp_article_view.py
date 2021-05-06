from flask import request, send_file
from flask import json, jsonify, Response, blueprints
from aptamer_api.models.role import Role, RoleSchema
from aptamer_api.models.temp_article import TempArticle, TempArticleSchema
from aptamer_api.extensions import db, ma
from aptamer_api.models.article import Article, ArticleSchema
from aptamer_api.web.common_view import aptamer_bp
from aptamer_api.decorators.crossorigin import crossdomain
from aptamer_api.decorators.authentication import authentication
from aptamer_api.providers.temp_article_provider import TempArticleProvider
from aptamer_api.providers.article_provider import ArticleProvider
from aptamer_api.providers.user_provider import UserProvider
import pandas as pd
import math
from io import BytesIO

temp_article_schema = TempArticleSchema(many=False)
temp_article_schema_many = TempArticleSchema(many=True)
article_schema = ArticleSchema(many=False)
article_schema_many = ArticleSchema(many=True)
article_provider = ArticleProvider()
provider = TempArticleProvider()
user_provider = UserProvider()


@aptamer_bp.route("/temp_articles/count", methods=['GET'])
@crossdomain(origin='*')
@authentication
def get_temp_article_count():
    properties = TempArticle.query.filter_by(status="Pending").all()
    result = temp_article_schema_many.dump(properties)
    dict = {"count": len(result)}
    response = Response(json.dumps(dict), 200, mimetype="application/json")
    return response


@aptamer_bp.route("/temp_articles", methods=['GET'])
@crossdomain(origin='*')
@authentication
def get_temp_article():
    try:
        id = request.args.get('id')
        user = user_provider.get_authenticated_user()
        is_researcher_administrator = user_provider.has_role(user, 'Researcher') or user_provider.has_role(user, 'Administrator')
        if is_researcher_administrator:
            if id:
                properties = TempArticle.query.filter_by(id=id).first()
                result = temp_article_schema.dump(properties)
                return jsonify(result)
            else:
                properties = provider.query_all_pending(TempArticle)
                result = temp_article_schema_many.dump(properties)
                response = jsonify(result)
        else:
            error = {"message": "Access Denied"}
            response = Response(json.dumps(error), 403, mimetype="application/json")
    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")
    return response

@aptamer_bp.route("/temp_articles", methods=['POST'])
@crossdomain(origin='*')
@authentication
def add_temp_article():
    try:
        data = request.get_json()
        data["status"] = "Pending"
        data["operator"] = user_provider.get_authenticated_user().name
        temp_article = provider.add(data)
        result = temp_article_schema.dump(temp_article)
        response = jsonify(result)

    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response


@aptamer_bp.route("/temp_articles", methods=['PUT'])
@crossdomain(origin='*')
@authentication
def update_temp_article():
    try:
        user = user_provider.get_authenticated_user()
        is_researcher_administrator = user_provider.has_role(user, 'Researcher') or user_provider.has_role(user, 'Administrator')

        if is_researcher_administrator:
            data = request.get_json()
            temp_article = TempArticle.query.filter_by(id=data.get('id')).first()
            if not temp_article:
                temp_article = TempArticle.query.filter_by(pubmedid=data.get('pubmedid')).first()
            if temp_article:
                if data.get('id') is None:
                    data['id'] = temp_article.id
                data["status"] = "Pending"
                data["operator"] = user_provider.get_authenticated_user().name
                provider.update(data, temp_article)
                db.session.commit()
                response = Response(json.dumps(data), 200, mimetype="application/json")
            else:
                response = Response(json.dumps(data), 404, mimetype="application/json")

        else:
            error = {"message": "Access Denied"}
            response = Response(json.dumps(error), 403, mimetype="application/json")
    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response


@aptamer_bp.route("/temp_articles", methods=['DELETE'])
@crossdomain(origin='*')
@authentication
def delete_temp_article():
    try:
        user = user_provider.get_authenticated_user()
        is_researcher_administrator = user_provider.has_role(user, 'Researcher') or user_provider.has_role(user,
                                                                                                           'Administrator')
        if is_researcher_administrator:
            data = request.get_json()
            temp_article = TempArticle.query.filter_by(id=data.get('id')).first()
            if not temp_article:
                temp_article = TempArticle.query.filter_by(pubmedid=data.get('pubmedid')).first()
            if temp_article:
                db.session.delete(temp_article)
                db.session.commit()
                response = Response(json.dumps(data), 200, mimetype="application/json")
            else:
                response = Response(json.dumps(data), 404, mimetype="application/json")
        else:
            error = {"message": "Access Denied"}
            response = Response(json.dumps(error), 403, mimetype="application/json")
    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")
    return response


@aptamer_bp.route("/temp_articles/upload", methods=['POST'])
@crossdomain(origin='*')
@authentication
def upload_temp_articles():
    user = user_provider.get_authenticated_user()
    raw_data = request.get_data()
    data = pd.read_excel(raw_data, engine="openpyxl")
    try:
        for _, row in data.iterrows():
            d = dict(row)
            if type(d["PubMed ID"]) == int or type(d["Year of publication"]) == int:
                temp_article = {
                    "id": provider.generate_id(field=TempArticle.id),
                    "name": "",
                    "pubmedid": "" if str(d["PubMed ID"]) == "nan" else str(int(d["PubMed ID"])),
                    "doinumber": "" if type(d["DOI number"]) == float else str(d["DOI number"]),
                    "yearofpublication": "" if type(d["Year of publication"]) == float else str(
                        d["Year of publication"]),
                    "aptamertargettype": "" if type(d["Aptamer Target Type"]) == float else str(
                        d["Aptamer Target Type"]),
                    "aptamertargetname": "" if type(d["Aptamer Target Name"]) == float else str(
                        d["Aptamer Target Name"]),
                    "aptamersequence": "" if type(d["Aptamer Sequence"]) == float else str(d["Aptamer Sequence"]),
                    # "aptamersequence": "CATCCATGGG",
                    "templatesequence": "" if type(d[
                                                       "Template sequence: e.g., GCAATGGTACGGTACTGTC-N40-AATCAGTGCACGCTACTTTGCTAA"]) == float else str(
                        d["Template sequence: e.g., GCAATGGTACGGTACTGTC-N40-AATCAGTGCACGCTACTTTGCTAA"]),
                    "lengthofrandomregion": "" if str(d["Length of random region"]) == 'nan' else str(
                        d["Length of random region"]),
                    "templatebias": "" if type(d["Template Bias"]) == float else str(d["Template Bias"]),
                    "selexmethod": "" if type(d["SELEX Method"]) == float else str(d["SELEX Method"]),
                    "numberofselectionrounds": "" if str(d["Number of Selection Rounds"]) == "nan" else str(
                        d["Number of Selection Rounds"]),
                    "separationpartitioningmethod": "" if type(
                        d["Separation (Partitioning) Method"]) == float else str(
                        d["Separation (Partitioning) Method"]),
                    "elutionrecoverymethod": "" if type(d["Elution/Recovery method"]) == float else str(
                        d["Elution/Recovery method"]),
                    "selectionsolutionbufferingagent": "" if type(
                        d["Selection Solution Buffering Agent"]) == float else str(
                        d["Selection Solution Buffering Agent"]),
                    "selectionsolutionph": "" if str(d["Selection Solution pH"]) == "nan" else str(
                        round(d["Selection Solution pH"], 1)),
                    "selectionsolutiontemperature": "" if str(
                        d["Selection Solution Temperature °C"]) == "nan" else str(
                        d["Selection Solution Temperature °C"]),
                    "concentrationkm": "" if str(d["Concentration K (M)"]) == "nan" else str(
                        d["Concentration K (M)"]),
                    "concentrationmgm": "" if str(d["Concentration Mg (M)"]) == "nan" else str(
                        d["Concentration Mg (M)"]),
                    "concentrationnam": "" if str(d["Concentration Na (M)"]) == "nan" else str(
                        d["Concentration Na (M)"]),
                    "concentrationznm": "" if str(d["Concentration Zn (M)"]) == "nan" else str(
                        d["Concentration Zn (M)"]),
                    "concentrationcam": "" if str(d["Concentration Ca (M)"]) == "nan" else str(
                        d["Concentration Ca (M)"]),
                    "concentrationotherm": "" if str(d["Concentration Other (M)"]) == "nan" else str(
                        d["Concentration Other (M)"]),
                    "affinitymethod": "" if type(d["Affinity Method"]) == float else str(d["Affinity Method"]),
                    "affinitymethodconditions": "" if type(d["Affinity Method Conditions"]) == float else str(
                        d["Affinity Method Conditions"]),
                    "aptamertype": "" if type(d["Aptamer Type"]) == float else str(d["Aptamer Type"]),
                    "othermodification": "" if type(d["Other modification"]) == float else str(
                        d["Other modification"]),
                    "kdvalueinmolar": "" if str(d["KD Value (in Molar)"]) == "nan" else str(
                        d["KD Value (in Molar)"]),
                    "kderror": "" if str(d["KD Error"]) == "nan" else str(d["KD Error"]),
                    "testedapplicationpurpose": "" if type(d["Tested application/ purpose"]) == float else str(
                        d["Tested application/ purpose"]),
                    "mutationalanalysis": "" if type(d["Mutational Analysis"]) == float else str(
                        d["Mutational Analysis"]),
                    "minamersyesno": "" if type(d["Minamers  (yes/no)"]) == float else str(d["Minamers  (yes/no)"]),
                    "minimeronesequence": "n/a" if str(d["Minimer 1 sequence"]) == "nan" else str(
                        d["Minimer 1 sequence"]),
                    "minimeronekd": "n/a" if str(d["Minimer 1 Kd"]) == "nan" else str(d["Minimer 1 Kd"]),
                    "minimertwosequence": "n/a" if str(d["Minimer 2 sequence"]) == "nan" else str(
                        d["Minimer 2 sequence"]),
                    "minimertwokd": "n/a" if str(d["Minimer 2 Kd"]) == "nan" else str(d["Minimer 2 Kd"]),
                    "minimerthreesequence": "n/a" if str(d["Minimer 3 sequence"]) == "nan" else str(
                        d["Minimer 3 sequence"]),
                    "minimerthreekd": "n/a" if str(d["Minimer 3 Kd"]) == "nan" else str(d["Minimer 3 Kd"]),
                    "notes": "" if type(d["Notes"]) == float else str(d["Notes"]),
                    "status": "Pending",
                    "operator": user_provider.get_authenticated_user().name
                }
                temp_articles = TempArticle(temp_article)
                db.session.add(temp_articles)
        db.session.commit()
        response = Response(json.dumps({"success": True}), 200, mimetype="application/json")
    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response


@aptamer_bp.route("/temp_articles/decline", methods=['PUT'])
@crossdomain(origin='*')
@authentication
def decline_temp_article():
    try:
        user = user_provider.get_authenticated_user()
        is_researcher_administrator = user_provider.has_role(user, 'Researcher') or user_provider.has_role(user, 'Administrator')

        if is_researcher_administrator:
            data = request.get_json()
            temp_article = TempArticle.query.filter_by(id=data.get('id')).first()
            if not temp_article:
                temp_article = TempArticle.query.filter_by(pubmedid=data.get('pubmedid')).first()
            if temp_article:
                if data.get('id') is None:
                    data['id'] = temp_article.id
                temp_article.status = "Declined"
                temp_article.operator = user_provider.get_authenticated_user().name
                provider.update(data, temp_article)
                db.session.commit()
                response = Response(json.dumps(data), 200, mimetype="application/json")
            else:
                response = Response(json.dumps(data), 404, mimetype="application/json")
        else:
            error = {"message": "Access Denied"}
            response = Response(json.dumps(error), 403, mimetype="application/json")
    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response

@aptamer_bp.route("/temp_articles/approve", methods=['POST'])
@crossdomain(origin='*')
@authentication
def approve_temp_article():
    try:
        user = user_provider.get_authenticated_user()
        is_researcher_administrator = user_provider.has_role(user, 'Researcher') or user_provider.has_role(user, 'Administrator')
        if is_researcher_administrator:
            data = request.get_json()
            data["status"] = "Approved"
            data["operator"] = user_provider.get_authenticated_user().name
            article = article_provider.add(data)
            result = article_schema.dump(article)
            response = jsonify(result)
            update_status_to_approve_temp_article(data)
        else:
            error = {"message": "Access Denied"}
            response = Response(json.dumps(error), 403, mimetype="application/json")

    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response

def update_status_to_approve_temp_article(data):
    temp_article = TempArticle.query.filter_by(id=data.get('id')).first()
    if not temp_article:
        temp_article = TempArticle.query.filter_by(pubmedid=data.get('pubmedid')).first()
    if temp_article:
        if data.get('id') is None:
            data['id'] = temp_article.id
        provider.update(data, temp_article)
        temp_article.status = "Approved"
        temp_article.operator = user_provider.get_authenticated_user().name
        db.session.commit()

@aptamer_bp.route("/temp_articles/export", methods=['GET'])
@crossdomain(origin='*')
@authentication
def export_temp_articles():
    try:
        specific_users_info = [{
            # "ID": s_a.id,
            "PubMed ID": "",
            "DOI number": "",
            "Year of publication": "",
            "Aptamer Target Type": "",
            "Aptamer Target Name": "",
            "Aptamer Sequence": "",
            "Template sequence: e.g., GCAATGGTACGGTACTGTC-N40-AATCAGTGCACGCTACTTTGCTAA": "",
            "Length of random region": "",
            "Template Bias": "",
            "SELEX Method": "",
            "Number of Selection Rounds": "",
            "Separation (Partitioning) Method": "",
            "Elution/Recovery method": "",
            "Selection Solution Buffering Agent": "",
            "Selection Solution pH": "",
            "Selection Solution Temperature °C": "",
            "Concentration K (M)": "",
            "Concentration Mg (M)": "",
            "Concentration Na (M)": "",
            "Concentration Zn (M)": "",
            "Concentration Ca (M)": "",
            "Concentration Other (M)": "",
            "Affinity Method": "",
            "Affinity Method Conditions": "",
            "Aptamer Type": "",
            "Other modification": "",
            "KD Value (in Molar)": "",
            "KD Error": "",
            "Tested application/ purpose": "",
            "Mutational Analysis": "",
            "Minamers  (yes/no)": "",
            "Minimer 1 sequence": "",
            "Minimer 1 Kd": "",
            "Minimer 2 sequence": "",
            "Minimer 2 Kd": "",
            "Minimer 3 sequence": "",
            "Minimer 3 Kd": "",
            "Notes": ""
        }]
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            pd.DataFrame(specific_users_info).to_excel(writer,
                                           sheet_name="template",
                                           index=False)
            workbook = writer.book
            worksheet = writer.sheets["template"]
            format = workbook.add_format()
            format.set_align('center')
            format.set_align('vcenter')
            worksheet.set_column('A:A', 12, format)
            worksheet.set_column('B:B', 38, format)
            worksheet.set_column('C:C', 22, format)
            worksheet.set_column('D:D', 38, format)
            worksheet.set_column('E:E', 15, format)
            worksheet.set_column('F:AL', 18, format)
            writer.save()
        output.seek(0)
        return send_file(output,
                         attachment_filename="Template" + '.xlsx',
                         mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                         as_attachment=True, cache_timeout=-1)
    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 404, mimetype="application/json")
        return response