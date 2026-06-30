"use client";

import { useActionState, useId, useState } from "react";
import { Send } from "lucide-react";
import { submitPredictionAction } from "@/app/actions";
import { Button } from "@/components/ui/Button";
import { Field, FormMessage, FormSuccess, SelectInput, TextInput } from "@/components/ui/Field";
import type { Prediction } from "@/types/api";

export function PredictionForm({
  awayTeamName,
  awayTeamId,
  homeTeamName,
  homeTeamId,
  matchId,
  poolId,
  prediction,
}: {
  awayTeamName: string;
  awayTeamId: string | null;
  homeTeamName: string;
  homeTeamId: string | null;
  matchId: string;
  poolId: string;
  prediction?: Prediction;
}) {
  const [state, action, pending] = useActionState(submitPredictionAction, {});
  const [homeGoals, setHomeGoals] = useState(
    prediction?.predicted_home_goals?.toString() ?? "",
  );
  const [awayGoals, setAwayGoals] = useState(
    prediction?.predicted_away_goals?.toString() ?? "",
  );
  const feedbackId = useId();
  const describedBy = state.error || state.ok ? feedbackId : undefined;
  const isTied =
    homeGoals !== "" &&
    awayGoals !== "" &&
    Number(homeGoals) === Number(awayGoals);
  const hasKnownTeams = Boolean(homeTeamId && awayTeamId);

  return (
    <form
      action={action}
      aria-describedby={describedBy}
      className="grid gap-3 sm:grid-cols-[1fr_1fr_auto] sm:items-end"
    >
      <input name="pool_id" type="hidden" value={poolId} />
      <input name="match_id" type="hidden" value={matchId} />
      <Field label={`${homeTeamName} goals`}>
        <TextInput
          aria-describedby={describedBy}
          aria-invalid={state.error ? true : undefined}
          inputMode="numeric"
          min={0}
          name="predicted_home_goals"
          onChange={(event) => setHomeGoals(event.target.value)}
          placeholder={homeTeamName}
          required
          type="number"
          value={homeGoals}
        />
      </Field>
      <Field label={`${awayTeamName} goals`}>
        <TextInput
          aria-describedby={describedBy}
          aria-invalid={state.error ? true : undefined}
          inputMode="numeric"
          min={0}
          name="predicted_away_goals"
          onChange={(event) => setAwayGoals(event.target.value)}
          placeholder={awayTeamName}
          required
          type="number"
          value={awayGoals}
        />
      </Field>
      <Button disabled={pending} type="submit">
        <Send aria-hidden="true" size={16} />
        {pending ? "Saving" : "Save"}
      </Button>
      {isTied ? (
        hasKnownTeams ? (
          <div className="sm:col-span-3">
            <Field label="Advancing winner">
              <SelectInput
                aria-describedby={describedBy}
                aria-invalid={state.error ? true : undefined}
                defaultValue={prediction?.predicted_winner_team_id ?? ""}
                name="predicted_winner_team_id"
                required
              >
                <option value="">Choose advancing team</option>
                <option value={homeTeamId ?? ""}>{homeTeamName}</option>
                <option value={awayTeamId ?? ""}>{awayTeamName}</option>
              </SelectInput>
            </Field>
          </div>
        ) : (
          <p className="rounded-md bg-slate-100 px-3 py-2 text-sm text-slate-700 sm:col-span-3">
            Tied predictions need known teams before an advancing winner can be selected.
          </p>
        )
      ) : (
        <input name="predicted_winner_team_id" type="hidden" value="" />
      )}
      <div className="sm:col-span-3">
        <FormMessage id={state.error ? feedbackId : undefined} message={state.error} />
        <FormSuccess id={state.ok ? feedbackId : undefined} message={state.ok ? "Prediction saved." : undefined} />
      </div>
    </form>
  );
}
