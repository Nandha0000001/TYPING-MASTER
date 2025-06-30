"""
This module contains all the text data used in the typing application,
including practice texts, words for games, lessons, and chatbot responses.
"""

# Typing test texts by difficulty level
EASY_TEXTS = [
    "The quick brown fox jumps over the lazy dog. ",
    "Typing is an essential skill in today's digital world. ",
    "Learning to type without looking at the keyboard is called touch typing. ",
    "Reading is a good way to expand your vocabulary. ",
    "Water is essential for all living things. "
]

MEDIUM_TEXTS = [
    "Computer programming is the process of designing and building an executable computer program to accomplish a specific computing result or to perform a specific task. ",
    "The Internet is the global system of interconnected computer networks that uses the Internet protocol suite to link devices worldwide. ",
    "Climate change includes both global warming driven by human-induced emissions of greenhouse gases and the resulting large-scale shifts in weather patterns. "
]

HARD_TEXTS = [
    "The creation of a quantum computer that could effectively solve problems that are practically unsolvable by classical computers, such as factoring large numbers or simulating quantum systems, would revolutionize computing and potentially render many current cryptographic methods obsolete. ",
    "Neuroplasticity, the brain's ability to reorganize itself by forming new neural connections throughout life, enables the neurons (nerve cells) in the brain to compensate for injury and disease and to adjust their activities in response to new situations or to changes in their environment. ",
    "In the field of computational linguistics, morphological parsing involves segmenting a word into its component morphemes and assigning to them their correct morphosyntactic features. This process is intrinsically intertwined with the larger domain of natural language processing and often necessitates sophisticated algorithms capable of handling the syntactic and semantic complexities inherent in human languages, particularly those with rich morphological systems like Finnish or Turkish.",
    "The philosophical concept of epistemological solipsism posits that knowledge of anything outside one's own mind is unsure; the external world and other minds cannot be known and might not exist outside the mind. This stands in contrast to metaphysical solipsism, the view that only one's mind and its contents exist, and reality is merely the product of one's own subjective perceptions, raising profound questions about the nature of consciousness and the verification of objective reality.",
    "The biodiversity of a region is influenced by a multiplicity of interconnected factors including geography, climate, evolutionary history, and human activities. Ecosystems characterized by high biodiversity generally demonstrate enhanced resilience to environmental stressors and perturbations, a principle increasingly recognized as critical in conservation biology and ecological restoration efforts aimed at mitigating the impacts of habitat fragmentation, climate change, and other anthropogenic pressures on natural systems."
]

# Words for typing game by difficulty level
EASY_WORDS = [
"the", "and", "you", "is", "was", "for", "are", "to", "in", "at",
    "it", "on", "he", "as", "do", "we", "can", "go", "see", "my",
    "up", "by", "me", "of", "no", "so", "us", "am", "if", "an",
    "or", "be", "ok", "hi", "yes", "day", "cat", "dog", "run", "eat"
]

MEDIUM_WORDS = [
    "computer", "system", "program", "design", "network", "science", "digital", "language",
    "keyboard", "monitor", "software", "hardware", "database", "internet", "algorithm",
    "function", "variable", "structure", "interface", "protocol", "graphics", "memory",
    "processor", "device", "platform", "security", "virtual", "storage", "wireless", "browser",
    "document", "resource", "framework", "component", "solution", "application", "technology",
    "development", "innovation", "generation", "information", "communication", "processing",
    "encryption", "authentication", "operation", "performance", "integration", "configuration", "implementation"
]

HARD_WORDS = [
    "pseudocode", "optimization", "parallelism", "cryptography", "virtualization",
    "architecture", "synchronization", "serialization", "abstraction", "polymorphism",
    "encapsulation", "inheritance", "disambiguation", "interpolation", "extrapolation",
    "authentication", "authorization", "infrastructure", "sustainability", "accessibility",
    "interoperability", "decentralization", "standardization", "normalization", "cybersecurity",
    "bioinformatics", "nanotechnology", "thermodynamics", "superconductivity", "electromagnetism",
    "neuroplasticity", "crystallography", "spectroscopy", "phenomenology", "epistemology",
    "anthropomorphic", "multidisciplinary", "interdependence", "internationalization", "localization",
    "parameterization", "recursiveness", "metaprogramming", "defragmentation", "decompression"
]

