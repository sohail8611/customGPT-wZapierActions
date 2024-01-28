### Zapier Integration

import requests, json, os
import config
## This api key must be moved to secrets of os from there we'll read it. Currently keeping it here for testing purpose.
ZAPIER_API_KEY = config.ZAPIER_API_KEY


def get_list_of_available_actions_in_zapier():
  req_url = "https://actions.zapier.com/api/v1/exposed/"
  headers_list = {
      "Accept": "*/*",
      "User-Agent": "Thunder Client (https://www.thunderclient.com)",
      "x-api-key": ZAPIER_API_KEY
  }

  response = requests.get(req_url, headers=headers_list)

  if response.status_code == 200:
    available_actions_string = "The following are the actions you can perform:\n"
    data = response.json()

    for i in data['results']:
      required_params = ''
      for key in i['params']:
        if key != "instructions":
          required_params += f"{str(key)} : {str(i['params'][key])}\n"

      available_actions_string += f"\n\naction_id: {i['id']}\ndescription: {i['description']}\nThis action takes instruction string as input and the input must mention the following:\n{required_params}"
    return available_actions_string
  else:
    return {"error": "Request failed", "status_code": response.status_code}


def perform_action(id, instructions):
  # Define the URL
  req_url = f"https://actions.zapier.com/api/v1/exposed/{id}/execute/"

  # Set the headers
  headers_list = {
      "Accept": "*/*",
      "User-Agent": "Python Requests",
      "x-api-key": ZAPIER_API_KEY,
      "Content-Type": "application/json"
  }

  # Create the payload
  payload = json.dumps({"instructions": instructions})

  # Send the POST request
  response = requests.post(req_url, data=payload, headers=headers_list)

  res = response.json()

  performed_action_details = "After calling this action the following details were returned:\n"
  try:
    if res['status'] == 'error':
      performed_action_details += f"action_called: {res['action_used']}\nstatus: {res['status']}\nerror_message: {res['error']} "
      return performed_action_details

    elif res['status'] == 'success':

      performed_action_details = "The action was called successfully and the following details were returned:\n"
      performed_action_details += f"action_called: {res['action_used']}\nstatus: {res['status']}\ninput_parameters_used: {str(res['input_params'])}\nresult: {str(res['result'])}"
      return performed_action_details

  except Exception as e:
    if 'details' in res:
      performed_action_details += str(res['details'])
      return performed_action_details
    else:
      return "error: " + str(e)


###### Now create function for performing actions....

# Example usage
# data = get_list_of_available_actions_in_zapier()
# print(data)
