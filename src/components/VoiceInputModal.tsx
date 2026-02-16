import { Mic, X } from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";
import { Button } from "@/components/ui/button";

interface VoiceInputModalProps {
  onClose: () => void;
  onResult: (text: string) => void;
}

const VoiceInputModal = ({ onClose, onResult }: VoiceInputModalProps) => {
  const { t } = useLanguage();

  // Placeholder — real speech recognition would go here
  const handleSimulate = () => {
    onResult("How to control aphids in mustard crop?");
  };

  return (
    <div className="fixed inset-0 z-[100] bg-foreground/80 flex flex-col items-center justify-center p-6">
      <div className="bg-card rounded-2xl p-8 w-full max-w-sm flex flex-col items-center gap-6">
        <div className="w-24 h-24 rounded-full bg-primary/10 flex items-center justify-center animate-pulse-mic">
          <Mic className="w-12 h-12 text-primary" />
        </div>
        <p className="text-xl font-semibold text-foreground">{t("listening")}</p>
        <p className="text-body-sm text-muted-foreground text-center">{t("speakNow")}</p>

        <div className="flex gap-3 w-full">
          <Button variant="outline" className="flex-1 h-12 touch-target" onClick={onClose}>
            {t("cancel")}
          </Button>
          <Button className="flex-1 h-12 touch-target" onClick={handleSimulate}>
            {t("tryAgain")}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default VoiceInputModal;
