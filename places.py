from flask import Blueprint
from flask.ext.restful import reqparse, Resource
from bson.objectid import ObjectId
from pymongo import Connection
from datetime import datetime
from dbconfig import db

places_api = Blueprint('places_api',__name__)

parser = reqparse.RequestParser()
parser.add_argument('name', type=str)
parser.add_argument('address', type=str)
parser.add_argument('lat', type=float)
parser.add_argument('lng', type=float)
parser.add_argument('city', type=str)
parser.add_argument('country', type=str)
parser.add_argument('cc', type=str)
parser.add_argument('zipCode', type=str)		
parser.add_argument('phone', type=str)
parser.add_argument('email', type=str)
parser.add_argument('website', type=str)
parser.add_argument('twitter', type=str)
parser.add_argument('facebook', type=str)
parser.add_argument('categoryId', type=str)
parser.add_argument('tags', type=str)
parser.add_argument('photoUrls', type=str)
parser.add_argument('halalType', type=str)
parser.add_argument('halalDisplayValue', type=str)
parser.add_argument('bodyId', type=str)
parser.add_argument('foursquareId', type=str)

class PlacesAPI(Resource):
	
	def __init__(self):		
		parser.add_argument('limit', type=int)
		parser.add_argument('sort', type=str)
		parser.add_argument('skip', type=int)
		parser.add_argument('minified', type=str)
		parser.add_argument('order', type=int)
		
		super(PlacesAPI, self).__init__()

	def get(self):		
		args = parser.parse_args()		
		limit = args['limit']
		sort = args['sort']
		city = args['city']
		minified = args['minified']
		order = args['order']
		skip = args['skip']
				
		projection = None if minified=='false' else {'photos':0,'tags':0,'dateLastUpdated':0}
		sortBy = sort if sort else 'dateLastUpdated'
		sortOrder = order if order else -1
		limit = limit if limit else 100
		skip = skip if skip else 0

		queryFilter = {}
		if city :
			queryFilter = {'location.lowerCity':city.lower()}		

		rawQueryResult = db['places'].find(queryFilter,projection)
		queryResult = rawQueryResult.sort(sortBy, sortOrder).limit(limit).skip(skip)
		
		places = []
		for place in queryResult:						
			categoryId = place['categoryId']			
			category = db['categories'].find_one({'_id':ObjectId(categoryId)},{'name' : 1,'short_name' : 1,'_id':0})			
			place['category'] = category			

			if 'bodyId' in place['halal']:
				halalbodies = db['halalbodies'].find_one({'_id':ObjectId(place['halal']['bodyId'])},{'_id':0,'name':1,'shortName':1,'country':1,'halalLogo':1})
				place['halal']['bodies'] = halalbodies

			places.append(place)
		
		jsonResponse = {'status' : True, 'minified' : minified, 'limit':limit, 'sort':sort, 'result': {'places' : places,'count':rawQueryResult.count()}}
		return jsonResponse, 200, {'Access-Control-Allow-Origin' : 'http://localhost'}

	def post(self):			
		args = parser.parse_args()

		foursquareId = args['foursquareId']
		lowerAddress = args['address'].lower().strip()
		lowerName = args['name'].lower().strip()

		if lowerAddress :
			existingPlace = db['places'].find(
				{ 
					'$or' : [
						{'source.id': foursquareId},
						{ 
							'$and' : [
								{'location.lowerAddress': lowerAddress},
								{'lowerName': lowerName}
							]
						},
					]
				})
		else :
			existingPlace = db['places'].find({'source.id':foursquareId})

		if existingPlace.count() > 0 :
			result = {
				'message' : 'Possible duplicate of places.',
				'place' : existingPlace,			
			}
			jsonResponse = {'status' : False, 'result':result}
			return jsonResponse, 403, {'Access-Control-Allow-Origin' : '*'}

		photoList = []
		photoUrlArray = []
		photosUrlString = args['photoUrls'].strip()
		if photosUrlString:
			photoUrlArray = photosUrlString.split(',')			
			for key in range(len(photoUrlArray)):
				photo = {
					"url" : photoUrlArray[key],
					"source" : "api.foursquare.com"
				}
				photoList.append(photo)

		tagString = args['tags']
		tagArray = tagString.split(',')
		for index,tag in enumerate(tagArray):
			tagArray[index] = tag.lower().strip()

		place = {
					"name" : args['name'],
					"lowerName" : lowerName,
					"location" : {
						"geocode" : {
							"type" : "Point",
							"coordinates" : [args['lng'], args['lat']]
						},
						"address" : args['address'],
						"lowerAddress" : lowerAddress,
						"city" : args['city'],
						"lowerCity" : args['city'].lower().strip(),
						"country" : args['country'],
						"lowerCountry" : args['country'].lower().strip(),
						"cc" : args['cc'],
						"zipCode" : args['zipCode']
					},										
					"contact" : {
						"phone" : args['phone'],
						"email" : args['email'],
						"website" : args['website'],
						"twitter" : args['twitter'],
						"facebook" : args['facebook']
					},
					"categoryId" :	args['categoryId'],
					"tags" : tagArray,
					"photos" : photoList,
					"halal" : {
						"type" : args['halalType'],
						"displayValue" : args['halalDisplayValue'],
						"description" : "",
						"bodyId" : args['bodyId']
					},
					"source" : {
						"type" : 1,
						"name" : "Foursquare API",
						"id" : args["foursquareId"],
						"link" : "api.foursquare.com"
					},
					"dateLastUpdated" : str(datetime.now())
				}
		objectId = db['places'].insert(place)
		jsonResponse = {'status' : True, 'result':objectId, 'photo':{'sent':photosUrlString,'array':photoUrlArray,'size':len(photoUrlArray),'list':photoList}}
		
		return jsonResponse, 200, {'Access-Control-Allow-Origin' : '*'}


