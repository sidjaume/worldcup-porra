import Link from "next/link";
import { STAGES } from "@/lib/format";
import type { TournamentStage } from "@/types/api";

export function StageTabs({
  activeStage,
  basePath,
}: {
  activeStage: TournamentStage;
  basePath: string;
}) {
  return (
    <nav aria-label="Prediction stage" className="flex gap-2 overflow-x-auto pb-1">
      {STAGES.map((stage) => (
        <Link
          aria-current={activeStage === stage.value ? "page" : undefined}
          className={`shrink-0 whitespace-nowrap rounded-full border px-4 py-2 text-sm font-semibold transition ${
            activeStage === stage.value
              ? "border-grass bg-grass text-white"
              : "border-line bg-white text-slate-600 hover:border-grass/40 hover:text-ink"
          }`}
          href={`${basePath}?stage=${stage.value}`}
          key={stage.value}
        >
          {stage.label}
        </Link>
      ))}
    </nav>
  );
}
