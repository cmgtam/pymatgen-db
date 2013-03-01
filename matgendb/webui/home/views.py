# Create your views here.

import json

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseBadRequest, \
    HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
import os
from matgendb.query_engine import QueryEngine
from pymatgen import Element, Composition
import bson
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.encoding import force_unicode
import datetime


config = json.loads(os.environ["MGDB_CONFIG"])
qe = QueryEngine(host=config["host"], port=config["port"],
                 database=config["database"], user=config["readonly_user"],
                 password=config["readonly_password"],
                 collection=config["collection"],
                 aliases_config=config.get("aliases_config", None))


def index(request):
    d = config.copy()
    d["ndocs"] = qe.collection.count()
    return render_to_response("home/templates/index.html",
                              RequestContext(request, d))

@csrf_exempt
def query(request):
    if request.method == 'POST':
        try:
            critstr = request.POST["criteria"]
            try:
                criteria = {"pretty_formula": Composition(critstr).reduced_formula}
            except:
                try:
                    criteria = {"task_id": int(critstr)}
                except ValueError:
                    try:
                        syms = [Element(sym).symbol
                                for sym in critstr.split("-")]
                        syms.sort()
                        criteria = {"chemsys": "-".join(syms)}
                    except:
                        criteria = json.loads(critstr)
            properties = request.POST["properties"].split()
            if not properties:
                properties = None
        except ValueError:
            d = {"valid_response": False,
                 "error_msg": "Bad criteria or properties."}
            return HttpResponse(
                json.dumps(d), mimetype="application/json")


        results = list(qe.query(criteria=criteria,
                                properties=properties))
        d = {"valid_response": True, "results": results,
             "properties": properties}
        return HttpResponse(json.dumps(d, cls=MongoJSONEncoder),
                            mimetype="application/json")


class MongoJSONEncoder(DjangoJSONEncoder):
    """
    Encodes Mongo DB objects into JSON
    In particular is handles BSON Object IDs and Datetime objects

    eg.

    >>> from django.core.serializers import json
    >>> json.dumps(mongo_doc, cls=MongoJSONEncoder)
    """

    def default(self, obj):
        if isinstance(obj, bson.objectid.ObjectId):
            return force_unicode(obj)
        elif isinstance(obj, datetime.datetime):
            return str(obj)
        return super(MongoJSONEncoder, self).default(obj)