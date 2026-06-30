"use client";

import Link from "next/link";
import { useActionState, useEffect, useId, useMemo, useState } from "react";
import type { ReactNode } from "react";
import {
  Calculator,
  Clock,
  Plus,
  RefreshCw,
  Save,
  Search,
} from "lucide-react";
import {
  completeMatchAction,
  createMatchAction,
  rescoreMatchAction,
  syncTournamentAction,
  updateKickoffAction,
  updateMatchStatusAction,
  updateMatchTeamsAction,
} from "@/app/admin/actions";
import type { AdminActionState } from "@/app/admin/actions";
import { Button } from "@/components/ui/Button";
import { Field, FormMessage, FormSuccess, SelectInput, TextInput } from "@/components/ui/Field";
import {
  filterMatches,
  isStale,
  latestSyncDate,
  syncStatus,
  type SourceFilter,
} from "@/lib/admin-operations";
import {
  formatDateTime,
  matchStatusLabel,
  scoreLine,
  stageLabel,
  STAGES,
  teamName,
} from "@/lib/format";
import type {
  Match,
  MatchStatus,
  SyncResult,
  Team,
  Tournament,
  TournamentStage,
} from "@/types/api";

const STATUS_FILTERS: { label: string; value: "all" | MatchStatus }[] = [
  { label: "All", value: "all" },
  { label: "Scheduled", value: "scheduled" },
  { label: "Locked", value: "locked" },
  { label: "In progress", value: "in_progress" },
  { label: "Completed", value: "completed" },
  { label: "Cancelled", value: "cancelled" },
];
const SOURCE_FILTERS = [
  { label: "All", value: "all" },
  { label: "Provider", value: "provider" },
  { label: "Manual override", value: "manual" },
  { label: "Not synced", value: "not_synced" },
] as const satisfies { label: string; value: SourceFilter }[];
const OPERATIONAL_STATUS_OPTIONS: { label: string; value: Exclude<MatchStatus, "completed"> }[] = [
  { label: "Scheduled", value: "scheduled" },
  { label: "Locked", value: "locked" },
  { label: "In progress", value: "in_progress" },
  { label: "Cancelled", value: "cancelled" },
];

