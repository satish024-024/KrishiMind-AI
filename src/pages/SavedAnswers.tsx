import { Bookmark } from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";
import Header from "@/components/Header";
import BottomNav from "@/components/BottomNav";

const SavedAnswers = () => {
  const { t } = useLanguage();

  return (
    <div className="min-h-screen bg-background pb-20 md:pb-0">
      <Header />
      <main className="container max-w-2xl mx-auto px-4 py-8 flex flex-col items-center justify-center text-center space-y-4">
        <div className="w-20 h-20 rounded-full bg-muted flex items-center justify-center">
          <Bookmark className="w-10 h-10 text-muted-foreground" />
        </div>
        <h2 className="text-xl font-bold text-foreground">{t("savedAnswers")}</h2>
        <p className="text-body text-muted-foreground">{t("noSaved")}</p>
      </main>
      <BottomNav />
    </div>
  );
};

export default SavedAnswers;
