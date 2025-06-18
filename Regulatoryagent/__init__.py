
import os
from openai import AzureOpenAI
import azure.functions as func
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

endpoint = os.getenv("ENDPOINT_URL", "https://ai-hubchaapaidev027880339867.openai.azure.com/")
deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4o")

# Initialize Azure OpenAI client with Entra ID authentication
cognitiveServicesResource = os.getenv('AZURE_COGNITIVE_SERVICES_RESOURCE', 'YOUR_COGNITIVE_SERVICES_RESOURCE')
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    f'{cognitiveServicesResource}.default'
)
# token_provider = get_bearer_token_provider(
#     DefaultAzureCredential()
# )

client = AzureOpenAI(
    azure_endpoint=endpoint,
    # azure_ad_token_provider=token_provider,
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    api_version='2024-05-01-preview'
)
def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        user_message = req_body.get("message")

        if not user_message:
            return func.HttpResponse("Missing 'message' in request body.", status_code=400)
        
        system_prompt = os.environ["SYSTEM_PROMPT"]

        completion = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=800,
            temperature=0.7,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            extra_body={
                "data_sources": [
                    {
                        "type": "azure_search",
                        "parameters": {
                            "endpoint": os.environ["AZURE_AI_SEARCH_ENDPOINT"],
                            "index_name": os.environ["AZURE_AI_SEARCH_INDEX"],
                            "authentication": {
                                "type": "api_key",
                                "key": os.environ["AZURE_AI_SEARCH_SERVICE_KEY"]
                            
                            }
                        }
                    }
                ]
            }
        )

        result_json = completion.model_dump_json(indent=2)
        return func.HttpResponse(result_json, mimetype="application/json", status_code=200)

    except ValueError:
        return func.HttpResponse("Invalid JSON in request body.", status_code=400)
    except Exception as e:
        return func.HttpResponse(f"Internal Server Error: {str(e)}", status_code=500)