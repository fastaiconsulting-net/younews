from openai import OpenAI


def dummy_script():
    return """
        Good morning, in today's news: U.S. and EU Finalize Trade Agreement, Imposing 15% Tariffs on Most EU Goods.

        The United States and European Union have announced a new trade framework. The U.S. will impose a 15% tariff on most EU imports, contingent on reciprocal European actions, including specific auto tariffs. In exchange, the EU will eliminate tariffs on industrial goods and many agricultural products. The agreement also commits to $750 billion in U.S. energy purchases and $600 billion in EU investments by 2028. The deal addresses non-tariff barriers, digital trade, and environmental standards. This comes after a July meeting between President Trump and EU Commission President Ursula von der Leyen, avoiding a threatened escalation of tariffs.

        European leaders, including German Chancellor Friedrich Merz and French Prime Minister François Bayrou, have expressed concerns that the deal could harm the European economy, hinting at potential political tensions within the EU.

        The key numbers are a 15% tariff on most EU goods and a total commitment of $1.35 trillion in investments, with $750 billion in energy and $600 billion in EU investments by 2028.

        The timeline today: at 8:00 BST, the joint statement was issued; by 8:30 BST, European leaders voiced their concerns. 

        Thank you for listening. This report is brought to you by FastAI Consulting, AI made useful.
    """


class AudioScript:
    def generate_audio_script(openai_client: OpenAI, title: str, markdown_text: str, model: str = "gpt-4.1-nano"):
        instructions = AudioScript.generate_audio_instructions(title)
        response = openai_client.responses.create(
            model=model,
            instructions=instructions,
            input=markdown_text,
        )
        return response.output_text
    
    def save_script(script: str, output_path: str = 'audio_script.txt'):
        with open(output_path, "w") as f:
            f.write(script)

    def generate_audio_instructions(title: str):
        return f"""
        Convert this markdown file into a script to read out loud by a news reader.

        - The news organisation is FastAI Consulting.
        - There should be no implicit extra info like '[News Reader Voice]'. Everything in the script should be read out loud.
        - Do not add any info that is not in the report.
        - Include all information from the report.
        - Do not report the time or date.
        - Get to the point, deliver maximum information in the shortest time possible.

        Structure the report in the following way:

        "Good morning, in todays news: {title}"

        - Start with a short introduction.
        - Then read out the news items in the following format:
            - [News Item Title]
            - [News Item Description]
            - [News Item Link]

        'Thank you for listening. This report is brought to you by FastAI Consulting, AI made useful.'

        """


class GenerateAudio:
    def __init__(self, client: OpenAI, voice: str = "onyx", model: str = "gpt-4o-mini-tts"):
        self.client = client
        self.voice = voice
        self.model = model

    def generate_audio_generator_instructions(self):
        return "Read it as a CNN journalist reading the morning news."

    def generate_audio(self, script: str, output_file: str = "audio.wav"):

        with self.client.audio.speech.with_streaming_response.create(
            model=self.model,
            voice=self.voice,
            input=script,
            instructions=self.generate_audio_generator_instructions(),
        ) as response:
            response.stream_to_file(output_file)