class PlaceAPI(Resource):	

	def __init__(self):		
		super(PlaceAPI, self).__init__()


	def get(self, place_id):
		queryResult = db.places.find_one({'_id':ObjectId(place_id)})

		categoryId = queryResult['categoryId']
		category = db['categories'].find_one({'_id':ObjectId(categoryId)},{'name' : 1,'short_name' : 1, '_id':0})
		queryResult['category'] = category		

		if 'bodyId' in queryResult['halal']:
			halalbodies = db['halalbodies'].find_one({'_id':ObjectId(queryResult['halal']['bodyId'])},{'_id':0})
			queryResult['halal']['bodies'] = halalbodies

		jsonResult = {'status':True, 'result': {'place' : queryResult}}
		
		return jsonResult

	def delete(self, place_id):
		db['places'].remove({'_id':ObjectId(place_id)})
		jsonResponse = {'status':True, 'result': {'message':"Place has been deleted."}}

		return jsonResponse

	def put(self, place_id):
		args = parser.parse_args()

		tagString = args['tags']
		tagArray = tagString.split(',')

		photosUrlString = args['photoUrls']
		photoUrlArray = photosUrlString.split(',')

		photoList = []

		for key in range(len(photoUrlArray)):
			photo = {
				"url" : photoUrlArray[key],
				"source" : "api.foursquare.com"
			}
			photoList.append(photo)

		place = {
					"name" : args['name'],
					"lowerName" : args['name'].lower().strip(),
					"location" : {
						"geocode" : {
							"type" : "Point",
							"coordinates" : [args['lng'], args['lat']]
						},
						"address" : args['address'],
						"lowerAddress" : args['address'].lower().strip(),
						"city" : args['city'],
						"lowerCity" : args['city'].lower().strip(),
						"country" : args['country'],
						"lowerCountry" : args['country'].lower().strip(),
						"cc" : args['cc'],
						"zipCode" : args['zipCode']
					},										
					"contact" : {
						"phone" : args['phone'],
						"email" : args['email'],
						"website" : args['website'],
						"twitter" : args['twitter'],
						"facebook" : args['facebook']
					},
					"categoryId" :	args['categoryId'],
					"tags" : tagArray,
					"photos" : photoList,
					"halal" : {
						"type" : args['halalType'],
						"displayValue" : args['halalDisplayValue'],
						"description" : "",
						"bodyId" : args['bodyId']
					},
					"source" : {
						"type" : 1,
						"name" : "Foursquare API",
						"id" : args["foursquareId"],
						"link" : "api.foursquare.com"
					},
					"dateLastUpdated" : str(datetime.now())
				}

		db['places'].update({'_id':ObjectId(place_id)}, place, False)
		jsonResponse = {'status':True, 'result' : {'message':'Place has been updated.'}}
		return jsonResponse
