from openai import OpenAI
import utils
import time, json
import os
import config
#Shall replace the API key from the envirnment variable, currently hard coding

client = OpenAI(api_key=config.OPENAI_API_KEY)

print("Running Assistant...")
print("Creating new thread ...")

## Each time we run the code, it shall create a new thread. i.e new conversation
## The assistant Id is hardcoded since we'll be using same assistant for responses
thread = client.beta.threads.create()
assistant_id = config.ASSISTANT_ID

user_query = ''
print("------Conversation Started------\n\n")
print("Youtube: D DOT PY")
while True:

  ### Get User input
  user_query = input("\n\nGPT: ")
  if user_query == 'exit':
    break

  #Add the user input as message to the thread
  message = client.beta.threads.messages.create(thread_id=thread.id,
                                                role="user",
                                                content=user_query)

  ### Now create a run with the above thread_id & assistant ID,
  ### The run will generate response for the latest added message i.e the user's iunput
  run = client.beta.threads.runs.create(thread_id=thread.id,
                                        assistant_id=assistant_id)

  while True:
    time.sleep(1)
    run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    print("\rRun_status: ", run.status, " " * 12, end='')
    if run.status == 'completed':
      messages_ = client.beta.threads.messages.list(thread_id=thread.id)
      response = messages_.data[0].content[0].text.value
      print("\nAssistant: " + response)
      break

    if run.status == 'requires_action':
      # print("\nAssistant: " + run.action.instructions)

      tools_list = run.required_action.submit_tool_outputs.tool_calls
      tools_responses = []
      for i in tools_list:
        if i.function.name == 'list_actions':
          print("\rRun_status: calling ", i.function.name, " " * 10, end='')
          list_of_available_actions = utils.get_list_of_available_actions_in_zapier(
          )
          tools_responses.append({
              "tool_call_id": i.id,
              "output": str(list_of_available_actions)
          })

        elif i.function.name == 'perform_action':
          print("\rRun_status: calling ", i.function.name, " " * 12, end='')
          arguments = json.loads(i.function.arguments)
          print("instructions: ",
                arguments.get('instructions', 'No instructions provided'))
          performed_action_status_details = utils.perform_action(
              arguments.get('action_id', ''),
              arguments.get('instructions', ''))
          tools_responses.append({
              "tool_call_id": i.id,
              "output": str(performed_action_status_details)
          })


      # Submit tool outputs
      run = client.beta.threads.runs.submit_tool_outputs(
          thread_id=thread.id, run_id=run.id, tool_outputs=tools_responses)