export function AdminOperations({
  activeStage,
  matches,
  teams,
  tournament,
}: {
  activeStage: TournamentStage;
  matches: Match[];
  teams: Team[];
  tournament: Tournament;
}) {
  const [statusFilter, setStatusFilter] = useState<"all" | MatchStatus>("all");
  const [sourceFilter, setSourceFilter] = useState<SourceFilter>("all");
  const [query, setQuery] = useState("");
  const [accessDenied, setAccessDenied] = useState(false);

  const latestProviderSyncAt = useMemo(() => latestSyncDate(matches), [matches]);
  const filteredMatches = useMemo(
    () => filterMatches(matches, statusFilter, sourceFilter, query),
    [matches, query, sourceFilter, statusFilter],
  );

  if (accessDenied) {
    return <AdminAccessDeniedState />;
  }

  return (
    <div className="grid gap-5">
      <header className="grid gap-2">
        <p className="text-sm font-semibold uppercase tracking-wide text-grass">
          {tournament.name} {tournament.year}
        </p>
        <h1 className="text-3xl font-bold">Tournament operations</h1>
        <p className="text-slate-600">
          Review provider sync and correct knockout match data.
        </p>
        <p className="text-sm text-slate-600">
          Last visible provider sync:{" "}
          <span className="font-semibold text-ink">
            {latestProviderSyncAt ? formatDateTime(latestProviderSyncAt.toISOString()) : "Not synced"}
          </span>
        </p>
      </header>

      <div className="grid gap-4 lg:grid-cols-[minmax(0,1.25fr)_minmax(280px,0.75fr)]">
        <SyncPanel
          latestProviderSyncAt={latestProviderSyncAt}
          matches={matches}
          onAccessDenied={() => setAccessDenied(true)}
          tournament={tournament}
        />
        <CreateMatchPanel
          onAccessDenied={() => setAccessDenied(true)}
          teams={teams}
          tournament={tournament}
        />
      </div>

      <section
        aria-label="Match filters"
        className="grid gap-3 rounded-lg border border-line bg-white p-4 shadow-soft"
      >
        <nav aria-label="Admin stage" className="flex gap-2 overflow-x-auto pb-1">
          {STAGES.map((stage) => (
            <Link
              aria-current={activeStage === stage.value ? "page" : undefined}
              className={`whitespace-nowrap rounded-md border px-3 py-2 text-sm font-semibold ${
                activeStage === stage.value
                  ? "border-grass bg-grass text-white"
                  : "border-line bg-white text-ink hover:bg-mint"
              }`}
              href={`/admin/tournaments/${tournament.id}?stage=${stage.value}`}
              key={stage.value}
            >
              {stage.label}
            </Link>
          ))}
        </nav>
        <div className="grid gap-3 md:grid-cols-[1fr_1fr_2fr]">
          <Field label="Status">
            <SelectInput
              value={statusFilter}
              onChange={(event) =>
                setStatusFilter(event.target.value as "all" | MatchStatus)
              }
            >
              {STATUS_FILTERS.map((filter) => (
                <option key={filter.value} value={filter.value}>
                  {filter.label}
                </option>
              ))}
            </SelectInput>
          </Field>
          <Field label="Source">
            <SelectInput
              value={sourceFilter}
              onChange={(event) => setSourceFilter(event.target.value as SourceFilter)}
            >
              {SOURCE_FILTERS.map((filter) => (
                <option key={filter.value} value={filter.value}>
                  {filter.label}
                </option>
              ))}
            </SelectInput>
          </Field>
          <Field label="Search teams or bracket position">
            <span className="relative">
              <Search
                aria-hidden="true"
                className="pointer-events-none absolute left-3 top-3 text-slate-500"
                size={16}
              />
              <TextInput
                className="w-full pl-9"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Spain, TBD, #3"
              />
            </span>
          </Field>
        </div>
      </section>

      <section aria-label="Match operations" className="grid gap-4 md:grid-cols-2">
        {matches.length === 0 ? (
          <EmptyMessage>No matches are available for this stage yet.</EmptyMessage>
        ) : filteredMatches.length === 0 ? (
          <EmptyMessage>No matches match the current filters.</EmptyMessage>
        ) : (
          filteredMatches.map((match) => (
            <MatchOperationCard
              key={match.id}
              match={match}
              onAccessDenied={() => setAccessDenied(true)}
              teams={teams}
              tournamentId={tournament.id}
            />
          ))
        )}
      </section>
    </div>
  );
}

export function AdminAccessDeniedState() {
  return (
    <section className="rounded-lg border border-coral bg-white p-5 shadow-soft" role="alert">
      <h1 className="text-2xl font-bold">Admin access is required.</h1>
      <p className="mt-2 text-sm text-slate-700">
        Your session is valid, but the backend did not authorize tournament
        operations for this account.
      </p>
    </section>
  );
}

export function NoTournamentsState() {
  return (
    <section className="rounded-lg border border-line bg-white p-5 text-sm text-slate-600 shadow-soft">
      No tournaments are available.
    </section>
  );
}

