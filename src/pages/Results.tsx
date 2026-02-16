import { useState, useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { ArrowLeft, PenLine, RotateCcw, Phone, Bookmark, AlertTriangle } from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import AnswerCard from "@/components/AnswerCard";
import SkeletonCard from "@/components/SkeletonCard";
import BottomNav from "@/components/BottomNav";

// Mock data
const mockDbAnswers = [
  { answer: "For stem borer control in paddy, apply Carbofuran 3G granules at 25 kg/ha in the leaf whorl at 30 days after transplanting. Alternatively, spray Chlorantraniliprole 18.5 SC at 0.3 ml/litre at the time of egg hatching. Ensure proper water management and remove affected tillers.", crop: "Paddy", state: "Punjab", category: "Pest Control" },
  { answer: "Use light traps to monitor moth population. When moth count exceeds 5 per trap per night, apply insecticide. Neem-based formulations like Azadirachtin 1500 ppm at 5ml/litre can be used as a safer alternative.", crop: "Paddy", state: "Haryana", category: "Pest Control" },
  { answer: "Trichogramma japonicum parasitoid can be released at 1 lakh/ha at weekly intervals starting from 30 days after transplanting. This biological control method is eco-friendly and effective.", crop: "Rice", state: "Tamil Nadu", category: "Pest Control" },
  { answer: "Maintain field sanitation by removing stubbles after harvest. Avoid excess nitrogen application as it makes the plant susceptible. Use resistant varieties like Pusa Basmati 1509.", crop: "Paddy", state: "UP", category: "Pest Control" },
  { answer: "Integrated pest management approach: combine cultural practices (proper spacing, balanced fertilization), biological control (Trichogramma release), and chemical control (as last resort) for effective long-term management.", crop: "Rice", state: "AP", category: "Pest Control" },
];

const mockAiAnswer = `## Stem Borer Management in Paddy

Based on verified Kisan Call Centre data, here are the recommended approaches:

**1. Chemical Control**
- Apply **Carbofuran 3G** at 25 kg/ha in leaf whorls
- Spray **Chlorantraniliprole 18.5 SC** at 0.3 ml/litre
- Best timing: 30 days after transplanting

**2. Biological Control**
- Release **Trichogramma japonicum** at 1 lakh/ha
- Weekly intervals from 30 DAT
- Eco-friendly and sustainable

**3. Cultural Practices**
- Remove stubbles after harvest
- Avoid excess nitrogen fertilization
- Use resistant varieties (e.g., Pusa Basmati 1509)
- Maintain proper plant spacing

**4. Monitoring**
- Install light traps to track moth populations
- Take action when count exceeds 5 moths/trap/night

> ⚠️ Always consult your local agriculture officer before applying any new pesticide.`;

const Results = () => {
  const { t } = useLanguage();
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const query = params.get("q") || "";
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 1500);
    return () => clearTimeout(timer);
  }, [query]);

  return (
    <div className="min-h-screen bg-background pb-20 md:pb-0">
      {/* Sticky header */}
      <header className="sticky top-0 z-50 bg-card border-b border-border px-4 py-3">
        <div className="container max-w-2xl mx-auto flex items-center gap-3">
          <button onClick={() => navigate("/")} className="touch-target flex items-center justify-center">
            <ArrowLeft className="w-5 h-5 text-foreground" />
          </button>
          <p className="flex-1 text-body font-medium text-foreground line-clamp-1">{query}</p>
          <button onClick={() => navigate("/")} className="touch-target flex items-center justify-center">
            <PenLine className="w-5 h-5 text-muted-foreground" />
          </button>
        </div>
      </header>

      <main className="container max-w-2xl mx-auto px-4 py-4 space-y-4">
        {/* Related chips */}
        <div className="flex gap-2 overflow-x-auto pb-1 -mx-1 px-1">
          {["How to prevent blight?", "Organic pest control", "Paddy disease management"].map((q) => (
            <button
              key={q}
              onClick={() => navigate(`/results?q=${encodeURIComponent(q)}`)}
              className="flex-shrink-0 px-3 py-1.5 rounded-full bg-chip text-chip-foreground text-body-sm font-medium hover:bg-primary hover:text-primary-foreground transition-colors"
            >
              {q}
            </button>
          ))}
        </div>

        {/* Tabbed answers */}
        <Tabs defaultValue="database" className="w-full">
          <TabsList className="w-full grid grid-cols-2 h-12 rounded-xl bg-muted">
            <TabsTrigger value="database" className="rounded-lg text-body-sm font-semibold data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
              📚 {t("dbAnswers")} ({mockDbAnswers.length})
            </TabsTrigger>
            <TabsTrigger value="ai" className="rounded-lg text-body-sm font-semibold data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
              🤖 {t("aiAnswer")}
            </TabsTrigger>
          </TabsList>

          <TabsContent value="database" className="mt-4 space-y-3">
            {loading ? (
              Array.from({ length: 3 }).map((_, i) => <SkeletonCard key={i} />)
            ) : (
              mockDbAnswers.map((ans, i) => (
                <AnswerCard
                  key={i}
                  index={i + 1}
                  answer={ans.answer}
                  crop={ans.crop}
                  state={ans.state}
                  category={ans.category}
                />
              ))
            )}
          </TabsContent>

          <TabsContent value="ai" className="mt-4">
            {loading ? (
              <div className="bg-card rounded-xl border border-border p-6 space-y-3 animate-pulse">
                <div className="h-4 bg-muted rounded w-3/4" />
                <div className="h-4 bg-muted rounded w-full" />
                <div className="h-4 bg-muted rounded w-5/6" />
                <div className="h-4 bg-muted rounded w-2/3" />
                <div className="h-4 bg-muted rounded w-full" />
                <div className="h-4 bg-muted rounded w-4/5" />
              </div>
            ) : (
              <div className="bg-card rounded-xl border border-border p-5 space-y-4">
                <div className="prose prose-sm max-w-none text-foreground">
                  {mockAiAnswer.split("\n").map((line, i) => {
                    if (line.startsWith("## ")) return <h2 key={i} className="text-lg font-bold text-foreground mb-2">{line.replace("## ", "")}</h2>;
                    if (line.startsWith("**") && line.endsWith("**")) return <p key={i} className="font-bold text-foreground mt-3">{line.replace(/\*\*/g, "")}</p>;
                    if (line.startsWith("- ")) {
                      const text = line.replace("- ", "").replace(/\*\*(.*?)\*\*/g, "$1");
                      return <p key={i} className="text-body text-foreground pl-4 py-0.5">• {text}</p>;
                    }
                    if (line.startsWith("> ⚠️")) return (
                      <div key={i} className="flex items-start gap-2 p-3 rounded-lg bg-warning/10 border border-warning/30 mt-3">
                        <AlertTriangle className="w-5 h-5 text-warning flex-shrink-0 mt-0.5" />
                        <p className="text-body-sm text-foreground">{line.replace("> ⚠️ ", "")}</p>
                      </div>
                    );
                    if (line.trim() === "") return null;
                    return <p key={i} className="text-body text-foreground">{line}</p>;
                  })}
                </div>

                <div className="border-t border-border pt-3 space-y-2">
                  <p className="text-caption text-muted-foreground">Generated by IBM Watsonx Granite using verified KCC data</p>
                  <p className="text-caption text-muted-foreground italic">{t("disclaimer")}</p>
                </div>
              </div>
            )}
          </TabsContent>
        </Tabs>

        {/* Action buttons */}
        <div className="flex gap-3 pt-2">
          <Button variant="outline" className="flex-1 h-12 touch-target" onClick={() => navigate("/")}>
            <RotateCcw className="w-4 h-4 mr-2" />
            {t("askNewQuestion")}
          </Button>
          <Button variant="outline" className="h-12 touch-target px-4">
            <Bookmark className="w-4 h-4" />
          </Button>
          <Button variant="outline" className="h-12 touch-target px-4">
            <Phone className="w-4 h-4" />
          </Button>
        </div>
      </main>

      <BottomNav />
    </div>
  );
};

export default Results;
