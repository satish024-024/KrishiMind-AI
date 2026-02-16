import { Globe, Volume2, Download, Trash2, Shield } from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";
import Header from "@/components/Header";
import BottomNav from "@/components/BottomNav";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";

const SettingsPage = () => {
  const { lang, setLang, t } = useLanguage();

  return (
    <div className="min-h-screen bg-background pb-20 md:pb-0">
      <Header />
      <main className="container max-w-2xl mx-auto px-4 py-6 space-y-6">
        <h2 className="text-xl font-bold text-foreground">{t("settings")}</h2>

        <div className="space-y-1">
          <div className="bg-card rounded-xl border border-border p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Globe className="w-5 h-5 text-muted-foreground" />
              <span className="text-body font-medium text-foreground">Language / भाषा</span>
            </div>
            <select
              value={lang}
              onChange={(e) => setLang(e.target.value as "en" | "hi")}
              className="bg-muted rounded-lg px-3 py-2 text-body-sm text-foreground border-none"
            >
              <option value="en">English</option>
              <option value="hi">हिंदी</option>
            </select>
          </div>

          <div className="bg-card rounded-xl border border-border p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Volume2 className="w-5 h-5 text-muted-foreground" />
              <span className="text-body font-medium text-foreground">Voice input</span>
            </div>
            <Switch defaultChecked />
          </div>

          <div className="bg-card rounded-xl border border-border p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Download className="w-5 h-5 text-muted-foreground" />
              <span className="text-body font-medium text-foreground">Offline reading</span>
            </div>
            <Switch />
          </div>
        </div>

        <div className="space-y-1">
          <Button variant="outline" className="w-full justify-start h-12 touch-target">
            <Trash2 className="w-5 h-5 mr-3" />
            Clear cache
          </Button>
          <Button variant="outline" className="w-full justify-start h-12 touch-target">
            <Shield className="w-5 h-5 mr-3" />
            Privacy policy
          </Button>
        </div>

        <p className="text-caption text-muted-foreground text-center">KrishiMind AI v1.0.0</p>
      </main>
      <BottomNav />
    </div>
  );
};

export default SettingsPage;
