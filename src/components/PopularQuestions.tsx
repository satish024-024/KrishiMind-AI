import { ChevronRight } from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";

const questions = {
  en: [
    "How to control stem borer in paddy?",
    "Best time to apply urea in wheat?",
    "PM-KISAN scheme eligibility and benefits",
    "How to manage late blight in potato?",
    "Drip irrigation setup cost for 1 acre",
  ],
  hi: [
    "धान में तना छेदक को कैसे नियंत्रित करें?",
    "गेहूं में यूरिया डालने का सही समय?",
    "PM-KISAN योजना पात्रता और लाभ",
    "आलू में झुलसा रोग का प्रबंधन कैसे करें?",
    "1 एकड़ के लिए ड्रिप सिंचाई की लागत",
  ],
};

interface PopularQuestionsProps {
  onSelect: (q: string) => void;
}

const PopularQuestions = ({ onSelect }: PopularQuestionsProps) => {
  const { lang, t } = useLanguage();
  const list = questions[lang];

  return (
    <section>
      <h2 className="text-lg font-bold text-foreground mb-3">{t("commonQuestions")}</h2>
      <div className="space-y-2">
        {list.map((q, i) => (
          <button
            key={i}
            onClick={() => onSelect(q)}
            className="w-full flex items-center justify-between p-3 rounded-xl bg-card border border-border hover:border-primary hover:bg-accent transition-colors text-left touch-target"
          >
            <span className="text-body text-foreground line-clamp-1 flex-1 mr-2">{q}</span>
            <ChevronRight className="w-5 h-5 text-muted-foreground flex-shrink-0" />
          </button>
        ))}
      </div>
    </section>
  );
};

export default PopularQuestions;
