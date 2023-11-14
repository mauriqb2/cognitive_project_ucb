import os
import requests
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk
from azure.ai.textanalytics import (
    TextAnalyticsClient,
    ExtractiveSummaryAction
)
from azure.ai.contentsafety import ContentSafetyClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.contentsafety.models import AnalyzeTextOptions

load_dotenv('env.txt')

def authenticate_clients():
    text_analytics_client = TextAnalyticsClient(
        endpoint=os.getenv("LANGUAGE_ENDPOINT"),
        credential=AzureKeyCredential(os.getenv("LANGUAGE_KEY"))
    )
    content_safety_client = ContentSafetyClient(
        endpoint=os.getenv("CONTENT_SAFETY_ENDPOINT"),
        credential=AzureKeyCredential(os.getenv("CONTENT_SAFETY_KEY"))
    )
    speech_config = speechsdk.SpeechConfig(
        subscription=os.getenv("SPEECH_KEY"),
        region=os.getenv("SPEECH_REGION")
    )
    speech_config.speech_synthesis_voice_name = 'es-BO-MarceloNeural'
    
    return text_analytics_client, content_safety_client, speech_config

def get_information_about_public_figure(api_key, figure_name):
    api_endpoint = os.getenv("API_GOOGLE_ENDPOINT")
    params = {
        'query': figure_name,
        'limit': 1,
        'indent': True,
        'key': api_key,
        'languages': 'es'
    }

    response = requests.get(api_endpoint, params=params)
    response_data = response.json()

    if response_data.get("itemListElement") and len(response_data["itemListElement"]) > 0:
        search_result = response_data["itemListElement"][0].get("result", {})
        description = search_result.get("detailedDescription", {}).get("articleBody")
        if description:
            return description.strip()
    return None

def detect_offensive_content(content_safety_client ,text_input: str):    
    request = AnalyzeTextOptions(text=text_input)
    
    try:
        response = content_safety_client.analyze_text(request)
        if response.hate_result and response.hate_result.severity != 0:
            return True
        if response.self_harm_result and response.self_harm_result.severity != 0:
            return True
        if response.sexual_result and response.sexual_result.severity != 0:
            return True
        if response.violence_result and response.violence_result.severity != 0:
            return True
        return False
    except HttpResponseError as e:
        print("Analyze text failed.")
        if e.error:
            print(f"Error code: {e.error.code}")
            print(f"Error message: {e.error.message}")
        raise


def synthesize_speech(speech_config, text):
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
    speech_synthesis_result = synthesizer.speak_text_async(text).get()
    handle_speech_synthesis_result(speech_synthesis_result)

def handle_speech_synthesis_result(speech_synthesis_result):
    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized successfully.")
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
            print("Did you set the speech resource key and region values?")

def get_speech_recognition_result(speech_config):
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, language="es-ES")

    print("Hable ahora...")
    result = speech_recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print(f"Reconocido: {result.text}")
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No se reconoció el discurso correctamente.")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation = result.cancellation_details
        print(f"Reconocimiento cancelado: {cancellation.reason}")
        if cancellation.reason == speechsdk.CancellationReason.Error:
            print(f"Detalles del error: {cancellation.error_details}")
    return None

def find_figure_name_in_text(client, text):
    try:
        result = client.recognize_entities(documents=[text])[0]
        for entity in result.entities:
            if entity.category == 'Person':
                return entity.text
        return None
    except Exception as err:
        print("Encountered exception. {}".format(err))
        return None
    
def get_summarized_text(client, document):
    actions = [ExtractiveSummaryAction(max_sentence_count=4)]
    poller = client.begin_analyze_actions(
        documents=[{"id": "1", "text": document, "language": "es"}],
        actions=actions,
    )

    print("Texto original:", document)

    result = poller.result()

    for doc in result:
        for action_result in doc:
            if action_result.is_error:
                print("Error:", action_result.error)
            else:
                for sentence in action_result.sentences:
                    print("Resumen:", sentence.text)
                    return sentence.text
    return "No se encontró un resumen adecuado."

def main():
    text_analytics_client, content_safety_client, speech_config = authenticate_clients()

    spoken_text = get_speech_recognition_result(speech_config)
    if not spoken_text:
        print("No se pudo reconocer el discurso correctamente.")
        return

    if "Alessandro" not in spoken_text:
        synthesize_speech(speech_config, "Por favor, comienza tu pregunta con 'Alessandro' seguido de la figura pública de tu interés.")
        return

    is_offensive = detect_offensive_content(content_safety_client, spoken_text)
    if is_offensive:
        synthesize_speech(speech_config, "Lo siento, no puedo ayudarte porque he detectado contenido ofensivo en tu pregunta.")
        return

    figure_name = find_figure_name_in_text(text_analytics_client, spoken_text.replace("Alessandro", ""))
    if not figure_name:
        synthesize_speech(speech_config, "Lo siento, soy un asistente únicamente orientado a darte información sobre figuras públicas.")
        return

    information = get_information_about_public_figure(os.getenv("API_GOOGLE_KEY"), figure_name)
    if not information:
        synthesize_speech(speech_config, f"Lo siento, no puedo ayudarte porque no tengo información sobre {figure_name}.")
        return
    
    response_text = get_summarized_text(text_analytics_client, information)
    if not response_text:
        response_text = information

    synthesize_speech(speech_config, response_text)

if __name__ == "__main__":
    main()