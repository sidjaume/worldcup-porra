"use client";

import { useActionState, useId } from "react";
import { Save } from "lucide-react";
import { updatePoolAction } from "@/app/actions";
import { Button } from "@/components/ui/Button";
import { Field, FormMessage, FormSuccess, TextInput } from "@/components/ui/Field";
import type { PoolDetail } from "@/types/api";

export function PoolSettingsForm({ pool }: { pool: PoolDetail }) {
  const [state, action, pending] = useActionState(updatePoolAction, {});
  const feedbackId = useId();
  const describedBy = state.error || state.ok ? feedbackId : undefined;

  return (
    <form action={action} aria-describedby={describedBy} className="grid gap-4">
      <input name="pool_id" type="hidden" value={pool.id} />
      <Field label="Pool name">
        <TextInput
          aria-describedby={describedBy}
          aria-invalid={state.error ? true : undefined}
          defaultValue={pool.name}
          name="name"
          required
        />
      </Field>
      <label className="flex items-center gap-2 text-sm font-medium">
        <input defaultChecked={pool.is_active} name="is_active" type="checkbox" />
        Active
      </label>
      <FormMessage id={state.error ? feedbackId : undefined} message={state.error} />
      <FormSuccess id={state.ok ? feedbackId : undefined} message={state.ok ? "Saved." : undefined} />
      <Button disabled={pending} type="submit">
        <Save aria-hidden="true" size={16} />
        {pending ? "Saving" : "Save pool"}
      </Button>
    </form>
  );
}
