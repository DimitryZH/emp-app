"Database layer - the datastore version"
import uuid
from google.cloud import datastore
import config

def get_client():
    return datastore.Client(project=config.GCP_PROJECT)

def list_employees():
    "Select all the employees from the database"
    try:
        client = get_client()
        query = client.query(kind='Employee')
        results = list(query.fetch())
        employees = []
        for entity in results:
            employee = dict(entity)
            employee['id'] = entity.key.name
            employees.append(employee)
        return employees
    except:
        return 0

def load_employee(employee_id):
    "Select one the employee from the database"
    try:
        client = get_client()
        key = client.key('Employee', employee_id)
        entity = client.get(key)
        if entity:
            employee = dict(entity)
            employee['id'] = entity.key.name
            return employee
        return None
    except:
        pass

def add_employee(object_key, full_name, location, job_title, badges):
    "Add an employee to the database"
    try:
        client = get_client()
        employee_id = str(uuid.uuid4())
        key = client.key('Employee', employee_id)
        entity = datastore.Entity(key=key)
        
        entity.update({
            'full_name': full_name,
            'job_title': job_title,
            'location': location
        })
        
        if object_key:
            entity['object_key'] = object_key
        if badges:
            entity['badges'] = badges.split(',')
            
        client.put(entity)
    except:
        pass

def update_employee(employee_id, object_key, full_name, location, job_title, badges):
    "Update an employee to the database"
    try:
        client = get_client()
        key = client.key('Employee', employee_id)
        entity = client.get(key)
        
        if entity:
            entity.update({
                'full_name': full_name,
                'job_title': job_title,
                'location': location
            })
            
            if object_key:
                entity['object_key'] = object_key
            if badges:
                entity['badges'] = badges.split(',')
            elif 'badges' in entity:
                del entity['badges']
                
            client.put(entity)
    except:
        pass

def delete_employee(employee_id):
    "Delete an employee."
    try:
        client = get_client()
        key = client.key('Employee', employee_id)
        client.delete(key)
    except:
        pass