from flask import Blueprint
from flask.ext.restful import reqparse, Resource
from bson.objectid import ObjectId
from pymongo import Connection
from datetime import datetime
from dbconfig import db

categories_api = Blueprint('categories_api',__name__)

parser = reqparse.RequestParser()

class CategoriesAPI(Resource):
	def __init__(self):
		parser.add_argument('name', type=str)
		parser.add_argument('short_name', type=str)
		parser.add_argument('foursquare_id', type=str)
		parser.add_argument('icon_url', type=str)
		super(CategoriesAPI, self).__init__()

	def post(self):
		args = parser.parse_args();
		category = {
			"name" : args['name'],
			"short_name" : args['short_name'],
			"icon_url" : args['icon_url'],
			"foursquare_id" : args['foursquare_id'],
			"date_last_updated" : str(datetime.now())
		}

		objectId = db['categories'].insert(category)
		jsonResponse = {'status':True, 'result': {'category' : objectId}}
		return jsonResponse, 200, {'Access-Control-Allow-Origin' : '*'}

	def get(self):
		categories = db['categories'].find({},{'date_last_updated':0}).sort('name', 1)
		return {'status':True, 'result': {'categories' : categories} }

class CategoryAPI(Resource):

	def __init__(self):
		parser.add_argument('name', type=str)
		parser.add_argument('short_name', type=str)
		parser.add_argument('foursquare_id', type=str)
		parser.add_argument('icon_url', type=str)
		super(CategoryAPI, self).__init__()
	
	def delete(self, category_id):
		db['categories'].remove({'_id':ObjectId(category_id)})
		jsonResponse = {'status' : True, 'message' : "Category has been deleted."}

		return jsonResponse, 200, {'Access-Control-Allow-Origin' : '*'}

	def put(self, category_id):
		args = parser.parse_args()

		category = {
			"name" : args['name'],
			"short_name" : args['short_name'],
			"icon_url" : "https://ss1.4sqi.net/img/categories_v2/food/default_bg_32-ed3a94563906ecfc0e8200f889bb7b3e.png",
			"foursquare_id" : args['foursquare_id'],
			"date_last_updated" : str(datetime.now())
		}

		result = db['categories'].update({'_id':ObjectId(category_id)}, category, False)
		jsonResponse = {'status':True, 'result' : {'category' : result}}

		return jsonResponse, 200, {'Access-Control-Allow-Origin' : '*'}