import { Bell } from "lucide-react";
import Header from "@/components/Header";
import BottomNav from "@/components/BottomNav";

const Notifications = () => (
  <div className="min-h-screen bg-background pb-20 md:pb-0">
    <Header />
    <main className="container max-w-2xl mx-auto px-4 py-8 flex flex-col items-center justify-center text-center space-y-4">
      <div className="w-20 h-20 rounded-full bg-muted flex items-center justify-center">
        <Bell className="w-10 h-10 text-muted-foreground" />
      </div>
      <h2 className="text-xl font-bold text-foreground">No updates yet</h2>
      <p className="text-body text-muted-foreground">Government scheme updates will appear here</p>
    </main>
    <BottomNav />
  </div>
);

export default Notifications;
