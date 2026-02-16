import { Home, Bookmark, Bell, Settings, HelpCircle } from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";
import { useLocation, useNavigate } from "react-router-dom";

const navItems = [
  { icon: Home, labelKey: "home", path: "/" },
  { icon: Bookmark, labelKey: "saved", path: "/saved" },
  { icon: Bell, labelKey: "notifications", path: "/notifications" },
  { icon: Settings, labelKey: "settings", path: "/settings" },
  { icon: HelpCircle, labelKey: "help", path: "/help" },
];

const BottomNav = () => {
  const { t } = useLanguage();
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 bg-card border-t border-border md:hidden">
      <div className="flex items-stretch justify-around">
        {navItems.map((item) => {
          const active = location.pathname === item.path;
          return (
            <button
              key={item.path}
              onClick={() => navigate(item.path)}
              className={`flex flex-col items-center justify-center gap-0.5 py-2 px-1 flex-1 touch-target transition-colors ${
                active
                  ? "text-primary"
                  : "text-muted-foreground"
              }`}
            >
              <item.icon className="w-5 h-5" />
              <span className="text-[11px] font-medium leading-tight">{t(item.labelKey)}</span>
            </button>
          );
        })}
      </div>
    </nav>
  );
};

export default BottomNav;
