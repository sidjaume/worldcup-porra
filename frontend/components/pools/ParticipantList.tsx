import type { Participant } from "@/types/api";

export function ParticipantList({ participants }: { participants: Participant[] }) {
  return (
    <div className="overflow-hidden rounded-lg border border-line">
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
  );
}
