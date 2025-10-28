import os
from configobj import ConfigObj
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from openai import OpenAI
from langchain_core.runnables import Runnable
from langchain_core.output_parsers import PydanticOutputParser

# Load environment variables from .env
load_dotenv()

class LLMManager:
    def __init__(self, config_path='config.ini'):
        self.config = self.load_config(config_path)
        # self.DEFAULT_FALLBACK_ORDER = ['lmstudio','ollama','openrouter', 'groq']
        self.orders = {
            "default": self.parse_order("default-order"),
            "offline": self.parse_order("offline-order"),
            "fast": self.parse_order("fast-order"),
        }
        self.DEFAULT_FALLBACK_ORDER = self.orders["default"]
        # self.DEFAULT_FALLBACK_ORDER = defaultcfg
        # self.DEFAULT_FALLBACK_ORDER = ['lmstudio','ollama']

    def parse_order(self, section):
        try:
            # ConfigObj already parses lists like order=['a','b']
            order = self.config[section]['order']
            if isinstance(order, str):
                # if written without [], split by comma
                order = [o.strip() for o in order.strip("[]").split(",")]
            return order
        except Exception as e:
            raise Exception(f"Could not parse order from [{section}]: {e}")
        
    def load_config(self, config_path):
        try:
            config = ConfigObj(config_path)
            if not config:
                raise ValueError("Config file is empty or not found")
            return config
        except Exception as e:
            raise Exception(f"Failed to load {config_path}: {e}")

    def setup_llm_with_fallback(self, fallback_order=None):
        if fallback_order is None:
            fallback_order = self.DEFAULT_FALLBACK_ORDER
        
        llm_instances = {}
        for source in fallback_order:
            try:
                cfg = self.config[f'llms_{source}']
                if source == 'openrouter':
                    api_key = os.getenv('OPENROUTER_API_KEY')
                    if not api_key:
                        raise ValueError("OPENROUTER_API_KEY not found")
                        
                    client = OpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=api_key,
                    )
                    llm_instances[source] = OpenRouterLLM(
                        client=client,
                        model=cfg['model'],
                        temperature=cfg['temperature'],
                        site_url=cfg['site_url'],
                        site_name=cfg['site_name']
                    )
                elif source == 'lmstudio':
                    api_key = 'lmstudio'
                    if not api_key:
                        raise ValueError("LMSTUDIO_API_KEY not found")
                    client = OpenAI(
                        base_url="http://127.0.0.1:1234/v1",
                        api_key=api_key,
                    )
                    # create and register an LMStudio wrapper so invoke_with_fallback can call it
                    llm_instances[source] = LMStudioLLM(
                        client=client,
                        model=cfg['model'],
                        temperature=float(cfg.get('temperature', 0.0))
                    )
                elif source == 'groq':
                    api_key = os.getenv('GROQ_API_KEY')
                    if not api_key:
                        raise ValueError("GROQ_API_KEY not found")
                    groq_client = ChatGroq(
                        model=cfg['model'],
                        temperature=float(cfg['temperature']),
                        api_key=api_key
                    )
                    llm_instances[source] = GroqLLMWrapper(groq_client)
                
                elif source == 'ollama':
                    llm_instances[source] = ChatOllama(
                        model=cfg['model'],
                        temperature=float(cfg['temperature'])
                    )
                else:
                    print(f"Unsupported LLM source in fallback: {source}")
                    continue
            except Exception as e:
                print(f"Failed to setup {source}: {e}")
                continue
        if not llm_instances:
            raise Exception("No LLMs could be set up from the fallback order.")
        return llm_instances

    def invoke_with_fallback(self, llm_instances, order_key, input_data, output_model=None):
        # Resolve order key → actual list
        if isinstance(order_key, str):
            if order_key not in self.orders:
                raise ValueError(f"Unknown fallback order '{order_key}'. Must be one of {list(self.orders.keys())}")
            fallback_order = self.orders[order_key]
        else:
            fallback_order = order_key  # allow passing list directly

        for source in fallback_order:
            if source in llm_instances:
                try:
                    llm = llm_instances[source]
                    if output_model:
                        llm = llm.with_structured_output(output_model)

                    result = llm.invoke(input_data)

                    if output_model:
                        print(f"✅ Used {source} (structured).")
                        return result

                    if hasattr(result, 'content'):
                        result = result.content
                    if not isinstance(result, str):
                        raise ValueError(f"Unexpected result type from {source}: {type(result)}")

                    print(f"✅ Used {source} (raw).")
                    return result
                except Exception as e:
                    print(f"⚠️ {source} failed: {e}. Trying next...")
                    continue
        return "❌ All LLMs in fallback chain failed."    



