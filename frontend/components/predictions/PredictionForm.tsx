"use client";

import { useActionState, useId } from "react";
import { Send } from "lucide-react";
import { submitPredictionAction } from "@/app/actions";
import { Button } from "@/components/ui/Button";
import { Field, FormMessage, FormSuccess, TextInput } from "@/components/ui/Field";
import type { Prediction } from "@/types/api";

export function PredictionForm({
  awayTeamName,
  homeTeamName,
  matchId,
  poolId,
  prediction,
}: {
  awayTeamName: string;
  homeTeamName: string;
  matchId: string;
  poolId: string;
  prediction?: Prediction;
}) {
  const [state, action, pending] = useActionState(submitPredictionAction, {});
  const feedbackId = useId();
  const describedBy = state.error || state.ok ? feedbackId : undefined;

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
          defaultValue={prediction?.predicted_home_goals}
          inputMode="numeric"
          min={0}
          name="predicted_home_goals"
          placeholder={homeTeamName}
          required
          type="number"
        />
      </Field>
      <Field label={`${awayTeamName} goals`}>
        <TextInput
          aria-describedby={describedBy}
          aria-invalid={state.error ? true : undefined}
          defaultValue={prediction?.predicted_away_goals}
          inputMode="numeric"
          min={0}
          name="predicted_away_goals"
          placeholder={awayTeamName}
          required
          type="number"
        />
      </Field>
      <Button disabled={pending} type="submit">
        <Send aria-hidden="true" size={16} />
        {pending ? "Saving" : "Save"}
      </Button>
      <div className="sm:col-span-3">
        <FormMessage id={state.error ? feedbackId : undefined} message={state.error} />
        <FormSuccess id={state.ok ? feedbackId : undefined} message={state.ok ? "Prediction saved." : undefined} />
      </div>
    </form>
  );
}
