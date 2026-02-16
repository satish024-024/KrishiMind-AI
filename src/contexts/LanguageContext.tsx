import React, { createContext, useContext, useState, useCallback } from "react";

type Language = "en" | "hi";

interface Translations {
  [key: string]: { en: string; hi: string };
}

const translations: Translations = {
  tagline: { en: "Your 24/7 Agricultural Expert", hi: "आपका 24/7 कृषि सलाहकार" },
  askPlaceholder1: { en: "How to control pests in wheat?", hi: "गेहूं में कीट नियंत्रण कैसे करें?" },
  askPlaceholder2: { en: "Best fertilizer for cotton?", hi: "कपास के लिए सबसे अच्छा उर्वरक?" },
  askPlaceholder3: { en: "Tomato blight treatment?", hi: "टमाटर में झुलसा रोग का इलाज?" },
  askButton: { en: "Ask", hi: "पूछें" },
  pestControl: { en: "Pest Control", hi: "कीट नियंत्रण" },
  fertilizers: { en: "Fertilizers", hi: "उर्वरक" },
  irrigation: { en: "Irrigation", hi: "सिंचाई" },
  diseases: { en: "Diseases", hi: "रोग" },
  govtSchemes: { en: "Govt Schemes", hi: "सरकारी योजनाएं" },
  weatherAdvice: { en: "Weather Advice", hi: "मौसम सलाह" },
  commonQuestions: { en: "Common Questions", hi: "आम सवाल" },
  connected: { en: "Connected", hi: "कनेक्टेड" },
  offline: { en: "Offline Mode", hi: "ऑफ़लाइन मोड" },
  home: { en: "Home", hi: "होम" },
  saved: { en: "Saved", hi: "सहेजा" },
  notifications: { en: "Updates", hi: "अपडेट" },
  settings: { en: "Settings", hi: "सेटिंग्स" },
  help: { en: "Help", hi: "मदद" },
  dbAnswers: { en: "Expert Answers", hi: "विशेषज्ञ उत्तर" },
  aiAnswer: { en: "AI Answer", hi: "AI उत्तर" },
  askNewQuestion: { en: "Ask New Question", hi: "नया सवाल पूछें" },
  callExpert: { en: "Call Expert", hi: "विशेषज्ञ को कॉल करें" },
  helpful: { en: "Helpful", hi: "उपयोगी" },
  notHelpful: { en: "Not Helpful", hi: "अनुपयोगी" },
  share: { en: "Share", hi: "शेयर" },
  poweredBy: { en: "Powered by IBM Watsonx", hi: "IBM Watsonx द्वारा संचालित" },
  expertAnswers: { en: "50,000+ Expert Answers", hi: "50,000+ विशेषज्ञ उत्तर" },
  heroLine1: { en: "Ask any farming question in Hindi or English", hi: "हिंदी या अंग्रेजी में कोई भी कृषि सवाल पूछें" },
  heroLine2: { en: "Get instant answers from Kisan Call Centre database + AI", hi: "किसान कॉल सेंटर डेटाबेस + AI से तुरंत जवाब पाएं" },
  about: { en: "About", hi: "हमारे बारे में" },
  privacy: { en: "Privacy", hi: "गोपनीयता" },
  feedback: { en: "Feedback", hi: "प्रतिक्रिया" },
  developedBy: { en: "Developed by KrishiMind AI Team", hi: "KrishiMind AI टीम द्वारा विकसित" },
  listening: { en: "Listening...", hi: "सुन रहे हैं..." },
  speakNow: { en: "Speak your question clearly", hi: "अपना सवाल स्पष्ट रूप से बोलें" },
  cancel: { en: "Cancel", hi: "रद्द करें" },
  submit: { en: "Submit", hi: "सबमिट" },
  tryAgain: { en: "Try Again", hi: "पुनः प्रयास करें" },
  noResults: { en: "No exact match found. Try rephrasing your question.", hi: "कोई सटीक परिणाम नहीं मिला। अपना सवाल दोबारा लिखें।" },
  offlineBanner: { en: "Offline Mode - Showing database answers only", hi: "ऑफ़लाइन मोड - केवल डेटाबेस उत्तर दिखा रहे हैं" },
  disclaimer: { en: "This is AI-generated advice. Verify with experts before application.", hi: "यह AI-जनित सलाह है। उपयोग से पहले विशेषज्ञों से सत्यापित करें।" },
  savedAnswers: { en: "Saved Answers", hi: "सहेजे गए उत्तर" },
  noSaved: { en: "No saved answers yet", hi: "अभी तक कोई उत्तर सहेजा नहीं गया" },
  recentQueries: { en: "Recent Queries", hi: "हाल के सवाल" },
};

interface LanguageContextType {
  lang: Language;
  setLang: (lang: Language) => void;
  t: (key: string) => string;
}

const LanguageContext = createContext<LanguageContextType>({
  lang: "en",
  setLang: () => {},
  t: (key) => key,
});

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [lang, setLang] = useState<Language>("en");

  const t = useCallback(
    (key: string) => translations[key]?.[lang] || key,
    [lang]
  );

  return (
    <LanguageContext.Provider value={{ lang, setLang, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => useContext(LanguageContext);