function SyncPanel({
  latestProviderSyncAt,
  matches,
  onAccessDenied,
  tournament,
}: {
  latestProviderSyncAt: Date | null;
  matches: Match[];
  onAccessDenied: () => void;
  tournament: Tournament;
}) {
  const [state, action, pending] = useActionState(syncTournamentAction, {});
  const feedbackId = useId();
  const status = syncStatus(latestProviderSyncAt);
  const manualOverrideCount = matches.filter((match) => match.admin_override).length;
  const hasSyncErrors = Boolean(state.syncResult?.errors.length);

  useAccessDeniedEffect(state, onAccessDenied);

  return (
    <section className="grid gap-4 rounded-lg border border-line bg-white p-4 shadow-soft">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-lg font-bold">Sync visibility</h2>
          <p className="text-sm text-slate-600">
            Match freshness is based on provider timestamps in loaded matches.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Badge tone={status === "Fresh" ? "good" : status === "Stale" ? "warn" : "neutral"}>
            {status}
          </Badge>
          <Badge tone="neutral">Manual overrides: {manualOverrideCount}</Badge>
          {hasSyncErrors ? <Badge tone="bad">Sync failed</Badge> : null}
        </div>
      </div>

      <form action={action} aria-describedby={feedbackId} className="grid gap-3">
        <input name="tournament_id" type="hidden" value={tournament.id} />
        <input name="year" type="hidden" value={tournament.year} />
        <ConfirmBox
          name="confirm_sync"
          text="Provider sync can update teams, kickoff times, statuses, and results. Manual overrides will be preserved by the backend."
        />
        <Button className="w-full sm:w-fit" disabled={pending} type="submit">
          <RefreshCw aria-hidden="true" size={16} />
          {pending ? "Running sync" : "Run sync"}
        </Button>
        <FormMessage id={state.error ? feedbackId : undefined} message={state.error} />
        {state.syncResult ? (
          state.syncResult.errors.length ? (
            <div
              className="grid gap-2 rounded-md border border-coral bg-white p-3 text-sm"
              id={feedbackId}
              role="alert"
            >
              <p className="font-semibold text-coral">Sync completed with errors.</p>
              <ul className="list-disc pl-5 text-slate-700">
                {state.syncResult.errors.map((error) => (
                  <li key={error}>{error}</li>
                ))}
              </ul>
              <p className="font-medium">
                Review affected matches and correct them manually.
              </p>
            </div>
          ) : (
            <div
              className="grid gap-2 rounded-md border border-line bg-mint p-3 text-sm"
              id={feedbackId}
              role="status"
            >
              <p className="font-semibold text-grass">Sync completed.</p>
              <SyncCounts result={state.syncResult} />
            </div>
          )
        ) : null}
      </form>
    </section>
  );
}

function CreateMatchPanel({
  onAccessDenied,
  teams,
  tournament,
}: {
  onAccessDenied: () => void;
  teams: Team[];
  tournament: Tournament;
}) {
  const [state, action, pending] = useActionState(createMatchAction, {});
  const feedbackId = useId();

  useAccessDeniedEffect(state, onAccessDenied);

  return (
    <section className="grid gap-4 rounded-lg border border-line bg-white p-4 shadow-soft">
      <div>
        <h2 className="text-lg font-bold">Create match</h2>
        <p className="text-sm text-slate-600">
          Add a missing knockout fixture through the documented admin endpoint.
        </p>
      </div>
      {teams.length === 0 ? (
        <p className="rounded-md bg-slate-100 px-3 py-2 text-sm text-slate-700">
          No teams are available yet. Run sync before creating matches.
        </p>
      ) : (
        <form action={action} aria-describedby={feedbackId} className="grid gap-3">
          <input name="tournament_id" type="hidden" value={tournament.id} />
          <div className="grid gap-3 sm:grid-cols-2">
            <Field label="Stage">
              <SelectInput name="stage" required>
                {STAGES.map((stage) => (
                  <option key={stage.value} value={stage.value}>
                    {stage.label}
                  </option>
                ))}
              </SelectInput>
            </Field>
            <Field label="Bracket position">
              <TextInput min={1} name="bracket_position" required type="number" />
            </Field>
          </div>
          <DateTimeLocalField label="Kickoff date and time" name="scheduled_at_iso" />
          <div className="grid gap-3 sm:grid-cols-2">
            <TeamSelect label="Home team" name="home_team_id" teams={teams} />
            <TeamSelect label="Away team" name="away_team_id" teams={teams} />
          </div>
          <ConfirmBox
            name="confirm_create"
            text="Create this knockout match? Review stage, position, teams, and kickoff before saving."
          />
          <FormMessage id={state.error ? feedbackId : undefined} message={state.error} />
          <FormSuccess id={state.ok ? feedbackId : undefined} message={state.message} />
          <Button disabled={pending} type="submit" variant="secondary">
            <Plus aria-hidden="true" size={16} />
            {pending ? "Creating match" : "Create match"}
          </Button>
        </form>
      )}
    </section>
  );
}

