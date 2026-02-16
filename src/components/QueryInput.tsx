import { useState, useEffect } from "react";
import { Mic, ArrowRight } from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";
import { Button } from "@/components/ui/button";
import VoiceInputModal from "./VoiceInputModal";

interface QueryInputProps {
  onSubmit: (query: string) => void;
  initialValue?: string;
}

const placeholderKeys = ["askPlaceholder1", "askPlaceholder2", "askPlaceholder3"];

const QueryInput = ({ onSubmit, initialValue = "" }: QueryInputProps) => {
  const { t } = useLanguage();
  const [query, setQuery] = useState(initialValue);
  const [placeholderIdx, setPlaceholderIdx] = useState(0);
  const [showVoice, setShowVoice] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      setPlaceholderIdx((prev) => (prev + 1) % placeholderKeys.length);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    setQuery(initialValue);
  }, [initialValue]);

  const handleSubmit = () => {
    if (query.trim()) onSubmit(query.trim());
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") handleSubmit();
  };

  return (
    <>
      <div className="w-full space-y-3">
        <div className="relative">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={t(placeholderKeys[placeholderIdx])}
            className="w-full h-[60px] rounded-xl border border-input bg-card px-4 pr-14 text-body text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:border-primary transition-colors"
          />
          <button
            onClick={() => setShowVoice(true)}
            className="absolute right-3 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-accent flex items-center justify-center touch-target text-accent-foreground hover:bg-primary hover:text-primary-foreground transition-colors"
            aria-label="Voice input"
          >
            <Mic className="w-5 h-5" />
          </button>
        </div>

        <Button
          onClick={handleSubmit}
          className="w-full h-12 text-body font-bold rounded-xl"
          disabled={!query.trim()}
        >
          <span>{t("askButton")}</span>
          <ArrowRight className="w-5 h-5 ml-2" />
        </Button>
      </div>

      {showVoice && (
        <VoiceInputModal
          onClose={() => setShowVoice(false)}
          onResult={(text) => {
            setQuery(text);
            setShowVoice(false);
          }}
        />
      )}
    </>
  );
};

export default QueryInput;
