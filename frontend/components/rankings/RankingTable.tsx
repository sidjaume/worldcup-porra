import type { RankingRow } from "@/types/api";

export function RankingTable({ rows }: { rows: RankingRow[] }) {
  if (rows.length === 0) {
    return <p className="text-sm text-slate-600">No rankings yet.</p>;
  }

  return (
    <div className="overflow-hidden rounded-lg border border-line">
      <table className="w-full border-collapse bg-white text-left text-sm">
        <thead className="bg-mint text-ink">
          <tr>
            <th className="px-4 py-3 font-semibold">Rank</th>
            <th className="px-4 py-3 font-semibold">Player</th>
            <th className="px-4 py-3 font-semibold">Points</th>
            <th className="px-4 py-3 font-semibold">Exact</th>
            <th className="px-4 py-3 font-semibold">Winners</th>
            <th className="px-4 py-3 font-semibold">Submitted</th>
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
  );
}