function MatchOperationCard({
  match,
  onAccessDenied,
  teams,
  tournamentId,
}: {
  match: Match;
  onAccessDenied: () => void;
  teams: Team[];
  tournamentId: string;
}) {
  const label = `${stageLabel(match.stage)} #${match.bracket_position}`;
  const winnerName =
    match.winner_team_id === match.home_team?.id
      ? teamName(match.home_team)
      : match.winner_team_id === match.away_team?.id
        ? teamName(match.away_team)
        : "TBD";

  return (
    <article className="grid gap-4 rounded-lg border border-line bg-white p-4 shadow-soft">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-grass">
            {label}
          </p>
          <h2 className="mt-1 text-xl font-bold">
            {teamName(match.home_team)} vs {teamName(match.away_team)}
          </h2>
        </div>
        <div className="flex flex-wrap justify-end gap-2">
          <Badge tone="neutral">{matchStatusLabel(match.status)}</Badge>
          <FreshnessBadge match={match} />
          {match.admin_override ? <Badge tone="warn">Manual override</Badge> : null}
        </div>
      </div>

      <dl className="grid grid-cols-2 gap-3 text-sm">
        <DataPoint label="Kickoff" value={formatDateTime(match.scheduled_at)} />
        <DataPoint label="Score" value={scoreLine(match)} />
        <DataPoint label="Advancing winner" value={winnerName} />
        <DataPoint label="Sync source" value={match.sync_source ?? "Not synced"} />
        <DataPoint
          label="Provider synced"
          value={
            match.provider_last_synced_at
              ? formatDateTime(match.provider_last_synced_at)
              : "Not synced"
          }
        />
      </dl>

      <div className="grid gap-2">
        {match.status !== "completed" ? (
          <>
            <details className="rounded-md border border-line p-3">
              <summary className="cursor-pointer font-semibold">
                Correct teams for {label}
              </summary>
              <TeamCorrectionForm
                label={label}
                match={match}
                onAccessDenied={onAccessDenied}
                teams={teams}
                tournamentId={tournamentId}
              />
            </details>
            <details className="rounded-md border border-line p-3">
              <summary className="cursor-pointer font-semibold">
                Correct status for {label}
              </summary>
              <StatusCorrectionForm
                label={label}
                match={match}
                onAccessDenied={onAccessDenied}
                tournamentId={tournamentId}
              />
            </details>
            <details className="rounded-md border border-line p-3">
              <summary className="cursor-pointer font-semibold">
                Correct kickoff for {label}
              </summary>
              <KickoffCorrectionForm
                label={label}
                match={match}
                onAccessDenied={onAccessDenied}
                tournamentId={tournamentId}
              />
            </details>
          </>
        ) : (
          <p className="rounded-md bg-slate-100 px-3 py-2 text-sm text-slate-600">
            Team, status, and kickoff correction are unavailable for completed matches.
          </p>
        )}

        {match.home_team && match.away_team ? (
          <details className="rounded-md border border-line p-3">
            <summary className="cursor-pointer font-semibold">
              {match.status === "completed" ? "Correct result" : "Enter result"} for{" "}
              {label}
            </summary>
            <ResultCorrectionForm
              label={label}
              match={match}
              onAccessDenied={onAccessDenied}
              tournamentId={tournamentId}
            />
          </details>
        ) : (
          <p className="rounded-md bg-slate-100 px-3 py-2 text-sm text-slate-600">
            Result entry is available when both teams are known.
          </p>
        )}

        {match.status === "completed" ? (
          <details className="rounded-md border border-line p-3">
            <summary className="cursor-pointer font-semibold">Rescore {label}</summary>
            <RescoreForm
              label={label}
              match={match}
              onAccessDenied={onAccessDenied}
              tournamentId={tournamentId}
            />
          </details>
        ) : null}
      </div>
    </article>
  );
}