class GroqLLMWrapper(Runnable):
    def __init__(self, groq_client):
        super().__init__()
        self.groq_client = groq_client  # This is the ChatGroq instance

    def invoke(self, input, config=None):
        return self.groq_client.invoke(input, config=config)

    def with_structured_output(self, schema):
        """Wrap Groq with PydanticOutputParser for structured outputs"""
        parser = PydanticOutputParser(pydantic_object=schema)

        class StructuredGroq:
            def __init__(self, groq_llm, parser):
                self.groq_llm = groq_llm
                self.parser = parser

            def invoke(self, prompt, config=None):
                # Add format instructions to force JSON-like response
                formatted_prompt = str(prompt) + "\n" + self.parser.get_format_instructions()
                response = self.groq_llm.invoke(formatted_prompt, config=config)
                # Handle AIMessage from Groq
                if hasattr(response, "content"):
                    response = response.content
                return self.parser.parse(response)

        return StructuredGroq(self, parser)


class OpenRouterLLM(Runnable):
    def __init__(self, client, model, temperature, site_url, site_name):
        super().__init__()
        self.client = client
        self.model = model
        self.temperature = temperature
        self.site_url = site_url
        self.site_name = site_name

    def invoke(self, input, config=None):
        prompt = str(input)
        try:
            completion = self.client.chat.completions.create(
                extra_headers={"HTTP-Referer": self.site_url, "X-Title": self.site_name},
                extra_body={},
                model=self.model,
                temperature=float(self.temperature),
                messages=[{"role": "user", "content": prompt}]
            )
            result = completion.choices[0].message.content
            if not result:
                raise ValueError("LLM returned an empty response")
            return result
        except Exception as e:
            print(f"Error during OpenRouter invocation: {e}")
            raise


class LMStudioLLM(Runnable):
    def __init__(self, client, model, temperature):
        super().__init__()
        self.client = client
        self.model = model
        self.temperature = temperature

    def invoke(self, input, config=None):
        prompt = str(input)
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                temperature=float(self.temperature),
                messages=[{"role": "user", "content": prompt}]
            )
            result = completion.choices[0].message.content
            if not result:
                raise ValueError("LMStudio returned an empty response")
            return result
        except Exception as e:
            print(f"Error during LMStudio invocation: {e}")
            raise

    def with_structured_output(self, schema):
        """Emulate structured output using PydanticOutputParser"""
        parser = PydanticOutputParser(pydantic_object=schema)

        class StructuredLMStudio:
            def __init__(self, llm, parser):
                self.llm = llm
                self.parser = parser

            def invoke(self, prompt, config=None):
                # add parser’s format instructions to the prompt
                formatted_prompt = str(prompt) + "\n" + self.parser.get_format_instructions()
                response = self.llm.invoke(formatted_prompt, config=config)
                return self.parser.parse(response)

        return StructuredLMStudio(self, parser)
# def run_with_fallback(llm_dict, model, prompt, fallback_order):
#     for name in fallback_order:  # e.g. ["groq", "ollama", "openrouter", "lmstudio"]
#         if name in llm_dict:
#             try:
#                 structured_llm = llm_dict[name].with_structured_output(model)
#                 return structured_llm.invoke(prompt)
#             except Exception as e:
#                 print(f"{name} failed: {e}")
#     raise RuntimeError("All LLMs failed.")
