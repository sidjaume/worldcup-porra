"use client";

import { useActionState } from "react";
import { Plus } from "lucide-react";
import { createPoolAction } from "@/app/actions";
import { Button } from "@/components/ui/Button";
import { Field, FormMessage, SelectInput, TextInput } from "@/components/ui/Field";
import type { Tournament } from "@/types/api";

export function CreatePoolForm({ tournaments }: { tournaments: Tournament[] }) {
  const [state, action, pending] = useActionState(createPoolAction, {});

  return (
    <form action={action} className="grid gap-4">
      <Field label="Pool name">
        <TextInput name="name" placeholder="Friends and family" required />
      </Field>
      <Field label="Tournament">
        <SelectInput name="tournament_id" required>
          <option value="">Select tournament</option>
          {tournaments.map((tournament) => (
            <option key={tournament.id} value={tournament.id}>
              {tournament.name}
            </option>
          ))}
        </SelectInput>
      </Field>
      <FormMessage message={state.error} />
      <Button disabled={pending} type="submit">
        <Plus aria-hidden="true" size={16} />
        Create pool
      </Button>
    </form>
  );
}
