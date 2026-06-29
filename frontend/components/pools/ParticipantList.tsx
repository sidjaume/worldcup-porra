import type { Participant } from "@/types/api";

export function ParticipantList({ participants }: { participants: Participant[] }) {
  if (participants.length === 0) {
    return <p className="text-sm text-slate-600">No active participants yet.</p>;
  }

  return (
    <>
      <div className="grid gap-3 md:hidden">
        {participants.map((participant) => (
          <article className="rounded-lg border border-line bg-white p-4" key={participant.user_id}>
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <h3 className="truncate font-semibold">{participant.display_name}</h3>
                <p className="mt-1 text-sm text-slate-600">
                  Joined {new Date(participant.joined_at).toLocaleDateString()}
                </p>
              </div>
              <span className="shrink-0 rounded-md bg-mint px-2 py-1 text-xs font-semibold capitalize text-grass">
                {participant.role}
              </span>
            </div>
          </article>
        ))}
      </div>
      <div className="hidden overflow-hidden rounded-lg border border-line md:block">
        <table className="w-full border-collapse bg-white text-left text-sm">
          <thead className="bg-mint text-ink">
            <tr>
              <th className="px-4 py-3 font-semibold">Participant</th>
              <th className="px-4 py-3 font-semibold">Role</th>
              <th className="px-4 py-3 font-semibold">Joined</th>
            </tr>
          </thead>
          <tbody>
            {participants.map((participant) => (
              <tr className="border-t border-line" key={participant.user_id}>
                <td className="px-4 py-3 font-medium">{participant.display_name}</td>
                <td className="px-4 py-3 capitalize text-slate-600">{participant.role}</td>
                <td className="px-4 py-3 text-slate-600">
                  {new Date(participant.joined_at).toLocaleDateString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
