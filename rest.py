from halalbodies import halalbodies_api, HalalBodiesAPI, HalalBodyAPI
from places import places_api, PlacesAPI, PlaceAPI
from nearbies import nearbies_api, NearbyPlacesAPI
from categories import categories_api, CategoriesAPI, CategoryAPI
from flask import Flask, make_response
from flask.ext.restful import Api
from bson.json_util import dumps


#Blueprint & Restfull Config
app = Flask(__name__)
app.register_blueprint(halalbodies_api)
app.register_blueprint(places_api)
app.register_blueprint(nearbies_api)
api = Api(app)

def toJson(obj, code, headers=None):
	resp = make_response(dumps(obj), code)
	resp.headers.extend(headers or {})
	return resp

#API Mapping
api.representations = {'application/json' : toJson}
api.add_resource(PlacesAPI, '/sharee/api/v1/places')
api.add_resource(NearbyPlacesAPI, '/sharee/api/v1/places/nearby')
api.add_resource(PlaceAPI, '/sharee/api/v1/places/<string:place_id>')
api.add_resource(CategoriesAPI, '/sharee/api/v1/places/categories')
api.add_resource(CategoryAPI, '/sharee/api/v1/places/categories/<string:category_id>')
api.add_resource(HalalBodiesAPI, '/sharee/api/v1/halal/bodies')
api.add_resource(HalalBodyAPI, '/sharee/api/v1/halal/bodies/<string:bodies_id>')


if __name__ == '__main__':
	app.run(debug=True)
