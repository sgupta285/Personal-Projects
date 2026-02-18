import { Badge } from "./ui/badge";

interface TrendBadgeProps {
  stage: "emerging" | "rising" | "peaking" | "declining" | "dead";
  className?: string;
}

export function TrendBadge({ stage, className = "" }: TrendBadgeProps) {
  const stageConfig = {
    emerging: { 
      label: "Emerging", 
      variant: "default" as const, 
      color: "bg-gradient-to-r from-blue-500/10 to-blue-600/10 text-blue-700 border-blue-300 hover:from-blue-500/20 hover:to-blue-600/20" 
    },
    rising: { 
      label: "Rising", 
      variant: "default" as const, 
      color: "bg-gradient-to-r from-green-500/10 to-green-600/10 text-green-700 border-green-300 hover:from-green-500/20 hover:to-green-600/20" 
    },
    peaking: { 
      label: "Peaking", 
      variant: "default" as const, 
      color: "bg-gradient-to-r from-orange-500/10 to-orange-600/10 text-orange-700 border-orange-300 hover:from-orange-500/20 hover:to-orange-600/20" 
    },
    declining: { 
      label: "Declining", 
      variant: "default" as const, 
      color: "bg-gradient-to-r from-yellow-500/10 to-yellow-600/10 text-yellow-700 border-yellow-300 hover:from-yellow-500/20 hover:to-yellow-600/20" 
    },
    dead: { 
      label: "Dead", 
      variant: "secondary" as const, 
      color: "bg-gradient-to-r from-gray-400/10 to-gray-500/10 text-gray-700 border-gray-300 hover:from-gray-400/20 hover:to-gray-500/20" 
    },
  };

  const config = stageConfig[stage];

  return (
    <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border transition-all duration-300 cursor-default ${config.color} ${className}`}>
      {config.label}
    </span>
  );
}