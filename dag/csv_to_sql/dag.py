import csv
import logging
import os.path

import airflow.models
import pendulum
from airflow import Dataset, DAG
from airflow.decorators import task

from example_client.client import Client, SampleRequest, SampleCollectionResponse

CUR_DIR = os.path.dirname(__file__)

with DAG(
        start_date=pendulum.now(),
        dag_id="csv_to_sql",
        template_searchpath=CUR_DIR):
    source_csv = Dataset(os.path.join(CUR_DIR, 'source.csv'))


    @task(task_id="extract_csv")
    def extract_csv(src: Dataset, **context):
        logging.info(f'uri: {src.uri}')
        with open(os.path.join(CUR_DIR, src.uri)) as f:
            reader = csv.DictReader(f)
            results = []
            for o in reader:
                results.append(o)
        return results


    @task(task_id="generate_sql",
          templates_dict={
              'select_query': 'sql/select.sql'
          }, templates_exts=['.sql', '.jinja2'])
    def generate_sql(templates_dict=None, **context):
        """This task does nothing but renders output from a given template above"""
        return templates_dict['select_query']


    @task(task_id="retrieve_from_rest_api")
    def retrieve_from_rest_api():
        # we can retrieve from variables
        # variables can be set from UI: http://localhost:8080/variable/list/
        username = airflow.models.Variable.get('creds_username', '')
        password = airflow.models.Variable.get('creds_password', '')
        c = Client(username=username, password=password)
        r = c.login()
        logging.info(f'status_code: {r.status_code}')
        request = SampleRequest(status=True)
        # basically do something return a json object
        response = c.do_something(request)
        # if we return serializable object, we can call it in other tasks via ti.xcom_pull
        return response.dict


    @task(task_id="transform_to_update_query")
    def transform_to_update_query(ti: airflow.models.TaskInstance = None):
        """Demonstrate how to transform data to easily render it in template for the next task"""
        input_dict = ti.xcom_pull('retrieve_from_rest_api')
        input_task = SampleCollectionResponse(**input_dict)
        result = []
        for v in input_task.result:
            obj_dict = v.dict
            obj_dict['new_name'] = f'new {v.name}'
            result.append(obj_dict)
        # we pass only the arrays of dict
        return result


    @task(task_id="update_query",
          templates_dict={
              'update_query': 'sql/update.sql'
          }, templates_exts=['.sql', '.jinja2'])
    def update_query(templates_dict=None, **context):
        """Demonstrate dumping template renders into files"""
        with open(os.path.join(CUR_DIR, 'output/update.gen.sql'), 'w') as f:
            f.write(templates_dict['update_query'])
        return True


    @task(task_id="generate_csv")
    def generate_csv(ti: airflow.models.TaskInstance = None):
        """Demonstrate dumping data into csv"""
        input_dict = ti.xcom_pull('retrieve_from_rest_api')
        input_task = SampleCollectionResponse(**input_dict)
        headers = input_task.result[0].dict.keys()
        with open(os.path.join(CUR_DIR, 'output/result.csv'), 'w') as f:
            writer = csv.DictWriter(f, headers)
            writer.writeheader()
            writer.writerows([v.dict for v in input_task.result])
        return True


    t1 = extract_csv(source_csv)
    t2 = transform_to_update_query()
    t2 >> update_query()
    t1 >> generate_sql() >> retrieve_from_rest_api() >> [t2, generate_csv()]
