import { useState } from "react";
import { ThumbsUp, ThumbsDown, Share2, ChevronDown, ChevronUp } from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";

interface AnswerCardProps {
  index: number;
  answer: string;
  crop?: string;
  state?: string;
  category?: string;
}

const AnswerCard = ({ index, answer, crop, state, category }: AnswerCardProps) => {
  const { t } = useLanguage();
  const [expanded, setExpanded] = useState(answer.length <= 200);
  const [feedback, setFeedback] = useState<"up" | "down" | null>(null);

  const displayText = expanded ? answer : answer.slice(0, 200) + "...";

  return (
    <div className="bg-card rounded-xl border border-border p-4 space-y-3 shadow-sm">
      <div className="flex items-start gap-3">
        <span className="w-7 h-7 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-body-sm font-bold flex-shrink-0">
          {index}
        </span>
        <div className="flex-1 min-w-0">
          <p className="text-body text-foreground leading-relaxed">{displayText}</p>
          {answer.length > 200 && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="mt-1 flex items-center gap-1 text-body-sm text-primary font-medium"
            >
              {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              {expanded ? "Less" : "More"}
            </button>
          )}
        </div>
      </div>

      {(crop || state || category) && (
        <div className="flex flex-wrap gap-2">
          {crop && <span className="px-3 py-1 rounded-full bg-chip text-chip-foreground text-caption font-medium">🌾 {crop}</span>}
          {state && <span className="px-3 py-1 rounded-full bg-chip text-chip-foreground text-caption font-medium">📍 {state}</span>}
          {category && <span className="px-3 py-1 rounded-full bg-chip text-chip-foreground text-caption font-medium">🐛 {category}</span>}
        </div>
      )}

      <div className="flex items-center gap-2 pt-1">
        <button
          onClick={() => setFeedback("up")}
          className={`flex items-center gap-1 px-3 py-1.5 rounded-lg text-body-sm touch-target transition-colors ${
            feedback === "up" ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground hover:bg-accent"
          }`}
        >
          <ThumbsUp className="w-4 h-4" />
          <span className="hidden sm:inline">{t("helpful")}</span>
        </button>
        <button
          onClick={() => setFeedback("down")}
          className={`flex items-center gap-1 px-3 py-1.5 rounded-lg text-body-sm touch-target transition-colors ${
            feedback === "down" ? "bg-destructive text-destructive-foreground" : "bg-muted text-muted-foreground hover:bg-accent"
          }`}
        >
          <ThumbsDown className="w-4 h-4" />
        </button>
        <button className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-body-sm bg-muted text-muted-foreground hover:bg-accent touch-target transition-colors ml-auto">
          <Share2 className="w-4 h-4" />
          <span className="hidden sm:inline">{t("share")}</span>
        </button>
      </div>
    </div>
  );
};

export default AnswerCard;
