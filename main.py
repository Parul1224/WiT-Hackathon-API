from cloudant.client import Cloudant
from flask import Flask, render_template, request, jsonify
import atexit
import os
import json
import math 

app = Flask(__name__, static_url_path='')
client = None
serviceProviderdb = None
foodDb = None
medicineDb = None
shelterDb = None
clothesDb = None


#-----------------------------------------------*Creating db instances*---------------------------------------------------------                
#------------------------------------------------------------------------------------------------------------------------------


def create_db_instances(client):
    serviceProviderDb = client.create_database('providers', throw_on_exists=False)
    foodDb = client.create_database('fooddb', throw_on_exists=False)
    medicineDb = client.create_database('medicinedb', throw_on_exists=False)
    shelterDb = client.create_database('shelterdb', throw_on_exists=False)
    clothesDb = client.create_database('clothesdb', throw_on_exists=False)


#-----------------------------------------------*Configuring cloud in local*--------------------------------------------------                      
#-----------------------------------------------------------------------------------------------------------------------------
 
 
if 'VCAP_SERVICES' in os.environ:
    vcap = json.loads(os.getenv('VCAP_SERVICES'))
    print('Found VCAP_SERVICES')
    if 'cloudantNoSQLDB' in vcap:
        creds = vcap['cloudantNoSQLDB'][0]['credentials']
        user = creds['username']
        password = creds['password']
        url = 'https://' + creds['host']
        client = Cloudant(user, password, url=url, connect=True)
        db = client.create_database(db_name, throw_on_exists=False)
elif "CLOUDANT_URL" in os.environ:
    client = Cloudant(os.environ['CLOUDANT_USERNAME'], os.environ['CLOUDANT_PASSWORD'], url=os.environ['CLOUDANT_URL'], connect=True)
    db = client.create_database(db_name, throw_on_exists=False)
elif os.path.isfile('vcap-local.json'):
    with open('vcap-local.json') as f:
        vcap = json.load(f)
        print('Found local VCAP_SERVICES')
        creds = vcap['services']['cloudantNoSQLDB'][0]['credentials']
        user = creds['username']
        password = creds['password']
        url = 'https://' + creds['host']
        client = Cloudant(user, password, url=url, connect=True)
        serviceProviderDb = client.create_database('providers', throw_on_exists=False)
        foodDb = client.create_database('fooddb', throw_on_exists=False)
        medicineDb = client.create_database('medicinedb', throw_on_exists=False)
        shelterDb = client.create_database('shelterdb', throw_on_exists=False)
        clothesDb = client.create_database('clothesdb', throw_on_exists=False)
            


# On IBM Cloud Cloud Foundry, get the port number from the environment variable PORT
# When running this app on the local machine, default the port to 8000
port = int(os.getenv('PORT', 8000))



@app.route('/')
def root():
    return app.send_static_file('index.html')

#-----------------------------------------------*Service Provider Registration*-------------------------------------------                       
#-------------------------------------------------------------------------------------------------------------------------


@app.route('/signUp', methods=['POST'])
def add_serviceProvider():
    try:
        data=request.get_json(force=True)
        name = data['name']
        email = data['email']
        phone = data['phone']
        address = data['address']
        latitude = data['latitude']
        longitude = data['longitude']
        serviceDonated = data['services']

    except KeyError as e:
        #for dispalying in postman
        msg='You have got a KeyError - reason "%s"' % str(e)
        
    if client:
        my_document = serviceProviderDb.create_document(data)
        data['_id'] = my_document['_id']
        populate_services(my_document)
        return jsonify(data)
    else:
        print('No database found for the service provider')
        return jsonify(data)    


#-----------------------------------------------*View All Service Providers*----------------------------------------------                      
#-------------------------------------------------------------------------------------------------------------------------        


@app.route('/api/visitors', methods=['GET'])
def get_visitor():
    if client:
        return jsonify(list(map(lambda doc: doc['name'], serviceProviderDb)))
    else:
        print('No database found for Owner details')
        return jsonify([])


#-----------------------------------------------*Populating Service Providers with it's corresponding services*---------------                  
#-----------------------------------------------------------------------------------------------------------------------------


def populate_services(my_document):
    serviceDonated = my_document['services']
    
    # Paramters
    latitude = my_document['latitude']
    longitude = my_document['longitude']
    address = my_document['address']
    phone = my_document['phone']
    _id = my_document['_id']
    name = my_document['name']

    for i in serviceDonated : 
        if(i=='food'):
            foodDb.create_document({
              '_id': _id,
              'name': name,
              'address': address,
              'phone': phone,
              'latitude': latitude,
              'longitude': longitude
            })
            
        elif(i=='clothes'):
            clothesDb.create_document({
              '_id': _id,
              'name': name,
              'address': address,
              'phone': phone,
              'latitude': latitude,
              'longitude': longitude
            })
            
        elif(i=='shelter'):
            shelterDb.create_document({
              '_id': _id,
              'name': name,
              'address': address,
              'phone': phone,
              'latitude': latitude,
              'longitude': longitude
            })

        elif(i=='medicine'):
            medicineDb.create_document({
              '_id': _id,
              'name': name,
              'address': address,
              'phone': phone,
              'latitude': latitude,
              'longitude': longitude
            })
            