function KickoffCorrectionForm({
  label,
  match,
  onAccessDenied,
  tournamentId,
}: {
  label: string;
  match: Match;
  onAccessDenied: () => void;
  tournamentId: string;
}) {
  const [state, action, pending] = useActionState(updateKickoffAction, {});
  const feedbackId = useId();

  useAccessDeniedEffect(state, onAccessDenied);

  return (
    <form action={action} aria-describedby={feedbackId} className="mt-3 grid gap-3">
      <input name="tournament_id" type="hidden" value={tournamentId} />
      <input name="match_id" type="hidden" value={match.id} />
      <p className="text-sm text-slate-700">
        Current kickoff: <span className="font-semibold">{formatDateTime(match.scheduled_at)}</span>.
        The backend uses kickoff time for prediction locking.
      </p>
      <DateTimeLocalField
        initialValue={match.scheduled_at}
        label="New kickoff date and time"
        name="scheduled_at_iso"
      />
      <ConfirmBox
        name="confirm_kickoff"
        text="Changing kickoff can change whether predictions are editable. Save this correction?"
      />
      <FormMessage id={state.error ? feedbackId : undefined} message={state.error} />
      <FormSuccess id={state.ok ? feedbackId : undefined} message={state.message} />
      <Button
        aria-label={`Save kickoff correction for ${label}`}
        disabled={pending}
        type="submit"
        variant="secondary"
      >
        <Clock aria-hidden="true" size={16} />
        {pending ? "Saving kickoff" : "Save kickoff correction"}
      </Button>
    </form>
  );
}

function TeamCorrectionForm({
  label,
  match,
  onAccessDenied,
  teams,
  tournamentId,
}: {
  label: string;
  match: Match;
  onAccessDenied: () => void;
  teams: Team[];
  tournamentId: string;
}) {
  const [state, action, pending] = useActionState(updateMatchTeamsAction, {});
  const feedbackId = useId();

  useAccessDeniedEffect(state, onAccessDenied);

  if (teams.length === 0) {
    return (
      <p className="mt-3 rounded-md bg-slate-100 px-3 py-2 text-sm text-slate-700">
        No teams are available yet. Run sync before correcting teams.
      </p>
    );
  }

  return (
    <form action={action} aria-describedby={feedbackId} className="mt-3 grid gap-3">
      <input name="tournament_id" type="hidden" value={tournamentId} />
      <input name="match_id" type="hidden" value={match.id} />
      <div className="grid gap-3 sm:grid-cols-2">
        <TeamSelect
          defaultValue={match.home_team?.id ?? ""}
          label="Home team"
          name="home_team_id"
          teams={teams}
        />
        <TeamSelect
          defaultValue={match.away_team?.id ?? ""}
          label="Away team"
          name="away_team_id"
          teams={teams}
        />
      </div>
      <ConfirmBox
        name="confirm_teams"
        text="Save this team correction? Either side may remain TBD, and the backend will mark the match as a manual override."
      />
      <FormMessage id={state.error ? feedbackId : undefined} message={state.error} />
      <FormSuccess id={state.ok ? feedbackId : undefined} message={state.message} />
      <Button
        aria-label={`Save team correction for ${label}`}
        disabled={pending}
        type="submit"
        variant="secondary"
      >
        <Save aria-hidden="true" size={16} />
        {pending ? "Saving teams" : "Save team correction"}
      </Button>
    </form>
  );
}

function StatusCorrectionForm({
  label,
  match,
  onAccessDenied,
  tournamentId,
}: {
  label: string;
  match: Match;
  onAccessDenied: () => void;
  tournamentId: string;
}) {
  const [state, action, pending] = useActionState(updateMatchStatusAction, {});
  const feedbackId = useId();

  useAccessDeniedEffect(state, onAccessDenied);

  return (
    <form action={action} aria-describedby={feedbackId} className="mt-3 grid gap-3">
      <input name="tournament_id" type="hidden" value={tournamentId} />
      <input name="match_id" type="hidden" value={match.id} />
      <Field label="Operational status">
        <SelectInput defaultValue={match.status} name="status" required>
          {OPERATIONAL_STATUS_OPTIONS.map((status) => (
            <option key={status.value} value={status.value}>
              {status.label}
            </option>
          ))}
        </SelectInput>
      </Field>
      <ConfirmBox
        name="confirm_status"
        text="Save this operational status correction? Completed results stay handled by the final-result form."
      />
      <FormMessage id={state.error ? feedbackId : undefined} message={state.error} />
      <FormSuccess id={state.ok ? feedbackId : undefined} message={state.message} />
      <Button
        aria-label={`Save status correction for ${label}`}
        disabled={pending}
        type="submit"
        variant="secondary"
      >
        <Save aria-hidden="true" size={16} />
        {pending ? "Saving status" : "Save status correction"}
      </Button>
    </form>
  );
}

