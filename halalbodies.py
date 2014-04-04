from flask import Blueprint
from flask.ext.restful import reqparse, Resource
from bson.objectid import ObjectId
from datetime import datetime
from dbconfig import db

halalbodies_api = Blueprint('halalbodies_api',__name__)

parser = reqparse.RequestParser()
parser.add_argument('name', type=str)
parser.add_argument('overview', type=str)
parser.add_argument('country', type=str)
parser.add_argument('halalLogo', type=str)
parser.add_argument('website', type=str)
parser.add_argument('phone', type=str)
parser.add_argument('fax', type=str)
parser.add_argument('pic', type=str)
parser.add_argument('email', type=str)
parser.add_argument('address', type=str)


class HalalBodiesAPI(Resource):

	def __init__(self):		
		super(HalalBodiesAPI, self).__init__()

	def get(self):
		bodies = db['halalbodies'].find({},{'dateLastUpdated':0}).sort('name', 1)
		return {'status':True, 'result': {'bodies' : bodies} }, 200, {'Access-Control-Allow-Origin' : '*'}

	def post(self):
		args = parser.parse_args()

		halalbodies = {
			'name' : args['name'],
			'overview' : args['overview'],
			'country' : args['country'],
			'halalLogo' : args['halalLogo'],
			'contact' : {
				'phone' : args['phone'],
				'fax' : args['fax'],
				'website' : args['website'],
				'email' : args['email'],
				'address' : args['address'],
				'pic' : args['pic']
			},
			'dateLastUpdated' : str(datetime.now())
		}

		objectId = db['halalbodies'].insert(halalbodies)
		jsonResponse = {'status':True, 'result': {'halalbodies' : objectId}}
		return jsonResponse, 200, {'Access-Control-Allow-Origin' : '*'}

	

class HalalBodyAPI(Resource):
	def __init__(self):		
		super(HalalBodyAPI, self).__init__()

	def put(self,bodies_id):
		args = parser.parse_args()

		halalbodies = {
			'name' : args['name'],
			'overview' : args['overview'],
			'country' : args['country'],
			'halalLogo' : args['halalLogo'],
			'contact' : {
				'phone' : args['phone'],
				'fax' : args['fax'],
				'website' : args['website'],
				'email' : args['email'],
				'address' : args['address'],
				'pic' : args['pic']
			},
			'dateLastUpdated' : str(datetime.now())
		}

		result = db['halalbodies'].update({'_id':ObjectId(bodies_id)},halalbodies,False, False)
		jsonResponse = {'status':True, 'result' : {'halalbodies' : result}}
		return jsonResponse, 200, {'Access-Control-Allow-Origin' : '*'}

	def delete(self, bodies_id):
		db['halalbodies'].remove({'_id':ObjectId(bodies_id)})
		jsonResponse = {'status' : True, 'message' : "Halal Bodies has been deleted."}
		return jsonResponse, 200, {'Access-Control-Allow-Origin' : '*'}