#-----------------------------------------------*Checking nearby food providers*--------------------------------------------------------                 
#---------------------------------------------------------------------------------------------------------------------------------------


@app.route('/register/food', methods=['POST'])
def register_for_food():
    data=request.get_json(force=True)
    latitude = data['latitude']
    longitude = data['longitude']

    topFoodProviderMap = calculateGaussianDistance(foodDb,latitude,longitude)
    
    if not topFoodProviderMap:
        return jsonify({"message":"Currently You don't have nearby food providers"}) 

    topFoodProviders = {}
    topFoodProviders = sort_dictionaryWithNearestProviders(topFoodProviderMap) 
    print(topFoodProviders) 

    payload = jsonifyPayload(foodDb,topFoodProviders)
    return payload

#-----------------------------------------------*Checking nearby shelter providers*--------------------------------------------------------                 
#------------------------------------------------------------------------------------------------------------------------------------------


@app.route('/register/shelter', methods=['POST'])
def register_for_shelter():
    data=request.get_json(force=True)
    latitude = data['latitude']
    longitude = data['longitude']

    topShelterProviderMap = calculateGaussianDistance(shelterDb,latitude,longitude)

    if not topShelterProviderMap :
        return jsonify({"message":"Currently You don't have nearby Selter and lodging providers "}) 

    topShelterProviders = {}
    topShelterProviders = sort_dictionaryWithNearestProviders(topShelterProviderMap) 
    print(topShelterProviders) 

    payload = jsonifyPayload(shelterDb,topShelterProviders)
    return payload  




#-----------------------------------------------*Checking nearby cloth providers*--------------------------------------------------------                 
#----------------------------------------------------------------------------------------------------------------------------------------

@app.route('/register/cloth', methods=['POST'])
def register_for_cloth():
    data=request.get_json(force=True)
    latitude = data['latitude']
    longitude = data['longitude']

    topClothProviderMap = calculateGaussianDistance(clothesDb,latitude,longitude)
    
    if not topClothProviderMap :
        return jsonify({"message":"Currently You don't have nearby Cloth providers "}) 

    topClothProviders = {}
    topClothProviders = sort_dictionaryWithNearestProviders(topClothProviderMap) 
    print(topClothProviders) 

    payload = jsonifyPayload(clothesDb,topClothProviders)
    return payload      
    



#-----------------------------------------------*Checking nearby medicine providers*--------------------------------------------------------                 
#---------------------------------------------------------------------------------------------------------------------------------------


@app.route('/register/medicine', methods=['POST'])
def register_for_medicine():
    data=request.get_json(force=True)
    latitude = data['latitude']
    longitude = data['longitude']

    topMedicineProviderMap = calculateGaussianDistance(medicineDb,latitude,longitude)
    print(topMedicineProviderMap)

    if not topMedicineProviderMap :
        return jsonify({"message":"Currently You don't have nearby Medicine providers "})

    topMedicineProviders = {}
    topMedicineProviders = sort_dictionaryWithNearestProviders(topMedicineProviderMap) 
    print(topMedicineProviders) 

    payload = jsonifyPayload(medicineDb,topMedicineProviders)
    return payload  
 
    
#-----------------------------------------------*Checking Gaussian distance*--------------------------------------------------------                 
#---------------------------------------------------------------------------------------------------------------------------------------

def calculateGaussianDistance(object, latitude,longitude):
    nearbyServiceProviderMap = {}
    # Get all of the documents from food databse
    for document in object:
        serviceProviderLatitude = document['latitude']
        serviceProviderLongitude = document['longitude']
        latitudeDff = serviceProviderLatitude - latitude
        longitudeDiff = serviceProviderLongitude - longitude
        distance = math.sqrt((latitudeDff *latitudeDff) + (longitudeDiff*longitudeDiff))
        

        # We have set 5kms as benchmark
        if(distance <= 5):
            nearbyServiceProviderMap[document['_id']]=distance
        
    return nearbyServiceProviderMap       


#-----------------------------------------------*********************************--------------------------------------------------------                 
#---------------------------------------------------------------------------------------------------------------------------------------



def sort_dictionaryWithNearestProviders(dictionary):
    sort_orders = sorted(dictionary.items(), key=lambda x: x[1]) 
    return sort_orders

def jsonifyPayload(object,dictionary): 
    content = {}
    payload = []
    count = 0
    for item in dictionary: 
        if(count==5):
            break
        content = {''}     
        content = {'ServiceProvider': object[item[0]]['name'], 'address': object[item[0]]['address'] , 'phone': object[item[0]]['phone'],  'distance': item[1]}
        payload.append(content)
        content = {}
        count=count+1

    return jsonify(payload)



@atexit.register
def shutdown():
    if client:
        client.disconnect()
        
@app.route('/ping',methods=['GET'])
def ping():
    return jsonify(ping='pong')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
