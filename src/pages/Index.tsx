import { useNavigate } from "react-router-dom";
import { useLanguage } from "@/contexts/LanguageContext";
import Header from "@/components/Header";
import BottomNav from "@/components/BottomNav";
import QueryInput from "@/components/QueryInput";
import CategoryGrid from "@/components/CategoryGrid";
import PopularQuestions from "@/components/PopularQuestions";
import heroFarmer from "@/assets/hero-farmer.jpg";

const Index = () => {
  const { t } = useLanguage();
  const navigate = useNavigate();

  const handleQuery = (query: string) => {
    navigate(`/results?q=${encodeURIComponent(query)}`);
  };

  return (
    <div className="min-h-screen bg-background pb-20 md:pb-0">
      <Header />

      <main className="container max-w-2xl mx-auto px-4 py-6 space-y-8">
        {/* Hero Section */}
        <section className="text-center space-y-4">
          <div className="relative w-full aspect-[16/9] rounded-2xl overflow-hidden bg-muted">
            <img
              src={heroFarmer}
              alt="Indian farmer using smartphone in green field"
              className="w-full h-full object-cover"
              loading="eager"
            />
          </div>

          <div className="space-y-2">
            <p className="text-body font-semibold text-foreground">{t("heroLine1")}</p>
            <p className="text-body-sm text-muted-foreground">{t("heroLine2")}</p>
          </div>

          <div className="flex items-center justify-center gap-4 text-caption text-muted-foreground">
            <span>{t("poweredBy")}</span>
            <span>•</span>
            <span>{t("expertAnswers")}</span>
          </div>
        </section>

        {/* Query Input */}
        <section>
          <QueryInput onSubmit={handleQuery} />
        </section>

        {/* Category Grid */}
        <section>
          <CategoryGrid onSelect={handleQuery} />
        </section>

        {/* Popular Questions */}
        <PopularQuestions onSelect={handleQuery} />

        {/* Footer */}
        <footer className="text-center space-y-3 pt-4 border-t border-border">
          <p className="text-caption text-muted-foreground">{t("developedBy")}</p>
          <div className="flex items-center justify-center gap-4 text-caption">
            <button className="text-primary hover:underline">{t("about")}</button>
            <button className="text-primary hover:underline">{t("help")}</button>
            <button className="text-primary hover:underline">{t("privacy")}</button>
            <button className="text-primary hover:underline">{t("feedback")}</button>
          </div>
        </footer>
      </main>

      <BottomNav />
    </div>
  );
};

export default Index;
