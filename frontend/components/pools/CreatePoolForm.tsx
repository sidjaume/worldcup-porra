"use client";

import { useActionState, useId } from "react";
import { Plus } from "lucide-react";
import { createPoolAction } from "@/app/actions";
import { Button } from "@/components/ui/Button";
import { Field, FormMessage, SelectInput, TextInput } from "@/components/ui/Field";
import type { Tournament } from "@/types/api";

export function CreatePoolForm({ tournaments }: { tournaments: Tournament[] }) {
  const [state, action, pending] = useActionState(createPoolAction, {});
  const feedbackId = useId();

  return (
    <form
      action={action}
      aria-describedby={state.error ? feedbackId : undefined}
      className="grid gap-4"
    >
      <Field label="Pool name">
        <TextInput
          aria-describedby={state.error ? feedbackId : undefined}
          aria-invalid={state.error ? true : undefined}
          name="name"
          placeholder="Friends and family"
          required
        />
      </Field>
      <Field label="Tournament">
        <SelectInput
          aria-describedby={state.error ? feedbackId : undefined}
          aria-invalid={state.error ? true : undefined}
          name="tournament_id"
          required
        >
          <option value="">Select tournament</option>
          {tournaments.map((tournament) => (
            <option key={tournament.id} value={tournament.id}>
              {tournament.name}
            </option>
          ))}
        </SelectInput>
      </Field>
      <FormMessage id={feedbackId} message={state.error} />
      <Button disabled={pending} type="submit">
        <Plus aria-hidden="true" size={16} />
        {pending ? "Creating" : "Create pool"}
      </Button>
    </form>
  );
}
