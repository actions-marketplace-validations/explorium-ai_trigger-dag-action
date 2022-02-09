# Trigger Airflow (GCP) Dag Docker Action

This action takes a python pacakage and passes it as a parameter to trigger an Airflow (Composer GCP) DAG
## Inputs

```yaml
  entity_client_version:
    description: 'entity client version'
    required: true
    default: 'latest'
  dag_run_id:
    description: 'custom dag run id'
    required: true
    default: ''
  client_id:
    description: 'gcp client id'
    required: true
    default: ''
  compare_threshold:
    description: 'compare threshold'
    required: true
    default: ''
  send_slack_on_errors:
    description: 'send slack on errors'
    required: false
    default: 'true'
  webserver_id:
    description: 'webserver id'
    required: true
    default: ''         
  run_type:
    description: 'run type'
    required: true
    default: ''     
  dag_name:
    description: 'dag name'
    required: true
    default: ''
  google_application_credentials: 
    description: 'location of gcp credentials'
    required: true
    default: './gcp_creds.json'
```

## Outputs

## `result`

The result of the DAG

## Example usage

```yaml
uses: explorium-ai/trigger-dag-action@v1
with:
  dag_run_id: something
  client_id: something
  webserver_id: something
  dag_name: something
  google_application_credentials: something
  payload: '{"config":"something"}'
```
