"use client";

import { useActionState } from "react";
import { Send } from "lucide-react";
import { submitPredictionAction } from "@/app/actions";
import { Button } from "@/components/ui/Button";
import { FormMessage, TextInput } from "@/components/ui/Field";
import type { Prediction } from "@/types/api";

export function PredictionForm({
  matchId,
  poolId,
  prediction,
}: {
  matchId: string;
  poolId: string;
  prediction?: Prediction;
}) {
  const [state, action, pending] = useActionState(submitPredictionAction, {});

  return (
    <form action={action} className="grid gap-3 sm:grid-cols-[1fr_1fr_auto]">
      <input name="pool_id" type="hidden" value={poolId} />
      <input name="match_id" type="hidden" value={matchId} />
      <TextInput
        aria-label="Home goals"
        defaultValue={prediction?.predicted_home_goals}
        min={0}
        name="predicted_home_goals"
        placeholder="Home"
        required
        type="number"
      />
      <TextInput
        aria-label="Away goals"
        defaultValue={prediction?.predicted_away_goals}
        min={0}
        name="predicted_away_goals"
        placeholder="Away"
        required
        type="number"
      />
      <Button disabled={pending} type="submit">
        <Send aria-hidden="true" size={16} />
        Save
      </Button>
      <div className="sm:col-span-3">
        <FormMessage message={state.error} />
        {state.ok ? <p className="text-sm font-medium text-grass">Prediction saved.</p> : null}
      </div>
    </form>
  );
}
