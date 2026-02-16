import { HelpCircle, ChevronDown } from "lucide-react";
import Header from "@/components/Header";
import BottomNav from "@/components/BottomNav";
import { useLanguage } from "@/contexts/LanguageContext";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

const faqs = [
  { q: { en: "What is offline mode?", hi: "ऑफ़लाइन मोड क्या है?" }, a: { en: "Offline mode lets you search 50,000+ verified answers from the Kisan Call Centre database without internet. AI summaries require connection.", hi: "ऑफ़लाइन मोड आपको बिना इंटरनेट के किसान कॉल सेंटर डेटाबेस से 50,000+ सत्यापित उत्तर खोजने देता है। AI सारांश के लिए कनेक्शन आवश्यक है।" } },
  { q: { en: "Which languages are supported?", hi: "कौन सी भाषाएं समर्थित हैं?" }, a: { en: "Currently Hindi and English. More languages coming soon.", hi: "वर्तमान में हिंदी और अंग्रेजी। जल्द ही और भाषाएं आ रही हैं।" } },
  { q: { en: "How accurate are the answers?", hi: "उत्तर कितने सटीक हैं?" }, a: { en: "Database answers come from verified Kisan Call Centre experts. AI answers are generated from this verified data. Always consult local agriculture officers for critical decisions.", hi: "डेटाबेस उत्तर सत्यापित किसान कॉल सेंटर विशेषज्ञों से आते हैं। AI उत्तर इस सत्यापित डेटा से उत्पन्न होते हैं। महत्वपूर्ण निर्णयों के लिए हमेशा स्थानीय कृषि अधिकारियों से परामर्श करें।" } },
  { q: { en: "Can I save answers for later?", hi: "क्या मैं बाद के लिए उत्तर सहेज सकता हूँ?" }, a: { en: "Yes! Tap the bookmark icon on any answer to save it for offline reading.", hi: "हाँ! किसी भी उत्तर पर बुकमार्क आइकन टैप करके ऑफ़लाइन पढ़ने के लिए सहेजें।" } },
];

const HelpPage = () => {
  const { lang, t } = useLanguage();

  return (
    <div className="min-h-screen bg-background pb-20 md:pb-0">
      <Header />
      <main className="container max-w-2xl mx-auto px-4 py-6 space-y-6">
        <h2 className="text-xl font-bold text-foreground">{t("help")}</h2>

        <section className="space-y-3">
          <h3 className="text-lg font-semibold text-foreground">How to Use / कैसे उपयोग करें</h3>
          <div className="space-y-2">
            {[
              { step: "1", en: "Type or speak your farming question", hi: "अपना कृषि सवाल टाइप या बोलें" },
              { step: "2", en: "View expert answers from database", hi: "डेटाबेस से विशेषज्ञ उत्तर देखें" },
              { step: "3", en: "Read AI-generated summary", hi: "AI-जनित सारांश पढ़ें" },
              { step: "4", en: "Rate answers to help us improve", hi: "उत्तरों को रेट करें ताकि हम बेहतर बनें" },
            ].map((item) => (
              <div key={item.step} className="flex items-start gap-3 p-3 bg-card rounded-xl border border-border">
                <span className="w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-body-sm font-bold flex-shrink-0">
                  {item.step}
                </span>
                <p className="text-body text-foreground">{lang === "hi" ? item.hi : item.en}</p>
              </div>
            ))}
          </div>
        </section>

        <section>
          <h3 className="text-lg font-semibold text-foreground mb-3">FAQ</h3>
          <Accordion type="single" collapsible className="space-y-2">
            {faqs.map((faq, i) => (
              <AccordionItem key={i} value={`faq-${i}`} className="bg-card rounded-xl border border-border px-4">
                <AccordionTrigger className="text-body font-medium text-foreground hover:no-underline">
                  {faq.q[lang]}
                </AccordionTrigger>
                <AccordionContent className="text-body-sm text-muted-foreground">
                  {faq.a[lang]}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </section>
      </main>
      <BottomNav />
    </div>
  );
};

export default HelpPage;
