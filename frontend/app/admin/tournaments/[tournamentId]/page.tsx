import { redirect } from "next/navigation";
import {
  AdminAccessDeniedState,
  AdminOperations,
  NoTournamentsState,
} from "@/components/admin/AdminOperations";
import { AppShell } from "@/components/layout/AppShell";
import { ApiError } from "@/lib/api/client";
import { listMatches, listTeams, listTournaments } from "@/lib/api/tournaments";
import { requireSession } from "@/lib/auth/require-session";
import { STAGES } from "@/lib/format";
import type { TournamentStage } from "@/types/api";

export default async function AdminTournamentPage({
  params,
  searchParams,
}: {
  params: Promise<{ tournamentId: string }>;
  searchParams: Promise<{ stage?: TournamentStage }>;
}) {
  const { tournamentId } = await params;
  const { stage } = await searchParams;
  const activeStage = STAGES.some((item) => item.value === stage)
    ? stage!
    : "round_of_32";
  const session = await requireSession();

  try {
    const tournaments = await listTournaments(session.accessToken);
    const tournament = tournaments.find((item) => item.id === tournamentId);

    if (!tournament) {
      return (
        <AppShell user={session.user}>
          <NoTournamentsState />
        </AppShell>
      );
    }

    const [teams, matches] = await Promise.all([
      listTeams(session.accessToken, tournamentId),
      listMatches(session.accessToken, tournamentId, activeStage),
    ]);

    return (
      <AppShell user={session.user}>
        <AdminOperations
          activeStage={activeStage}
          matches={matches}
          teams={teams}
          tournament={tournament}
        />
      </AppShell>
    );
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      redirect("/auth/refresh");
    }
    if (error instanceof ApiError && error.status === 403) {
      return (
        <AppShell user={session.user}>
          <AdminAccessDeniedState />
        </AppShell>
      );
    }
    throw error;
  }
}
