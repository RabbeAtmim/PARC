# milo.py
import os
import sys
import subprocess
import ollama
import threading
import random
import time

# Dynamically locate binaries inside the active virtual environment (.venv)
VENV_BIN_DIR = os.path.dirname(sys.executable)
EDGE_TTS_BIN = os.path.join(VENV_BIN_DIR, "edge-tts")

# Voice selection
MILO_VOICE = "en-US-GuyNeural"

# List of Pre-defined dark humor jokes
DARK_JOKES = [
    "What does a burnt pizza and a pregnant woman have in common? Someone forgot to pull it out on time.",
    "Don't be racist. Racism is a crime. And crime is for black people.",
    "Any jokes can be funny with the right delivery. Except the abortion joke. They have no delivery.",
    "What is the best thing about marrying a 28 year old? There are 20 of them.",
    "What comes after a billion? Divorce.",
    "Why can't a pedophile get corona? Because COVID is 19.",
    "Why does lesbian have short hair? Because they can't keep it straight.",
    "What is the one thing Israel and Palestine have in common? Only the best shooters survive.",
    "What's the difference between a wife and a game? A game is difficult to beat.",
    "What do you call a rich person in Africa? A tourist.",
    "Suicidal thoughts are like suicidal people. If you ignore them, they will go away.",
    "What makes ISIS joke funny? The execution.",
    "Why is the iPhone X perfect for orphans? Because it has no home button.",
    "Abortion isn't murder. It's just cancelling your pre-order.",
    "What comes after death? Necrophile.",
    "What is the difference between pedophilia and necrophilia? About 5 minutes.",
    "Why do crippled people always be bullied? Because they can't take a stand for themselves.",
    "A woman said, 'I am pregnant'. What did her husband ask her? Is it a boy or an abortion.",
    "'I am sorry' and 'I apologize' mean the same things. Except at a funeral.",
    "What do pedophiles and teachers have in common? Both love to teach kids new things.",
    "What do you call a burning gay person? LGBBQ.",
    "Why are Americans so good in solving Rubik's cube? They know how to separate colors.",
    "What do you call a black person flying a plane? A pilot... you racist.",
    "What's the most effective way of population control? Establishing the asian education system all around the world.",
    "What do you call a group of trans women? Ex-men.",
    "If I had a taka for every time I was racist, I'd get robbed by some black guys.",
    "What's the difference between a man and a car? A car hitting a woman is an accident.",
    "What is common between a blind kid and an orphan? Both can't see their parents.",
    "Come on, don't be racist. It takes all the color to make a rainbow. Except black.",
    "What is the most positive thing in Africa? The H.I.V test.",
    "What do a pack of gum and a gun have in common? When you pull them out in class, everybody wants to be your friend.",
    "What’s the difference between a baby and a sweet potato? About 1500 calories.",
    "What do you call a blank sheet of paper? Women's rights.",
    "What's the biggest achievement of a girl? Reaching home safely after 10 pm.",
    "What's the difference between a bowling ball and a baby? You can't catch a bowling ball with a pitchfork.",
    "What's the difference between a dildo and a feminist? A dildo does something for the women.",
    "How do two lesbian pass their time when they are in a period? Finger painting.",
    "What does a pizza boy and a gynecologist have in common? They both can touch it, but can't have it.",
    "Why are cigarettes good for the environment? They kill people.",
    "What's yellow and can't swim? A bus full of children.",
    "What can a pedophile and a mathematician agree upon? 11 is a prime number.",
    "One day a man asked me a biology question. And I failed to answer. The question was, 'What is found in a cell?' Apparently black people weren't the answer.",
    "What do a pregnant 14 year old and her unborn baby have in common? They both think, 'My mum's gonna kill me.'",
    "What's worse than 10 babies in a tree? A baby on 10 trees.",
    "What's the difference between chocolate and humans? I can still buy dark chocolate.",
    "A man was caught drinking at the job. So, he was banned from there. He used to work in sperm bank.",
    "What comes after 69? Mouth wash.",
    "What's the difference between a Palestinian kid and an Israeli kid? Israeli kids celebrate diwali once in a year and enjoy the sound of crackers.",
    "What's the difference between a woman's hand and the law? You go to jail when you break the law.",
    "Why do the black people stink? So that blind people can also hate them.",
    "What is America's biggest fear? A black kid born in a Muslim family.",
    "What is the difference between Miss Universe of 2019 and you? You are Fair & Lovely.",
    "How will you find a blind man in a nude Beach? It's not hard.",
    "What's the best thing about dating a homeless woman? You can drop them anywhere you want.",
    "What's a group of useless people called? LGBTQ community.",
    "What's common between an orphan guy and a handless guy? Both can't hug their parents.",
    "You know, dark humor is like food. Not everyone gets it.",
    "Why are most NBA players black? Because they are good at shooting, stealing and sprinting.",
    "Why are asians good at chess? Because we are used to breaking into pieces.",
    "What is common between Hitler and Rabbit? Both can't finish a race.",
    "Why back in the days the movies were shot in Black and White? Because they were bored of shooting only black.",
    "Why are Asians good at mathematics? Because they aren't busy counting new genders.",
    "What should you do after doing something dirty with a deaf and mute girl? Break her fingers.",
    "What's the difference between a cockroach and a baby? You feel scared when you go to kill a cockroach.",
    "What do you call a dinner between two people who are in love? 69.",
    "Why does Stephen Hawking used to do one liner? Because he can't do standup.",
    "Why do women belong to the kitchen? Because they have eggs and milks with them.",
    "Dark humor is like a kid with cancer. Never gets old.",
    "Life is like sex. If you come fast you will lose.",
    "The coffee without milk is called Americano. Then what is the coffee without water called? Africano.",
    "We couldn't decide whether to cremate or bury my grandmother. So we let her live.",
    "Sex is like vegetables. If you were forced to have it as a kid then you probably won't like it as an adult.",
    "A dark joke is like cancer. It's even funnier if a child gets it.",
    "What do you mean by having sex using protection? Wearing sunglasses so you don't get pepper sprayed.",
    "What do 5 out of 6 people enjoy? Gang rape.",
    "What's white on the top and black on the bottom? Society.",
    "Have you ever tried African food? Neither do they.",
    "How do you make your girlfriend scream during sex? Call and tell her about it.",
    "How long does it take to manufacture bombs in Arabia? 9 months.",
    "Did you know condoms aren't biodegradable? It's better to have raw sex. Babies are biodegradable.",
    "What's the difference between a remote and a wife? We hit both when they aren't working.",
    "Jokes are like slaves. The darker; The better.",
    "I love telling jokes about orphans. After all what they're gonna do, tell their parents?",
    "What's the thing you can say both during sex and a funeral? This would be much better if you were alive.",
    "Why was 6 afraid of 7? Because 7 ate 9. But why was 10 afraid? Because it was in the middle of 9/11.",
    "What's common between love and a fart? Sometimes you can't hold them in. But when you do, it explodes.",
    "Life is like mathematics. If you can solve one problem, people will give you more.",
    "Hearts are like husbands. If it's still beating that means you are alive.",
    "What's the difference between banana and kid? We can peel off bananas in public.",
    "What's the similarities between aeroplane and rape? The ride gets more annoying when the kids start screaming.",
    "What is common between AIDS and frustration? You get it, when you play with random people.",
    "Why don't vegetarians moan during sex? Because they don't want to admit that a piece of meat can make them happy.",
    "What do you call the useless skin around a vagina? The woman.",
    "What's the difference between 3 cocks and a joke? You can't take a joke.",
    "Why don't Japanese people have squinty eyes? Atomic bombs are pretty damn bright.",
    "What's the difference between a car key and a kid? Car key doesn't turn me on.",
    "What's the difference between women and Ubers? Drunk men ask before getting inside of an Uber.",
    "What's the benefits of being an orphan? Teachers can't call your parents.",
    "Why do orphans have 363 days? Because they don't have mother and father's day.",
    "Which gun does not exist in Africa? The water gun.",
    "Do you know, The 'W' in the word 'Africa' stands for water.",
    "What is 1 + 1? The number of parents an orphan doesn't have.",
    "What is reverse exorcism? When a devil asks the priest to get out of the child.",
    "How many babies does it take to paint a wall? Depends how hard you throw them.",
    "Why don't orphans work as computer repair technicians? Because they can't find the motherboard.",
    "How do you know an orphan is lying? When they swear on their mother's life.",
    "What's the best thing about stage 4 cancer? There is no stage 5.",
    "Wives are like grenades. If you pull the ring, the house is gone.",
    "Why do black people only have nightmares? Because the last one who had a dream was shot.",
    "Genders are like the twin towers. There used to be two, and now it's a sensitive subject.",
    "Why did God make man before woman? Because he didn't want any advice on how to do it.",
    "What has 50 legs but can't walk? 25 disabled people.",
    "What's the difference between science and religion? Science builds planes and skyscrapers while religion brings them together.",
    "Dark humor is like skin, the darker it gets the less people like it.",
    "Why did the slave go to college? To get his master's degree.",
    "What do you call an obese girl with a rape whistle? Optimistic.",
    "Why are orphans bad at poker? Because they don't know what a full house is.",
    "Why do women always use the left hand? Because they don't have rights.",
    "What do you call a 90 year old black person? An antique farming machinery.",
    "What's the difference between an elevator and a black guy? An elevator can raise a family.",
    "When does a joke become a dad joke? When it leaves you and never comes back.",
    "Why do women always have sex with the lights off? Because they never like to see a man having a good time.",
    "How do you stop an argument between two deaf people? Switch off the lights.",
    "How does a black American woman fight against crime? She does an abortion.",
    "Why didn't the USA win the gold medal in shooting? Because the Olympics don't take place in highschool.",
    "What's the difference between a baby and a feminist? At some point a baby will grow up and stop crying.",
    "What do murderers and wheelchair users have in common? Both sit life sentences.",
    "What's the difference between a woman and a swimming pool? None. Expensive to buy, expensive to maintain and you are rarely in it.",
    "Life is like a box of chocolate. It ends faster for the overweight.",
    "What makes sad people jump? The bridge.",
    "I like violence as I like my bear... Domestic!!",
    "We treat our father like god. We ignore him until we need something.",
    "What's the difference between Jesus and his photo? Photo requires only one nail to hang."
]

