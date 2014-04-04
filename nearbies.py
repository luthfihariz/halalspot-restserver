from flask import Blueprint
from flask.ext.restful import reqparse, Resource
from bson.objectid import ObjectId
from pymongo import Connection
from datetime import datetime
from dbconfig import db

nearbies_api = Blueprint('nearbies_api',__name__)

parser = reqparse.RequestParser()

class NearbyPlacesAPI(Resource):

	def __init__(self):
		parser.add_argument('lat', type=float)
		parser.add_argument('lng', type=float)
		parser.add_argument('keyword', type=str)
		parser.add_argument('radius', type=float)
		parser.add_argument('sort', type=str)
		parser.add_argument('order', type=int)
		parser.add_argument('limit', type=int)
		parser.add_argument('skip', type=int)
		super(NearbyPlacesAPI, self).__init__()

	def get(self):
		args = parser.parse_args()
		lat = args['lat']
		lng = args['lng']
		keyword = args['keyword']
		radius = args['radius']
		sort = args['sort']
		order = args['order']
		limit = args['limit']		
		skip = args['skip']

		radius = radius if radius else 100000
		sort = sort if sort else 'distance'
		order = order if order else 1
		limit = limit if limit else 20
		radians = radius/float(6371000)
		skip = skip if skip else 0

		queryResult = db.places.aggregate([
			{'$geoNear': {
				'near': [lng, lat],
				'distanceField': 'distance',
				'distanceMultiplier': 6371,
				'spherical': True,
				'maxDistance': radians,
				'limit': limit,
				}
			},
			{'$sort': {sort: order}},
			{'$skip': skip}
		])

		places = []
		if len(queryResult['result']) > 0 :		
			for place in queryResult['result']:
				categoryId = place['categoryId']
				category = db['categories'].find_one({'_id':ObjectId(categoryId)},{'name' : 1,'short_name' : 1,'_id':0})
				place['category'] = category
				
				if 'bodyId' in place['halal']:
					halalbodies = db['halalbodies'].find_one({'_id':ObjectId(place['halal']['bodyId'])},
						{'_id':0,'name':1,'shortName':1,'country':1,'halalLogo':1})
					place['halal']['bodies'] = halalbodies

				places.append(place)

		jsonResponse = {'status': True, 'count' : len(queryResult['result']), 'result':{'places': places}}
		return jsonResponse