function ResultCorrectionForm({
  label,
  match,
  onAccessDenied,
  tournamentId,
}: {
  label: string;
  match: Match;
  onAccessDenied: () => void;
  tournamentId: string;
}) {
  const [state, action, pending] = useActionState(completeMatchAction, {});
  const [homeGoals, setHomeGoals] = useState(String(match.home_score ?? ""));
  const [awayGoals, setAwayGoals] = useState(String(match.away_score ?? ""));
  const feedbackId = useId();
  const isTied =
    homeGoals !== "" &&
    awayGoals !== "" &&
    Number(homeGoals) === Number(awayGoals);

  useAccessDeniedEffect(state, onAccessDenied);

  return (
    <form action={action} aria-describedby={feedbackId} className="mt-3 grid gap-3">
      <input name="tournament_id" type="hidden" value={tournamentId} />
      <input name="match_id" type="hidden" value={match.id} />
      <input name="home_team_id" type="hidden" value={match.home_team?.id ?? ""} />
      <input name="away_team_id" type="hidden" value={match.away_team?.id ?? ""} />
      <div className="grid gap-3 sm:grid-cols-2">
        <Field label={`${teamName(match.home_team)} end-of-play goals`}>
          <TextInput
            min={0}
            name="home_score"
            onChange={(event) => setHomeGoals(event.target.value)}
            required
            type="number"
            value={homeGoals}
          />
        </Field>
        <Field label={`${teamName(match.away_team)} end-of-play goals`}>
          <TextInput
            min={0}
            name="away_score"
            onChange={(event) => setAwayGoals(event.target.value)}
            required
            type="number"
            value={awayGoals}
          />
        </Field>
      </div>
      {isTied ? (
        <p className="rounded-md bg-slate-100 px-3 py-2 text-sm text-slate-700">
          For penalty-decided matches, enter the tied end-of-play score and
          choose the advancing team. Do not include penalty shoot-out goals.
        </p>
      ) : null}
      <Field label="Advancing winner">
        <SelectInput defaultValue={match.winner_team_id ?? ""} name="winner_team_id" required>
          <option value="">Choose winner</option>
          <option value={match.home_team?.id}>{teamName(match.home_team)}</option>
          <option value={match.away_team?.id}>{teamName(match.away_team)}</option>
        </SelectInput>
      </Field>
      <ConfirmBox
        name="confirm_result"
        text={
          match.status === "completed"
            ? "Update this final result? Rankings may change after predictions are rescored."
            : "Save final result? The backend will advance the winner and score predictions."
        }
      />
      <FormMessage id={state.error ? feedbackId : undefined} message={state.error} />
      <FormSuccess id={state.ok ? feedbackId : undefined} message={state.message} />
      <Button
        aria-label={`Save final result for ${label}`}
        disabled={pending}
        type="submit"
      >
        <Save aria-hidden="true" size={16} />
        {pending ? "Saving result" : "Save final result"}
      </Button>
    </form>
  );
}

function RescoreForm({
  label,
  match,
  onAccessDenied,
  tournamentId,
}: {
  label: string;
  match: Match;
  onAccessDenied: () => void;
  tournamentId: string;
}) {
  const [state, action, pending] = useActionState(rescoreMatchAction, {});
  const feedbackId = useId();

  useAccessDeniedEffect(state, onAccessDenied);

  return (
    <form action={action} aria-describedby={feedbackId} className="mt-3 grid gap-3">
      <input name="tournament_id" type="hidden" value={tournamentId} />
      <input name="match_id" type="hidden" value={match.id} />
      <ConfirmBox
        name="confirm_rescore"
        text="Recalculate scores for this completed match? Rankings may change."
      />
      <FormMessage id={state.error ? feedbackId : undefined} message={state.error} />
      <FormSuccess id={state.ok ? feedbackId : undefined} message={state.message} />
      <Button
        aria-label={`Recalculate scores for ${label}`}
        disabled={pending}
        type="submit"
        variant="secondary"
      >
        <Calculator aria-hidden="true" size={16} />
        {pending ? "Rescoring" : "Recalculate scores"}
      </Button>
    </form>
  );
}