def speak_milo(text: str):
    """Generates and plays speech using the active .venv's edge-tts executable."""
    print(f"[M.I.L.O]: {text}")
    try:
        output_file = "/tmp/milo_speech.mp3"

        # 1. Generate audio using edge-tts binary from .venv (runs fine as root)
        subprocess.run(
            [EDGE_TTS_BIN, "--voice", MILO_VOICE, "--text", text, "--write-media", output_file],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )

        # 2. Play audio output using ffplay forced through standard user 'atmim' to bypass root audio block
        subprocess.run(
            ["sudo", "-u", "atmim", "ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", output_file],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )

        # 3. Brief pause to let PulseAudio/ALSA release the sound card
        time.sleep(0.2)

    except Exception as e:
        print(f"[M.I.L.O TTS ERROR]: {e}")

def ask_milo(user_query: str):
    """Handles conversation routing using Hermes 3 via Ollama."""

    # --- NEW INTERCEPT LOGIC ---
    clean_query = user_query.lower()

    try:
    # Your existing jarvis execution code here
    pass
except Exception as e:
    print(f"[JARVIS Error] Task execution failed: {e}")

    if "dark joke" in clean_query or "dark humor" in clean_query:
        selected_joke = random.choice(DARK_JOKES)
        speak_milo(selected_joke)
        return  # This stops execution so Ollama is not called
    # ---------------------------

    model_name = 'hermes3:3b'

    try:
        response = ollama.chat(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are a sharp, humorous, bold, conversational buddy, named MILO (Mindful Interctive Language Operator), an AI working alongside PARC (Personal Assist and Response Core). You explain concepts clearly, think out loud, and provide direct answers."
                },
                {"role": "user", "content": user_query}
            ]
        )
        answer = response['message']['content']
        speak_milo(answer)
    except Exception as e:
        speak_milo("I'm having trouble connecting to my local neural network.")
        print(f"[M.I.L.O LLM ERROR]: {e}")

def handle_milo_intent(raw_text: str) -> bool:
    """Intercepts input containing 'milo' and handles it asynchronously."""
    clean_text = raw_text.lower().strip()
    wake_words = ["milo", "my lo", "maiolo", "my lo", "mylow", "meelo"]

    if any(wake in clean_text for wake in wake_words):
        print("[ROUTER] Routing to M.I.L.O module...")

        query = clean_text
        for wake in wake_words:
            query = query.replace(wake, "")
        query = query.strip(",. ")

        if not query:
            query = "What can you do for me?"

        # Run ask_MILO in a separate thread so it doesn't freeze PARC's loop
        milo_thread = threading.Thread(target=ask_milo, args=(query,), daemon=True)
        milo_thread.start()
        return True  # Command handled by MILO

    return False  # Command intended for PARC

def on_user_entered_room():
    """Triggered by wifi_radar.py when human presence transitions from vacant to occupied."""
    # Generate a brief 1-sentence welcome back message via Hermes 3
    ask_milo(
        "I just walked into the room. Give me a brief, sharp, 1-sentence welcome back greeting."
    )


