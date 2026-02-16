const SkeletonCard = () => (
  <div className="bg-card rounded-xl border border-border p-4 space-y-3 animate-pulse">
    <div className="flex items-start gap-3">
      <div className="w-7 h-7 rounded-full bg-muted" />
      <div className="flex-1 space-y-2">
        <div className="h-4 bg-muted rounded w-full" />
        <div className="h-4 bg-muted rounded w-4/5" />
        <div className="h-4 bg-muted rounded w-3/5" />
      </div>
    </div>
    <div className="flex gap-2">
      <div className="h-6 bg-muted rounded-full w-16" />
      <div className="h-6 bg-muted rounded-full w-20" />
    </div>
  </div>
);

export default SkeletonCard;