function DateTimeLocalField({
  initialValue,
  label,
  name,
}: {
  initialValue?: string;
  label: string;
  name: string;
}) {
  const [localValue, setLocalValue] = useState(toDateTimeLocalValue(initialValue));
  const isoValue = localValue ? new Date(localValue).toISOString() : "";

  return (
    <Field label={label}>
      <TextInput
        name={`${name}_local`}
        onChange={(event) => setLocalValue(event.target.value)}
        required
        type="datetime-local"
        value={localValue}
      />
      <input name={name} type="hidden" value={isoValue} />
    </Field>
  );
}

function TeamSelect({
  defaultValue,
  label,
  name,
  teams,
}: {
  defaultValue?: string;
  label: string;
  name: string;
  teams: Team[];
}) {
  return (
    <Field label={label}>
      <SelectInput defaultValue={defaultValue} name={name}>
        <option value="">TBD</option>
        {teams.map((team) => (
          <option key={team.id} value={team.id}>
            {team.name}
          </option>
        ))}
      </SelectInput>
    </Field>
  );
}

function ConfirmBox({ name, text }: { name: string; text: string }) {
  return (
    <label className="flex items-start gap-2 rounded-md bg-slate-100 px-3 py-2 text-sm text-slate-700">
      <input className="mt-1 size-4" name={name} type="checkbox" value="yes" />
      <span>{text}</span>
    </label>
  );
}

function useAccessDeniedEffect(
  state: AdminActionState,
  onAccessDenied: () => void,
) {
  useEffect(() => {
    if (state.accessDenied) {
      onAccessDenied();
    }
  }, [onAccessDenied, state.accessDenied]);
}

function SyncCounts({ result }: { result: SyncResult }) {
  return (
    <dl className="grid grid-cols-2 gap-2 text-slate-700">
      <DataPoint label="Teams created" value={String(result.teams_created)} />
      <DataPoint label="Teams updated" value={String(result.teams_updated)} />
      <DataPoint label="Matches created" value={String(result.matches_created)} />
      <DataPoint label="Matches updated" value={String(result.matches_updated)} />
    </dl>
  );
}

function DataPoint({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs font-semibold uppercase tracking-wide text-slate-500">
        {label}
      </dt>
      <dd className="font-medium text-ink">{value}</dd>
    </div>
  );
}

function EmptyMessage({ children }: { children: string }) {
  return (
    <p className="rounded-lg border border-line bg-white p-5 text-sm text-slate-600 shadow-soft md:col-span-2">
      {children}
    </p>
  );
}

function Badge({
  children,
  tone,
}: {
  children: ReactNode;
  tone: "bad" | "good" | "neutral" | "warn";
}) {
  const styles = {
    bad: "border-coral bg-white text-coral",
    good: "border-grass bg-mint text-grass",
    neutral: "border-line bg-slate-100 text-slate-700",
    warn: "border-gold bg-white text-gold",
  };

  return (
    <span className={`rounded-md border px-2 py-1 text-xs font-semibold ${styles[tone]}`}>
      {children}
    </span>
  );
}

function FreshnessBadge({ match }: { match: Match }) {
  if (!match.provider_last_synced_at) {
    return <Badge tone="neutral">Not synced</Badge>;
  }
  if (isStale(new Date(match.provider_last_synced_at))) {
    return <Badge tone="warn">Stale</Badge>;
  }
  return <Badge tone="good">Fresh</Badge>;
}

function toDateTimeLocalValue(value?: string): string {
  if (!value) {
    return "";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "";
  }
  const localDate = new Date(date.getTime() - date.getTimezoneOffset() * 60_000);
  return localDate.toISOString().slice(0, 16);
}
