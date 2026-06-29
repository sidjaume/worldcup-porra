import type { RankingRow } from "@/types/api";

export function RankingTable({ rows }: { rows: RankingRow[] }) {
  if (rows.length === 0) {
    return <p className="text-sm text-slate-600">No rankings yet.</p>;
  }

  return (
    <>
      <div className="grid gap-3 md:hidden">
        {rows.map((row) => (
          <article className="rounded-lg border border-line bg-white p-4" key={row.user_id}>
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-600">
                  Rank {row.rank}
                </p>
                <h3 className="truncate text-base font-bold">{row.display_name}</h3>
              </div>
              <p className="rounded-md bg-mint px-3 py-1 text-sm font-bold text-grass">
                {row.total_points} pts
              </p>
            </div>
            <dl className="mt-4 grid grid-cols-3 gap-3 text-sm">
              <div>
                <dt className="text-slate-600">Exact scores</dt>
                <dd className="font-semibold">{row.exact_scores}</dd>
              </div>
              <div>
                <dt className="text-slate-600">Winners</dt>
                <dd className="font-semibold">{row.correct_winners}</dd>
              </div>
              <div>
                <dt className="text-slate-600">Predictions</dt>
                <dd className="font-semibold">
                  {row.predictions_submitted}/{row.predictions_scored}
                </dd>
              </div>
            </dl>
          </article>
        ))}
      </div>
      <div className="hidden overflow-hidden rounded-lg border border-line md:block">
        <table className="w-full border-collapse bg-white text-left text-sm">
        <thead className="bg-mint text-ink">
          <tr>
            <th className="px-4 py-3 font-semibold">Rank</th>
            <th className="px-4 py-3 font-semibold">Player</th>
            <th className="px-4 py-3 font-semibold">Points</th>
            <th className="px-4 py-3 font-semibold">Exact scores</th>
            <th className="px-4 py-3 font-semibold">Correct winners</th>
            <th className="px-4 py-3 font-semibold">Predictions</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr className="border-t border-line" key={row.user_id}>
              <td className="px-4 py-3 font-bold">{row.rank}</td>
              <td className="px-4 py-3 font-medium">{row.display_name}</td>
              <td className="px-4 py-3">{row.total_points}</td>
              <td className="px-4 py-3">{row.exact_scores}</td>
              <td className="px-4 py-3">{row.correct_winners}</td>
              <td className="px-4 py-3">
                {row.predictions_submitted}/{row.predictions_scored}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      </div>
    </>
  );
}