# Typing lessons
LESSONS = {
    "1": {
        "id": "1",
        "title": "Home Row Basics",
        "description": "Learn the home row keys (ASDF JKL;)",
        "content": "Place your fingers on the home row: left hand on ASDF, right hand on JKL;. Type without looking at the keyboard: asdf jkl; asdf jkl; fjdk slaa fjdk slaa",
        "difficulty": "beginner"
    },
    "2": {
        "id": "2",
        "title": "Home Row Words",
        "description": "Practice typing words using only home row keys",
        "content": "Type these home row words: add fall as dal fad lad salad flask half lass jail sail fall salsa",
        "difficulty": "beginner"
    },
    "3": {
        "id": "3",
        "title": "Adding E and I",
        "description": "Add the E and I keys to your practice",
        "content": "Type these words with E and I: fie die lie field side idea die fill slide file life like",
        "difficulty": "beginner"
    },
    "4": {
        "id": "4",
        "title": "Top Row Basics",
        "description": "Learn the top row keys (QWERTY UIOP)",
        "content": "Practice reaching for the top row: qwerty uiop qwerty uiop quest port quiet worry pointer",
        "difficulty": "intermediate"
    },
    "5": {
        "id": "5",
        "title": "Bottom Row Basics",
        "description": "Learn the bottom row keys (ZXCVB NM,./)",
        "content": "Practice reaching for the bottom row: zxcvb nm,./ zxcvb nm,./ zen mix cab verb next moon",
        "difficulty": "intermediate"
    },
    "6": {
        "id": "6",
        "title": "Numbers and Symbols",
        "description": "Practice typing numbers and common symbols",
        "content": "Practice typing numbers and symbols: 1234567890 !@#$%^&*() 1a 2b 3c 4d 5e $100 %50 &co",
        "difficulty": "intermediate"
    },
    "7": {
        "id": "7",
        "title": "Full Keyboard Integration",
        "description": "Use all keys together in sentences",
        "content": "The quick brown fox jumps over the lazy dog. Pack my box with five dozen liquor jugs. How vexingly quick daft zebras jump!",
        "difficulty": "advanced"
    },
    "8": {
        "id": "8",
        "title": "Speed Building",
        "description": "Focus on increasing your typing speed",
        "content": "Type as quickly and accurately as you can: The five boxing wizards jump quickly. A quick movement of the enemy will jeopardize five gunboats. All questions asked by five watch experts amazed the judge.",
        "difficulty": "advanced"
    },
    "9": {
        "id": "9",
        "title": "Accuracy Practice",
        "description": "Focus on typing accurately with difficult combinations",
        "content": "Focus on accuracy: Peter Piper picked a peck of pickled peppers. She sells seashells by the seashore. How can a clam cram in a clean cream can?",
        "difficulty": "advanced"
    },
    "10": {
        "id": "10",
        "title": "Programming Syntax",
        "description": "Practice typing common programming syntax",
        "content": "function calculateSum(a, b) { return a + b; } if (x > 0 && y < 10) { console.log('Valid coordinates'); } const users = ['John', 'Mary', 'Alex'];",
        "difficulty": "expert"
    }
}

# Chatbot responses
CHATBOT_RESPONSES = {
    "how to improve typing": "To improve your typing skills: 1) Practice regularly, 2) Focus on accuracy before speed, 3) Learn proper finger positioning, 4) Use touch typing techniques, and 5) Take our structured lessons starting with the home row keys.",
    
    "what is wpm": "WPM (Words Per Minute) is a measure of typing speed. It's calculated by dividing the number of characters typed by 5 (average word length) and then dividing by the time taken in minutes. A good typing speed is 40-60 WPM, while professional typists can reach 70-90 WPM.",
    
    "typing accuracy": "Typing accuracy is the percentage of correctly typed characters. To improve accuracy: 1) Slow down and focus on correct keystrokes, 2) Practice problem keys identified in your error analysis, 3) Maintain proper hand positioning, and 4) Don't look at the keyboard while typing.",
    
    "touch typing": "Touch typing is typing without looking at the keyboard. Start by placing your fingers on the home row (ASDF for left hand, JKL; for right hand) and learn which finger is responsible for each key. Our lessons can guide you through the process step by step.",
    
    "hand position": "Proper hand position: 1) Place your fingers on the home row (ASDF for left hand, JKL; for right hand), 2) Keep your wrists straight and slightly elevated, 3) Maintain a slight curve in your fingers, 4) Use your thumbs for the space bar, and 5) Sit with good posture.",
    
    "typing practice": "For effective typing practice: 1) Start with our structured lessons, 2) Practice regularly (10-15 minutes daily is better than an hour once a week), 3) Focus on problem areas identified in your performance statistics, 4) Use our typing game for a fun alternative to standard practice.",
    
    "keyboard shortcuts": "Common keyboard shortcuts include: Ctrl+C (copy), Ctrl+V (paste), Ctrl+X (cut), Ctrl+Z (undo), Ctrl+Y (redo), Ctrl+A (select all), Ctrl+S (save), Alt+Tab (switch applications), and Windows/Command+Space (search).",
    
    "ergonomics": "Typing ergonomics: 1) Adjust your chair so your feet are flat on the floor, 2) Position your screen at eye level, 3) Keep your keyboard at elbow height, 4) Maintain good posture with a straight back, 5) Take regular breaks (5 minutes every hour), and 6) Consider an ergonomic keyboard for extended typing.",
    
    "finger exercises": "Finger exercises for typists: 1) Finger stretches (spread fingers wide, then make a fist), 2) Wrist rotations, 3) Finger taps on a surface, 4) Hand and finger massage, and 5) Specific typing exercises like repeatedly typing 'asdf jkl;' to strengthen home row muscle memory.",
    
    "help": "I can answer questions about typing speed, accuracy, touch typing techniques, hand positioning, practice methods, keyboard shortcuts, ergonomics, and finger exercises. Just ask me what you'd like to know!"
}
