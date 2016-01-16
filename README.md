# HalalSpot Rest API

This repository contains Rest API for HalalSpot android application. API routing can be seen in rest.py.

There are several endpoint used by the application :

* /sharee/api/v1/places

To create, update and delete halal restaurants from database.

* /sharee/api/v1/places/id

To return single object of halal restaurants. Id is a number.

* /sharee/api/v1/places/nearby

To return nearby halal restaurants based on longitude and latitude given from the parameter. It is using geospatial query feature from MongoDB, $geoNear.

* etc
