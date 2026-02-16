import { Bug, Leaf, Droplets, Microscope, Building2, CloudSun } from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";

const categories = [
  { icon: Bug, labelKey: "pestControl", emoji: "🐛", prompt_en: "How to control pests in my crop?", prompt_hi: "मेरी फसल में कीट नियंत्रण कैसे करें?" },
  { icon: Leaf, labelKey: "fertilizers", emoji: "🌾", prompt_en: "Best fertilizer recommendation", prompt_hi: "सबसे अच्छा उर्वरक सुझाव" },
  { icon: Droplets, labelKey: "irrigation", emoji: "💧", prompt_en: "Irrigation schedule and tips", prompt_hi: "सिंचाई अनुसूची और सुझाव" },
  { icon: Microscope, labelKey: "diseases", emoji: "🦠", prompt_en: "How to treat crop disease?", prompt_hi: "फसल रोग का इलाज कैसे करें?" },
  { icon: Building2, labelKey: "govtSchemes", emoji: "🏛️", prompt_en: "Government schemes for farmers", prompt_hi: "किसानों के लिए सरकारी योजनाएं" },
  { icon: CloudSun, labelKey: "weatherAdvice", emoji: "🌡️", prompt_en: "Weather-based farming advice", prompt_hi: "मौसम आधारित कृषि सलाह" },
];

interface CategoryGridProps {
  onSelect: (prompt: string) => void;
}

const CategoryGrid = ({ onSelect }: CategoryGridProps) => {
  const { lang, t } = useLanguage();

  return (
    <div className="grid grid-cols-3 gap-3">
      {categories.map((cat) => (
        <button
          key={cat.labelKey}
          onClick={() => onSelect(lang === "hi" ? cat.prompt_hi : cat.prompt_en)}
          className="flex flex-col items-center gap-2 p-4 rounded-xl bg-card border border-border hover:border-primary hover:bg-accent transition-colors touch-target"
        >
          <span className="text-2xl">{cat.emoji}</span>
          <span className="text-body-sm font-medium text-foreground text-center leading-tight">
            {t(cat.labelKey)}
          </span>
        </button>
      ))}
    </div>
  );
};

export default CategoryGrid;
