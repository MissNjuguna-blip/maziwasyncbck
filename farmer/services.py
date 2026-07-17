import json
import os
from groq import Groq
import joblib
from dotenv import load_dotenv

class CattleAIService:
    def __init__(self):
        # constructor that will load the ML file and initialize grow AI engine
        base_dir = os.path.abspath(__file__)
        # read keys inside local .env config file into memory
        load_dotenv()
        # oading our trained model
        self.model = joblib.load(os.path.join(base_dir,'cattle_disease_model.pkl'))

        # load the features/x/inputs
        self.model = joblib.load(os.path.join(base_dir,'model_faetures.pkl'))

        # extract sympofrom the model_faetures path
        self.valid_symptoms = [
            f for f in self.model_features
            if f not in ['Age','Temperature'] and not f.startwith('Animal')
        ]
        # set up and authenticate the groq cloud collection
        self.groq_client=Groq(api_key=os.environ.get('GROQ_API_KEY'))

        # method to extract the farmer conversation and structure symptoms
        def extract_symptoms_with_groq(self,farmer_text):
            # command groq to force responsee strictly with valid symptoms in json format
            system_prompt = f"""
                You are a veterinary assistant. Analyse the text and extract symptoms matching exactly this list:
                {self.valid_symptoms}
                Respond with a JSON object:{{"symptoms:["symptom_name"]}}
                """
            
            try:
                # request processing from the LLM model
                completion = self.groq_client.chat.completions.create(
                    messages = [
                        {"role":"system","content":system_prompt},
                        {"role":"user","content":f"Farmer text: \"{farmer_text}\""}
                    ],
                    model = "llama-3.3-8b-instant",
                    temperature = 0.0,
                    response_format = {"type":"json_object"}
                )
                response_text = completion.choices[0].message.content.strip()
                result_json = json.loads(response_text)
                return result_json.get('symptoms',[])
            except Exception as e:
                print(f"Groq Extration Error",{e})

    def get_treatment_recommendation (self,disease,animal_type):
        # query the groq LLM to generate anstant medical advice and emergency instruction
        system_prompt = ("""
             You are an expert in live stock veterinan. provide clear,professional treatment recommendations under 120 words using short bullets points. 
            include  a vet disclaimer
             """)
        
        try:
             # request processing from the LLM model
                completion = self.groq_client.chat.completions.create(
                    messages = [
                        {"role":"system","content":system_prompt},
                        {"role":"user","content":f"Treatment recommendation for a {animal_type} with {disease}"}
                    ],
                    model = "llama-3.3-8b-instant",
                    temperature = 0.3, #higher values allows AI to be more creative                    
                )
                return completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"Groq treatment Error{e}")
            return "Treatment temporary"
    
    # predict method
    def predict (self,animal_type,age,temp,description):
        #  use the LLM extraction utility to filter symptoms out of the incoming text string
        extracted_symptoms = self.extract_symptoms_with_groq(description)

        # build a baseline dictionary mapping all training features name to zero values
        input_data = {feature:0 for feature in self.model}

        # map raw numeric inputs to their respective matching feature keys
        input_data['Age'] = age
        input_data['Temperature'] = temp
        
        # convert animal string into one columns key format name string 'Animal_cow'
        animal_key = f"Animal_{str(animal_type).strip().lower()}"
        if animal_key in input_data:
            input_data[animal_key]=1

        for symptom in extracted_symptoms:
            if symptom in input_data:
                input_data[symptom] = 1
                # flatten the dict into ordered list matching the exact index setup model expects
                final_input_vector = [input_data[feature] for feature in self.model_features]
                
                # predicting using model providing it with theorderd feattre/x/input
                prediction = self.model.prediction([final_input_vector])
                predicted_disease = prediction[0]

                treatment_plan = self.get_treatment_recommendation(predicted_disease,animal_type)

                # return consolidated final pipeline payload output directly back to DRF response
                return {
                    "status":"success",
                    "extracted_symptoms_by_ai":extracted_symptoms,
                    "predicted_disease":predicted_disease,
                    "treatment_recommendation":treatment_plan
                }